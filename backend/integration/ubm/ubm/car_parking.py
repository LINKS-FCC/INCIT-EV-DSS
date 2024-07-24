import numpy as np
from geopandas import GeoDataFrame


def calculate_car_parked(gdf: GeoDataFrame, total_urban_trips: np.ndarray, total_incoming_trips: np.ndarray,
                         total_outgoing_trips: np.ndarray, average_number_of_trips: np.ndarray):
    """
    Calculate the number of car parked in the city of study during the day and during the night for each zone.

    Parameters
    ----------
    gdf: GeoDataFrame
        GeoDataFrame to be augmented with car parked data.
    total_urban_trips: np.ndarray
        Total number of internal city trips (O and D in the city)
    total_incoming_trips: np.ndarray
        Total number of incoming trips. These are the trips of people who lives outside the city during the night and
        are in the city during the day.
    total_outgoing_trips: np.ndarray
        Total number of outgoing trips. These are the trips of people who lives inside the city during the night and
        are outside the city during the day.
    average_number_of_trips: np.ndarray
        Average number of trips per vehicle of the city under investigation.

    Returns
    -------
    gdf: GeoDataFrame
        GeoDataFrame augmented with car parked data.
    """
    assert total_urban_trips.shape == total_incoming_trips.shape == total_outgoing_trips.shape, "Trips arrays are not equal in shape"
    # Assuming that outgoing/incoming will have one trip for each vehicle.
    night_parking = (total_urban_trips / average_number_of_trips + total_outgoing_trips)
    day_parking = (total_urban_trips / average_number_of_trips + total_incoming_trips)
    night_parking_series = []
    outgoing_night_parking_series = []
    night_parking_series_plot = []
    day_parking_series = []
    incoming_day_parking_series = []
    day_parking_series_plot = []
    for ratio in gdf['enact_pop_night_ratio']:
        night_parking_series.append(night_parking * ratio)
        outgoing_night_parking_series.append(total_outgoing_trips * ratio)
        night_parking_series_plot.append(night_parking[0] * ratio)
    for ratio in gdf['enact_pop_day_ratio']:
        day_parking_series.append(day_parking * ratio)
        incoming_day_parking_series.append(total_incoming_trips * ratio)
        day_parking_series_plot.append(day_parking[0] * ratio)
    gdf['day_parking'] = day_parking_series
    gdf['day_parking_incoming'] = incoming_day_parking_series
    gdf['day_parking_bevs'] = gdf['day_parking'] * gdf['bevs_ratio']
    gdf['day_parking_incoming_bevs'] = gdf['day_parking_incoming'] * gdf['bevs_ratio']
    gdf['day_parking_phevs'] = gdf['day_parking'] * gdf['phevs_ratio']
    gdf['day_parking_incoming_phevs'] = gdf['day_parking_incoming'] * gdf['phevs_ratio']
    gdf['night_parking'] = night_parking_series
    gdf['night_parking_outgoing'] = outgoing_night_parking_series
    gdf['night_parking_bevs'] = gdf['night_parking'] * gdf['bevs_ratio']
    gdf['night_parking_outgoing_bevs'] = gdf['night_parking_outgoing'] * gdf['bevs_ratio']
    gdf['night_parking_phevs'] = gdf['night_parking'] * gdf['phevs_ratio']
    gdf['night_parking_outgoing_phevs'] = gdf['night_parking_outgoing'] * gdf['phevs_ratio']
    # Just for plotting
    gdf['day_parking_plot'] = day_parking_series_plot
    gdf['day_parking_plot_bevs'] = gdf['day_parking_plot'] * gdf['bevs_ratio']
    gdf['day_parking_plot_phevs'] = gdf['day_parking_plot'] * gdf['phevs_ratio']
    gdf['night_parking_plot'] = night_parking_series_plot
    gdf['night_parking_plot_bevs'] = gdf['night_parking_plot'] * gdf['bevs_ratio']
    gdf['night_parking_plot_phevs'] = gdf['night_parking_plot'] * gdf['phevs_ratio']
    return gdf
