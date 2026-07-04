"use strict";
// StudyGuard AI desktop SPA -- V2. Consumes ONLY the REST API (same StudyGuardService
// as the web dashboard). Falls back to embedded demo data if the API is unreachable,
// so the UI is always fully populated and testable offline.
const API = "/api/v1";
const PAGES = ["Overview", "Analytics", "AI Coach", "Goals", "Sessions", "Settings", "About"];
let USING_MOCK = false;

function mockAnalytics() {
  const days = [];
  const base = new Date("2026-01-01T00:00:00Z");
  const focusSeq = [58, 63, 60, 68, 74, 70, 79, 82, 78, 85, 88, 83, 90, 91];
  for (let i = 0; i < focusSeq.length; i++) {
    const d = new Date(base.getTime() + i * 86400000);
    days.push({ date: d.toISOString().slice(0, 10), study_minutes: 45 + (i % 5) * 8, avg_focus: focusSeq[i], avg_posture: 70 + (i % 6) * 3, sample_count: 60 });
  }
  return { days, streak: 14, trends: { focus: { direction: "improving", slope_per_day: 2.1 }, posture: { direction: "stable", slope_per_day: 0.2 } } };
}
function mockGoals() {
  return {
    xp: 1444, level: 15, xp_into_level: 44, xp_to_next_level: 56, streak_days: 14, consistency: 1.0,
    achievements: [
      { key: "first_session", title: "First session", description: "Completed your first study session.", unlocked: true },
      { key: "streak_3", title: "On a roll", description: "Studied 3 days in a row.", unlocked: true },
      { key: "streak_7", title: "Week warrior", description: "Studied 7 days in a row.", unlocked: true },
      { key: "focus_master", title: "Focus master", description: "Reached an average focus of 90+ in a day.", unlocked: true },
      { key: "marathon", title: "Marathoner", description: "Studied 2+ hours in a single day.", unlocked: false }
    ],
    daily_goal: { period: "daily", target_minutes: 60, actual_minutes: 90, progress: 1.0, achieved: true },
    weekly_goal: { period: "weekly", target_minutes: 300, actual_minutes: 410, progress: 1.0, achieved: true }
  };
}
function mockCoach() {
  return [
    { key: "focus_vs_prev_day", category: "focus", title: "Focus vs. yesterday", message: "You focused better than the previous study day (+8 points).", evidence: ["today avg focus 91 vs previous 83"], supporting_metrics: { delta: 8 }, confidence: "medium" },
    { key: "best_time_of_day", category: "habit", title: "Your peak study time", message: "You tend to focus best in the evening.", evidence: ["highest average focus around 20:00 UTC"], supporting_metrics: {}, confidence: "high" },
    { key: "streak", category: "habit", title: "Consistency", message: "You're on a 14-day study streak \u2014 keep the momentum!", evidence: ["14 consecutive study days"], supporting_metrics: {}, confidence: "high" }
  ];
}
function mockHourly() { return { "9": 62, "10": 66, "14": 58, "19": 88, "20": 91, "21": 84 }; }
function mockSessions() { return mockAnalytics().days.map(d => ({ date: d.date, study_minutes: d.study_minutes, avg_focus: d.avg_focus, avg_posture: d.avg_posture })); }
function mockSettings() { return { theme: "Dark", camera_index: 0, enable_coach: true }; }
function mockAbout() { return { version: "0.1.0" }; }

async function api(path, mock) {
  try {
    const res = await fetch(API + path, { cache: "no-store" });
    if (!res.ok) throw new Error(String(res.status));
    USING_MOCK = false;
    return await res.json();
  } catch (err) {
    USING_MOCK = true;
    return mock();
  }
}

function el(html) { const d = document.createElement("div"); d.innerHTML = html.trim(); return d.firstChild; }
function demoChip() { return USING_MOCK ? '<div class="demo-chip">\u26A1 Demo data \u2014 backend not connected</div>' : ""; }
function skeletonGrid(n) { return '<div class="grid">' + Array.from({ length: n }).map(() => '<div class="skeleton"></div>').join("") + "</div>"; }
function kpi(label, value, trendHtml) {
  return '<div class="card"><div class="kpi-label">' + label + '</div><div class="kpi-value">' + value + '</div>' + (trendHtml || "") + '</div>';
}
function confidenceBadge(level) { return '<span class="badge ' + level + '">' + level + ' confidence</span>'; }

