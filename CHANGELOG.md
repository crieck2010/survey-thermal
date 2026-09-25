# Changelog

All notable changes to this project follow [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-09-25

Initial release.

- LST conversions: Landsat C2L2 ST_B10 (DN × 0.01 → K → °C) primary path;
  brightness-temperature fallback (TOA radiance → Planck inversion →
  emissivity correction) for Landsat 8/9 TIRS band 10.
- Per-zone per-pass LST time series (°C) with incremental CSV appends,
  deduped on (zone_id, pass_id, index); columns mirror the sibling engines.
- Urban heat-island intensity per zone per pass vs. a rural reference zone
  (user-supplied or auto-selected coolest zone).
- Day-of-year heat-anomaly z-scores (hot direction), mirroring
  survey-vegetation's phenology-aware approach.
- Heatwave event flagging: N consecutive passes with max LST ≥ threshold.
- Diverging blue→red QML style for LST maps; GeoJSON/CSV outputs for QGIS.
- Seeded synthetic demo (urban +4.5 °C UHI, planted 2024 heatwave).
- CLI: `lst | timeseries | uhi | heatwave | anomalies | demo`.
