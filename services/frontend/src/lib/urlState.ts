import { useCallback, useEffect, useState } from "react";

// Shareable state lives in the URL: which recording, which corpus, which language.
export interface ViewState {
  recording: string | null;
  corpus: "upload" | "validation" | "test";
  lang: "vi" | "en";
  t: number | null; // seek target in seconds (from a search result)
}

function read(): ViewState {
  const params = new URLSearchParams(window.location.search);
  const corpus = params.get("corpus");
  const t = params.get("t");
  return {
    recording: params.get("recording"),
    corpus: corpus === "validation" || corpus === "test" ? corpus : "upload",
    lang: params.get("lang") === "en" ? "en" : "vi",
    t: t !== null && Number.isFinite(Number(t)) ? Number(t) : null,
  };
}

function write(state: ViewState): void {
  const params = new URLSearchParams();
  if (state.recording) params.set("recording", state.recording);
  if (state.corpus !== "upload") params.set("corpus", state.corpus);
  if (state.lang !== "vi") params.set("lang", state.lang);
  if (state.t !== null) params.set("t", state.t.toFixed(2));
  const query = params.toString();
  window.history.pushState(null, "", query ? `?${query}` : window.location.pathname);
}

export function useViewState(): [ViewState, (patch: Partial<ViewState>) => void] {
  const [state, setState] = useState<ViewState>(read);
  useEffect(() => {
    const onPop = () => setState(read());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  const update = useCallback((patch: Partial<ViewState>) => {
    setState((current) => {
      const next = { ...current, ...patch };
      write(next);
      return next;
    });
  }, []);
  return [state, update];
}
