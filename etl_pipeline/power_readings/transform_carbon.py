"""Script with the functions to transform the carbon intensity data from the NESO API."""

from extract_carbon import extract_carbon_intensity_data, get_utc_settlement_time
from datetime import datetime


def transform_generation_mix(region: dict) -> list[float]:
    """Transforms the generation mix data into a list of percentages for each fuel type."""

    fuel_types = region["generationmix"]

    return [f["perc"] for f in fuel_types]


def transform_carbon_intensity_data(carbon_data: list[dict]) -> list[list]:
    """
    Transform the regional carbon intensity data 
    into the format specified in the ERD, ready 
    to be uploaded to the RDS.
    """

    transformed_data = []

    for region in carbon_data:
        time = datetime.now()
        region_id = region["regionid"]
        intensity = region["intensity"]["forecast"]
        l = [time, intensity, region_id]
        generation = transform_generation_mix(region)
        l.extend(generation)
        transformed_data.append(l)

    return transformed_data


if __name__ == "__main__":
    time = get_utc_settlement_time()
    region_data = extract_carbon_intensity_data(
        time[0], time[1])

    test = transform_carbon_intensity_data(region_data)[1]
    print(test)
    for t in test:
        print(type(t))
