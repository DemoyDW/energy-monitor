"""Script with the functions to transform the carbon intensity data from the NESO API."""

from datetime import datetime, timedelta


def transform_generation_mix(region: dict) -> list[float]:
    """Transforms the generation mix data into a list of percentages for each fuel type."""

    fuel_types = region["generationmix"]

    # Ordering values to account for schema's incorrect ordering
    fuel_ordering = [3, 1, 0, 4, 6, 2, 5, 8, 7]

    return [fuel_types[f]["perc"] for f in fuel_ordering]


def transform_carbon_intensity_data(carbon_data: list[dict]) -> list[list]:
    """
    Transform the regional carbon intensity data 
    into the format specified in the ERD, ready 
    to be uploaded to the RDS.
    """

    transformed_data = []

    for region in carbon_data:

        # Accounting for the fact we are triggering at 5 past the hour for pricing
        # but the settlement readings are for the time on the hour/half-hour
        settlement_time = datetime.now() - timedelta(minutes=5)

        region_id = region["regionid"]
        intensity = region["intensity"]["forecast"]
        l = [settlement_time, intensity, region_id]

        generation = transform_generation_mix(region)
        l.extend(generation)
        transformed_data.append(l)

    return transformed_data
