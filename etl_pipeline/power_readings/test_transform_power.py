"""
Tests for transform script of power readings
"""
from datetime import datetime, timedelta, timezone
import pandas as pd
from transform_power import calculate_avg_demand_last_settlement, summarise_energy_generation
import pytest

SETTLEMENT = datetime.now(timezone.utc) - timedelta(minutes=5)


@pytest.mark.parametrize(("times", "values", "average"), [
    ([SETTLEMENT - timedelta(minutes=5 + i * 5) for i in range(6)],
     [400, 500, 600, 700, 550, 600], 558.33),
    ([SETTLEMENT], [0], 0),
    ([SETTLEMENT - timedelta(minutes=25 + i * 5) for i in range(4)],
     [100, 200, 300, 400], 200)
])
def test_calc_avg_demand_last_settlement(times, values, average):

    df = pd.DataFrame({
        'startTime': times,
        'demand': values
    })

    test_avg = calculate_avg_demand_last_settlement(df)

    assert round(test_avg, 2) == average


def test_summarise_energy():
    df = pd.DataFrame({
        'fuelType': ['INTELEC', 'INTEW', 'INTFR'],
        'data': [
            [{'generation': 100}, {'generation': 200}],
            [{'generation': 300}],
            [{'generation': 400}]
        ]
    })

    result = summarise_energy_generation(df)
    assert 'country' in result
    assert 'generation' in result
    countries = list(result['country'])
    generation = list(result["generation"])
    assert countries == ['Belgium', 'France', 'Ireland']
    assert generation == [150, 400, 300]
