"""
Script for extracting the csv from the national grid website using the link they had
which updates when there are new outages, had to use an agent to bypass the security of
the website as it was stopping access to the csv.
"""

from io import StringIO
import requests
import pandas as pd


def generate_outage_csv():
    """ 
    Takes the url for the csv and download the csv using pandas and requests, also has to create
    an agent to bypass the security. 
    """

    url = "https://connecteddata.nationalgrid.co.uk/dataset/d6672e1e-c684-4cea-bb78-c7e5248b62a2/resource/292f788f-4339-455b-8cc0-153e14509d4d/download/power_outage_ext.csv"

    # Needed to bypass security by faking who we are
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    # Load into pandas
    df = pd.read_csv(StringIO(resp.text))

    # Save locally
    df.to_csv("power_outage_ext.csv", index=False)
    print("Downloaded", len(df), "rows")
