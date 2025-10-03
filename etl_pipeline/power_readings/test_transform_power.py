"""
Tests for transform script of power readings
"""
from datetime import datetime, timedelta, timezone
import pandas as pd
from transform_power import calculate_avg_demand_last_settlement, summarise_energy_generation


def test_calc_avg_demand_last_settlement():
    now = datetime.now(timezone.utc) - timedelta(minutes=5)

    times = [now - timedelta(minutes=i * 5) for i in range(6)]
    values = [400, 500, 600, 700, 550, 600]
    df = pd.DataFrame({
        'startTime': times,
        'demand': values
    })

    avg = calculate_avg_demand_last_settlement(df)

    assert round(avg, 2) == 558.33


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
