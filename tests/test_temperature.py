"""Tests for thermal conversions: ST scaling, Planck inversion, emissivity."""

import math

import pytest

from thermal.temperature import (
    BAND10_CONSTANTS,
    C2_UM_K,
    LAMBDA_B10_UM,
    brightness_temp_to_lst_c,
    celsius_stats,
    dn_to_radiance,
    emissivity_correct,
    kelvin_to_celsius,
    radiance_to_brightness_temp,
    st_dn_to_celsius,
    st_dn_to_kelvin,
)


def test_st_dn_to_kelvin_scalar():
    # Landsat C2L2: DN 30000 -> 300.00 K
    assert st_dn_to_kelvin(30000) == pytest.approx(300.0)


def test_st_dn_to_celsius_scalar():
    assert st_dn_to_celsius(30000) == pytest.approx(300.0 - 273.15)


def test_kelvin_to_celsius_zero():
    assert kelvin_to_celsius(273.15) == pytest.approx(0.0)


def test_dn_to_radiance():
    assert dn_to_radiance(30000, 0.0003342, 0.1) == pytest.approx(
        30000 * 0.0003342 + 0.1
    )


def test_planck_inversion_hand_computed():
    # Hand-computed: L=10.0 W/m^2/sr/um, Landsat 8 constants
    k1, k2 = 774.8853, 1321.0789
    expected = k2 / math.log(k1 / 10.0 + 1.0)
    assert radiance_to_brightness_temp(10.0, k1, k2) == pytest.approx(expected)


def test_planck_inversion_known_temperature():
    # Invert: a 300 K blackbody at 10.9 um has radiance k1/(exp(k2/300)-1)
    k1, k2 = BAND10_CONSTANTS["landsat8"]["k1"], BAND10_CONSTANTS["landsat8"]["k2"]
    L = k1 / (math.exp(k2 / 300.0) - 1.0)
    assert radiance_to_brightness_temp(L, k1, k2) == pytest.approx(300.0, rel=1e-6)


def test_planck_inversion_nonpositive_radiance_is_nan():
    assert math.isnan(radiance_to_brightness_temp(0.0, 774.8853, 1321.0789))
    assert math.isnan(radiance_to_brightness_temp(-5.0, 774.8853, 1321.0789))


def test_emissivity_correct_perfect_emitter_unchanged():
    assert emissivity_correct(300.0, emissivity=1.0) == pytest.approx(300.0)


def test_emissivity_correct_hand_computed():
    tb, eps = 300.0, 0.98
    expected = tb / (1.0 + (LAMBDA_B10_UM * tb / C2_UM_K) * math.log(eps))
    assert emissivity_correct(tb, emissivity=eps) == pytest.approx(expected)


def test_emissivity_correct_raises_lst():
    # Lower emissivity -> larger upward correction
    assert emissivity_correct(300.0, 0.95) > emissivity_correct(300.0, 0.98) > 300.0


def test_emissivity_correct_rejects_bad_emissivity():
    with pytest.raises(ValueError):
        emissivity_correct(300.0, emissivity=0.0)
    with pytest.raises(ValueError):
        emissivity_correct(300.0, emissivity=1.5)


def test_full_fallback_path_sane_range():
    # Typical TIRS B10 DN for a warm land pixel
    lst_c = brightness_temp_to_lst_c(30000, sensor="landsat8", emissivity=0.98)
    assert 0.0 < lst_c < 60.0


def test_full_fallback_path_unknown_sensor():
    with pytest.raises(ValueError):
        brightness_temp_to_lst_c(30000, sensor="landsat7")


def test_fallback_landsat9_differs_slightly_from_landsat8():
    l8 = brightness_temp_to_lst_c(30000, sensor="landsat8")
    l9 = brightness_temp_to_lst_c(30000, sensor="landsat9")
    assert l8 != l9
    assert abs(l8 - l9) < 3.0  # same ballpark, different constants


def test_array_path_nan_safe():
    import numpy as np

    out = st_dn_to_celsius(np.array([30000.0, float("nan")]))
    assert out[0] == pytest.approx(26.85)
    assert math.isnan(out[1])


def test_celsius_stats_known_values():
    mean, median, std, vmin, vmax, p10, p90, n = celsius_stats([10.0, 20.0, 30.0])
    assert mean == pytest.approx(20.0)
    assert median == pytest.approx(20.0)
    assert vmin == pytest.approx(10.0)
    assert vmax == pytest.approx(30.0)
    assert n == 3.0


def test_celsius_stats_empty():
    stats = celsius_stats([])
    assert math.isnan(stats[0])
    assert stats[7] == 0.0


def test_celsius_stats_ignores_nan():
    mean, *_rest, n = celsius_stats([10.0, float("nan"), 30.0])
    assert mean == pytest.approx(20.0)
    assert n == 2.0
