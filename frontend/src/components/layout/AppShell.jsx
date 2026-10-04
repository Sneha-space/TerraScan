import React, { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Files, Inbox, LayoutGrid, Menu, Rows3, X } from "lucide-react";
import { getHealth, getStats } from "../../api/endpoints";
import config from "../../config";

/** Fire after changing a record's status so the sidebar count updates. */
export const RECORDS_CHANGED = "terrascan:records-changed";

const NAV = [
  { to: "/", label: "Overview", icon: LayoutGrid, end: true },
  { to: "/review", label: "Review queue", icon: Inbox, countKey: "needs_review" },
  { to: "/records", label: "Records", icon: Rows3 },
  { to: "/uploads", label: "Uploads", icon: Files },
];

// name only - there is no logo yet
function Wordmark() {
  return (
    <div>
      <span className="title block text-[1.15rem] leading-6">{config.appName}</span>
      <span className="block text-xs text-ink-faint">{config.appTagline}</span>
    </div>
  );
}

function ServerStatus({ online }) {
  if (online === null) return null;
  return (
    <p className="flex items-center gap-2 text-xs text-ink-faint" role="status">
      <span
        className={`h-2 w-2 rounded-full ${online ? "bg-seal" : "bg-correction"}`}
        aria-hidden="true"
      />
      {online ? "Server connected" : "Server not reachable"}
    </p>
  );
}

function NavItems({ counts }) {
  return (
    <ul className="space-y-1">
      {NAV.map(({ to, label, icon: Icon, end, countKey }) => {
        const count = countKey ? counts?.[countKey] : null;
        return (
          <li key={to}>
            <NavLink
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex h-10 items-center gap-3 rounded-control border px-3 text-sm transition-colors ${
                  isActive
                    ? "border-rule bg-sheet font-semibold text-ink"
                    : "border-transparent text-ink-soft hover:bg-rule-soft hover:text-ink"
                }`
              }
            >
              <Icon className="h-[18px] w-[18px] shrink-0" aria-hidden="true" />
              <span className="flex-1">{label}</span>
              {count > 0 && (
                <span className="tabular rounded-stamp bg-correction-wash px-1.5 text-xs font-semibold text-correction">
                  {count}
                  <span className="sr-only"> waiting</span>
                </span>
              )}
            </NavLink>
          </li>
        );
      })}
    </ul>
  );
}

export default function AppShell() {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [counts, setCounts] = useState(null);
  const [online, setOnline] = useState(null);

  // the queue count changes as records are verified: refresh it on every
  // page change, and when a page announces RECORDS_CHANGED
  useEffect(() => {
    setMenuOpen(false);
    const refresh = () =>
      getStats()
        .then((res) => setCounts(res.data.records))
        .catch(() => setCounts(null));
    refresh();
    window.addEventListener(RECORDS_CHANGED, refresh);
    return () => window.removeEventListener(RECORDS_CHANGED, refresh);
  }, [location.pathname]);

  useEffect(() => {
    const check = () =>
      getHealth()
        .then(() => setOnline(true))
        .catch(() => setOnline(false));
    check();
    const timer = setInterval(check, 30000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e) => e.key === "Escape" && setMenuOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[15.5rem_minmax(0,1fr)]">
      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen flex-col border-r border-rule px-4 py-6 lg:flex">
        <Wordmark />
        <nav className="mt-10 flex-1" aria-label="Main">
          <NavItems counts={counts} />
        </nav>
        <ServerStatus online={online} />
      </aside>

      {/* Phone and tablet top bar */}
      <div className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-rule bg-paper/95 px-4 backdrop-blur lg:hidden">
        <Wordmark />
        <button
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          className="flex h-10 w-10 items-center justify-center rounded-control text-ink hover:bg-rule-soft"
        >
          {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {menuOpen && (
        <div className="fixed inset-0 top-14 z-20 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-ink/20"
            aria-label="Close menu"
            onClick={() => setMenuOpen(false)}
          />
          <nav
            id="mobile-menu"
            aria-label="Main"
            className="relative border-b border-rule bg-paper px-4 pb-5 pt-3"
          >
            <NavItems counts={counts} />
            <div className="mt-5">
              <ServerStatus online={online} />
            </div>
          </nav>
        </div>
      )}

      <main className="w-full min-w-0 px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
        <Outlet />
      </main>
    </div>
  );
}
