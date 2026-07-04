# Component Hierarchies (React, Flutter, Desktop)

## React (web dashboard / Next.js) — ⚠ target hierarchy
```
<App>
  <ThemeProvider>            // tokens.css variables + theme switch
  <AppShell>
    <TopBar> Logo, Search, CommandK, ThemeToggle, Avatar
    <SideNav> NavItem[]
    <Main>
      <PageHeader title actions/>
      <Routes>
        <Dashboard> KpiRow, TrendChart, RadarChart, CoachList, GoalCard
        <Analytics> Tabs, DateRange, Chart, InsightCallout, ExportMenu
        <Coach> WeeklyNarrative, CoachCard[]
        <Reports> ReportView, DownloadPdfButton
        <Goals> XpBar, AchievementGrid, StreakCalendar
        <Plugins> PluginCard[], ConsentDialog
        <Settings> SettingsNav, SettingsSection[]
      </Routes>
    <InsightRail> NextBreak, RecentEvents
  <CommandPalette/> <Toaster/> <DialogRoot/>
```
Primitives: `Button, Card, Badge, ProgressRing, Chart/*, Table, Tooltip,
Snackbar, Dialog, Skeleton` (map 1:1 to COMPONENTS.md).

## Flutter (mobile) — ❌ target hierarchy
```
MaterialApp(theme: sgTheme(light), darkTheme: sgTheme(dark))
  Scaffold
    body: IndexedStack[ HomePage, CoachPage, TimelinePage, GoalsPage, ProfilePage ]
    bottomNavigationBar: NavigationBar(destinations 5)
    floatingActionButton: StartSessionFab
  Widgets: StudyScoreRing, KpiChip, CoachBubble, TimelineTile, TrendChart,
           AchievementCard, GoalRing, WeekHeatmap
```

## Desktop (pywebview + SPA today; native shell) — hierarchy
```
DesktopApp (desktop/main.py)
  Tray + Window(webview -> SPA)
  SPA (desktop/frontend): AppShell > SideNav + View(router)
    Views: Overview, Analytics, Coach, Goals, Sessions, Settings, About
  Service layer (StudyGuardService via REST) — no business logic in UI
```

Status: ✅ hierarchies specified · ⚠ web/desktop SPA implements a subset ·
❌ Flutter app not implemented.