async function pageOverview(view) {
  view.innerHTML = skeletonGrid(4) + skeletonGrid(4);
  const [a, g, coach, hourly] = await Promise.all([
    api("/analytics", mockAnalytics), api("/goals", mockGoals), api("/coach", mockCoach), api("/hourly", mockHourly)
  ]);
  const days = a.days || [];
  const last = days.length ? days[days.length - 1] : { avg_focus: 0, avg_posture: 0, study_minutes: 0 };
  const prev = days.length > 1 ? days[days.length - 2] : last;
  const study = Math.round((last.avg_focus + last.avg_posture) / 2);
  const delta = Math.round(last.avg_focus - prev.avg_focus);
  const trend = delta === 0 ? "" : '<div class="kpi-trend ' + (delta > 0 ? "up" : "down") + '">' + (delta > 0 ? "\u25B2" : "\u25BC") + " " + Math.abs(delta) + " vs prev day</div>";

  view.innerHTML = '<div class="page-enter">' + demoChip() +
    '<h1>Overview</h1><p class="sub">Your study intelligence at a glance</p>' +
    '<div class="ring-row">' +
      '<div class="ring-card"><div id="ring-focus"></div><div class="kpi-label">Focus score</div></div>' +
      '<div class="ring-card"><div id="ring-energy"></div><div class="kpi-label">Energy (posture)</div></div>' +
      '<div class="ring-card"><div id="ring-burnout"></div><div class="kpi-label">Burnout meter</div></div>' +
    '</div>' +
    '<div class="grid">' + kpi("Study Score", study, trend) + kpi("Streak", g.streak_days + " d") + kpi("Level", g.level) + kpi("XP", g.xp) + '</div>' +
    '<div class="card" style="margin-bottom:20px"><div class="kpi-label">Weekly focus trend</div><div id="spark-focus" style="margin-top:8px"></div></div>' +
    '<div id="coach-preview"></div>';

  if (window.SG) {
    SG.ring(document.getElementById("ring-focus"), { value: last.avg_focus, size: 96, stroke: 10, color: "#4F46E5" });
    SG.ring(document.getElementById("ring-energy"), { value: last.avg_posture, size: 96, stroke: 10, color: "#10B981" });
    const burnout = Math.max(0, Math.min(100, 100 - g.consistency * 100 + (delta < 0 ? 20 : 0)));
    SG.ring(document.getElementById("ring-burnout"), { value: burnout, size: 96, stroke: 10, color: burnout > 60 ? "#DC2626" : "#F59E0B" });
    SG.sparkline(document.getElementById("spark-focus"), days.map(d => d.avg_focus), { color: "#7C3AED", height: 56 });
  }
  await renderCoachThinking(document.getElementById("coach-preview"), coach.slice(0, 1));
}

async function renderCoachThinking(container, messages) {
  if (!container) return;
  container.innerHTML = '<div class="card"><span class="coach-avatar">\u2728</span><span class="thinking-dots"><span></span><span></span><span></span></span></div>';
  await new Promise(r => setTimeout(r, window.SG && SG.REDUCED ? 0 : 550));
  container.innerHTML = messages.map(m =>
    '<div class="msg"><span class="coach-avatar">\u2728</span>' + confidenceBadge(m.confidence) +
    '<div style="margin-top:6px"><b>' + m.title + "</b><div>" + m.message + "</div>" +
    (m.evidence && m.evidence.length ? '<div class="evidence">Evidence: ' + m.evidence.join("; ") + "</div>" : "") +
    "</div></div>"
  ).join("");
}

