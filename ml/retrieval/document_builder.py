"""Deterministic retrieval document construction from caption and timeline."""

from collections.abc import Mapping, Sequence


def build_document(caption: str, timeline: Mapping[str, object]) -> dict[str, object]:
    """Build the indexed text and denormalized filters for one recording.

    The canonical event summary is retained alongside prose because captions may
    omit exact times. Input events are sorted; caller-owned mappings are not changed.
    """
    recording_id = str(timeline["recording_id"])
    duration = float(timeline["duration_s"])
    events = sorted(
        timeline.get("events", []),
        key=lambda e: (float(e["onset_s"]), int(e["event_id"])),
    )
    lines = [
        "[caption]",
        caption.strip(),
        "",
        "[canonical event summary]",
    ]
    for event in events:
        lines.append(
            f"{event['class_id']} {float(event['onset_s']):.3f}-{float(event['offset_s']):.3f}s "
            f"({float(event['score']):.3f})"
        )
    classes = sorted({str(e["class_id"]) for e in events})
    lines.extend(
        [
            f"duration {duration:.3f}s; events {len(events)}; "
            f"max polyphony {max_polyphony(events)}",
            f"classes {', '.join(classes) if classes else '(none)'}",
        ]
    )
    return {
        "recording_id": recording_id,
        "text": "\n".join(lines),
        "class_ids": classes,
        "total_events": len(events),
        "max_polyphony": max_polyphony(events),
    }


def max_polyphony(events: Sequence[Mapping[str, object]]) -> int:
    """Return maximum number of concurrently active half-open intervals."""
    points = sorted(
        (float(e["onset_s"]), 1) for e in events
    ) + sorted((float(e["offset_s"]), -1) for e in events)
    active = maximum = 0
    for _, delta in sorted(points, key=lambda point: (point[0], point[1])):
        active += delta
        maximum = max(maximum, active)
    return maximum
