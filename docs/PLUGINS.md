# Plugin Marketplace

StudyGuard has two plugin systems (detectors and data sources) plus seams for
exporters, notifications, and coach strategies. Third parties publish a package
exposing an entry point — no core changes.

## Registered built-ins
| Plugin | Type | Status |
| --- | --- | --- |
| camera | data source | ✅ implemented |
| demo | data source | ✅ implemented (seed) |
| google_calendar (mock + OAuth seam) | data source | ✅ mock; OAuth planned |
| study (PostureFocusDetector) | detector | ✅ implemented |
| json / csv / markdown | exporter | ✅ implemented |

## Example (this repo): Pomodoro
`plugins/pomodoro_plugin.py` is a complete example data source that turns a
Pomodoro schedule into `planned_minutes` metric points. Load it and it registers
as `pomodoro`.

## Planned marketplace entries (seams ready)
calendar (Notion/Outlook/Apple), wearable (Fit/Apple Health/Garmin/Fitbit),
Moodle/Canvas LMS, Discord/OBS/Spotify/focus-music (notification/context).

## Author a plugin
Implement the 5-method `DataSource` (or `Detector`) protocol, decorate with
`@register_source("key")`, and expose an entry point:
```toml
[project.entry-points."studyguard.detectors"]
my_detector = "my_pkg.module:MyDetector"
```
