"""Script with the functions to transform the carbon intensity data from the NESO API."""

from datetime import datetime, timedelta


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
        # We are taking readings every half-hour, starting at 5 minutes past the hour
        # to account for the price reading. However, the readings we are taking are for
        # the half-hour settlement period from half-past to the hour, therefore we want
        # the reading time to reflect this by being on the hour/half-hour, hence, we subtract 5 minutes.
        time = datetime.now() - timedelta(minutes=5)
        region_id = region["regionid"]
        intensity = region["intensity"]["forecast"]
        l = [time, intensity, region_id]
        generation = transform_generation_mix(region)
        l.extend(generation)
        transformed_data.append(l)

    return transformed_data
