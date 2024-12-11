import os

import numpy as np
import pandas as pd
import requests
from clint.textui import progress

from ubm.car_parking import calculate_car_parked
from ubm.charging import charging_behaviour_sim
from ubm.enact_pop import add_enact_pop_stat_to_gdf
from ubm.surveys import calculate_bevs_phevs_percentage
from ubm.utils.stuff import load_yaml
from ubm.zoning import shapefile_path_to_geodataframe


def get_trips_info(input_data: dict):
    """
    Get information about trips from the input file.

    Parameters
    ----------
    input_data: dict
        Input Data Dictionary

    Returns
    -------
    total_urban_trips: np.ndarray
        Total Number of Urban Trips
    total_incoming_trips: np.ndarray
        Total Number of Incoming Trips
    total_outgoing_trips: np.ndarray
        Total Number of Ougoing Trips
    average_number_trips: np.ndarray
        Average Number of Trips

    """
    return np.asarray(input_data['total_urban_trips']), np.asarray(input_data['total_incoming_trips']), np.array(
        np.asarray(input_data['total_outgoing_trips'])), np.asarray(input_data['average_number_trips'])


def generate_csv(impact, parking, power, n_cars, n_cars_new, starting_soc, final_soc, folder: str = "./output_sample/", name: str = "mean",
                 it: int = 1000, days: int = 7):
    """
    Generate CSV for Power and Charging Infrastructure Modules.

    Parameters
    ----------
    impact: array_like
        Impact Matrix
    parking: array_like
        Parking Matrix
    folder: str
        Output folder.
    name: str
        Common name of the files.
    it: int
        Number of Epochs/Iteration
    days: int
        Number of simulation days.

    """
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
    np.savetxt(f"{folder}impact_kwh_{name}_{it}it_{days}d.csv", impact, delimiter=',', fmt="%.2f")
    np.savetxt(f"{folder}power_kw_{name}_{it}it_{days}d.csv", power, delimiter=',', fmt="%.2f")
    np.savetxt(f"{folder}n_cars_{name}_{it}it_{days}d.csv", n_cars, delimiter=',', fmt="%.2f")
    np.savetxt(f"{folder}parking_all_{name}_{it}it_{days}d.csv", parking.sum(axis=0), delimiter=',', fmt="%.2f")
    np.savetxt(f"{folder}parking_short_{name}_{it}it_{days}d.csv", parking[0], delimiter=',', fmt="%.2f")
    np.savetxt(f"{folder}parking_medium_{name}_{it}it_{days}d.csv", parking[1], delimiter=',', fmt="%.2f")
    np.savetxt(f"{folder}parking_long_{name}_{it}it_{days}d.csv", parking[2], delimiter=',', fmt="%.2f")
    if name == "mean":
        for i in range(len(n_cars_new)):
            np.savetxt(f"{folder}n_cars_new_{name}_{it}it_{days}d_number{i}.csv", n_cars_new[i].mean, delimiter=',', fmt="%.2f")
            np.savetxt(f"{folder}starting_soc_{name}_{it}it_{days}d_number{i}.csv", starting_soc[i].mean, delimiter=',', fmt="%.2f")
            np.savetxt(f"{folder}final_soc_{name}_{it}it_{days}d_number{i}.csv", final_soc[i].mean, delimiter=',', fmt="%.2f")
    else:
        pass
        #for i in range(len(n_cars_new)):
         #   np.savetxt(f"{folder}n_cars_new_{name}_{it}it_{days}d_number{i}.csv", n_cars_new[i].get_mean_confidence_interval(), delimiter=',', fmt="%.2f")
          #  np.savetxt(f"{folder}starting_soc_{name}_{it}it_{days}d_number{i}.csv", starting_soc[i].get_mean_confidence_interval(), delimiter=',', fmt="%.2f")
           # np.savetxt(f"{folder}final_soc_{name}_{it}it_{days}d_number{i}.csv", final_soc[i].get_mean_confidence_interval(), delimiter=',', fmt="%.2f")    