async function pageAnalytics(view) {
  view.innerHTML = skeletonGrid(4);
  const a = await api("/analytics", mockAnalytics);
  const days = a.days || [];
  const rows = days.map(d => "<tr><td>" + d.date + "</td><td>" + d.study_minutes + "</td><td>" + Math.round(d.avg_focus) + "</td><td>" + Math.round(d.avg_posture) + "</td></tr>").join("");
  const heat = days.map(d => {
    const v = d.avg_focus / 100;
    const alpha = 0.15 + v * 0.75;
    return '<div class="heat-cell" title="' + d.date + ": " + Math.round(d.avg_focus) + '" style="background:rgba(79,70,229,' + alpha.toFixed(2) + ')"></div>';
  }).join("");
  view.innerHTML = '<div class="page-enter">' + demoChip() +
    '<h1>Analytics</h1><p class="sub">Focus trend, calendar heatmap, and daily table</p>' +
    '<div class="card" style="margin-bottom:16px"><div class="kpi-label">Weekly trend</div><div id="spark-analytics" style="margin-top:8px"></div></div>' +
    '<div class="card" style="margin-bottom:16px"><div class="kpi-label">Study heatmap</div><div class="heatmap" style="margin-top:10px">' + heat + '</div></div>' +
    '<div class="card"><table><thead><tr><th>Date</th><th>Minutes</th><th>Focus</th><th>Posture</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
  if (window.SG) SG.sparkline(document.getElementById("spark-analytics"), days.map(d => d.avg_focus), { color: "#4F46E5", height: 64 });
}

async function pageCoach(view) {
  view.innerHTML = '<h1>AI Coach</h1><p class="sub">Explainable, evidence-backed coaching</p><div class="card"><span class="coach-avatar">\u2728</span><span class="thinking-dots"><span></span><span></span><span></span></span></div>';
  const coach = await api("/coach", mockCoach);
  await new Promise(r => setTimeout(r, window.SG && SG.REDUCED ? 0 : 450));
  view.innerHTML = '<div class="page-enter">' + demoChip() + '<h1>AI Coach</h1><p class="sub">Explainable, evidence-backed coaching</p>' +
    coach.map(m =>
      '<div class="msg"><span class="coach-avatar">\u2728</span>' + confidenceBadge(m.confidence) +
      '<div style="margin-top:6px"><b>' + m.title + "</b><div>" + m.message + "</div>" +
      (m.evidence && m.evidence.length ? '<div class="evidence">Evidence: ' + m.evidence.join("; ") + "</div>" : "") + "</div></div>"
    ).join("");
}

async function pageGoals(view) {
  view.innerHTML = skeletonGrid(4);
  const g = await api("/goals", mockGoals);
  const wasUnlocked = JSON.parse(sessionStorage.getItem("sg-unlocked") || "[]");
  const newlyUnlocked = g.achievements.filter(a => a.unlocked && !wasUnlocked.includes(a.key));
  sessionStorage.setItem("sg-unlocked", JSON.stringify(g.achievements.filter(a => a.unlocked).map(a => a.key)));
  const glyphs = { first_session: "\uD83C\uDF93", streak_3: "\uD83D\uDD25", streak_7: "\uD83C\uDFC6", focus_master: "\uD83C\uDFAF", marathon: "\uD83E\uDDBE" };
  const achv = g.achievements.map(a =>
    '<div class="achv ' + (a.unlocked ? "unlocked" : "locked") + '"><div class="glyph">' + (glyphs[a.key] || "\uD83C\uDF96\uFE0F") + '</div><b>' + a.title + "</b><div class=\"sub\" style=\"margin:4px 0 0;font-size:12px\">" + a.description + "</div></div>"
  ).join("");
  view.innerHTML = '<div class="page-enter">' + demoChip() + '<h1>Goals &amp; Achievements</h1><p class="sub">Level up by studying consistently</p>' +
    '<div class="grid">' + kpi("Level", g.level) + kpi("XP", g.xp) + kpi("To next level", g.xp_to_next_level + " XP") + kpi("Streak", g.streak_days + " d") + '</div>' +
    '<div class="card" style="margin-bottom:16px"><div class="kpi-label">Daily goal</div><div class="bar"><span style="width:' + Math.round(g.daily_goal.progress * 100) + '%"></span></div>' +
    '<div class="kpi-label" style="margin-top:14px">Weekly goal</div><div class="bar"><span style="width:' + Math.round(g.weekly_goal.progress * 100) + '%"></span></div></div>' +
    '<div class="achv-grid">' + achv + '</div>';
  if (window.SG && newlyUnlocked.length) { SG.confetti(); SG.toast("Achievement unlocked: " + newlyUnlocked[0].title); }
}

