"""
generate_location_image.py
--------------------------
Stage 3 — CLI Arguments

Generates a PNG image of a geographic location using QGIS headless mode.
Uses a NSW Spatial Services WMS layer as the basemap.

Usage (from OSGeo4W Shell):
    python-qgis generate_location_image.py [OPTIONS]

Examples:
    python-qgis generate_location_image.py
    python-qgis generate_location_image.py --lat -33.8688 --lon 151.2093
    python-qgis generate_location_image.py --lat -33.8688 --lon 151.2093 --scale 25000
    python-qgis generate_location_image.py --lat -33.8688 --lon 151.2093 --scale 25000 --width 1920 --height 1080 --output sydney.png

Output:
    location_output.png in the same directory as this script (default),
    or the path specified by --output.

Requirements:
    QGIS 3.x installed (tested on 3.44.9)
    Run from OSGeo4W Shell, NOT a regular Python interpreter
"""

import sys
import os
import argparse


# ── Defaults ─────────────────────────────────────────────────────────────────
DEFAULT_LATITUDE        = -33.8688   # Sydney CBD
DEFAULT_LONGITUDE       = 151.2093
DEFAULT_SCALE           = 50000      # 1:50,000 — zoom level equivalent (~suburb scale)
DEFAULT_IMAGE_WIDTH_PX  = 1920
DEFAULT_IMAGE_HEIGHT_PX = 1080
DEFAULT_OUTPUT_FILE     = "location_output.png"

# WMS source — NSW Base Map (Stage 2)
WMS_URL   = "https://maps.six.nsw.gov.au/arcgis/services/public/NSW_Base_Map/MapServer/WMSServer"
WMS_LAYER = "LPIMap_PlacePoint"
LAYER_NAME = "NSW_Basemap"
# ─────────────────────────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a PNG map image for a geographic location using QGIS headless mode.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--lat", "--latitude",
        type=float,
        default=DEFAULT_LATITUDE,
        dest="latitude",
        metavar="DEGREES",
        help="Latitude of the map centre (decimal degrees, negative = south)",
    )
    parser.add_argument(
        "--lon", "--longitude",
        type=float,
        default=DEFAULT_LONGITUDE,
        dest="longitude",
        metavar="DEGREES",
        help="Longitude of the map centre (decimal degrees, negative = west)",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=DEFAULT_SCALE,
        metavar="DENOMINATOR",
        help="Map scale denominator, e.g. 50000 means 1:50,000",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_IMAGE_WIDTH_PX,
        dest="width",
        metavar="PIXELS",
        help="Output image width in pixels",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_IMAGE_HEIGHT_PX,
        dest="height",
        metavar="PIXELS",
        help="Output image height in pixels",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        metavar="PATH",
        help="Output PNG file path (relative paths resolve to the script directory)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Resolve relative output paths against the script directory, not cwd
    if not os.path.isabs(args.output):
        args.output = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)

    print(f"Location  : {args.latitude}, {args.longitude}")
    print(f"Scale     : 1:{args.scale:,}")
    print(f"Image size: {args.width} × {args.height} px")
    print(f"Output    : {args.output}")

    # 1. Initialise QGIS application in headless mode
    from qgis.core import (
        QgsApplication,
        QgsRasterLayer,
        QgsProject,
        QgsPointXY,
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform,
        QgsMapSettings,
        QgsMapRendererParallelJob,
        QgsRectangle,
    )
    from qgis.PyQt.QtGui import QImage, QPainter, QColor
    from qgis.PyQt.QtCore import QSize, Qt

    QgsApplication.setPrefixPath(r"E:\Program Files\QGIS 3.44.9", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    print("QGIS initialised OK")

    # 2. Load WMS layer
    wms_params = (
        f"url={WMS_URL}"
        f"&layers={WMS_LAYER}"
        f"&styles=default"
        f"&format=image/png"
        f"&crs=EPSG:4326"
        f"&version=1.3.0"
    )
    layer = QgsRasterLayer(wms_params, LAYER_NAME, "wms")
    if not layer.isValid():
        print("Layer error:", layer.error().message())
        qgs.exitQgis()
        sys.exit(1)
    QgsProject.instance().addMapLayer(layer)  # moved inside the valid branch

    # 3. Transform centre point to Web Mercator
    crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")
    crs_3857 = QgsCoordinateReferenceSystem("EPSG:3857")
    transform = QgsCoordinateTransform(crs_4326, crs_3857, QgsProject.instance())

    centre_4326 = QgsPointXY(args.longitude, args.latitude)
    centre_3857 = transform.transform(centre_4326)
    print(f"Centre (Web Mercator): {centre_3857.x():.2f}, {centre_3857.y():.2f}")

    # 4. Build map extent from centre + scale
    dpi = 96
    metres_per_pixel = args.scale * 0.000264583
    half_w = (args.width  / 2) * metres_per_pixel
    half_h = (args.height / 2) * metres_per_pixel

    extent = QgsRectangle(
        centre_3857.x() - half_w,
        centre_3857.y() - half_h,
        centre_3857.x() + half_w,
        centre_3857.y() + half_h,
    )
    print(f"Extent: {extent}")

    # 5. Configure map settings
    settings = QgsMapSettings()
    settings.setLayers([layer])
    settings.setOutputSize(QSize(args.width, args.height))
    settings.setExtent(extent)
    settings.setDestinationCrs(crs_3857)
    settings.setBackgroundColor(QColor(255, 255, 255))

    # 6. Render
    print("Rendering map...")
    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()

    image = job.renderedImage()
    if image.isNull():
        print("ERROR: Rendered image is null.")
        qgs.exitQgis()
        sys.exit(1)

    # 7. Save output
    saved = image.save(args.output, "PNG")
    if saved:
        print(f"SUCCESS: Image saved to {args.output}")
    else:
        print("ERROR: Failed to save image.")

    # 8. Clean up
    qgs.exitQgis()


if __name__ == "__main__":
    main()
