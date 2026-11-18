import { useEffect, useState } from "react";
import api, { errText } from "./api.js";

const Bar = ({ label, value, max = 100 }) => (
  <div className="bar">
    <span>{label}</span>
    <div role="progressbar" aria-valuenow={value} aria-valuemax={max}>
      <i style={{ width: `${(100 * value) / max}%` }} />
    </div>
    <b>{value}</b>
  </div>
);

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/dashboard/").then((r) => setData(r.data)).catch((e) => setError(errText(e)));
  }, []);

  if (error) return <p role="alert" className="err">{error}</p>;
  if (!data) return <p className="card narrow">Loading…</p>;
  if (!data.resume_count && !data.interview_count)
    return (
      <section className="card narrow">
        <h2>Nothing here yet</h2>
        <p>Upload a resume in the Workspace to see your scores.</p>
      </section>
    );

  return (
    <main className="grid">
      <section className="card">
        <h2>Resume</h2>
        <p className="big">{data.latest_resume_score ?? "-"}</p>
        <small>{data.resume_count} analysed · skills: {data.strongest_skills.join(", ") || "none"}</small>
      </section>
      <section className="card">
        <h2>Interviews</h2>
        <p className="big">{data.avg_interview_score}/10</p>
        <small>{data.interview_count} sessions{data.weakest_category && ` · weakest: ${data.weakest_category}`}</small>
      </section>
      <section className="card">
        <h2>Score by category</h2>
        {Object.entries(data.category_scores).map(([k, v]) => <Bar key={k} label={k} value={v} max={10} />)}
      </section>
      <section className="card">
        <h2>Roadmaps</h2>
        {data.roadmap_progress.map((r) => <Bar key={r.id} label={r.role} value={r.progress} />)}
      </section>
    </main>
  );
}