import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  BookOpen, Briefcase, FileText, History as HistoryIcon, LayoutDashboard,
  LogOut, Mic, Settings as SettingsIcon, ShieldCheck, Sparkles, User as UserIcon,
} from "lucide-react";

const LINKS = [
  ["/dashboard", "Dashboard", LayoutDashboard],
  ["/app", "Workspace", FileText],
  ["/defense", "Defend Resume", ShieldCheck],
  ["/stories", "Story Bank", BookOpen],
  ["/tracker", "Job Tracker", Briefcase],
  ["/voice", "Voice Practice", Mic],
  ["/history", "History", HistoryIcon],
  ["/profile", "Profile", UserIcon],
  ["/settings", "Settings", SettingsIcon],
];

export function PublicLayout() {
  const loggedIn = !!localStorage.getItem("access");
  return (
    <>
      <header className="site-header">
        <Link to="/" className="logo"><Sparkles size={22} /> PrepWise AI</Link>
        <nav>
          {loggedIn ? (
            <Link className="cta" to="/dashboard">Open app</Link>
          ) : (
            <>
              <Link to="/login">Log in</Link>
              <Link className="cta" to="/register">Get started</Link>
            </>
          )}
        </nav>
      </header>
      <Outlet />
      <footer className="site-footer">
        PrepWise AI · Scores are estimates from transparent rules, not official ATS or hiring results.
      </footer>
    </>
  );
}

export function AppShell() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const title = LINKS.find(([to]) => to === pathname)?.[1] ?? "PrepWise AI";

  return (
    <div className="shell">
      <aside className="sidebar">
        <Link to="/" className="logo"><Sparkles size={22} /> PrepWise AI</Link>
        {LINKS.map(([to, label, Icon]) => (
          <NavLink key={to} to={to} className={({ isActive }) => `side-link${isActive ? " active" : ""}`}>
            <Icon size={18} /> {label}
          </NavLink>
        ))}
        <div className="spacer" />
        <button className="ghost" onClick={() => { localStorage.clear(); navigate("/"); }}>
          <LogOut size={16} /> Log out
        </button>
      </aside>
      <div className="content">
        <div className="topbar"><h1>{title}</h1></div>
        <Outlet />
      </div>
    </div>
  );
}