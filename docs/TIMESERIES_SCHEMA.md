# Time-series schema

`lst_timeseries.csv` — one row per (zone, pass). Column order is stable and
append-only: new columns go at the end. Mirrors the sibling analytics
engines (survey-vegetation, survey-flood, survey-burn, survey-coast).

| Column | Type | Meaning |
|---|---|---|
| `zone_id` | string | zone identifier (dedupe key) |
| `zone_name` | string | human-readable zone name |
| `pass_id` | string | pass identifier (dedupe key) |
| `date` | string | acquisition date, ISO YYYY-MM-DD |
| `doy` | int | day of year (1–366) |
| `year` | int | calendar year |
| `index` | string | always `"lst"` (dedupe key) |
| `mean` | float | zonal mean LST, °C |
| `median` | float | zonal median LST, °C |
| `std` | float | zonal std dev, °C |
| `minimum` | float | zonal minimum LST, °C |
| `maximum` | float | zonal maximum LST, °C |
| `p10` | float | 10th percentile, °C |
| `p90` | float | 90th percentile, °C |
| `valid_pixels` | float | finite-LST pixels inside the zone |
| `total_pixels` | float | pixels inside the zone (incl. NaN) |
| `cloud_cover` | float | scene cloud cover, percent 0–100 |

## survey-monitor contract

The columns survey-monitor thresholds consume:

- `mean` — per-pass zonal mean LST (°C); e.g. alert when a district's mean
  exceeds 35 °C.
- `maximum` — per-pass zonal max LST (°C); e.g. alert on extreme-heat days.

A monitor site config per zone watches these columns directly.

## Related outputs

- `uhi.csv` — per-zone per-pass UHI intensity vs. the reference zone
  (`uhi_c` = zone mean − reference mean, °C).
- `anomalies.csv` — day-of-year z-score heat anomalies.
- `heatwaves.csv` — heatwave events (start/end dates, duration, peak max).
