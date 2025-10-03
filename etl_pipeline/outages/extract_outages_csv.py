import os
import requests
import pandas as pd
from io import StringIO

URL = "https://connecteddata.nationalgrid.co.uk/dataset/d6672e1e-c684-4cea-bb78-c7e5248b62a2/resource/292f788f-4339-455b-8cc0-153e14509d4d/download/power_outage_ext.csv"


def generate_outage_csv(save_path: str | None = None) -> pd.DataFrame:
    """
    Fetch the outage CSV and return it as a DataFrame.
    If save_path is provided, also write the CSV to that path
    (use '/tmp/...' inside AWS Lambda).
    """
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()

    df = pd.read_csv(StringIO(resp.text))

    if save_path:
        # /tmp is the only writable dir in Lambda
        try:
            df.to_csv(save_path, index=False)
            print(f"Downloaded {len(df)} rows into {save_path}")
        except OSError as e:
            # If running in Lambda without /tmp, just skip saving
            print("Skipping local save:", repr(e))

    return df
