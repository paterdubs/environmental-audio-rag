import type { Caption, Language } from "../api/types";
import { captionSegments } from "../lib/timeline";

interface Props {
  captions: Caption[];
  language: Language;
  activeEvent: number | null;
  onHover: (eventId: number | null) => void;
}

/** The caption in the chosen language; every mention is linked to its evidence event. */
export function CaptionView({ captions, language, activeEvent, onHover }: Props) {
  const caption = captions.find((c) => c.language === language) ?? captions[0];
  if (!caption) return null;
  const grounded = caption.evidence.length > 0;
  return (
    <figure className="caption">
      <blockquote lang={caption.language}>
        {captionSegments(caption.text, caption.evidence).map((segment, index) =>
          segment.eventId === null ? (
            <span key={index}>{segment.text}</span>
          ) : (
            <mark
              key={index}
              className={activeEvent === segment.eventId ? "is-active" : ""}
              onMouseEnter={() => onHover(segment.eventId)}
              onMouseLeave={() => onHover(null)}
            >
              {segment.text}
            </mark>
          ),
        )}
      </blockquote>
      <figcaption>
        <code>{caption.captioner_version}</code> · {caption.grounding_mode} ·{" "}
        {grounded
          ? language === "vi"
            ? `${caption.evidence.length} trích dẫn tới sự kiện`
            : `${caption.evidence.length} evidence links`
          : language === "vi"
            ? "không có sự kiện để mô tả"
            : "no event to describe"}
      </figcaption>
    </figure>
  );
}
