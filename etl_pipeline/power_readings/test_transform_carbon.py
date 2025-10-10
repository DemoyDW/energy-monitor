"""Tests for the functions that transform the carbon intensity data from the NESO API."""

from transform_carbon import transform_generation_mix, transform_carbon_intensity_data
from datetime import datetime
from copy import deepcopy


def test_transform_generation_mix(generation_mix):
    """Test that transform_generation_mix works as intended on the API's data."""

    generation_data = {'generationmix': generation_mix}
    transform = transform_generation_mix(generation_data)

    assert transform == [0, 0, 0, 0, 0, 0, 0, 98.9, 1.1]
    assert all(isinstance(d, (float, int)) for d in transform)
    assert isinstance(transform, list)


def test_transform_carbon_intensity_data(generation_mix):
    """Test that transform_carbon_intensity_data works as intended on the API's data."""

    generation_mix_2 = deepcopy(generation_mix)
    generation_mix_2[-1]["perc"] = 79.2
    generation_mix_2[-2]["perc"] = 20.8

    carbon_data = [{'regionid': 1, 'dnoregion': 'Scottish Hydro Electric Power Distribution', 'shortname': 'North Scotland',
                    'intensity': {'forecast': 0, 'index': 'very low'},
                    'generationmix': generation_mix},
                   {'regionid': 2, 'dnoregion': 'SP Distribution', 'shortname': 'South Scotland',
                    'intensity': {'forecast': 1, 'index': 'very low'},
                    'generationmix': generation_mix_2}]

    transform = transform_carbon_intensity_data(carbon_data)

    assert len(transform) == 2
    assert isinstance(transform[0][0], datetime)
    assert isinstance(transform[1][0], datetime)
    assert transform[0][1:] == [0, 1, 0, 0, 0, 0, 0, 0, 0, 98.9, 1.1]
    assert transform[1][1:] == [1, 2, 0, 0, 0, 0, 0, 0, 0, 79.2, 20.8]
