import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import api, { errText } from "./api.js";

export function Forgot() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setMessage("");
    try {
      const { data } = await api.post("/auth/password-reset/", { email });
      setMessage(data.detail);
    } catch (err) { setError(errText(err)); }
  };

  return (
    <form className="card narrow" onSubmit={submit}>
      <h1>Forgot password</h1>
      <label>Your email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
      {error && <p role="alert" className="err">{error}</p>}
      {message && <p role="status">{message}</p>}
      <button>Send reset link</button>
      <Link to="/login">Back to log in</Link>
    </form>
  );
}

export function Reset() {
  const [params] = useSearchParams();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/auth/password-reset/confirm/", {
        uid: params.get("uid"), token: params.get("token"), password,
      });
      navigate("/login");
    } catch (err) { setError(errText(err)); }
  };

  return (
    <form className="card narrow" onSubmit={submit}>
      <h1>Choose a new password</h1>
      <label>New password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
      {error && <p role="alert" className="err">{error}</p>}
      <button>Update password</button>
    </form>
  );
}