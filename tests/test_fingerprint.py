"""Test cho T2/T3.

Các ngưỡng trong file này là **hợp đồng đã đo**, không phải kỳ vọng. Hai test
`documents_*` khoá lại giới hạn đã biết của phương pháp: chúng trượt khi hành vi
đổi, kể cả đổi theo hướng tốt lên — và lúc đó phải cập nhật ADR-0007 chứ không
phải sửa con số cho qua.
"""

import numpy as np
import pytest
import soundfile as sf

from ml.dataops.fingerprint import (
    FingerprintConfig,
    best_alignment,
    content_hash,
    fingerprint,
    fit_standardizer,
    frame_validity,
    global_vector,
    load_pcm,
    quantize_int16,
)

CONFIG = FingerprintConfig()
SAMPLE_RATE = 16_000


def _tone(seconds: float, frequency: float = 440.0) -> np.ndarray:
    time = np.linspace(0.0, seconds, int(seconds * SAMPLE_RATE), endpoint=False)
    return (0.5 * np.sin(2 * np.pi * frequency * time)).astype(np.float32)


def _noise(seconds: float, seed: int) -> np.ndarray:
    generator = np.random.default_rng(seed)
    return generator.standard_normal(int(seconds * SAMPLE_RATE)).astype(np.float32) * 0.2


def _resample_roundtrip(waveform: np.ndarray, tmp_path, name: str) -> np.ndarray:
    """Mô phỏng đúng đường đi xuyên dataset: lưu ở 44.1 kHz rồi decode về 16 kHz."""
    import librosa

    path = tmp_path / f"{name}.wav"
    upsampled = librosa.resample(waveform, orig_sr=SAMPLE_RATE, target_sr=44_100)
    sf.write(path, upsampled, 44_100, subtype="PCM_16")
    return load_pcm(path)


# ---------- T2 ----------


def test_content_hash_ignores_container(tmp_path) -> None:
    """Cùng mẫu PCM, khác container → cùng hash. Đây là điều T2 hứa."""
    samples = quantize_int16(_noise(2.0, seed=1))
    wav, flac = tmp_path / "a.wav", tmp_path / "a.flac"
    sf.write(wav, samples, SAMPLE_RATE, subtype="PCM_16")
    sf.write(flac, samples, SAMPLE_RATE, subtype="PCM_16")

    assert wav.read_bytes() != flac.read_bytes()
    assert content_hash(load_pcm(wav)) == content_hash(load_pcm(flac))


def test_content_hash_reproduces_stored_pcm(tmp_path) -> None:
    """Hash phải bằng hash của chính int16 đã lưu — không lệch một LSB nào."""
    samples = quantize_int16(_noise(1.0, seed=2))
    path = tmp_path / "stored.wav"
    sf.write(path, samples, SAMPLE_RATE, subtype="PCM_16")

    np.testing.assert_array_equal(quantize_int16(load_pcm(path)), samples)


def test_content_hash_separates_different_audio() -> None:
    assert content_hash(_noise(1.0, seed=3)) != content_hash(_noise(1.0, seed=4))


def test_quantize_clips_to_int16_range() -> None:
    quantized = quantize_int16(np.array([-2.0, 0.0, 2.0], dtype=np.float32))
    assert quantized.tolist() == [-32768, 0, 32767]


def test_documents_t2_cannot_catch_bit_depth_change(tmp_path) -> None:
    """Giới hạn đã đo: T2 trượt khi đổi bit-depth, T3 bắt được. DATA_PLAN §7.2
    ngụ ý T2 lo được việc này — đo cho thấy không."""
    waveform = _noise(3.0, seed=5)
    wide, narrow = tmp_path / "w24.wav", tmp_path / "w16.wav"
    sf.write(wide, waveform, SAMPLE_RATE, subtype="PCM_24")
    sf.write(narrow, waveform, SAMPLE_RATE, subtype="PCM_16")
    loaded_wide, loaded_narrow = load_pcm(wide), load_pcm(narrow)

    assert content_hash(loaded_wide) != content_hash(loaded_narrow)
    mismatch = quantize_int16(loaded_wide) != quantize_int16(loaded_narrow)
    assert mismatch.mean() > 0.4  # lệch hệ thống, không phải biên hiếm

    match = best_alignment(
        fingerprint(loaded_wide, CONFIG), fingerprint(loaded_narrow, CONFIG), CONFIG
    )
    assert match.similarity == pytest.approx(1.0, abs=1e-4)


# ---------- T3 ----------


def test_fingerprint_shape_and_normalization() -> None:
    matrix = fingerprint(_noise(5.0, seed=6), CONFIG)

    assert matrix.shape == (9, CONFIG.dimensions)  # 5 s, frame 1 s, hop 0.5 s
    assert CONFIG.dimensions == 40
    np.testing.assert_allclose(np.linalg.norm(matrix, axis=1), 1.0, atol=1e-5)


def test_fingerprint_handles_audio_shorter_than_one_frame() -> None:
    assert fingerprint(_noise(0.4, seed=7), CONFIG).shape == (1, CONFIG.dimensions)


def test_fingerprint_is_invariant_to_gain() -> None:
    waveform = _noise(4.0, seed=8)
    np.testing.assert_allclose(
        fingerprint(waveform * 0.1, CONFIG), fingerprint(waveform * 0.9, CONFIG), atol=1e-4
    )


