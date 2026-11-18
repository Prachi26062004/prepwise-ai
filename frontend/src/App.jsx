import { useState } from "react";
import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import api, { errText } from "./api.js";
import Dashboard from "./dashboard.jsx";
import Stories from "./Stories.jsx";
import Tracker from "./Tracker.jsx";
import History from "./History.jsx";
import Profile from "./Profile.jsx";
import Settings from "./Settings.jsx";
import { Forgot, Reset } from "./PasswordReset.jsx";
import Voice from "./Voice.jsx";
import Bullets from "./Bullets.jsx";
import Landing from "./Landing.jsx";
import { AppShell, PublicLayout } from "./Layouts.jsx";
import Defense from "./Defense.jsx";

const isLoggedIn = () => !!localStorage.getItem("access");
const Guard = ({ children }) => (isLoggedIn() ? children : <Navigate to="/login" />);

function Auth({ register }) {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (register) await api.post("/auth/register/", form);
      const { data } = await api.post("/auth/login/", {
        username: form.username,
        password: form.password,
      });
      localStorage.setItem("access", data.access);
      navigate("/app");
    } catch (err) {
      setError(errText(err));
    }
  };

  return (
    <form className="card narrow" onSubmit={submit}>
      <h1>{register ? "Create your account" : "Log in"}</h1>
      <label>Username<input value={form.username} onChange={set("username")} required /></label>
      {register && <label>Email<input type="email" value={form.email} onChange={set("email")} /></label>}
      <label>Password<input type="password" value={form.password} onChange={set("password")} required /></label>
      {error && <p role="alert" className="err">{error}</p>}
      <button>{register ? "Sign up" : "Log in"}</button>
      {!register && <Link to="/forgot">Forgot password?</Link>}
    </form>
  );
}

function Workspace() {
  const [resume, setResume] = useState(null);
  const [job, setJob] = useState("");
  const [match, setMatch] = useState(null);
  const [bullets, setBullets] = useState([]);
  const [role, setRole] = useState("Software Engineer");
  const [category, setCategory] = useState("technical");
  const [session, setSession] = useState(null);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState({});
  const [roadmap, setRoadmap] = useState(null);
  const [message, setMessage] = useState("");

  const run = async (fn) => {
    setMessage("");
    try { await fn(); } catch (err) { setMessage(errText(err)); }
  };

  const upload = (e) => run(async () => {
    const fd = new FormData();
    fd.append("file", e.target.files[0]);
    const { data } = await api.post("/resumes/", fd);
    setResume(data);
    setBullets((await api.get(`/resumes/${data.id}/bullets/`)).data);
  });

  const compare = () => run(async () => {
    const { data } = await api.post("/match/", { resume_id: resume.id, job_description: job });
    setMatch(data);
  });

  const startInterview = () => run(async () => {
    const { data } = await api.post("/interviews/sessions/", { resume_id: resume.id, role, category });
    setSession(data);
    setAnswers({});
    setResults({});
  });

  const grade = (q) => run(async () => {
    const { data } = await api.post(`/interviews/sessions/${session.id}/answer/`, {
      question: q,
      answer: answers[q] || "",
    });
    setResults({ ...results, [q]: data });
  });

  const makeRoadmap = () => run(async () => {
    if (!match || match.missing_skills.length === 0) {
      setMessage("No missing skills found. Compare with a job description that lists skills you lack.");
      return;
    }
    const { data } = await api.post("/roadmaps/", { role, skills: match.missing_skills });
    setRoadmap(data);
  });

  const toggleWeek = (week, done) => run(async () => {
    const { data } = await api.patch(`/roadmaps/${roadmap.id}/`, { week, done });
    setRoadmap(data);
  });

  const remove = () => run(async () => {
    await api.delete(`/resumes/${resume.id}/`);
    setResume(null); setMatch(null); setBullets([]); setSession(null); setRoadmap(null);
  });

  const a = resume?.analysis;
  return (
    <main className="grid">
      {message && <p role="alert" className="err wide">{message}</p>}

      <section className="card">
        <h2>1. Upload resume</h2>
        <input type="file" accept=".pdf,.docx" onChange={upload} aria-label="Resume file" />
        {a && (
          <>
            <p className="big">{a.score}/100</p>
            <small>{a.disclaimer}</small>
            <p><b>Skills:</b> {a.technical_skills.join(", ") || "none detected"}</p>
            <ul>{a.suggestions.map((s) => <li key={s}>{s}</li>)}</ul>
            <button className="ghost" onClick={remove}>Delete resume and analysis</button>
          </>
        )}
      </section>
      {bullets.length > 0 && <Bullets resumeId={resume.id} bullets={bullets} />}

      {resume && (
        <section className="card">
          <h2>2. Match a job</h2>
          <textarea rows={5} value={job} onChange={(e) => setJob(e.target.value)} placeholder="Paste the job description" />
          <button onClick={compare}>Compare</button>
          {match && (
            <>
              <p className="big">{match.score}%</p>
              <small>{match.disclaimer}</small>
              <p><b>Matching:</b> {match.matching_skills.join(", ") || "-"}</p>
              <p><b>Missing:</b> {match.missing_skills.join(", ") || "-"}</p>
              <button onClick={makeRoadmap}>Create learning roadmap</button>
            </>
          )}
        </section>
      )}

      {roadmap && (
        <section className="card">
          <h2>Learning roadmap ({roadmap.progress}% done)</h2>
          {roadmap.weeks.map((w) => (
            <label key={w.week} style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <input
                type="checkbox"
                style={{ width: "auto" }}
                checked={w.done}
                onChange={(e) => toggleWeek(w.week, e.target.checked)}
              />
              Week {w.week}: {w.topic}
            </label>
          ))}
        </section>
      )}

      {resume && (
        <section className="card wide">
          <h2>3. Practice interview</h2>
          <label>Role<input value={role} onChange={(e) => setRole(e.target.value)} /></label>
          <label>
            Type
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="technical">Technical</option>
              <option value="behavioral">Behavioral</option>
              <option value="hr">HR</option>
            </select>
          </label>
          <button onClick={startInterview}>Start interview</button>
          {session && session.questions.map((q) => (
            <div key={q} className="q">
              <p>{q}</p>
              <textarea rows={3} value={answers[q] || ""} onChange={(e) => setAnswers({ ...answers, [q]: e.target.value })} />
              <button onClick={() => grade(q)}>Evaluate answer</button>
              {results[q] && (
                <p>
                  <b>{results[q].score}/10</b> {results[q].feedback} {results[q].missing.join(" ")}
                  {results[q].star && results[q].star.missing.length > 0 &&
                    ` STAR parts not found: ${results[q].star.missing.join(", ")}.`}
                </p>
              )}
            </div>
          ))}
        </section>
      )}
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Auth />} />
        <Route path="/register" element={<Auth register />} />
        <Route path="/forgot" element={<Forgot />} />
        <Route path="/reset" element={<Reset />} />
      </Route>

      <Route element={<Guard><AppShell /></Guard>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/app" element={<Workspace />} />
        <Route path="/stories" element={<Stories />} />
        <Route path="/tracker" element={<Tracker />} />
        <Route path="/voice" element={<Voice />} />
        <Route path="/history" element={<History />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/defense" element={<Defense />} />
      </Route>
    </Routes>
  );
}