import { useEffect, useState } from "react";
import api, { errText } from "./api.js";

export default function History() {
  const [sessions, setSessions] = useState(null);
  const [open, setOpen] = useState(null);
  const [error, setError] = useState("");

  const load = () => api.get("/interviews/sessions/").then((r) => setSessions(r.data)).catch((e) => setError(errText(e)));
  useEffect(() => { load(); }, []);

  const toggle = async (id) => {
    if (open?.id === id) return setOpen(null);
    try {
      setOpen((await api.get(`/interviews/sessions/${id}/`)).data);
    } catch (err) { setError(errText(err)); }
  };

  const remove = async (id) => {
    await api.delete(`/interviews/sessions/${id}/`);
    setOpen(null);
    load();
  };

  if (!sessions) return <p className="card narrow">{error || "Loading…"}</p>;

  return (
    <main className="grid">
      {error && <p role="alert" className="err wide">{error}</p>}
      {sessions.length === 0 && (
        <section className="card narrow">
          <h2>No interviews yet</h2>
          <p>Start a practice interview in the Workspace and it will show up here.</p>
        </section>
      )}
      {sessions.map((s) => (
        <section key={s.id} className="card">
          <h2>{s.role}</h2>
          <small>{s.category} · {s.level} · {new Date(s.created_at).toLocaleDateString()}</small>
          <p className="big">{s.avg_score ?? "-"}{s.avg_score !== null && <small>/10</small>}</p>
          <small>{s.answered} of {s.questions.length} questions answered</small>
          <div>
            <button className="ghost" onClick={() => toggle(s.id)}>
              {open?.id === s.id ? "Hide details" : "View details"}
            </button>{" "}
            <button className="ghost" onClick={() => remove(s.id)}>Delete</button>
          </div>
          {open?.id === s.id && open.answers.map((a, i) => (
            <div key={i} className="q">
              <p><b>{a.question}</b></p>
              <p>{a.answer}</p>
              <p><b>{a.score}/10</b> {a.feedback}</p>
              {a.missing.length > 0 && <small>To improve: {a.missing.join(" ")}</small>}
            </div>
          ))}
          {open?.id === s.id && open.answers.length === 0 && <p><small>No answers saved for this session.</small></p>}
        </section>
      ))}
    </main>
  );
}