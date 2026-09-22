from pathlib import Path

import pandas as pd

from ml.dataops.datased import normalize_events
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]


def test_normalize_datased_source_schema(tmp_path: Path) -> None:
    source = tmp_path / "Polyphonic_sound_detection.csv"
    pd.DataFrame(
        [
            {
                "sound_name": "S-0001.wav",
                "class_name": "Cat fight and moans",
                "start_perc": 0.1,
                "end_perc": 0.2,
                "start_time": 1.0,
                "end_time": 2.0,
                "event_length": 1.0,
            }
        ]
    ).to_csv(source, index=False)
    recordings = pd.DataFrame(
        [
            {
                "recording_id": "S-0001",
                "audio_relative_path": "SED_wav/S-0001.wav",
                "duration_s": 10.0,
            }
        ]
    )
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")

    events, audit = normalize_events(
        source, mode="polyphonic", recordings=recordings, taxonomy=taxonomy
    )

    assert events.loc[0, "class_id"] == "cat_fights_and_moans"
    assert audit["classes"] == 1
