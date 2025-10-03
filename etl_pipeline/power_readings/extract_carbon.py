"""Script with the functions to extract the carbon intensity data from the NESO API."""

from requests import get


def extract_carbon_intensity_data(start_time: str, end_time: str) -> list[dict]:
    """Extracts the regional carbon intensity data from the API for a given time window."""

    url = f"https://api.carbonintensity.org.uk/regional/intensity/{start_time}/{end_time}"
    response = get(url)
    data = response.json()["data"][0]["regions"]

    return data
