import { useEffect, useRef, useState } from "react";
import api, { errText } from "./api.js";

const FILLERS = ["um", "uh", "like", "basically", "actually", "literally", "you know", "kind of", "sort of"];
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function measure(text, seconds) {
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const lower = text.toLowerCase();
  const fillers = {};
  FILLERS.forEach((f) => {
    const n = (lower.match(new RegExp(`(?<![a-z'])${f}(?![a-z'])`, "g")) || []).length;
    if (n) fillers[f] = n;
  });
  const wpm = seconds >= 5 && words > 0 ? Math.round(words / (seconds / 60)) : null;
  return { words, fillers, wpm, fillerTotal: Object.values(fillers).reduce((a, b) => a + b, 0) };
}

export default function Voice() {
  const [question, setQuestion] = useState("");
  const [transcript, setTranscript] = useState("");
  const [listening, setListening] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const recRef = useRef(null);
  const timerRef = useRef(null);
  const finalRef = useRef("");

  useEffect(() => () => {
    recRef.current?.stop();
    clearInterval(timerRef.current);
    window.speechSynthesis?.cancel();
  }, []);

    const getQuestion = async () => {
    setError(""); setResult(null); setLoading(true);
    try {
      const { data } = await api.post("/interviews/questions/", { role: "Software Engineer", category: "behavioral" });
      setQuestion(data.questions[Math.floor(Math.random() * data.questions.length)]);
    } catch (err) {
      setError(errText(err));
    } finally {
      setLoading(false);
    }
  };

  const speak = () => {
    if (!question || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(question));
  };

  const start = () => {
    if (!Recognition) {
      setError("This browser has no speech recognition. Use Chrome or Safari, or type your answer below.");
      return;
    }
    setError(""); setResult(null); setSeconds(0); setTranscript("");
    finalRef.current = "";
    const rec = new Recognition();
    rec.lang = "en-US";
    rec.continuous = true;
    rec.interimResults = true;
    rec.onresult = (e) => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const text = e.results[i][0].transcript;
        if (e.results[i].isFinal) finalRef.current += text + " ";
        else interim += text;
      }
      setTranscript(finalRef.current + interim);
    };
    rec.onerror = (e) => setError(`Microphone problem: ${e.error}. Check the browser's mic permission.`);
    rec.onend = () => { setListening(false); clearInterval(timerRef.current); };
    recRef.current = rec;
    rec.start();
    setListening(true);
    const began = Date.now();
    timerRef.current = setInterval(() => setSeconds(Math.round((Date.now() - began) / 1000)), 500);
  };

  const stop = () => recRef.current?.stop();

  const evaluate = async () => {
    setError("");
    try {
      setResult((await api.post("/interviews/evaluate/", { question, answer: transcript })).data);
    } catch (err) { setError(errText(err)); }
  };

  const m = measure(transcript, seconds);

  return (
    <main className="grid">
      {error && <p role="alert" className="err wide">{error}</p>}

      <section className="card">
        <h2>1. Get a question</h2>
        <button onClick={getQuestion} disabled={loading}>{loading ? "Getting a question…" : "New behavioral question"}</button>
        {question && (
          <>
            <p><b>{question}</b></p>
            <button className="ghost" onClick={speak}>Read it aloud</button>
          </>
        )}
      </section>

      <section className="card">
        <h2>2. Answer out loud</h2>
        {!listening
          ? <button onClick={start} disabled={!question}>Start speaking</button>
          : <button onClick={stop}>Stop ({seconds}s)</button>}
        <small><br />Your browser sends audio to its maker (Google or Apple) to transcribe it.</small>
        <label>
          Transcript (you can edit it)
          <textarea rows={6} value={transcript} onChange={(e) => setTranscript(e.target.value)} />
        </label>
      </section>

      {transcript.trim() && (
        <section className="card">
          <h2>3. Speaking stats</h2>
          <p><b>{m.words}</b> words in <b>{seconds}s</b></p>
          <p>Pace: <b>{m.wpm ? `${m.wpm} words/min` : "speak for at least 5 seconds"}</b></p>
          <p>Filler words: <b>{m.fillerTotal}</b>
            {m.fillerTotal > 0 && <small> ({Object.entries(m.fillers).map(([k, v]) => `${k} ×${v}`).join(", ")})</small>}
          </p>
          <small>
            These are counts only. "Like" is sometimes a normal word, and pace includes your pauses.
            The app cannot judge confidence or personality from speech.
          </small>
          <div><button onClick={evaluate}>Also score this answer</button></div>
          {result && (
            <p>
              <b>{result.score}/10</b> {result.feedback} {result.missing.join(" ")}
              {result.source === "heuristic" && <small> (basic scoring; no AI used)</small>}
            </p>
          )}
        </section>
      )}
    </main>
  );
}