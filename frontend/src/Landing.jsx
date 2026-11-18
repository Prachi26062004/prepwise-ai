import { Link } from "react-router-dom";
import {
  BookOpen, Briefcase, FileText, Mic, Sparkles, Target, ListChecks, TrendingUp,
} from "lucide-react";

const FEATURES = [
  [FileText, "Resume analysis", "Upload a PDF or DOCX and get a transparent score, detected skills and clear fixes."],
  [ListChecks, "Bullet Proof Score", "See which bullets lack action verbs or evidence, and get honest rewrite suggestions."],
  [Target, "Job matching", "Compare your resume with any job post and see matching and missing skills."],
  [Sparkles, "Mock interviews", "Practice technical, behavioral and HR questions with feedback on each answer."],
  [BookOpen, "Story Bank", "Save real stories in STAR format and find the best one for each question."],
  [Mic, "Voice practice", "Speak your answer and see words per minute and filler-word counts."],
  [Briefcase, "Job tracker", "Move applications from Saved to Offer and see your match score on each."],
  [TrendingUp, "Progress dashboard", "Track scores over time and spot your weakest interview category."],
];

const STEPS = [
  ["Upload your resume", "We read it in memory and keep only the extracted text. Delete it any time."],
  ["Compare with a job", "Paste a job description to see gaps and a learning roadmap."],
  ["Practice and improve", "Answer questions by typing or speaking, then review feedback and your history."],
];

export default function Landing() {
  return (
    <>
      <section className="hero">
        <div className="hero-inner">
          <div>
            <span className="badge"><Sparkles size={14} /> Resume and interview prep in one place</span>
            <h1>Prepare smarter. <span>Get hired faster.</span></h1>
            <p className="lead">
              Analyze your resume, match it to real job posts, and rehearse interviews with feedback you can act on.
            </p>
            <div className="hero-actions">
              <Link className="cta" to="/register">Analyze my resume</Link>
              <Link className="cta ghost" to="/login">I already have an account</Link>
            </div>
          </div>

          <div className="card mock" aria-hidden="true">
            <small>Example report (sample data)</small>
            <p className="big">78</p>
            <div className="bar"><span>Skills</span><div><i style={{ width: "85%" }} /></div><b>85</b></div>
            <div className="bar"><span>Experience</span><div><i style={{ width: "70%" }} /></div><b>70</b></div>
            <div className="bar"><span>Projects</span><div><i style={{ width: "60%" }} /></div><b>60</b></div>
            <small>Add measurable results to your project bullets.</small>
          </div>
        </div>
      </section>

      <section className="section">
        <h2>Everything for your job hunt</h2>
        <p className="sub">From a stronger resume to a confident interview, in one workspace.</p>
        <div className="features">
          {FEATURES.map(([Icon, title, text]) => (
            <div key={title} className="card feature">
              <div className="icon"><Icon size={22} /></div>
              <h3>{title}</h3>
              <p>{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>How it works</h2>
        <p className="sub">Three steps, no setup.</p>
        <div className="steps">
          {STEPS.map(([title, text]) => (
            <div key={title} className="card step">
              <h3>{title}</h3>
              <p style={{ color: "var(--muted)", margin: 0 }}>{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="cta-band">
          <h2>Ready for your next interview?</h2>
          <p>Create a free account and analyze your first resume in a minute.</p>
          <Link className="cta" to="/register">Get started</Link>
        </div>
      </section>
    </>
  );
}