def download_datasets(folder: str = "./datasets/"):
    """
    Download dataset from the repository on the GitLab space.

    Parameters
    ----------
    folder: str
        Destination datasets folder
    """
    print("Download ENACT-POP datasets...")
    token = "-LZyrVdYxDzQxfro-umu"
    api = "https://gitlab.linksfoundation.com/api/v4/projects/150/repository/files/"
    night_raster_link = "ubm%2Fnight_0311_avg_t.tif/raw"
    day_raster_link = "ubm%2Fday_0311_avg_t.tif/raw"
    corine_raster_link = "ubm%2Fcorine.4326.tif/raw"
    # TODO: These 3 if-else can be generalized in a single one
    if not os.path.exists(folder + "night_0311_avg_t.tif"):
        print("Night Dataset Download...")
        r = requests.get(api + night_raster_link, headers={'PRIVATE-TOKEN': token}, stream=True)
        with open(folder + "night_0311_avg_t.tif", 'wb') as f:
            total_length = int(r.headers.get('X-Gitlab-Size'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1,
                                      hide=False, label="night_0311_avg_t.tif"):
                if chunk:
                    f.write(chunk)
                    f.flush()
    else:
        print("Night Dataset already downloaded!")
    if not os.path.exists(folder + "day_0311_avg_t.tif"):
        print("Day Dataset Download...")
        r = requests.get(api + day_raster_link, headers={'PRIVATE-TOKEN': token}, stream=True)
        with open(folder + "day_0311_avg_t.tif", 'wb') as f:
            total_length = int(r.headers.get('X-Gitlab-Size'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1,
                                      hide=False, label="day_0311_avg_t.tif"):
                if chunk:
                    f.write(chunk)
                    f.flush()
    else:
        print("Day Dataset already downloaded!")
    if not os.path.exists(folder + "corine.4326.tif"):
        print("Corine Dataset Download...")
        r = requests.get(api + corine_raster_link, headers={'PRIVATE-TOKEN': token}, stream=True)
        with open(folder + "corine.4326.tif", 'wb') as f:
            total_length = int(r.headers.get('X-Gitlab-Size'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1,
                                      hide=False, label="corine.4326.tif"):
                if chunk:
                    f.write(chunk)
                    f.flush()
    else:
        print("Corine Dataset already downloaded!")


def mobility_main(input: str, config, output_folder, max_epoch=10, simulation_days=7, impact_past=None,
                  parking_past=None):
    """
    Default Main Flow

    Parameters
    ----------
    input: str
        Filepath to the YAML with inputs.
    config: str
        Filepath to the YAML with configs.
    output_folder: str
        Folder path to use for the outputs.
    max_epoch: int
        Max number of iterations.
    simulation_days: int
        Simulation Days for each iteration.
    impact_past: OnlineStats
        Previously generated OnlineStats about impact to continue a previous simulation.
    parking_past: OnlineStats
        Previously generated OnlineStats about parking to continue a previous simulation.

    Returns
    -------
    impact: OnlineStats
        Impact OnlineStats
    parking: OnlineStats
        Parking OnlineStats
    """
    download_datasets()
    # Load Input Data and Behaviour
    input_data = load_yaml(input)
    behaviour = load_yaml(config)

    # Loading Zoning and augmenting it with JRC's ENACT-POP data
    filename = input_data['zoning_shp_path']
    gdf = shapefile_path_to_geodataframe(filename)
    gdf = add_enact_pop_stat_to_gdf(gdf)

    # Get Information about Trips and Vehicles
    urban_trips, in_trips, out_trips, avg_n_trips = get_trips_info(input_data)
    gdf = calculate_bevs_phevs_percentage(gdf, input_data)
    gdf = calculate_car_parked(gdf, urban_trips, in_trips, out_trips, avg_n_trips)

    # Simulate Charging Behaviour
    impact, parking, power, n_cars, n_cars_new_last, starting_soc_new, final_soc_new, parking_total_new, parking_same_duration_new, total_cars_parked_in_zones = charging_behaviour_sim(gdf, behaviour, max_epoch=max_epoch, simulation_days=simulation_days, impact_past=impact_past, parking_past=parking_past)
    print("impact: \n", len(impact.mean))
    print("parking: \n", len(parking.mean), len(parking.mean[0]))
    print("power: \n", len(power.mean))
    print("n_cars: \n", len(n_cars.mean))
    print("n_cars_new_last: \n", len(n_cars_new_last))
    print("starting_soc_new: \n", len(starting_soc_new))
    print("final_soc_new: \n", len(final_soc_new))
    print("parking_total_new: \n", len(parking_total_new))
    print("parking_same_duration_new: \n", len(parking_same_duration_new))
    print("total_cars_parked_in_zones: \n", len(total_cars_parked_in_zones))
    # generate_csv(impact.mean, parking.mean, power.mean, n_cars.mean, n_cars_new, starting_soc, final_soc, folder=output_folder, name='mean', it=max_epoch,
    #              days=simulation_days)
    #generate_csv(impact.get_mean_confidence_interval(), parking.get_mean_confidence_interval(),
    #             power.get_mean_confidence_interval(), n_cars.get_mean_confidence_interval(), n_cars_new, starting_soc, final_soc, folder=output_folder,
    #             name='confidence', it=max_epoch, days=simulation_days)
    return 
