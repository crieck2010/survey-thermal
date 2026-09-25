# LST spec

How land-surface-temperature rasters are produced and what they mean.

## Sources

| Path | Input | Output | Notes |
|---|---|---|---|
| Primary | Landsat Collection 2 Level-2 `ST_B10` | °C | USGS-retrieved surface temperature; `K = DN × 0.01` |
| Fallback | Landsat L1 TIRS band 10 DN | °C | Planck inversion + emissivity correction (see `docs/MATHS.md`) |

The primary path is preferred whenever C2L2 scenes are available: USGS's
atmospheric correction beats a single-channel inversion. The fallback
exists for archives and sensors without a science-grade LST product.

## Resolution honesty

Landsat thermal is **100 m native**, resampled to 30 m in Collection 2.
A 30 m LST pixel does not resolve 30 m thermal features — treat small
hotspots (single buildings, narrow streets) as indicative, not measured.
The synthetic demo uses 30 m pixels to match this.

## Raster outputs

- `*_lst_<YYYY-MM-DD>.tif` — per-pass LST in °C, float32, NaN = nodata
  (clouds, outside AOI).
- `*_lst_<YYYY-MM-DD>.qml` — diverging blue→red pseudocolor style
  (10 °C → 50 °C) for QGIS.

## Reference-zone methodology (UHI)

UHI intensity = zone mean − reference mean on the same pass. The reference
zone should be:

1. Vegetated, rural, and cloud-free — not water (water is cool but not
   rural land) and not a different elevation/aspect regime.
2. Imaged on the same passes as the target zones (UHI is only computed
   where both have finite means).
3. Under the same overpass conditions (Landsat ~10:00 local solar time;
   don't mix sensors or overpass times).

`--reference` accepts an explicit zone id. Without it, the coolest zone by
mean LST is auto-selected — a heuristic, sensitive to cloud-contaminated
passes and water bodies. Vet the reference before publishing numbers.

## What LST is not

- Not air temperature: LST is *surface* skin temperature, typically hotter
  than 2 m air temperature on sunny days.
- Not a microclimate study: 100 m native resolution, single daily overpass,
  emissivity assumptions. Screening-grade, not engineering-grade.
