"""
Extract script to download the latest power outage CSV from National Grid.
"""

import requests
import pandas as pd
from io import StringIO


def generate_outage_csv() -> pd.DataFrame:
    """
    Download the latest power outage CSV from National Grid
    and save a local copy.

    Returns:
        pd.DataFrame: The outage data as a pandas DataFrame.
    """
    url = (
        "https://connecteddata.nationalgrid.co.uk/dataset/"
        "d6672e1e-c684-4cea-bb78-c7e5248b62a2/resource/"
        "292f788f-4339-455b-8cc0-153e14509d4d/download/power_outage_ext.csv"
    )

    # Needed to bypass security by faking who we are
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()  # Raise if request fails

    # Load into pandas
    df = pd.read_csv(StringIO(resp.text))

    # Save locally
    df.to_csv("power_outage_ext.csv", index=False)
    print(f"Downloaded {len(df)} rows into power_outage_ext.csv")

    return df


if __name__ == "__main__":
    generate_outage_csv()
