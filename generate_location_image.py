"""
generate_location_image.py
--------------------------
Stage 1 — Foundational Win

Generates a PNG image of a geographic location using QGIS headless mode.
Uses an XYZ tile layer (OpenStreetMap) as the basemap.

Usage (from OSGeo4W Shell):
    python-qgis generate_location_image.py

Output:
    location_output.png in the same directory as this script.

Requirements:
    QGIS 3.x installed (tested on 3.44.9)
    Run from OSGeo4W Shell, NOT a regular Python interpreter
"""

import sys
import os


# ── Configuration ────────────────────────────────────────────────────────────
LATITUDE   = -33.8688   # Sydney CBD
LONGITUDE  = 151.2093
SCALE      = 50000      # 1:50,000 — zoom level equivalent (~suburb scale)
IMAGE_WIDTH_PX  = 1920
IMAGE_HEIGHT_PX = 1080
OUTPUT_FILE = "location_output.png"

# XYZ tile URL — OpenStreetMap (Stage 1)
## TILE_URL = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0"
## LAYER_NAME = "OpenStreetMap"

# WMS URL — NSW Base Map (Stage 2)
WMS_URL = "https://maps.six.nsw.gov.au/arcgis/services/public/NSW_Base_Map/MapServer/WMSServer"
WMS_LAYER = "LPIMap_PlacePoint"
LAYER_NAME = "NSW_Basemap"
# ─────────────────────────────────────────────────────────────────────────────

def main():
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

    # Supply path to QGIS install — headless flag = True
    QgsApplication.setPrefixPath(r"E:\Program Files\QGIS 3.44.9", True)
    qgs = QgsApplication([], False)  # False = no GUI
    qgs.initQgis()
    print("QGIS initialised OK")

    # 2. Load XYZ tile layer (OSM basemap)
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
        QgsProject.instance().addMapLayer(layer)

    # 3. Set up coordinate reference systems
    # Tile layers use EPSG:3857 (Web Mercator) internally
    # We supply lat/lon in EPSG:4326 and transform it
    crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")
    crs_3857 = QgsCoordinateReferenceSystem("EPSG:3857")
    transform = QgsCoordinateTransform(crs_4326, crs_3857, QgsProject.instance())

    centre_4326 = QgsPointXY(LONGITUDE, LATITUDE)
    centre_3857 = transform.transform(centre_4326)
    print(f"Centre (Web Mercator): {centre_3857.x():.2f}, {centre_3857.y():.2f}")

    # 4. Build map extent from centre + scale
    # At 96 DPI, pixels → metres conversion: 1 px = 0.000264583 m
    dpi = 96
    metres_per_pixel = SCALE * 0.000264583
    half_w = (IMAGE_WIDTH_PX  / 2) * metres_per_pixel
    half_h = (IMAGE_HEIGHT_PX / 2) * metres_per_pixel

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
    settings.setOutputSize(QSize(IMAGE_WIDTH_PX, IMAGE_HEIGHT_PX))
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
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
    saved = image.save(output_path, "PNG")
    if saved:
        print(f"SUCCESS: Image saved to {output_path}")
    else:
        print("ERROR: Failed to save image.")

    # 8. Clean up
    qgs.exitQgis()


if __name__ == "__main__":
    main()
