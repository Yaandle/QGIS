# QGIS Location Image Generator

Generates a PNG of a geographic location using QGIS headless mode and a
NSW Spatial Services WMS basemap.

## Run

Open **OSGeo4W Shell** and invoke `python-qgis-ltr.bat` with script path:

    cd "E:\Program Files\QGIS 3.44.9\bin"
    python-qgis-ltr.bat "E:\QGIS\generate_location_image.py" [OPTIONS]

**All arguments are optional — omitting any falls back to the default.**

### Options

| Flag | Alias | Default | Description |
|---|---|---|---|
| `--lat` | `--latitude` | `-33.8688` | Latitude of map centre (decimal degrees) |
| `--lon` | `--longitude` | `151.2093` | Longitude of map centre (decimal degrees) |
| `--scale` | | `50000` | Scale denominator (e.g. `50000` → 1:50,000) |
| `--width` | | `1920` | Output image width in pixels |
| `--height` | | `1080` | Output image height in pixels |
| `--output` | `-o` | `location_output.png` | Output PNG path |


### Config (**Default Fallback**)

Edit the top of `generate_location_image.py`:

    LATITUDE        -33.8688
    LONGITUDE       151.2093
    SCALE           50000
    IMAGE_WIDTH_PX  1920
    IMAGE_HEIGHT_PX 1080
    OUTPUT_FILE     location_output.png

## Sources

Stage 1 — OpenStreetMap XYZ tiles
Stage 2 — NSW Spatial Services WMS (LPIMap_PlacePoint)
  

## Output

`location_output.png` in E:\QGIS\ (default), or the path specified by --output.

## Stages

- [x] Stage 1 — OSM tile layer to PNG
- [x] Stage 2 — NSW Spatial WMS layer
- [x] Stage 3 — CLI arguments

### generate_location_image.py

```
Stage 1 — Foundational Win
--------------------------
Generates a PNG image of a geographic location using QGIS headless mode.
Uses an XYZ tile layer (OpenStreetMap) as the basemap.

Usage (from OSGeo4W Shell):
    python-qgis generate_location_image.py

Output:
    location_output.png in the same directory as this script.

Requirements:
    QGIS 3.x installed (tested on 3.44.9)
    Run from OSGeo4W Shell, NOT a regular Python interpreter
```

```
Stage 2 — Repetition + Variation
--------------------------

Generates a PNG image of a geographic location using QGIS headless mode.
Uses an WMS URL (NSW Base Map) as the basemap.

Usage (from OSGeo4W Shell):
    python-qgis generate_location_image.py

Output:
    location_output.png in the same directory as this script.

Requirements:
    QGIS 3.x installed (tested on 3.44.9)
    Run from OSGeo4W Shell, NOT a regular Python interpreter
```


```
Stage 3 — CLI Arguments/System Formation
--------------------------
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
```
