import { useEffect, useRef, useState } from "react";
import api, { errText } from "./api.js";

const LABELS = { defended: "Defended", shaky: "Shaky", unsupported: "Unsupported" };

export default function Defense() {
  const [resumes, setResumes] = useState([]);
  const [resumeId, setResumeId] = useState("");
  const [session, setSession] = useState(null);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const pastes = useRef(0);

  useEffect(() => {
    api.get("/resumes/").then((r) => { setResumes(r.data); if (r.data[0]) setResumeId(String(r.data[0].id)); }).catch((e) => setError(errText(e)));
        api.get("/defense/").then((r) => setSession(r.data && r.data.claims ? r.data : null)).catch(() => {});
  }, []);

  const start = async () => {
    setError(""); setBusy(true);
    try { setSession((await api.post("/defense/", { resume_id: Number(resumeId) })).data); setText(""); }
    catch (err) { setError(errText(err)); }
    setBusy(false);
  };

  const active = session?.claims?.find((c) => !c.followup_answer);
  const stage2 = active && active.answer;

  const submit = async () => {
    setError(""); setBusy(true);
    try {
      const { data } = await api.post(`/defense/claims/${active.id}/answer/`, { answer: text, paste_attempts: pastes.current });
      pastes.current = 0;
      setSession({ ...session, claims: session.claims.map((c) => (c.id === data.id ? data : c)) });
      setText(""); setNotice("");
    } catch (err) { setError(errText(err)); }
    setBusy(false);
  };

  const blockPaste = (e) => {
    e.preventDefault();
    pastes.current += 1;
    setNotice("Pasting is turned off. Write this in your own words. It only helps you if it's really yours.");
  };

  const done = session && !active;
  const counts = (v) => session.claims.filter((c) => c.verdict === v).length;

  return (
    <main className="grid">
      {error && <p role="alert" className="err wide">{error}</p>}

      <section className="card">
        <h2>Defend your resume</h2>
        <p>
          An interviewer picks claims from <b>your</b> resume and asks you to back them up, then asks one follow-up.
          Each claim ends as Defended, Shaky or Unsupported.
        </p>
        {resumes.length === 0 ? <small>Upload a resume in the Workspace first.</small> : (
          <>
            <label>Resume
              <select value={resumeId} onChange={(e) => setResumeId(e.target.value)}>
                {resumes.map((r) => <option key={r.id} value={r.id}>{r.filename}</option>)}
              </select>
            </label>
            <button onClick={start} disabled={busy}>{session ? "Start a new session" : "Start"}</button>
          </>
        )}
      </section>

      {active && (
        <section className="card">
          <h2>Claim {session.claims.indexOf(active) + 1} of {session.claims.length}</h2>
          <small>{active.claim}</small>
          <p><b>{stage2 ? active.followup : active.question}</b></p>
          {stage2 && active.feedback && <small>Feedback so far: {active.feedback}</small>}
          <textarea rows={6} value={text} onChange={(e) => setText(e.target.value)} onPaste={blockPaste}
            onDrop={(e) => e.preventDefault()} placeholder="Type your answer in your own words" />
          {notice && <small role="status">{notice}</small>}
          <button onClick={submit} disabled={busy || text.trim().length < 10}>
            {busy ? "Judging…" : stage2 ? "Submit follow-up answer" : "Submit answer"}
          </button>
        </section>
      )}

      {done && (
        <section className="card wide">
          <h2>Your defense report</h2>
          <p>
            <span className="verdict v-defended">Defended {counts("defended")}</span>{" "}
            <span className="verdict v-shaky">Shaky {counts("shaky")}</span>{" "}
            <span className="verdict v-unsupported">Unsupported {counts("unsupported")}</span>
          </p>
          {session.claims.map((c) => (
            <div key={c.id} className="q">
              <p><b>{c.claim}</b> <span className={`verdict v-${c.verdict}`}>{LABELS[c.verdict]}</span></p>
              <small>{c.feedback}</small>
              {c.paste_attempts > 0 && <small><br />Paste attempts blocked: {c.paste_attempts}</small>}
            </div>
          ))}
          <small>
            Defended: you can back it up. Shaky or Unsupported: practise it, or remove it from your resume.
            Verdicts are estimates, not proof of what you know.
          </small>
        </section>
      )}
    </main>
  );
}