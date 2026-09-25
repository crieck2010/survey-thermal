# The maths

How survey-thermal turns thermal-infrared pixels into temperature analytics,
in plain language. No remote-sensing degree required.

## 1. What the satellite actually measures

Landsat's thermal band (TIRS band 10, ~10.9 µm) doesn't measure temperature
directly — it measures **radiance**: how much thermal-infrared energy reaches
the sensor. Two conversions turn that into land surface temperature (LST).

## 2. Primary path: Landsat Collection 2 Level-2

USGS already did the hard work for C2L2 products. The `ST_B10` band is
surface temperature stored as an integer:

```
kelvin   = DN × 0.01
celsius  = kelvin − 273.15
```

So a DN of 30000 → 300.00 K → 26.85 °C. That's it — one multiplication.

## 3. Fallback path: brightness temperature (Planck inversion)

When only top-of-atmosphere (Level-1) data is available, we invert Planck's
law ourselves:

```
L   = ML × Qcal + AL            # DN → radiance (W/m²/sr/µm)
Tb  = K2 / ln(K1 / L + 1)       # radiance → brightness temperature (K)
```

`K1`, `K2`, `ML`, `AL` are per-sensor constants from the Landsat metadata
(Landsat 8: K1 = 774.8853, K2 = 1321.0789; Landsat 9: K1 = 799.0284,
K2 = 1329.2405). Brightness temperature is the temperature a *perfect
blackbody* would need to emit that radiance — real surfaces aren't perfect,
so one more step is needed.

## 4. Emissivity correction

Real land emits slightly less than a blackbody. The single-channel
correction (Artis & Carnahan / Weng form) adjusts for that:

```
LST = Tb / (1 + (λ·Tb/ρ) · ln(ε))
```

with λ = 10.9 µm (band 10's effective wavelength), ρ = 14388 µm·K, and
ε the broadband emissivity (default 0.98 — typical for vegetation; urban
~0.95–0.97, water ~0.99). Lower emissivity → larger upward correction.
This is the documented assumption of the fallback path: one emissivity for
the whole scene, which is honest for screening work and wrong in detail.

## 5. Urban heat-island intensity

UHI is a *difference*, not an absolute temperature:

```
UHI(zone, pass) = mean_LST(zone, pass) − mean_LST(reference, pass)   [°C]
```

Both means come from the same satellite pass, so sensor calibration and
overpass-time effects cancel. The reference should be vetted rural land —
see the reference-zone methodology in the README.

## 6. Heat anomalies (z-scores)

A July LST is judged against the zone's own history for the same
day-of-year window (±15 days, prior years only):

```
z = (value − baseline_mean) / baseline_std
```

z ≥ +2 flags a hot anomaly. Same approach as survey-vegetation's
phenology-aware anomalies, mirrored here because temperature has the same
seasonality problem NDVI does.

## 7. Heatwaves

A heatwave event is declared when a zone's per-pass **maximum** LST
(the hottest pixel — heat stress lives in the extremes) meets or exceeds
a threshold (default 38 °C) for N consecutive passes (default 3).
Missing data breaks a streak: no data is not evidence of heat.
