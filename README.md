# survey-thermal

> **Part of [earthwatch-suite](https://github.com/crieck2010/earthwatch-suite)** —
> the remote-sensing project (satellite imagery, change detection, site
> monitoring). Terrestrial surveying lives in
> [survey-suite](https://github.com/crieck2010/survey-suite); the two stay
> compatible through the
> [cross-suite contracts](https://github.com/crieck2010/earthwatch-suite/blob/main/docs/CONTRACTS.md).

The **land-surface-temperature analytics engine** for earthwatch-suite:
per-pass LST maps from satellite thermal imagery, urban heat-island (UHI)
intensity per zone, per-zone temperature time series, day-of-year heat
anomalies, and heatwave event flagging.

Two LST paths: **Landsat Collection 2 Level-2 `ST_B10`** (DN × 0.00341802 + 149 → Kelvin
→ °C) as the primary, and a **brightness-temperature fallback** (TOA
radiance → Planck inversion → emissivity correction) for Landsat 8/9 TIRS
band 10 when only Level-1 data exists.

## Quickstart (no network — synthetic demo)

```bash
pip install survey-thermal
survey-thermal demo --out-dir ./thermal-demo
```

That runs the full pipeline on seeded synthetic data: two zones (urban
downtown, rural meadow) over 2022–2024, a planted +4.5 °C urban heat
island, and a planted summer-2024 heatwave — and prints what it found:

```
=== survey-thermal demo (synthetic, 2022–2024) ===
timeseries rows : 72 -> ./thermal-demo/lst_timeseries.csv
UHI records     : 36 (mean downtown UHI: +4.51 °C)
hot anomalies   : 3 -> ./thermal-demo/anomalies.csv
heatwave events : 1 -> ./thermal-demo/heatwaves.csv
```

## Installation

Requires Python 3.9+ and numpy.

```bash
# Core engine (stdlib + numpy)
pip install .

# With real satellite acquisition (survey-imagery STAC pipeline)
pip install ".[acquire]"

# With GeoTIFF read/write
pip install ".[raster]"

# Everything
pip install ".[full]"
```

## CLI reference

```
survey-thermal lst --scene <tif> --source st|toa --out lst.tif
    Convert a thermal scene to an LST map (°C) + QML style.
    --source st  : Landsat C2L2 ST_B10 (default)
    --source toa : brightness-temp fallback (--sensor landsat8|landsat9,
                   --emissivity 0.98)

survey-thermal timeseries --zones zones.geojson --start 2022-01-01 \
    --end 2024-12-31 --out lst_timeseries.csv
    Per-zone per-pass LST series (incremental appends, deduped).
    Add --synthetic to run on seeded demo data instead of real acquisition.

survey-thermal uhi --timeseries lst_timeseries.csv [--reference meadow] \
    --out uhi.csv
    UHI intensity (°C) per zone per pass vs. the reference zone.
    Without --reference, the coolest zone is auto-selected (heuristic —
    vet it; see docs/LST_SPEC.md).

survey-thermal heatwave --timeseries lst_timeseries.csv \
    [--threshold 38.0] [--consecutive 3] --out heatwaves.csv
    Flag events where max LST ≥ threshold for N consecutive passes.

survey-thermal anomalies --timeseries lst_timeseries.csv \
    [--field mean|maximum] --out anomalies.csv
    Day-of-year z-score heat anomalies (hot direction).

survey-thermal demo --out-dir ./thermal-demo
    The full synthetic pipeline in one command.
```

## Output schemas

- `lst_timeseries.csv` — one row per (zone, pass): zonal LST stats in °C.
  See `docs/TIMESERIES_SCHEMA.md`. The `mean` and `maximum` columns are the
  **survey-monitor contract**: a monitor site config per zone can threshold
  them directly (e.g. alert when downtown's mean LST exceeds 35 °C).
- `uhi.csv` — per-zone per-pass UHI intensity (`uhi_c`) vs. the reference.
- `anomalies.csv` — day-of-year z-score heat anomalies.
- `heatwaves.csv` — heatwave events (start/end, duration, peak max).
- `*_lst_<date>.tif` + `.qml` — per-pass LST maps with a diverging
  blue→red QGIS style.

## Suite integration

```python
# survey-monitor: watch a zone's mean LST (thresholds on the CSV columns)
# site config: index "lst", metric "mean", threshold 35.0 (°C)

# survey-change: diff two LST rasters for heat-delta maps
# survey-qgis: drag the .tif + .qml straight into QGIS
```

Real acquisition reuses survey-imagery's STAC search and reads the `tirs1`
(ST_B10) band via lazy import — nothing thermal is reimplemented there,
and nothing here duplicates survey-imagery. See `docs/LST_SPEC.md` for the
source comparison and resolution honesty notes.

## The maths

`docs/MATHS.md` explains every conversion at an accessible level:
ST_B10 scaling, the Planck inversion, emissivity correction, UHI as a
pass-aligned difference, day-of-year z-scores, and heatwave streak logic.

## Limitations (honest)

- **Resolution:** Landsat thermal is 100 m native, resampled to 30 m.
  Small hotspots are indicative, not measured.
- **Emissivity:** the fallback path assumes one emissivity per scene.
  Use the C2L2 path when available.
- **Clouds:** thermal can't see through cloud; clouded pixels are NaN and
  never count. `cloud_cover` percent travels on every record for gating.
- **Diurnal cycle:** Landsat overpasses ~10:00 local solar time. Don't mix
  sensors or overpass times in one series.
- **LST ≠ air temperature:** surface skin temperature runs hotter than
  2 m air temp on sunny days.
- **Scaling:** defaults assume Landsat Collection 2 ST scaling
  (DN × 0.00341802 + 149 K, verified against live STAC metadata). When
  feeding a real STAC item, prefer its per-asset `raster:bands`
  scale/offset via `st_scale_offset_from_stac()`.
- **Screening tool**, not a microclimate study or a heat-health warning
  system.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