def test_fingerprint_survives_resample_roundtrip(tmp_path) -> None:
    """Mọi so khớp DataSEC↔DataSED đều qua một lần resample. Tín hiệu trắng là
    trường hợp xấu nhất vì có năng lượng sát Nyquist."""
    waveform = _noise(6.0, seed=9)
    resampled = _resample_roundtrip(waveform, tmp_path, "rt")

    match = best_alignment(fingerprint(waveform, CONFIG), fingerprint(resampled, CONFIG), CONFIG)

    assert match.similarity > 0.99


def test_best_alignment_finds_shifted_excerpt() -> None:
    source = _noise(12.0, seed=10)
    whole = fingerprint(source, CONFIG)
    excerpt = fingerprint(source[4 * SAMPLE_RATE : 10 * SAMPLE_RATE], CONFIG)

    match = best_alignment(excerpt, whole, CONFIG)

    assert match.similarity > 0.99
    assert match.overlap_s >= 3.0
    assert match.lag_frames == 8  # trễ 4 s, hop 0.5 s


def test_best_alignment_scores_structurally_different_audio_low() -> None:
    tone = fingerprint(_tone(8.0), CONFIG)
    noise = fingerprint(_noise(8.0, seed=11), CONFIG)

    assert best_alignment(tone, noise, CONFIG).similarity < 0.5


def test_documents_flat_spectrum_negatives_score_high() -> None:
    """Hai nguồn nhiễu trắng **không liên quan** vẫn đạt ~0.88, tức trên ngưỡng
    review 0.85 của DATA_PLAN §7.3. Đây là bằng chứng ngưỡng mặc định phải được
    hiệu chuẩn trên negative thật, không phải hằng số tin được."""
    left = fingerprint(_noise(8.0, seed=12), CONFIG)
    right = fingerprint(_noise(8.0, seed=13), CONFIG)

    assert best_alignment(left, right, CONFIG).similarity > 0.85


def test_best_alignment_rejects_overlap_below_minimum() -> None:
    matrix = fingerprint(_noise(2.0, seed=14), CONFIG)

    match = best_alignment(matrix, matrix, CONFIG, min_overlap_s=30.0)

    assert match.overlap_frames == 0
    assert match.similarity == 0.0


def test_overlap_seconds_matches_frame_geometry() -> None:
    assert CONFIG.overlap_seconds(1) == pytest.approx(1.0)
    assert CONFIG.overlap_seconds(5) == pytest.approx(3.0)
    assert CONFIG.frames_for_seconds(3.0) == 5


def test_global_vector_is_unit_norm() -> None:
    vector = global_vector(fingerprint(_noise(6.0, seed=15), CONFIG))
    assert np.linalg.norm(vector) == pytest.approx(1.0, abs=1e-5)


def test_fingerprint_rejects_empty_audio() -> None:
    with pytest.raises(ValueError):
        fingerprint(np.array([], dtype=np.float32), CONFIG)


# ---------- frame lặng và chuẩn hoá corpus ----------


def test_silent_frames_do_not_penalise_self_similarity() -> None:
    """Một cặp DataSED byte-identical đo được chỉ 0.95 = 57/60 vì 3 frame lặng.
    Frame không mang thông tin phải bị loại khỏi trung bình, không tính là 0."""
    waveform = np.concatenate([_noise(4.0, seed=20), np.zeros(3 * SAMPLE_RATE, np.float32)])
    matrix = fingerprint(waveform, CONFIG)

    assert not frame_validity(matrix).all()  # có frame lặng thật
    assert best_alignment(matrix, matrix, CONFIG).similarity == pytest.approx(1.0, abs=1e-6)


def test_frame_validity_flags_zero_rows() -> None:
    matrix = np.zeros((3, CONFIG.dimensions), dtype=np.float32)
    matrix[1, 0] = 1.0
    assert frame_validity(matrix).tolist() == [False, True, False]


def test_standardizer_preserves_identity_and_unit_norm() -> None:
    matrices = [fingerprint(_noise(5.0, seed=seed), CONFIG) for seed in (21, 22, 23)]
    standardizer = fit_standardizer(matrices)
    applied = standardizer.apply(matrices[0])

    np.testing.assert_allclose(np.linalg.norm(applied, axis=1), 1.0, atol=1e-5)
    assert best_alignment(applied, applied, CONFIG).similarity == pytest.approx(1.0, abs=1e-6)


def test_standardizer_keeps_silent_frames_invalid() -> None:
    matrices = [fingerprint(_noise(5.0, seed=24), CONFIG)]
    silent = np.zeros((2, CONFIG.dimensions), dtype=np.float32)
    applied = fit_standardizer(matrices).apply(np.vstack([matrices[0], silent]))

    assert frame_validity(applied)[-2:].tolist() == [False, False]


def test_standardizer_checksum_changes_with_statistics() -> None:
    first = fit_standardizer([fingerprint(_noise(5.0, seed=25), CONFIG)])
    second = fit_standardizer([fingerprint(_tone(5.0), CONFIG)])
    assert first.checksum != second.checksum


def test_fit_standardizer_rejects_all_silent_corpus() -> None:
    with pytest.raises(ValueError):
        fit_standardizer([np.zeros((4, CONFIG.dimensions), dtype=np.float32)])
