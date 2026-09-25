# Changelog

All notable changes to this project follow [Semantic Versioning](https://semver.org/).

## [0.1.1] — 2026-09-25
### Fixed
- **Landsat C2 surface-temperature scaling (data bug):** `ST_B10` used
  `kelvin = DN × 0.01`; the verified Collection 2 constants are
  `K = DN × 0.00341802 + 149`. Old scaling was off by hundreds of degrees
  on real data; synthetic tests never caught it. Values verified against
  live STAC `raster:bands` metadata (Element84 Earth Search, Planetary
  Computer `landsat-c2-l2`).
- Scaling is now metadata-driven: `st_dn_to_kelvin(dn, scale=None,
  offset=None)` accepts per-asset overrides, and new helper
  `st_scale_offset_from_stac(asset_dict)` reads `scale`/`offset` from a
  STAC asset's `raster:bands` entry, falling back to the C2 constants.
### Added
- Regression tests for the C2 constants (DN 50000 → 319.901 K, DN 0 → 149.0 K),
  metadata-override parity, and STAC-metadata extraction.
- README limitations note advising per-scene `raster:bands` preference.

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
