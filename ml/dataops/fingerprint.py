"""Content hashing (T2) and acoustic fingerprinting (T3) for the D3 dedup gate.

DATA_PLAN §7.2 định nghĩa ba tầng. T1 (SHA-256 trên bytes) đã nằm trong
`inventory.py`. Module này lo T2 và T3.

Vì sao T2 hash trên PCM **lượng tử hoá 16-bit**: cùng một bản ghi lưu ở 16-bit và
24-bit, sau khi decode sang float và resample 16 kHz, gần như chắc chắn **không**
bằng nhau từng bit. So khớp float là so khớp vô nghĩa. Lượng tử hoá về int16
trước khi hash biến "khớp tuyệt đối" thành một định nghĩa vận hành được.

Ba chi tiết của T3 lệch khỏi cách đọc chữ nghĩa của DATA_PLAN §7.3, đều vì đo
được là cách đọc kia hỏng (xem ADR-0007):

1. **Bỏ hệ số MFCC thứ 0.** `C0` là log-năng lượng nên phụ thuộc gain. Trích
   đoạn và file gốc có peak khác nhau → sau peak-normalize, `C0` lệch mạnh và
   chiếm gần hết norm của vector, kéo cosine của hai đoạn **giống hệt nhau**
   xuống 0.15. Lấy `n_mfcc = 21` rồi bỏ `C0` cho đúng 20 hệ số như đặc tả.
2. **Delta gộp bằng trung bình trị tuyệt đối.** Trung bình có dấu của delta trên
   một cửa sổ triệt tiêu về gần 0 (đo được: norm 0.25 so với 13.9 của nửa MFCC),
   tức 20 trong 40 chiều gần như không mang thông tin.
3. **Chuẩn hoá L2 từng nửa trước khi ghép.** Nếu không, nửa nào có thang lớn hơn
   sẽ quyết định toàn bộ cosine.
4. **`fmax = 7000` thay vì Nyquist 8000.** DataSEC là 16 kHz còn DataSED là
   44.1 kHz, nên mọi so khớp xuyên dataset đều đi qua một lần resample. Dải sát
   Nyquist chính là dải mà bộ lọc chống chồng phổ của resampler can thiệp. Đo
   được: với tín hiệu trắng, một vòng resample 16k→44.1k→16k kéo cosine của hai
   bản **cùng nội dung** xuống 0.577 khi `fmax = 8000`, và giữ nguyên 1.000 khi
   `fmax = 7000`.

Giới hạn đã đo của T2: nó **không** bắt được đổi bit-depth. Giữa PCM_16 và
PCM_24 của cùng một tín hiệu, 49.5% mẫu lệch đúng 1 LSB — lệch hệ thống ở tầng
libsndfile, không phải trường hợp biên hiếm. Không ngưỡng bit nào vá được vì
lệch tỷ lệ thuận. Phần này để T3 lo: cặp 24-bit/16-bit cho cosine đúng 1.000.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import librosa
import numpy as np

PCM_SAMPLE_RATE = 16_000
INT16_SCALE = 32_768.0
INT16_MIN = -32_768
INT16_MAX = 32_767


@dataclass(frozen=True)
class FingerprintConfig:
    """Tham số T3 theo DATA_PLAN §7.3."""

    sample_rate: int = PCM_SAMPLE_RATE
    frame_s: float = 1.0
    hop_s: float = 0.5
    n_mfcc: int = 21  # 21 hệ số, bỏ C0 → còn đúng 20 như đặc tả
    n_fft: int = 1_024
    mfcc_hop_length: int = 160
    fmax: float = 7_000.0  # chặn dưới Nyquist: xem chú thích (4) ở đầu module

    @property
    def dimensions(self) -> int:
        return (self.n_mfcc - 1) * 2

    @property
    def checksum(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def overlap_seconds(self, frames: int) -> float:
        """Thời lượng thật mà `frames` frame chồng lấp phủ."""
        if frames <= 0:
            return 0.0
        return self.frame_s + self.hop_s * (frames - 1)

    def frames_for_seconds(self, seconds: float) -> int:
        """Số frame tối thiểu để phủ `seconds` giây."""
        if seconds <= self.frame_s:
            return 1
        return int(np.ceil((seconds - self.frame_s) / self.hop_s)) + 1


def load_pcm(path: Path, sample_rate: int = PCM_SAMPLE_RATE) -> np.ndarray:
    """Decode về mono float32 ở `sample_rate`."""
    waveform, _ = librosa.load(path, sr=sample_rate, mono=True)
    if waveform.size == 0:
        raise ValueError(f"Empty audio: {path}")
    return waveform.astype(np.float32, copy=False)


def quantize_int16(waveform: np.ndarray) -> np.ndarray:
    """Lượng tử hoá theo đúng thang libsndfile dùng khi đọc PCM_16 (2^15)."""
    scaled = np.round(np.clip(waveform, -1.0, 1.0) * INT16_SCALE)
    return np.clip(scaled, INT16_MIN, INT16_MAX).astype(np.int16)


def content_hash(waveform: np.ndarray) -> str:
    """T2: SHA-256 trên PCM đã decode, resample và lượng tử hoá 16-bit."""
    return hashlib.sha256(quantize_int16(waveform).tobytes()).hexdigest()


def fingerprint(waveform: np.ndarray, config: FingerprintConfig) -> np.ndarray:
    """T3: chuỗi vector (MFCC 20 + delta) đã chuẩn hoá L2, một vector mỗi frame.

    Trả về mảng `(n_frames, 40)` float32. File ngắn hơn một frame vẫn sinh đúng
    một frame — loại bỏ ở đây sẽ làm clip ngắn không bao giờ bị đối chiếu.
    """
    if waveform.ndim != 1:
        raise ValueError("Expected mono waveform")
    if waveform.size == 0:
        raise ValueError("Cannot fingerprint empty audio")

    peak = float(np.max(np.abs(waveform)))
    normalized = waveform / peak if peak > 0 else waveform

    frame_length = int(round(config.frame_s * config.sample_rate))
    hop_length = int(round(config.hop_s * config.sample_rate))
    if normalized.size < frame_length:
        normalized = np.pad(normalized, (0, frame_length - normalized.size))

    starts = range(0, normalized.size - frame_length + 1, hop_length)
    vectors = [
        _frame_vector(normalized[start : start + frame_length], config) for start in starts
    ]
    stacked = np.stack(vectors).astype(np.float32)
    norms = np.linalg.norm(stacked, axis=1, keepdims=True)
    return stacked / np.maximum(norms, 1e-8)


def _frame_vector(frame: np.ndarray, config: FingerprintConfig) -> np.ndarray:
    mfcc = librosa.feature.mfcc(
        y=frame,
        sr=config.sample_rate,
        n_mfcc=config.n_mfcc,
        n_fft=config.n_fft,
        hop_length=config.mfcc_hop_length,
        fmax=config.fmax,
    )[1:]  # bỏ C0: log-năng lượng, phụ thuộc gain
    delta = librosa.feature.delta(mfcc) if mfcc.shape[1] > 2 else np.zeros_like(mfcc)
    return np.concatenate(
        [_unit(mfcc.mean(axis=1)), _unit(np.abs(delta).mean(axis=1))]
    )


def _unit(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    return vector / norm if norm > 0 else vector


@dataclass(frozen=True)
class MatchResult:
    similarity: float
    overlap_frames: int
    overlap_s: float
    lag_frames: int


VALID_NORM_MIN = 0.5


def frame_validity(matrix: np.ndarray) -> np.ndarray:
    """Frame tĩnh lặng cho vector 0 và không mang thông tin.

    Tính chúng vào trung bình cosine là phạt oan file có khoảng lặng: đo được
    một cặp DataSED **byte-identical** chỉ đạt 0.95 = 57/60 vì 3 frame lặng.
    """
    return np.linalg.norm(matrix, axis=1) > VALID_NORM_MIN


@dataclass(frozen=True)
class Standardizer:
    """Chuẩn hoá z-score theo thống kê corpus, ước lượng trên frame hợp lệ.

    Không có bước này, cosine bị chi phối bởi hình dạng phổ **trung bình** mà mọi
    bản ghi môi trường đều chia sẻ: đo được 52.6% cặp ngẫu nhiên khác nhãn vượt
    ngưỡng review 0.85, và negative max (0.983) còn cao hơn positive min. Sau khi
    chuẩn hoá: negative max 0.865, 0/3000 vượt 0.95.
    """

    mean: np.ndarray
    std: np.ndarray

    @property
    def checksum(self) -> str:
        digest = hashlib.sha256()
        digest.update(np.ascontiguousarray(self.mean, dtype=np.float64).tobytes())
        digest.update(np.ascontiguousarray(self.std, dtype=np.float64).tobytes())
        return digest.hexdigest()

    def apply(self, matrix: np.ndarray) -> np.ndarray:
        valid = frame_validity(matrix)
        standardized = np.zeros_like(matrix, dtype=np.float32)
        standardized[valid] = (matrix[valid] - self.mean) / self.std
        norms = np.linalg.norm(standardized, axis=1, keepdims=True)
        return np.divide(standardized, np.maximum(norms, 1e-8)).astype(np.float32)


def fit_standardizer(matrices: Sequence[np.ndarray], epsilon: float = 1e-6) -> Standardizer:
    stacked = np.concatenate([matrix for matrix in matrices])
    valid = stacked[frame_validity(stacked)]
    if valid.size == 0:
        raise ValueError("No valid frames to fit a standardizer")
    return Standardizer(mean=valid.mean(axis=0), std=valid.std(axis=0) + epsilon)


def _diagonal_sums(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Tổng của mọi đường chéo, một lượt vector hoá.

    Vòng lặp Python trên từng lag là nút cổ chai thật: đo được 899 µs cho một cặp
    cỡ trung vị, tức 54 phút cho riêng 3.62 triệu cặp xuyên dataset. `bincount`
    gom theo chỉ số `j - i` nên chỉ duyệt ma trận một lần.

    Trả về `(sums, lengths)` đánh chỉ số theo `lag + rows - 1`.
    """
    rows, columns = matrix.shape
    offsets = (np.arange(columns)[None, :] - np.arange(rows)[:, None] + rows - 1).ravel()
    size = rows + columns - 1
    lengths = np.bincount(offsets, minlength=size)
    sums = np.bincount(offsets, weights=matrix.ravel().astype(np.float64), minlength=size)
    return sums, lengths


