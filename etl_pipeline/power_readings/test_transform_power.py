"""
Tests for transform script of power readings
"""
from datetime import datetime, timedelta, timezone
import pandas as pd
from transform_power import calculate_avg_demand_last_settlement, summarise_energy_generation
import pytest

SETTLEMENT = datetime.now(timezone.utc) - timedelta(minutes=5)


@pytest.mark.parametrize(("times", "demand_values", "average"), [
    ([SETTLEMENT - timedelta(minutes=5 + i * 5) for i in range(6)],
     [400, 500, 600, 700, 550, 600], 558.33),
    ([SETTLEMENT], [0], 0),
    ([SETTLEMENT - timedelta(minutes=25 + i * 5) for i in range(4)],
     [100, 200, 300, 400], 200)
])
def test_calc_avg_demand_last_settlement(times, demand_values, average):

    df = pd.DataFrame({
        'startTime': times,
        'demand': demand_values
    })

    test_avg = calculate_avg_demand_last_settlement(df)

    assert round(test_avg, 2) == average


@pytest.mark.parametrize(("fuel_types", "generation_mix", "test_countries", "generation_avgs"),
                         [(['INTELEC', 'INTEW', 'INTFR'],
                           [[{'generation': 100}, {'generation': 200}],
                            [{'generation': 300}],
                            [{'generation': 400}]],
                           ['Belgium', 'France', 'Ireland'],
                           [150, 400, 300]),
                         (['INTELEC', 'INTELEC', 'INTELEC'],
                          [[{"generation": 100}], [{"generation": 101}],
                              [{"generation": 102}]],
                          ["Belgium"],
                          [101])])
def test_summarise_energy(fuel_types, generation_mix, test_countries, generation_avgs):
    df = pd.DataFrame({
        'fuelType': fuel_types,
        'data': generation_mix
    })

    result = summarise_energy_generation(df)
    assert 'country' in result
    assert 'generation' in result
    countries = list(result['country'])
    generation = list(result["generation"])
    assert countries == test_countries
    assert generation == generation_avgs
