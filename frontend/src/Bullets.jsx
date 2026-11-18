import { useState } from "react";
import api, { errText } from "./api.js";

const MESSAGES = {
  unavailable: "AI isn't available right now. Check that your Gemini key is set.",
  rejected: "The suggestion added facts that weren't in your bullet, so it was discarded. Try again.",
};

export default function Bullets({ resumeId, bullets }) {
  const [rewrites, setRewrites] = useState({});
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const rewrite = async (bullet) => {
    setError(""); setBusy(bullet);
    try {
      const { data } = await api.post(`/resumes/${resumeId}/rewrite/`, { bullet });
      setRewrites({ ...rewrites, [bullet]: data });
    } catch (err) { setError(errText(err)); }
    setBusy("");
  };

  return (
    <section className="card">
      <h2>Bullet Proof Score</h2>
      <small>Weakest bullets first. Replace placeholders only with figures that are true.</small>
      {error && <p role="alert" className="err">{error}</p>}
      {bullets.slice(0, 5).map((b) => {
        const r = rewrites[b.bullet];
        return (
          <div key={b.bullet} className="q">
            <p><b>{b.score}/100</b> {b.bullet}</p>
            <ul>{b.tips.map((t) => <li key={t}>{t}</li>)}</ul>
            <button className="ghost" onClick={() => rewrite(b.bullet)} disabled={busy === b.bullet}>
              {busy === b.bullet ? "Rewriting…" : "Rewrite"}
            </button>
            {r?.rewrite && (
              <p>
                <b>Suggestion:</b> {r.rewrite}{" "}
                <button className="ghost" onClick={() => navigator.clipboard.writeText(r.rewrite)}>Copy</button>
              </p>
            )}
            {r && !r.rewrite && <p className="err">{MESSAGES[r.source] || "No suggestion."}</p>}
          </div>
        );
      })}
    </section>
  );
}