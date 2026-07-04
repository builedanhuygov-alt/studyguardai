# Demo assets & scenarios

StudyGuard ships two zero-setup demo paths so a judge can evaluate without a
webcam:

- **Demo Mode:** `studyguard demo` — a scripted, data-driven walkthrough (seed
  data via the demo source; no camera).
- **Presentation Mode:** `studyguard present` — the same, looped for a live pitch.
- **Web dashboard / Desktop app:** both default to the demo (seed) service, so
  they render full analytics offline.

## Scenario clips (add real footage here)
Drop short consented clips to test the live detector with `--video`:
```
demo/student_good.mp4     # upright, looking at screen
demo/student_bad.mp4      # slouching
demo/student_leave.mp4    # walks away (AWAY)
demo/student_sleep.mp4    # head down
demo/student_phone.mp4    # looking away / distracted
```
Then: `studyguard --video demo/student_good.mp4`.

> These `.mp4` files are **not** committed (privacy + repo size, and we don't
> fabricate footage). Record them locally or use Demo Mode for a no-camera demo.
