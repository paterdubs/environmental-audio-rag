import type { Language, SedEvent } from "../api/types";
import { buildLanes, formatSeconds, percent } from "../lib/timeline";
import type { TaxonomyView } from "../lib/useTaxonomy";

interface Props {
  events: SedEvent[];
  duration: number;
  currentTime: number;
  language: Language;
  taxonomy: TaxonomyView;
  activeEvent: number | null;
  onHover: (eventId: number | null) => void;
  onSeek: (seconds: number) => void;
}

const TICKS = 6;

export function Timeline({ events, duration, currentTime, language, taxonomy, activeEvent, onHover, onSeek }: Props) {
  const lanes = buildLanes(events, taxonomy.order);
  if (lanes.length === 0) {
    return (
      <p className="notice">
        {language === "vi"
          ? "Hệ thống không phát hiện sự kiện nào vượt ngưỡng trong bản ghi này."
          : "No event above threshold was detected in this recording."}
      </p>
    );
  }
  const ticks = Array.from({ length: TICKS + 1 }, (_, i) => (duration * i) / TICKS);
  return (
    <div className="timeline" role="group" aria-label={language === "vi" ? "Dòng thời gian sự kiện" : "Event timeline"}>
      <div className="timeline-axis" aria-hidden="true">
        {ticks.map((t) => (
          <span key={t} style={{ left: `${percent(t, duration)}%` }}>
            {formatSeconds(t, language)}
          </span>
        ))}
      </div>
      {lanes.map((lane) => (
        <div className="lane" key={lane.classId}>
          <span className="lane-label" title={lane.classId}>
            <span className="swatch" style={{ background: taxonomy.color(lane.classId) }} />
            {taxonomy.name(lane.classId, language)}
          </span>
          <div className="lane-track">
            {lane.events.map((event) => (
              <button
                type="button"
                key={event.event_id}
                className={`bar ${activeEvent === event.event_id ? "is-active" : ""}`}
                style={{
                  left: `${percent(event.onset_s, duration)}%`,
                  width: `max(3px, ${percent(event.offset_s - event.onset_s, duration)}%)`,
                  background: taxonomy.color(lane.classId),
                }}
                title={`${taxonomy.name(lane.classId, language)} · ${formatSeconds(event.onset_s, language)}–${formatSeconds(event.offset_s, language)} s · ${event.score.toFixed(2)}`}
                aria-label={`${taxonomy.name(lane.classId, language)} ${formatSeconds(event.onset_s, language)}–${formatSeconds(event.offset_s, language)} s`}
                onMouseEnter={() => onHover(event.event_id)}
                onMouseLeave={() => onHover(null)}
                onFocus={() => onHover(event.event_id)}
                onBlur={() => onHover(null)}
                onClick={() => onSeek(event.onset_s)}
              />
            ))}
          </div>
        </div>
      ))}
      <div className="playhead-layer" aria-hidden="true">
        <span className="playhead" style={{ left: `${percent(currentTime, duration)}%` }} />
      </div>
    </div>
  );
}
