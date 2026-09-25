import { RecordingList } from "./components/RecordingList";
import { RecordingView } from "./components/RecordingView";
import { SearchPanel } from "./components/SearchPanel";
import { StatusBar } from "./components/StatusBar";
import { UploadPanel } from "./components/UploadPanel";
import { useTaxonomy } from "./lib/useTaxonomy";
import { useViewState } from "./lib/urlState";

export function App() {
  const [view, update] = useViewState();
  const taxonomy = useTaxonomy();
  const vi = view.lang === "vi";
  return (
    <div className="shell">
      <StatusBar language={view.lang} onLanguage={(lang) => update({ lang })} />
      <main className="layout">
        <aside className="rail">
          <UploadPanel language={view.lang} onUploaded={(id) => update({ recording: id, corpus: "upload", t: null })} />
          <RecordingList
            corpus={view.corpus}
            selected={view.recording}
            language={view.lang}
            taxonomy={taxonomy}
            onCorpus={(corpus) => update({ corpus })}
            onSelect={(recording) => update({ recording, t: null })}
          />
        </aside>
        <div className="main-column">
          {view.recording && taxonomy ? (
            <RecordingView recordingId={view.recording} seekTo={view.t} language={view.lang} taxonomy={taxonomy} />
          ) : (
            <section className="panel stage empty-stage">
              <h2>{vi ? "Chọn hoặc tải lên một bản ghi" : "Pick or upload a recording"}</h2>
              <p>
                {vi
                  ? "Dòng thời gian cho thấy mỗi sự kiện hệ thống phát hiện; mô tả chỉ nói điều có sự kiện làm bằng chứng — rê chuột lên một cụm từ để thấy sự kiện của nó."
                  : "The timeline shows every detected event; the caption only states what an event supports — hover a phrase to see its evidence."}
              </p>
            </section>
          )}
          {taxonomy && (
            <SearchPanel
              corpus={view.corpus}
              language={view.lang}
              taxonomy={taxonomy}
              onOpen={(recording, t) => update({ recording, t })}
            />
          )}
        </div>
      </main>
    </div>
  );
}
