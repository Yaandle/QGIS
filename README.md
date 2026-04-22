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
- [x] Stage 3 — CLI arguments + config.yaml
- [ ] Stage 5 — Speed + Experimentation

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
    python-qgis-ltr generate_location_image.py [OPTIONS]

Examples:
    python-qgis-ltr generate_location_image.py
    python-qgis-ltr generate_location_image.py --lat -33.8688 --lon 151.2093
    python-qgis-ltr generate_location_image.py --lat -33.8688 --lon 151.2093 --scale 25000
    python-qgis generate_location_image.py --lat -33.8688 --lon 151.2093 --scale 25000 --width 1920 --height 1080 --output sydney.png

Output:
    location_output.png in the same directory as this script (default),
    or the path specified by --output.

Requirements:
    QGIS 3.x installed (tested on 3.44.9)
    Run from OSGeo4W Shell, NOT a regular Python interpreter
```


```
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

Usage (from OSGeo4W Shell):
    python-qgis generate_location_image.py [OPTIONS]

Examples:
    python-qgis-ltr generate_location_image.py
    python-qgis-ltr generate_location_image.py --lat -33.8688 --lon 151.2093
    python-qgis-ltr generate_location_image.py --label "exp2_scale_2000" --scale 2000
    python-qgis-ltr generate_location_image.py --label "exp4_composite" --layers "LPIMap_PlacePoint,NSW_Cadastre"

Output:
    location_output.png (default) + results.csv log
---
# The Five Experiments

Experiment 1 — Source Type 
Experiment 2 — Scale
Experiment 3 — Location
Experiment 4 — Layer Composition
Experiment 5 — Render Performance
---

## Experiment 1 — Source Type

Tested base WMS vs overlay WMS in isolation at the same location and scale.

| Layer         | Time  |
|--------------|------:|
| Base only     | 2.89s |
| Overlay only  | 3.82s |

Both sources are viable individually. The overlay at 3.82s was unexpectedly competitive — the 37s result from the first data set was server variance, not a real characteristic.

The finding is that layer type alone does not determine performance. Server state does.

---

## Experiment 2 — Scale

Tested composite layers across four scale denominators at Sydney CBD.

| Scale       | Time   |
|------------|-------:|
| 1:200,000  | 14.64s |
| 1:50,000   | 12.65s |
| 1:10,000   | 4.99s  |
| 1:2,000    | 2.25s  |

Smaller extents are faster. The 10k and 2k scales align with efficient tile levels on the server.

The 200k result reflects the server assembling data across a large geographic extent.

Street-level requests are the fastest configuration.

---

## Experiment 3 — Location

Tested composite layers across geographic locations at a consistent scale.

| Location                 | Time  |
|--------------------------|------:|
| Sydney CBD               | 5.73s |
| Bathurst                 | 2.39s |
| Rural (-31.5, 146.0)     | 2.67s |
| Dubbo                    | 3.00s |

NSW Spatial WMS covers the state uniformly. There are no coverage gaps.

Observed slowdowns are attributable to server load at the time of request.

Geographic location is not a performance variable for this source.

---

## Experiment 4 — Layer Composition

Composite render times show that QGIS handles parallel layer fetching efficiently.

The primary finding is visual rather than performance-based:

- The overlay introduces noise at most scales  
- The base layer is cleaner and more legible on its own  

This shifts the focus from performance to output quality, leading into Stage 6.

---

## Experiment 5 — Render Performance

The primary bottleneck is server availability.

It is not:
- Geographic location  
- Scale  
- QGIS initialization  
- Local hardware  

Evidence: identical requests returning between ~2 seconds and ~120 seconds across runs.

The pipeline itself is consistent and performant. Variability is external.

**Engineering implication:**
- Implement retry logic  
- Do not rely solely on timeout tuning  

---
```
