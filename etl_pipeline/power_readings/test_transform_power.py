"""
Tests for transform script of power readings
"""
from datetime import datetime, timedelta, timezone
import pandas as pd
from transform_power import calculate_avg_for_last_settlement, summarize_energy_generation, combine_company_generation


def test_calc_avg_settlement():
    now = datetime.now(timezone.utc) - timedelta(minutes=5)

    times = [now - timedelta(minutes=i * 5) for i in range(6)]
    values = [400, 500, 600, 700, 550, 600]
    df = pd.DataFrame({
        'startTime': times,
        'demand': values
    })

    avg = calculate_avg_for_last_settlement(df, 'demand')

    assert round(avg, 2) == 558.33


def test_summarize_energy():
    df = pd.DataFrame({
        'fuelType': ['Interconnector1', 'Interconnector1', 'Interconnector2'],
        'data': [
            [{'generation': 100}, {'generation': 200}],
            [{'generation': 300}],
            [{'generation': 400}]
        ]
    })

    mappings = {
        'Interconnector1': 'Italy',
        'Interconnector2': 'England'
    }

    result = summarize_energy_generation(df, mappings)
    assert 'country' in result
    assert 'generation' in result
    countries = list(result['country'])
    assert countries == ['England', 'Italy']


def test_combine_countries():
    data = {
        'country': ['France (IFA)', 'France (IFA2)', 'Belgium (ElecLink)', 'Belgium (Nemo Link)', 'Denmark (Viking Link)'],
        'generation': [501.00, 992.00, 997.50, 881.00, -107.00]
    }
    df = pd.DataFrame(data)

    result = combine_company_generation(df)
    countries = list(result['country'])
    generation = list(result['generation'])
    assert countries == ['Belgium', 'Denmark', 'France']
    assert generation == [1878.5, -107.0, 1493.0]
