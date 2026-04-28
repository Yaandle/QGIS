# QGIS Location Image Generator

Generates a PNG of a geographic location using QGIS headless mode and a
NSW Spatial Services WMS basemap.

![QGISTask.gif]

## Run

### Single image
Open **OSGeo4W Shell** and invoke `python-qgis-ltr.bat` with script path:

    cd "E:\Program Files\QGIS 3.44.9\bin"
    python-qgis-ltr.bat "E:\QGIS\generate_location_image.py" [OPTIONS]

**All arguments are optional — omitting any falls back to the default.**

| Flag | Alias | Default | Description |
|---|---|---|---|
| `--lat` | `--latitude` | `-33.8688` | Latitude of map centre (decimal degrees) |
| `--lon` | `--longitude` | `151.2093` | Longitude of map centre (decimal degrees) |
| `--scale` | | `50000` | Scale denominator (e.g. `50000` → 1:50,000) |
| `--width` | | `1920` | Output image width in pixels |
| `--height` | | `1080` | Output image height in pixels |
| `--output` | `-o` | `location_output.png` | Output PNG path |

### Batch render
    python-qgis-ltr.bat "E:\QGIS\batch_render.py" [OPTIONS]

| Flag | Default | Description |
|---|---|---|
| `--jobs` | `jobs.csv` | Path to input CSV |
| `--retries` | `3` | Max retries per job on server failure |
| `--backoff` | `5` | Base backoff in seconds (doubles each retry) |
| `--layers` | `base,overlay` | Layer stack override for all jobs |

Input CSV columns: `label, lat, lon, scale, width, height, layers`
(`scale`, `width`, `height`, `layers` are optional per row — fall back to config defaults.)

### Config (Default Fallback)

Edit `config.yaml` in the same directory as the script.

## Sources

- Base: NSW Spatial Services WMS (LPIMap_PlacePoint)
- Overlay: NSW Spatial Services WMS (NSW_Cadastre)

## Output

- Single: `location_output.png` in `E:\QGIS\` (default), or path specified by `--output`
- Batch: `outputs/<label>.png` per job + `results.csv` log

`results.csv` columns: `label, lat, lon, scale, width, height, layers, attempt, status, render_s, output, error`

Every attempt is logged — retries appear as separate rows with incrementing `attempt`.

## Stages

- [x] Stage 1 — OSM tile layer to PNG
- [x] Stage 2 — NSW Spatial WMS layer
- [x] Stage 3 — CLI arguments + config.yaml
- [x] Stage 5 — Speed + Experimentation
- [x] Stage 8 — Real World Iteration



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
Stage 5 — Speed + Experimentation
--------------------------

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
```

### Stage 8 — Real World Iteration
--------------------------

Batch pipeline with retry logic, failure-aware logging, and a 33-job stress test across scale, location, layer composition, output size, and server variance.

#### New files

| File | Purpose |
|---|---|
| `batch_render.py` | Batch entry point — reads jobs CSV, manages retries, writes log |
| `renderer.py` | Extracted render function — called per job, never exits the process |
| `jobs.csv` | Input job list |

    Usage (from OSGeo4W Shell):
        cd "E:\Program Files\QGIS 3.44.9\bin"
        python-qgis-ltr.bat "E:\QGIS\batch_render.py" --jobs "E:\QGIS\jobs.csv" --retries 3 --backoff 5

| Flag | Default | Description |
|---|---|---|
| `--jobs` | `jobs.csv` | Path to input CSV |
| `--retries` | `3` | Max retries per job on server failure |
| `--backoff` | `5` | Base backoff in seconds (doubles each retry) |
| `--layers` | `base,overlay` | Layer stack override for all jobs |

Input CSV columns: `label, lat, lon, scale, width, height, layers`
(`scale`, `width`, `height`, `layers` are optional per row — fall back to config defaults.)

#### Key findings

**4K output is expensive.**
3840×2160 averaged ~51s across two runs vs ~4s for 1920×1080 — roughly a 13× penalty for a 4× pixel increase. Not suitable for batch use without a tiled rendering strategy.

**Aspect ratio affects render time independently of pixel count.**
2048×2048 (4.2MP) took 17.21s while 2560×1440 (3.7MP) took 3.09s. A square canvas is disproportionately slow — server tile assembly is sensitive to canvas shape, not just total resolution.

**Scale variance is noise above street level.**
The scale ladder (1:2,000 → 1:1,000,000) ranged 1.51s–4.54s — all within the server noise floor. No meaningful trend. Scale is not a performance variable for this pipeline above street level.

**Compositing adds negligible time.**
Base: 1.68s. Overlay: 1.03s. Composite: 1.62s. QGIS fetches layers in parallel — a two-layer stack is effectively free. The overlay endpoint has intermittent severe latency (102.29s spike, one hard layer_error observed) that is a server-side condition, not a pipeline cost.

**Geographic coverage is NSW only.**
The NSW Spatial Services WMS has no coverage outside NSW. Non-NSW locations return blank tiles instantly via the QGIS tile cache — not real renders. All valid geographic data is NSW-only.

**Noise floor is ~2 seconds.**
Ten identical repeat runs ranged 1.88s–3.58s. True baseline is ~2s with occasional 3–4s spikes. Differences smaller than 2 seconds between runs should not be interpreted as signal.

**The pipeline shows no degradation over long runs.**
120 consecutive jobs with no retries, no null images, no timing drift across repeat and stamina blocks. The bottleneck remains the server.
```
