from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ml.taxonomy import Taxonomy, normalize_text

SOURCE_COLUMNS = (
    "sound_name",
    "class_name",
    "start_perc",
    "end_perc",
    "start_time",
    "end_time",
    "event_length",
)


def locate_datased(root: Path) -> tuple[Path, dict[str, Path]]:
    wav_directories = [path for path in root.rglob("SED_wav") if path.is_dir()]
    if len(wav_directories) != 1:
        raise RuntimeError(f"Expected one SED_wav directory, found {wav_directories}")
    labels: dict[str, Path] = {}
    for mode, name in (
        ("polyphonic", "Polyphonic_sound_detection.csv"),
        ("monophonic", "Monophonic_sound_detection.csv"),
    ):
        matches = list(root.rglob(name))
        if len(matches) != 1:
            raise RuntimeError(f"Expected one {name}, found {matches}")
        labels[mode] = matches[0]
    return wav_directories[0], labels


def build_recordings(inventory: pd.DataFrame, wav_directory: Path, root: Path) -> pd.DataFrame:
    prefix = wav_directory.relative_to(root).as_posix() + "/"
    recordings = inventory[inventory["relative_path"].str.startswith(prefix)].copy()
    recordings["recording_id"] = recordings["relative_path"].map(lambda value: Path(value).stem)
    if recordings["recording_id"].duplicated().any():
        raise ValueError("DataSED recording IDs are not unique")
    recordings = recordings.rename(
        columns={"sha256": "content_sha256", "relative_path": "audio_relative_path"}
    )
    columns = [
        "recording_id",
        "file_id",
        "audio_relative_path",
        "content_sha256",
        "bytes",
        "sample_rate",
        "channels",
        "frames",
        "duration_s",
        "format",
        "subtype",
    ]
    return recordings[columns].sort_values("recording_id").reset_index(drop=True)


def normalize_events(
    source_path: Path,
    *,
    mode: str,
    recordings: pd.DataFrame,
    taxonomy: Taxonomy,
) -> tuple[pd.DataFrame, dict]:
    source = pd.read_csv(source_path)
    if tuple(source.columns) != SOURCE_COLUMNS:
        raise ValueError(f"Unexpected DataSED columns in {source_path}: {list(source.columns)}")
    numeric = ["start_perc", "end_perc", "start_time", "end_time", "event_length"]
    source[numeric] = source[numeric].apply(pd.to_numeric, errors="raise")
    if source.isna().any().any():
        raise ValueError(f"Null values in {source_path}")

    audio_by_name = {
        Path(row.audio_relative_path).name: row
        for row in recordings.itertuples(index=False)
    }
    missing_audio = sorted(set(source["sound_name"]).difference(audio_by_name))
    if missing_audio:
        raise ValueError(f"Labels reference missing audio: {missing_audio[:10]}")

    aliases = taxonomy.alias_to_id
    normalized_labels = source["class_name"].map(normalize_text)
    unknown_labels = sorted(set(normalized_labels).difference(aliases))
    if unknown_labels:
        raise ValueError(f"Unknown source labels: {unknown_labels}")
    source["class_id"] = normalized_labels.map(aliases)
    allowed = set(
        taxonomy.polyphonic_class_ids if mode == "polyphonic" else taxonomy.class_ids
    )
    disallowed = sorted(set(source["class_id"]).difference(allowed))
    if disallowed:
        raise ValueError(f"Classes invalid for {mode}: {disallowed}")

    if (source["start_time"] < 0).any() or (source["end_time"] <= source["start_time"]).any():
        raise ValueError(f"Invalid event time bounds in {source_path}")
    duration_error = (source["event_length"] - (source["end_time"] - source["start_time"])).abs()
    if duration_error.max() > 0.051:
        raise ValueError(f"Event duration mismatch up to {duration_error.max():.3f}s")

    rows: list[dict] = []
    end_overrun = 0.0
    percent_error = 0.0
    for source_index, row in source.iterrows():
        recording = audio_by_name[str(row["sound_name"])]
        duration = float(recording.duration_s)
        end_overrun = max(end_overrun, float(row["end_time"]) - duration)
        percent_error = max(
            percent_error,
            abs(float(row["start_perc"]) - float(row["start_time"]) / duration),
            abs(float(row["end_perc"]) - float(row["end_time"]) / duration),
        )
        rows.append(
            {
                "event_id": f"datased:{mode}:{source_index + 1:06d}",
                "recording_id": recording.recording_id,
                "audio_relative_path": recording.audio_relative_path,
                "label_mode": mode,
                "raw_class_label": row["class_name"],
                "class_id": row["class_id"],
                "onset_s": float(row["start_time"]),
                "offset_s": float(row["end_time"]),
                "source_start_fraction": float(row["start_perc"]),
                "source_end_fraction": float(row["end_perc"]),
                "source_event_length_s": float(row["event_length"]),
                "source_row": source_index + 2,
            }
        )
    if end_overrun > 0.051:
        raise ValueError(f"Event exceeds recording duration by {end_overrun:.3f}s")
    if percent_error > 0.011:
        raise ValueError(f"Source percentage mismatch up to {percent_error:.3f}")

    events = pd.DataFrame(rows)
    duplicate_columns = ["recording_id", "class_id", "onset_s", "offset_s"]
    duplicate_rows = int(events.duplicated(duplicate_columns, keep=False).sum())
    audit = {
        "mode": mode,
        "source_file": source_path.name,
        "events": len(events),
        "recordings_with_events": int(events["recording_id"].nunique()),
        "classes": int(events["class_id"].nunique()),
        "raw_labels": sorted(events["raw_class_label"].unique()),
        "maximum_end_overrun_s": max(0.0, end_overrun),
        "maximum_fraction_error": percent_error,
        "duplicate_annotation_rows": duplicate_rows,
        "event_duration_s": {
            "minimum": float((events["offset_s"] - events["onset_s"]).min()),
            "median": float(np.median(events["offset_s"] - events["onset_s"])),
            "maximum": float((events["offset_s"] - events["onset_s"]).max()),
        },
    }
    return events, audit
