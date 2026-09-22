from pathlib import Path

import numpy as np
import soundfile as sf

from ml.dataops.inventory import build_inventory, inventory_summary


def test_inventory_reads_audio_and_detects_exact_duplicate(tmp_path: Path) -> None:
    waveform = np.zeros(800, dtype=np.float32)
    sf.write(tmp_path / "a.wav", waveform, 8000, subtype="PCM_16")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "b.wav").write_bytes((tmp_path / "a.wav").read_bytes())
    records = build_inventory("tiny", tmp_path, workers=1)
    summary = inventory_summary(records)
    assert summary["files"] == 2
    assert summary["sample_rates"] == {8000: 2}
    assert len(summary["exact_duplicate_groups"]) == 1

