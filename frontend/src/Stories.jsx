import { useEffect, useState } from "react";
import api, { errText } from "./api.js";

const empty = { title: "", tags: "", situation: "", task: "", action: "", result: "" };

export default function Stories() {
  const [stories, setStories] = useState([]);
  const [form, setForm] = useState(empty);
  const [question, setQuestion] = useState("");
  const [matches, setMatches] = useState(null);
  const [error, setError] = useState("");

  const load = () => api.get("/stories/").then((r) => setStories(r.data)).catch((e) => setError(errText(e)));
  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const tags = form.tags.split(",").map((t) => t.trim()).filter(Boolean);
      await api.post("/stories/", { ...form, tags });
      setForm(empty);
      load();
    } catch (err) { setError(errText(err)); }
  };

  const remove = async (id) => {
    await api.delete(`/stories/${id}/`);
    load();
  };

  const find = async () => {
    setError("");
    try {
      setMatches((await api.post("/stories/suggest/", { question })).data);
    } catch (err) { setError(errText(err)); }
  };

  return (
    <main className="grid">
      {error && <p role="alert" className="err wide">{error}</p>}

      <section className="card">
        <h2>Add a story</h2>
        <small>Write only things that really happened.</small>
        <form onSubmit={save} style={{ display: "grid", gap: 10 }}>
          <label>Title<input value={form.title} onChange={set("title")} required /></label>
          <label>Tags (comma separated)<input value={form.tags} onChange={set("tags")} placeholder="teamwork, conflict, deadline" /></label>
          <label>Situation<textarea rows={2} value={form.situation} onChange={set("situation")} /></label>
          <label>Task<textarea rows={2} value={form.task} onChange={set("task")} /></label>
          <label>Action (what YOU did)<textarea rows={3} value={form.action} onChange={set("action")} /></label>
          <label>Result<textarea rows={2} value={form.result} onChange={set("result")} /></label>
          <button>Save story</button>
        </form>
      </section>

      <section className="card">
        <h2>Find a story for a question</h2>
        <textarea rows={3} value={question} onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Tell me about a time you resolved a team conflict." />
        <button onClick={find}>Find best story</button>
        {matches && matches.length === 0 && <p><small>No saved story matches. Add one with matching tags.</small></p>}
        {matches && matches.map((s) => (
          <div key={s.id} className="q">
            <p><b>{s.title}</b></p>
            {s.missing.length > 0 && <small>Still needs: {s.missing.join(", ")}</small>}
          </div>
        ))}
      </section>

      <section className="card wide">
        <h2>Your stories ({stories.length})</h2>
        {stories.length === 0 && <p><small>No stories yet. Add your first one on the left.</small></p>}
        {stories.map((s) => (
          <div key={s.id} className="q">
            <p><b>{s.title}</b> {s.tags.length > 0 && <small>· {s.tags.join(", ")}</small>}</p>
                        {s.situation && <p><b>Situation:</b> {s.situation}</p>}
            {s.task && <p><b>Task:</b> {s.task}</p>}
            {s.action && <p><b>Action:</b> {s.action}</p>}
            {s.result && <p><b>Result:</b> {s.result}</p>}
            {s.missing.length > 0 && <small>Missing or too short: {s.missing.join(", ")}</small>}
            <div><button className="ghost" onClick={() => remove(s.id)}>Delete</button></div>
          </div>
        ))}
      </section>
    </main>
  );
}