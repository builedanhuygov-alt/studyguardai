"""Labeling helper: sample frames from a video into PNGs + a labels template.

Usage: python tools/label_clip.py input.mp4 out_dir --every 15
Writes out_dir/frame_00000.png ... and out_dir/labels.csv with a blank 'status'
column (fill with AWAY/FOCUSED/SLOUCHING/DISTRACTED). Then build a labels.json
for the evaluation pipeline.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2


def main() -> None:
    parser = argparse.ArgumentParser(description="Sample frames for manual labeling.")
    parser.add_argument("video")
    parser.add_argument("out_dir")
    parser.add_argument("--every", type=int, default=15, help="sample every Nth frame")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.video!r}")

    rows = []
    index = sampled = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if index % args.every == 0:
            name = f"frame_{sampled:05d}.png"
            cv2.imwrite(str(out / name), frame)
            rows.append({"frame": name, "status": ""})
            sampled += 1
        index += 1
    cap.release()

    with (out / "labels.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["frame", "status"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Extracted {sampled} frames to {out}. Fill 'status' in labels.csv, then evaluate.")


if __name__ == "__main__":
    main()
