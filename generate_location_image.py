"""
generate_location_image.py
--------------------------
Stage 5 — Speed + Experimentation

Generates a PNG image of a geographic location using QGIS headless mode.
Uses a NSW Spatial Services WMS layer as the basemap.

Defaults are loaded from config.yaml in the same directory as this script.
CLI arguments override config values.

Added (Stage 5):
  - Render timing logged to results.csv
  - --layers flag for multi-layer composition (comma-separated)
  - --label flag to tag each run in the log
"""

import sys
import os
import argparse
import yaml
import time
import csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.yaml")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def parse_args(cfg):
    loc = cfg["location"]
    mp  = cfg["map"]
    out = cfg["output"]

    parser = argparse.ArgumentParser(
        description="Generate a PNG map image for a geographic location using QGIS headless mode.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--lat", "--latitude",  type=float, default=loc["latitude"],  dest="latitude")
    parser.add_argument("--lon", "--longitude", type=float, default=loc["longitude"], dest="longitude")
    parser.add_argument("--scale",              type=int,   default=mp["scale"])
    parser.add_argument("--width",              type=int,   default=mp["width"])
    parser.add_argument("--height",             type=int,   default=mp["height"])
    parser.add_argument("--output", "-o",       type=str,   default=out["file"])

    parser.add_argument("--label", type=str, default="run")
    parser.add_argument("--layers", type=str, default=None)

    return parser.parse_args()


def main():
    cfg  = load_config()
    args = parse_args(cfg)

    src  = cfg["source"]
    src2 = cfg["source2"]

    WMS_URL    = src["wms_url"]
    WMS_LAYER  = src["wms_layer"]
    LAYER_NAME = src["layer_name"]


    if not os.path.isabs(args.output):
        args.output = os.path.join(SCRIPT_DIR, args.output)

    if args.output == os.path.join(SCRIPT_DIR, cfg["output"]["file"]):
        args.output = os.path.join(SCRIPT_DIR, f"outputs/{args.label}.png")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    from qgis.core import (
        QgsApplication, QgsRasterLayer, QgsProject,
        QgsPointXY, QgsCoordinateReferenceSystem,
        QgsCoordinateTransform, QgsMapSettings,
        QgsMapRendererParallelJob, QgsRectangle,
    )
    from qgis.PyQt.QtGui import QColor
    from qgis.PyQt.QtCore import QSize

    QgsApplication.setPrefixPath(r"E:\Program Files\QGIS 3.44.9", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    from qgis.core import QgsNetworkAccessManager
    QgsNetworkAccessManager.instance().setTimeout(120 * 1000)

    # --- layer builder ---
    def build_layer(url, wms_layer, layer_name):
        params = (
            f"url={url}&layers={wms_layer}"
            f"&styles=default&format=image/png&crs=EPSG:4326&version=1.3.0"
            f"&timeout=120"
        )
        lyr = QgsRasterLayer(params, layer_name, "wms")
        if not lyr.isValid():
            print(f"Layer error ({layer_name}): {lyr.error().message()}")
            return None
        QgsProject.instance().addMapLayer(lyr)
        return lyr

    # --- registry-driven layer stack ---
    LAYER_REGISTRY = {
        "base":    lambda: build_layer(WMS_URL, WMS_LAYER, LAYER_NAME),
        "overlay": lambda: build_layer(src2["wms_url"], src2["wms_layer"], src2["layer_name"]),
    }

    requested = [l.strip() for l in (args.layers or "base,overlay").split(",")]

    # top → bottom = last → first
    layers = list(filter(None, [LAYER_REGISTRY[k]() for k in reversed(requested)]))

    layers_label = args.layers or "base,overlay"

    # --- transform ---
    crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")
    crs_3857 = QgsCoordinateReferenceSystem("EPSG:3857")
    transform = QgsCoordinateTransform(crs_4326, crs_3857, QgsProject.instance())

    centre_3857 = transform.transform(QgsPointXY(args.longitude, args.latitude))

    metres_per_pixel = args.scale * 0.000264583
    half_w = (args.width  / 2) * metres_per_pixel
    half_h = (args.height / 2) * metres_per_pixel

    extent = QgsRectangle(
        centre_3857.x() - half_w, centre_3857.y() - half_h,
        centre_3857.x() + half_w, centre_3857.y() + half_h,
    )

    settings = QgsMapSettings()
    settings.setLayers(layers)
    settings.setOutputSize(QSize(args.width, args.height))
    settings.setExtent(extent)
    settings.setDestinationCrs(crs_3857)
    settings.setBackgroundColor(QColor(255, 255, 255))

    # --- render timing ---
    t0 = time.perf_counter()
    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()
    elapsed = time.perf_counter() - t0

    image = job.renderedImage()
    if image.isNull():
        print("ERROR: Rendered image is null.")
        qgs.exitQgis()
        sys.exit(1)

    image.save(args.output, "PNG")

    # --- logging ---
    log_path = os.path.join(SCRIPT_DIR, "results.csv")
    write_header = not os.path.exists(log_path)

    with open(log_path, "a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["label", "lat", "lon", "scale", "width", "height", "layers", "render_s", "output"])
        w.writerow([
            args.label,
            args.latitude,
            args.longitude,
            args.scale,
            args.width,
            args.height,
            layers_label,
            f"{elapsed:.2f}",
            args.output
        ])

    print(f"Render time: {elapsed:.2f}s")

    qgs.exitQgis()


if __name__ == "__main__":
    main()