def diagonal_means(gram: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Trung bình của mọi đường chéo. `(means, lengths)` theo `lag + rows - 1`."""
    sums, lengths = _diagonal_sums(gram)
    return sums / np.maximum(lengths, 1), lengths


def best_alignment(
    left: np.ndarray,
    right: np.ndarray,
    config: FingerprintConfig,
    *,
    min_overlap_s: float = 3.0,
) -> MatchResult:
    """Trượt cửa sổ, lấy cosine trung bình trên đoạn chồng lấp dài nhất đạt ngưỡng.

    Vector đã chuẩn hoá L2 nên tích vô hướng **chính là** cosine; trung bình trên
    một đường chéo của ma trận `left @ right.T` là điểm của một lag.
    """
    if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[1]:
        raise ValueError("Fingerprints must be 2-D with matching dimensions")

    gram = left @ right.T
    sums, lengths = _diagonal_sums(gram)
    valid_left, valid_right = frame_validity(left), frame_validity(right)
    if valid_left.all() and valid_right.all():
        counts = lengths.astype(np.float64)
    else:
        counts, _ = _diagonal_sums(np.outer(valid_left, valid_right).astype(np.float64))
    means = sums / np.maximum(counts, 1.0)
    eligible = counts >= config.frames_for_seconds(min_overlap_s)
    if not eligible.any():
        return MatchResult(similarity=0.0, overlap_frames=0, overlap_s=0.0, lag_frames=0)

    scores = np.where(eligible, means, -np.inf)
    index = int(np.argmax(scores))
    frames = int(counts[index])
    return MatchResult(
        similarity=float(means[index]),
        overlap_frames=frames,
        overlap_s=config.overlap_seconds(frames),
        lag_frames=index - left.shape[0] + 1,
    )


def global_vector(fingerprint_matrix: np.ndarray) -> np.ndarray:
    """Một vector đại diện cả file, dùng cho pre-filter rẻ trước khi chạy T3 đầy đủ."""
    mean = fingerprint_matrix.mean(axis=0)
    norm = float(np.linalg.norm(mean))
    return (mean / norm if norm > 0 else mean).astype(np.float32)