async function pageSessions(view) {
  view.innerHTML = skeletonGrid(3);
  const s = await api("/sessions", mockSessions);
  const rows = s.map(x => "<tr><td>" + x.date + "</td><td>" + x.study_minutes + "</td><td>" + Math.round(x.avg_focus) + "</td><td>" + Math.round(x.avg_posture) + "</td></tr>").join("");
  view.innerHTML = '<div class="page-enter">' + demoChip() + '<h1>Sessions</h1><p class="sub">Session timeline</p><div class="card"><table><thead><tr><th>Date</th><th>Minutes</th><th>Focus</th><th>Posture</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
}

async function pageSettings(view) {
  let s;
  try { s = await fetch("/desktop/settings", { cache: "no-store" }).then(r => r.json()); } catch (e) { s = mockSettings(); }
  view.innerHTML = '<div class="page-enter"><h1>Settings</h1><p class="sub">Stored locally on this device</p>' +
    '<div class="card">' +
    '<label class="kpi-label">Theme</label><div style="margin:4px 0 14px">' + s.theme + '</div>' +
    '<label class="kpi-label">Camera index</label><div style="margin:4px 0 14px">' + s.camera_index + '</div>' +
    '<label class="kpi-label">AI coach</label><div>' + (s.enable_coach ? "Enabled" : "Disabled") + '</div>' +
    '</div></div>';
}

async function pageAbout(view) {
  let h;
  try { h = await fetch("/metrics", { cache: "no-store" }).then(r => r.json()); } catch (e) { h = mockAbout(); }
  view.innerHTML = '<div class="page-enter"><h1>About</h1><div class="card">' +
    '<div class="kpi-value">StudyGuard AI</div><p>Version ' + h.version + '</p>' +
    '<p class="sub">Privacy-first, on-device AI study coach. The camera is one of many data sources. No raw frames are ever stored.</p>' +
    '<p class="sub">Dashboard \u2192 Service \u2192 Domain.</p></div></div>';
}

const ROUTER = { Overview: pageOverview, Analytics: pageAnalytics, "AI Coach": pageCoach, Goals: pageGoals, Sessions: pageSessions, Settings: pageSettings, About: pageAbout };
const ICONS = { Overview: "\uD83C\uDFE0", Analytics: "\uD83D\uDCC8", "AI Coach": "\u2728", Goals: "\uD83C\uDFC6", Sessions: "\uD83D\uDD52", Settings: "\u2699\uFE0F", About: "\u2139\uFE0F" };

async function render(page) {
  const view = document.getElementById("view");
  document.querySelectorAll("#nav button").forEach(b => b.classList.toggle("active", b.dataset.page === page));
  try { await ROUTER[page](view); }
  catch (e) { view.innerHTML = '<div class="page-enter"><h1>' + page + '</h1><div class="card">Could not load data: ' + e.message + '</div></div>'; }
  if (window.SG) { SG.revealOnScroll(".reveal"); }
}

function buildNav() {
  const nav = document.getElementById("nav");
  PAGES.forEach(p => {
    const b = document.createElement("button");
    b.dataset.page = p;
    b.innerHTML = '<span>' + (ICONS[p] || "") + "</span><span>" + p + "</span>";
    b.onclick = () => render(p);
    nav.appendChild(b);
  });
}

function setupCommandPalette() {
  if (!window.SG) return;
  const items = PAGES.map(p => ({ label: p, hint: "Go to page" }));
  const palette = SG.commandPalette({ items: items, onRun: (item) => render(item.label) });
  const opener = document.getElementById("cmdk-open");
  if (opener) opener.addEventListener("click", palette.open);
}

async function boot() {
  buildNav();
  setupCommandPalette();
  await render("Overview");
  const splash = document.getElementById("splash");
  if (splash) { splash.classList.add("hidden"); setTimeout(() => splash.remove(), 500); }
}

window.addEventListener("DOMContentLoaded", boot);
