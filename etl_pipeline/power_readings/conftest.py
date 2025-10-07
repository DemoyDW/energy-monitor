"""Conftest file used to create functions to be used repeatably for testing."""

import pytest


@pytest.fixture
def generation_mix():

    return {'generationmix': [{'fuel': 'biomass', 'perc': 0},
                              {'fuel': 'coal', 'perc': 0},
                              {'fuel': 'imports', 'perc': 0},
                              {'fuel': 'gas', 'perc': 0},
                              {'fuel': 'nuclear', 'perc': 0},
                              {'fuel': 'other', 'perc': 0},
                              {'fuel': 'hydro', 'perc': 0},
                              {'fuel': 'solar', 'perc': 1.1},
                              {'fuel': 'wind', 'perc': 98.9}]}
