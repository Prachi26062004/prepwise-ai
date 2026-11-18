import { useEffect, useState } from "react";
import api, { errText } from "./api.js";

export default function Profile() {
  const [form, setForm] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/auth/profile/")
      .then((r) => setForm({ ...r.data, skills: r.data.skills.join(", ") }))
      .catch((e) => setError(errText(e)));
  }, []);

  if (!form) return <p className="card narrow">{error || "Loading…"}</p>;

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    setError(""); setMessage("");
    try {
      const skills = form.skills.split(",").map((s) => s.trim()).filter(Boolean);
      await api.put("/auth/profile/", { ...form, skills });
      setMessage("Profile saved.");
    } catch (err) { setError(errText(err)); }
  };

  return (
    <form className="card narrow" style={{ maxWidth: 560 }} onSubmit={save}>
      <h1>Your profile</h1>
      <label>Target role<input value={form.target_role} onChange={set("target_role")} placeholder="e.g. Python Developer" /></label>
      <label>
        Experience level
        <select value={form.experience_level} onChange={set("experience_level")}>
          <option>Beginner</option>
          <option>Intermediate</option>
          <option>Advanced</option>
        </select>
      </label>
      <label>Education<textarea rows={3} value={form.education} onChange={set("education")} /></label>
      <label>Experience<textarea rows={3} value={form.experience} onChange={set("experience")} /></label>
      <label>Skills (comma separated)<input value={form.skills} onChange={set("skills")} /></label>
      {error && <p role="alert" className="err">{error}</p>}
      {message && <p role="status">{message}</p>}
      <button>Save profile</button>
    </form>
  );
}