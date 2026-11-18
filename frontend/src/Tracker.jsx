import { useEffect, useState } from "react";
import api, { errText } from "./api.js";

const COLUMNS = [
  ["saved", "Saved"],
  ["applied", "Applied"],
  ["interview", "Interview"],
  ["offer", "Offer"],
  ["rejected", "Rejected"],
];
const empty = { company: "", role: "", link: "", description: "" };

export default function Tracker() {
  const [apps, setApps] = useState([]);
  const [form, setForm] = useState(empty);
  const [error, setError] = useState("");

  const load = () => api.get("/applications/").then((r) => setApps(r.data)).catch((e) => setError(errText(e)));
  useEffect(() => { load(); }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const add = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/applications/", form);
      setForm(empty);
      load();
    } catch (err) { setError(errText(err)); }
  };

  const move = async (id, status) => {
    try {
      await api.patch(`/applications/${id}/`, { status });
      load();
    } catch (err) { setError(errText(err)); }
  };

  const remove = async (id) => {
    await api.delete(`/applications/${id}/`);
    load();
  };

  return (
    <main style={{ padding: 24 }}>
      {error && <p role="alert" className="err">{error}</p>}

      <section className="card" style={{ maxWidth: 700, margin: "0 auto 24px" }}>
        <h2>Add a job</h2>
        <small>Paste the job description to see how well your latest resume matches it.</small>
        <form onSubmit={add} style={{ display: "grid", gap: 10 }}>
          <label>Company<input value={form.company} onChange={set("company")} required /></label>
          <label>Role<input value={form.role} onChange={set("role")} required /></label>
          <label>Link (optional)<input type="url" value={form.link} onChange={set("link")} placeholder="https://..." /></label>
          <label>Job description (optional)<textarea rows={4} value={form.description} onChange={set("description")} /></label>
          <button>Add to Saved</button>
        </form>
      </section>

      <div className="board">
        {COLUMNS.map(([key, label]) => {
          const items = apps.filter((a) => a.status === key);
          return (
            <section key={key} className="column">
              <h3>{label} ({items.length})</h3>
              {items.length === 0 && <small>Nothing here yet.</small>}
              {items.map((a) => (
                <div key={a.id} className="job">
                  <p><b>{a.role}</b><br />{a.company}</p>
                  {a.match_score !== null && <small>Match: {a.match_score}%</small>}
                  {a.missing_skills.length > 0 && <small><br />Missing: {a.missing_skills.join(", ")}</small>}
                  {a.link.startsWith("http") && (
                    <p><a href={a.link} target="_blank" rel="noopener noreferrer">Open posting</a></p>
                  )}
                  <select value={a.status} onChange={(e) => move(a.id, e.target.value)} aria-label="Move to column">
                    {COLUMNS.map(([k, l]) => <option key={k} value={k}>{l}</option>)}
                  </select>
                  <button className="ghost" onClick={() => remove(a.id)}>Delete</button>
                </div>
              ))}
            </section>
          );
        })}
      </div>
    </main>
  );
}