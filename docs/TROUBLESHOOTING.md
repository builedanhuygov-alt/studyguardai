# Troubleshooting

## `module 'cv2' has no attribute 'CascadeClassifier'`
A broken or conflicting OpenCV install. Reinstall a single distribution:
```bash
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python opencv-contrib-python-headless
pip install --force-reinstall opencv-python
python -c "import cv2; print(cv2.__version__, hasattr(cv2, 'CascadeClassifier'))"
```
Also ensure no local file named `cv2.py` shadows the package.

## Camera won't open
- Try another index: `python -m studyguard --camera 1`.
- Use replay/fallback: `python -m studyguard --video clip.mp4` or `--fake`.
- On Linux, ensure the user can access `/dev/video0`.

## No window appears / crashes on a headless server or macOS
- Headless machines have no display: run `--headless` (no GUI calls).
- On macOS, OpenCV windows must run on the main thread (the app already does this).
- In Docker/CI, prefer `--headless --fake` or run the test suite instead.

## Low FPS
- Lower the resolution: `--width 480`.
- Increase the detector stride via `sample_every` in `studyguard.toml`.
- Close other camera-using apps.

## `database is locked`
- Another process is writing the same SQLite file. Use a separate `--db` path,
  or stop the other instance. WAL mode is enabled to reduce contention.

## Verbose logs for a bug report
```bash
python -m studyguard --log-level DEBUG
```
Never attach raw video; only derived metrics/logs are needed.
