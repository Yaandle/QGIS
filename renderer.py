"""
renderer.py
-----------
Stage 8 — Real World Iteration

Core render function. Expects QGIS to already be initialised by the caller.
Returns a result dict — never raises or exits.
"""

import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def render(label, latitude, longitude, scale, width, height, layers_str, cfg, output_path):
    try:
        from qgis.core import (
            QgsRasterLayer, QgsProject,
            QgsPointXY, QgsCoordinateReferenceSystem,
            QgsCoordinateTransform, QgsMapSettings,
            QgsMapRendererParallelJob, QgsRectangle,
        )
        from qgis.PyQt.QtGui import QColor
        from qgis.PyQt.QtCore import QSize

        src  = cfg["source"]
        src2 = cfg["source2"]

        # Clear project layers from previous job
        QgsProject.instance().removeAllMapLayers()

        def build_layer(url, wms_layer, layer_name):
            params = (
                f"url={url}&layers={wms_layer}"
                f"&styles=default&format=image/png&crs=EPSG:4326&version=1.3.0"
                f"&timeout=120"
            )
            lyr = QgsRasterLayer(params, layer_name, "wms")
            if not lyr.isValid():
                return None, lyr.error().message()
            QgsProject.instance().addMapLayer(lyr)
            return lyr, None

        LAYER_REGISTRY = {
            "base":    lambda: build_layer(src["wms_url"],  src["wms_layer"],  src["layer_name"]),
            "overlay": lambda: build_layer(src2["wms_url"], src2["wms_layer"], src2["layer_name"]),
        }

        requested = [l.strip() for l in layers_str.split(",")]
        layers = []
        for key in reversed(requested):
            lyr, err = LAYER_REGISTRY[key]()
            if lyr is None:
                return {"status": "layer_error", "render_s": None, "output": None, "error": err}
            layers.append(lyr)

        crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")
        crs_3857 = QgsCoordinateReferenceSystem("EPSG:3857")
        transform = QgsCoordinateTransform(crs_4326, crs_3857, QgsProject.instance())
        centre    = transform.transform(QgsPointXY(longitude, latitude))

        mpp    = scale * 0.000264583
        half_w = (width  / 2) * mpp
        half_h = (height / 2) * mpp

        extent = QgsRectangle(
            centre.x() - half_w, centre.y() - half_h,
            centre.x() + half_w, centre.y() + half_h,
        )

        settings = QgsMapSettings()
        settings.setLayers(layers)
        settings.setOutputSize(QSize(width, height))
        settings.setExtent(extent)
        settings.setDestinationCrs(crs_3857)
        settings.setBackgroundColor(QColor(255, 255, 255))

        t0  = time.perf_counter()
        job = QgsMapRendererParallelJob(settings)
        job.start()
        job.waitForFinished()
        elapsed = time.perf_counter() - t0

        image = job.renderedImage()
        if image.isNull():
            return {"status": "null_image", "render_s": elapsed, "output": None, "error": "Rendered image is null"}

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path, "PNG")

        return {"status": "ok", "render_s": elapsed, "output": output_path, "error": None}

    except Exception as e:
        return {"status": "exception", "render_s": None, "output": None, "error": str(e)}
