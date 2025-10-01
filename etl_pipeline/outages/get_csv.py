import requests
import pandas as pd
from io import StringIO

url = "https://connecteddata.nationalgrid.co.uk/dataset/d6672e1e-c684-4cea-bb78-c7e5248b62a2/resource/292f788f-4339-455b-8cc0-153e14509d4d/download/power_outage_ext.csv"

# Needed to bypass security by faking who we are
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

resp = requests.get(url, headers=headers)
resp.raise_for_status()

# Load into pandas
df = pd.read_csv(StringIO(resp.text))

# Save locally
df.to_csv("power_outage_ext.csv", index=False)

print("Downloaded", len(df), "rows")
