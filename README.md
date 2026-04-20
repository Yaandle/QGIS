# QGIS Location Image Generator

Stage 1 complete. Generates a PNG of a geographic location using QGIS headless mode.

## Run

Open OSGeo4W Shell:

    cd "E:\Program Files\QGIS 3.44.9\bin"
    python-qgis-ltr.bat "E:\QGIS\generate_location_image.py"

## Config

Edit the top of `generate_location_image.py`:

    LATITUDE        -33.8688
    LONGITUDE       151.2093
    SCALE           50000
    IMAGE_WIDTH_PX  1920
    IMAGE_HEIGHT_PX 1080
    OUTPUT_FILE     location_output.png

## Output

`location_output.png` in E:\QGIS\

## Stages

- [x] Stage 1 — OSM tile layer to PNG
- [ ] Stage 2 — NSW Spatial WMS layer
- [ ] Stage 3 — CLI arguments
