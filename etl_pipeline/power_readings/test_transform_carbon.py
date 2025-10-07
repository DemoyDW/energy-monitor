"""Tests for the functions that transform the carbon intensity data from the NESO API."""

from transform_carbon import transform_generation_mix, transform_carbon_intensity_data
from datetime import datetime


def test_transform_generation_mix(generation_mix):
    """Test that transform_generation_mix works as intended on the API's data."""

    transform = transform_generation_mix(generation_mix)

    assert transform == [0, 0, 0, 0, 0, 0, 0, 98.9, 1.1]
    assert all(isinstance(d, (float, int)) for d in transform)
    assert isinstance(transform, list)


def test_transform_carbon_intensity_data():
    """Test that transform_carbon_intensity_data works as intended on the API's data."""

    carbon_data = [{'regionid': 1, 'dnoregion': 'Scottish Hydro Electric Power Distribution', 'shortname': 'North Scotland',
                    'intensity': {'forecast': 0, 'index': 'very low'},
                    'generationmix': [{'fuel': 'biomass', 'perc': 0},
                                      {'fuel': 'coal', 'perc': 0},
                                      {'fuel': 'imports', 'perc': 0},
                                      {'fuel': 'gas', 'perc': 0},
                                      {'fuel': 'nuclear', 'perc': 0},
                                      {'fuel': 'other', 'perc': 0},
                                      {'fuel': 'hydro', 'perc': 0},
                                      {'fuel': 'solar', 'perc': 0},
                                      {'fuel': 'wind', 'perc': 100}]},
                   {'regionid': 2, 'dnoregion': 'SP Distribution', 'shortname': 'South Scotland',
                    'intensity': {'forecast': 1, 'index': 'very low'},
                    'generationmix': [{'fuel': 'biomass', 'perc': 0.7},
                                      {'fuel': 'coal', 'perc': 0},
                                      {'fuel': 'imports', 'perc': 0},
                                      {'fuel': 'gas', 'perc': 0},
                                      {'fuel': 'nuclear', 'perc': 18.9},
                                      {'fuel': 'other', 'perc': 0},
                                      {'fuel': 'hydro', 'perc': 0},
                                      {'fuel': 'solar', 'perc': 1.2},
                                      {'fuel': 'wind', 'perc': 79.2}]}]

    transform = transform_carbon_intensity_data(carbon_data)

    assert len(transform) == 2
    assert isinstance(transform[0][0], datetime)
    assert isinstance(transform[1][0], datetime)
    assert transform[0][1:] == [0, 1, 0, 0, 0, 0, 0, 0, 0, 100, 0]
    assert transform[1][1:] == [1, 2, 0, 0, 0.7, 18.9, 0, 0, 0, 79.2, 1.2]
