import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import { api } from "../api/client";
import type { Language } from "../api/types";
import { formatClock, formatSeconds } from "../lib/timeline";
import type { TaxonomyView } from "../lib/useTaxonomy";
import { CaptionView } from "./CaptionView";
import { Timeline } from "./Timeline";

interface Props {
  recordingId: string;
  seekTo: number | null;
  language: Language;
  taxonomy: TaxonomyView;
}

/** Keeps a smooth playhead while playing (rAF), and applies a seek once audio can play. */
function usePlayback(recordingId: string, seekTo: number | null) {
  const audio = useRef<HTMLAudioElement>(null);
  const [time, setTime] = useState(0);
  useEffect(() => {
    const element = audio.current;
    if (!element) return;
    let frame = 0;
    const tick = () => {
      setTime(element.currentTime);
      if (!element.paused) frame = requestAnimationFrame(tick);
    };
    const onPlay = () => (frame = requestAnimationFrame(tick));
    const onReady = () => {
      if (seekTo !== null) element.currentTime = seekTo;
      setTime(element.currentTime);
    };
    element.addEventListener("play", onPlay);
    element.addEventListener("seeked", tick);
    element.addEventListener("loadedmetadata", onReady);
    return () => {
      cancelAnimationFrame(frame);
      element.removeEventListener("play", onPlay);
      element.removeEventListener("seeked", tick);
      element.removeEventListener("loadedmetadata", onReady);
    };
  }, [recordingId, seekTo]);
  const seek = (seconds: number) => {
    if (audio.current) audio.current.currentTime = seconds;
    setTime(seconds);
  };
  return { audio, time, seek };
}

export function RecordingView({ recordingId, seekTo, language, taxonomy }: Props) {
  const detail = useQuery({ queryKey: ["recording", recordingId], queryFn: () => api.recording(recordingId) });
  const [active, setActive] = useState<number | null>(null);
  const { audio, time, seek } = usePlayback(recordingId, seekTo);
  const vi = language === "vi";
  if (detail.isPending) return <section className="panel stage skeleton" aria-busy="true" />;
  if (detail.isError) return <section className="panel stage notice notice-error">{String(detail.error)}</section>;
  const { recording, events, captions, model_versions, taxonomy_versions } = detail.data;
  return (
    <section className="panel stage" aria-labelledby="stage-title">
      <div className="stage-head">
        <div>
          <p className="eyebrow">{recording.source_dataset === "upload" ? (vi ? "Bản tải lên" : "Upload") : `DataSED · ${recording.split}`}</p>
          <h2 id="stage-title">
            <code>{recording.recording_id}</code>
          </h2>
        </div>
        <dl className="facts">
          <div>
            <dt>{vi ? "Thời lượng" : "Duration"}</dt>
            <dd>{formatClock(recording.duration_s)}</dd>
          </div>
          <div>
            <dt>{vi ? "Sự kiện" : "Events"}</dt>
            <dd>{events.length}</dd>
          </div>
          <div>
            <dt>{vi ? "Vị trí" : "Position"}</dt>
            <dd className="mono">{formatSeconds(time, language)} s</dd>
          </div>
        </dl>
      </div>
      <audio ref={audio} controls preload="metadata" src={api.audioUrl(recording.recording_id)} className="player" />
      <Timeline
        events={events}
        duration={recording.duration_s}
        currentTime={time}
        language={language}
        taxonomy={taxonomy}
        activeEvent={active}
        onHover={setActive}
        onSeek={seek}
      />
      <CaptionView captions={captions} language={language} activeEvent={active} onHover={setActive} />
      <footer className="provenance-row">
        <span>model_version</span>
        <code>{model_versions.join(", ") || "—"}</code>
        <span>taxonomy_version</span>
        <code>{taxonomy_versions.join(", ") || "—"}</code>
      </footer>
    </section>
  );
}
