from geopandas import GeoDataFrame


def calculate_bevs_phevs_percentage(gdf: GeoDataFrame, input_data: dict):
    """
    Just a placeholder folder.

    TODO: To be implemented with WP2 surveys

    Parameters
    -------
    gdf: GeoDataFrame
        GeoDataFrame to be augmented with BEVs and PHEVs parked data.
    bevs_ratio: float
        BEVs market share
    phevs_ratio: float
        PHEVs market share

    Returns
    -------
    gdf: GeoDataFrame
        GeoDataFrame augmented with BEVs and PHEVs parked data.

    References
    ----------
    [1] https://www.eea.europa.eu/data-and-maps/indicators/proportion-of-vehicle-fleet-meeting-5/assessment#:~:text=In%202019%2C%20the%20share%20of,%25)%20and%20Sweden%20(12%20%25).
    """
    gdf["bevs_ratio"] = input_data["bevs_ratio"]
    gdf["phevs_ratio"] = input_data["phevs_ratio"]
    return gdf
