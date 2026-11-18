import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { errText } from "./api.js";

export default function Settings() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const deleteAccount = async (e) => {
    e.preventDefault();
    if (!window.confirm("This permanently deletes your account, resumes, interviews, stories and jobs. Continue?")) return;
    try {
      await api.delete("/auth/me/", { data: { password } });
      localStorage.clear();
      navigate("/");
    } catch (err) { setError(errText(err)); }
  };

  return (
    <main className="grid">
      <section className="card">
        <h2>Privacy</h2>
        <p>
          Your resume file is read in memory and never stored. Only the extracted text and analysis are saved.
          If AI is turned on, your typed answers and detected skills are sent to the AI provider.
        </p>
      </section>
      <form className="card" onSubmit={deleteAccount} style={{ display: "grid", gap: 10 }}>
        <h2>Delete my account</h2>
        <small>This removes everything you saved and cannot be undone.</small>
        <label>Confirm your password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        {error && <p role="alert" className="err">{error}</p>}
        <button>Delete everything</button>
      </form>
    </main>
  );
}