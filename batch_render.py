"""
batch_render.py
---------------
Stage 8 — Real World Iteration

Reads a list of render jobs from jobs.csv and renders each one using
renderer.py. Initialises QGIS once for the full batch — not per job.
Handles server failures with retry + exponential backoff.
Logs every attempt (success and failure) to results.csv.

Usage (from OSGeo4W Shell):
    python-qgis-ltr batch_render.py [OPTIONS]

Options:
    --jobs      Path to input CSV (default: jobs.csv)
    --retries   Max retries per job (default: 3)
    --backoff   Base backoff in seconds (default: 5)
    --layers    Override layer stack for all jobs (default: base,overlay)
"""

import os
import sys
import csv
import time
import argparse
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    with open(os.path.join(SCRIPT_DIR, "config.yaml"), "r") as f:
        return yaml.safe_load(f)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch map renderer — Stage 8",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--jobs",    type=str, default=os.path.join(SCRIPT_DIR, "jobs.csv"))
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--backoff", type=int, default=5)
    parser.add_argument("--layers",  type=str, default="base,overlay")
    return parser.parse_args()


def load_jobs(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def log_result(log_path, row):
    write_header = not os.path.exists(log_path)
    with open(log_path, "a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow([
                "label", "lat", "lon", "scale", "width", "height",
                "layers", "attempt", "status", "render_s", "output", "error"
            ])
        w.writerow(row)


def init_qgis():
    from qgis.core import QgsApplication, QgsNetworkAccessManager
    QgsApplication.setPrefixPath(r"E:\Program Files\QGIS 3.44.9", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    QgsNetworkAccessManager.instance().setTimeout(120 * 1000)
    return qgs

def load_jobs(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(row for row in f if not row.startswith("#"))
        return list(reader)
    

def main():
    args = parse_args()
    cfg  = load_config()
    mp   = cfg["map"]

    jobs     = load_jobs(args.jobs)
    log_path = os.path.join(SCRIPT_DIR, "results.csv")

    print(f"Loaded {len(jobs)} job(s) from {args.jobs}")
    print("Initialising QGIS...")
    qgs = init_qgis()
    print("QGIS ready.\n")

    from renderer import render

    summary = {"ok": 0, "failed": 0}

    for job in jobs:
        label  = job["label"]
        lat    = float(job["lat"])
        lon    = float(job["lon"])
        scale  = int(job.get("scale",  mp["scale"]))
        width  = int(job.get("width",  mp["width"]))
        height = int(job.get("height", mp["height"]))
        layers = job.get("layers", args.layers)

        output_path = os.path.join(SCRIPT_DIR, "outputs", f"{label}.png")

        print(f"[{label}] lat={lat} lon={lon} scale={scale} layers={layers}")

        success = False

        for attempt in range(1, args.retries + 2):
            print(f"  Attempt {attempt}...", end=" ", flush=True)

            result = render(
                label=label,
                latitude=lat,
                longitude=lon,
                scale=scale,
                width=width,
                height=height,
                layers_str=layers,
                cfg=cfg,
                output_path=output_path,
            )

            status   = result["status"]
            render_s = f"{result['render_s']:.2f}" if result["render_s"] is not None else ""
            error    = result["error"] or ""

            print(f"{status}" + (f" ({render_s}s)" if render_s else "") + (f" — {error}" if error else ""))

            log_result(log_path, [
                label, lat, lon, scale, width, height,
                layers, attempt, status, render_s, result["output"] or "", error
            ])

            if status == "ok":
                summary["ok"] += 1
                success = True
                break

            if status in ("layer_error", "exception"):
                print("  Hard failure — skipping retries.")
                summary["failed"] += 1
                break

            if attempt <= args.retries:
                wait = args.backoff * (2 ** (attempt - 1))
                print(f"  Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print("  Max retries reached.")
                summary["failed"] += 1

        if not success and status == "null_image":
            summary["failed"] += 1

        print()

    print("=" * 40)
    print(f"Done. {summary['ok']} succeeded, {summary['failed']} failed.")
    print(f"Log: {log_path}")

    qgs.exitQgis()


if __name__ == "__main__":
    main()
