import time
from typing import List, Tuple
import random

import numpy as np
from geopandas import GeoDataFrame
import pandas as pd
from numpy.random import default_rng
from numpy.random._generator import Generator

from ubm.models.bev import BEV, name_model_percentage_mapping, name_model_characteristics_mapping
from ubm.utils.online_stats import OnlineStats

def parking_matrix_calc(parkings, idx, day, starting, parking_hours):
    """
    Update Policy of Parking matrix. It modifies the proper matrix following the dictionary:
    parking_hours <3        => 0
    3 <= parking_hours < 8  => 1
    parking_hours >= 8      => 2

    Parameters
    ----------
    parkings: np.ndarray
        Parking Matrix
    idx: int
        Zone ID
    day: int
        Simulation Day
    starting: int
        Starting Hour
    parking_hours: int
        Number of hour of parking

    """
    parking_index = 0
    if parking_hours >= 8: 
        parking_index = 2
    elif parking_hours >= 3:
        parking_index = 1
    parkings[parking_index][idx][day][starting] += 1

def parking_total_calc(parking_total, zone_idx, days, starting, parking_hours, total_days):
    hour = starting
    for duration in range(parking_hours, 0, -1): #parking duration
        if hour < 24: #Don't skip to next day 
            parking_total[days][zone_idx][hour][duration-1] += 1
        elif hour >= 24 and days < total_days-1: #skip to next day
            hour = 0
            days += 1
            parking_total[days][zone_idx][hour][duration-1] += 1
        else: #over last day => end
            return 
        hour += 1

def parking_same_duration_calc(parking_same_duration, zone_idx, days, starting, parking_hours, simulation_days):
    for hour in range(starting, starting+parking_hours): #var with hour update for every loop
        if hour < 24: #all ok
            parking_same_duration[days][zone_idx][hour][parking_hours-1] += 1
        elif hour >= 24 and days < simulation_days-1: #skip to next day
            parking_same_duration[days+1][zone_idx][hour%24][parking_hours-1] += 1
        else: #over last day => end
            return 



def simulate_interaction(cars: List[BEV], n_zones: int, simulation_days: int, starting_time_night_home: dict,
                         starting_time_day_work: dict, starting_time_day_other: dict, energy_required: np.ndarray, spread_energy_required: np.ndarray, n_cars_new: np.ndarray, starting_soc: list, final_soc: list, parking_total: np.ndarray, parking_same_duration: np.ndarray, seed=None):
    """
    Simulation of the interaction of cars with the city in terms of charging behaviour.

    Parameters
    ----------
    cars: List[BEV]
        List of the cars in the city
    n_zones: int
        Number of Zones
    simulation_days: int
        Number of simulation days
    starting_time_day: dict
        Discrete Distribution of the Daytime start time of Charging
    starting_time_night: dict
        Discrete Distribution of the Nightime start time of Charging
    seed: int
        Seed for reproducibility

    Returns
    -------
    impact: np.ndarray
        Matrix with shape=(n_zones, simulation_days, 24) with information about the initial requested kWh
    parkings:: np.ndarray
        Matrix with shape=(3, n_zones, simulation_days, 24) with information about the number of car that start a
        parking and puts them in 3 bucket (x < 3h, 3h <= x < 8, x >= 8)
    """
    rng = default_rng(seed=seed)
    impact = np.zeros(shape=(n_zones, simulation_days, 24))
    power = np.zeros(shape=(n_zones, simulation_days, 24))
    n_car = np.zeros(shape=(n_zones, simulation_days, 24))
    parkings = np.zeros(shape=(3, n_zones, simulation_days, 24))
    tot_in_zones_by_day = np.zeros(shape=(simulation_days, n_zones))
    for days in range(simulation_days):
        for car_i, car in enumerate(cars):
            car.travel()
            kwh = car.charge()
            if kwh > 0:
                # Select day or night zone
                if car.charging_preference == 0:  # Night Charging
                    if car.night_zone_idx == -1:
                        continue
                    zone_idx = car.night_zone_idx
                else:  # Day Charging
                    if car.day_zone_idx == -1:
                        continue
                    zone_idx = car.day_zone_idx
                    if car.day_zone_idx == -1:
                        continue
                # Calculate behaviours
                starting = car.start_parking_time
                tot_in_zones_by_day[days][zone_idx] += 1
                impact[zone_idx][days][starting] += kwh if not car.is_phev else car.phev_actual_electrical_batt
                n_cars_new[days][zone_idx][starting][car.parking_hours-1] += 1
                starting_soc[days][zone_idx][starting][car.parking_hours-1].append(car.starting_soc)
                energy_required[days][zone_idx][starting] += kwh if not car.is_phev else car.phev_actual_electrical_batt / car.parking_hours
                
                if starting+car.parking_hours >= 24 and days < simulation_days-1:
                    final_soc[days+1][zone_idx][starting+car.parking_hours-24][car.parking_hours-1].append(car.final_soc)
                elif starting+car.parking_hours >= 24 and days == simulation_days-1:
                    pass
                else:
                    final_soc[days][zone_idx][starting+car.parking_hours][car.parking_hours-1].append(car.final_soc)
                    
                count_h = 0
                current_day = days
                while count_h < car.parking_hours:
                    current = (starting + count_h) % 24
                    if current == 0 and starting != 0:
                        current_day += 1
                        if current_day >= simulation_days:
                            break
                    n_car[zone_idx][current_day][current] += 1
                    power[zone_idx][current_day][current] += kwh if not car.is_phev else car.phev_actual_electrical_batt / car.parking_hours
                    spread_energy_required[current_day][zone_idx][current] += kwh / car.parking_hours if not car.is_phev else car.phev_actual_electrical_batt / car.parking_hours
                    count_h += 1
                parking_total_calc(parking_total, zone_idx, days, starting, car.parking_hours, simulation_days) #credo che la funzione modifichi direttamente la variabile senza doverla ritornare indietro e assegnarla
                parking_same_duration_calc(parking_same_duration, zone_idx, days, starting, car.parking_hours, simulation_days)
                parking_matrix_calc(parkings, zone_idx, days, starting, car.parking_hours)
    return impact, parkings, power, energy_required, spread_energy_required, n_car, n_cars_new, starting_soc, final_soc, parking_total, parking_same_duration, tot_in_zones_by_day


def single_iteration(n_bevs: int, n_bevs_in: int, n_bevs_out: int, behaviour: dict, zone_dist: dict, gdf: GeoDataFrame,
                     n_days: int, energy_required: np.ndarray, spread_energy_required: np.ndarray, n_cars_new: np.ndarray, starting_soc: list, final_soc: list, parking_total: np.ndarray, parking_same_duration: np.ndarray, timing=True) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float, np.ndarray]:
    """
    Execute a single iteration of Monte-Carlo, by generating the cars and starting the simualtion.

    Parameters
    ----------
    n_bevs: int
        Number of BEVs inside the city (with only internal trips)
    n_bevs_in: int
        Number of incoming BEVs
    n_bevs_out: int
        Number of outgoing BEVs
    behaviour: dict
        Set of distributions which defines the user behaviour.
    zone_dist: dict
        Set of distributions which defines the location of the user in terms of zone.
     gdf: GeoDataFrame
        It contains the data coming of the zoning augmented with JRC's ENACT-POP data and the calculated number of EVs
        for each zone.
    n_days: int
        Number of days in the iteration.
    timing: bool
        If `True` prints information about the duration, no information is printed out otherwise.

    Returns
    -------
    impact: np.ndarray
        Matrix with shape=(n_zones, simulation_days, 24) with information about the initial requested kWh
    parkings:: np.ndarray
        Matrix with shape=(3, n_zones, simulation_days, 24) with information about the number of car that start a
        parking and puts them in 3 bucket (x < 3h, 3h <= x < 8, x >= 8)

    """
    start = time.time()
    # Generate BEVs
    bevs = generate_bevs(n_bevs, behaviour, zone_dist['day'], zone_dist['night'], gdf["phevs_ratio"], gdf['bevs_ratio'])
    bevs_in = generate_bevs(n_bevs_in, behaviour, zone_dist['day'], zone_dist['night'], gdf["phevs_ratio"], gdf['bevs_ratio'], incoming=True)
    bevs_out = generate_bevs(n_bevs_out, behaviour, zone_dist['day'], zone_dist['night'], gdf["phevs_ratio"], gdf['bevs_ratio'], outgoing=True)
    bevs = bevs + bevs_in + bevs_out
    bev_end = time.time()
    
    # Simulation
    impact, parkings, powers, energy_required, spread_energy_required, n_cars, n_cars_new,  starting_soc, final_soc, parking_total, parking_same_duration, tot_in_zones_by_day = simulate_interaction(bevs, len(gdf), n_days, 
                                                            behaviour["starting_time_night_home"],
                                                            behaviour["starting_time_day_work"],
                                                            behaviour["starting_time_day_other"],
                                                            energy_required,
                                                            spread_energy_required, 
                                                            n_cars_new,
                                                            starting_soc, 
                                                            final_soc, parking_total, parking_same_duration)
    sim_end = time.time()
    return impact, parkings, powers, energy_required, spread_energy_required, n_cars, n_cars_new, starting_soc, final_soc, parking_total, parking_same_duration, bev_end - start, sim_end - bev_end, tot_in_zones_by_day


def calculateMatrices(simulation_days: int, number_zones: int, energy_required: np.ndarray, spread_energy_required: np.ndarray,  n_cars_new: np.ndarray, starting_soc: list, final_soc: list, parking_total: np.ndarray, parking_same_duration: np.ndarray, parking_past: OnlineStats = None):
    """
    For each zone, calculate the average over the days for the matrices: n_cars_new, starting_soc, final_soc. [requested by Lubiana]

    Parameters
    ----------
    simulation_days: int
        Number of days for a single step of iteration
    number_zones: int
        Number of zones in the city
    n_cars_new: np.ndarray (simulation_days x number_zones x hour_of_day x parking_duration)
        Matrix with number of vehicles for each cell.
    starting_soc: list 
        Matrix with list of initial SoC for each cell
    final_soc: list
        Matrix with list of final SoC for each cell
    parking_past: OnlineStats
        Previously generated OnlineStats about parking to continue a previous simulation.


    Returns
    -------
    n_cars_new_last: np.ndarray
        Equal to n_cars_new, but with the average over the days for each zone.
    starting_soc_new: np.ndarray
        Equal to starting_soc, but with the average over the days for each zone.
    final_soc_new: np.ndarray
        Equal to starting_soc, but with the average over the days for each zone.

    """


    starting_soc_new = []
    final_soc_new = []
    n_cars_new_last = []
    parking_total_new = []
    parking_same_duration_new = []
    energy_required_last = []
    spread_energy_required_last = []

    for _ in range(number_zones):
        temp = OnlineStats() if parking_past is None else parking_past
        temp_2 = OnlineStats() if parking_past is None else parking_past
        temp_3 = OnlineStats() if parking_past is None else parking_past
        temp_4 = OnlineStats() if parking_past is None else parking_past
        temp_5 = OnlineStats() if parking_past is None else parking_past
        temp_6 = OnlineStats() if parking_past is None else parking_past
        temp_7 = OnlineStats() if parking_past is None else parking_past
        
        n_cars_new_last.append(temp)
        starting_soc_new.append(temp_2)
        final_soc_new.append(temp_3)
        parking_total_new.append(temp_4)
        parking_same_duration_new.append(temp_5)
        energy_required_last.append(temp_6)
        spread_energy_required_last.append(temp_7)
        
    starting_soc_i_new = np.zeros(shape=(simulation_days, number_zones, 24, 24))
    final_soc_i_new = np.zeros(shape=(simulation_days, number_zones, 24, 24))
        
    for a in range(simulation_days):
        for b in range(number_zones):
            for c in range(24):
                for d in range(24):

                    if len(starting_soc[a][b][c][d]) != 0:
                        starting_soc_i_new[a][b][c][d] = sum(starting_soc[a][b][c][d])/len(starting_soc[a][b][c][d])
                    if len(final_soc[a][b][c][d]) != 0:
                        final_soc_i_new[a][b][c][d] = sum(final_soc[a][b][c][d])/len(final_soc[a][b][c][d]) 

    for d in range(simulation_days):
        for z in range(number_zones):
            n_cars_new_last[z].update(n_cars_new[d, z, :, :])
            starting_soc_new[z].update_new(starting_soc_i_new[d, z, :, :])
            final_soc_new[z].update_new(final_soc_i_new[d, z, :, :])
            parking_total_new[z].update(parking_total[d, z, :, :])
            parking_same_duration_new[z].update(parking_same_duration[d, z, :, :])
            energy_required_last[z].update(energy_required[d, z, :])
            spread_energy_required_last[z].update(spread_energy_required[d, z, :])

    return energy_required_last, spread_energy_required_last, n_cars_new_last, starting_soc_new, final_soc_new, parking_total_new, parking_same_duration_new



def charging_behaviour_sim(gdf: GeoDataFrame, behaviour: dict, max_epoch: int = 1, simulation_days: int = 7,
                           confidence: float = 0.95,
                           i_confidence_stop: float = 0.00, impact_past: OnlineStats = None,
                           parking_past: OnlineStats = None, timing: bool = True)-> Tuple[
    OnlineStats, OnlineStats, OnlineStats, OnlineStats, OnlineStats, OnlineStats, OnlineStats, OnlineStats, OnlineStats, list[int]]:
    """
    This method represent the core function of the Charging Behaviour Model. It takes as input the user behaviour thanks
    to the definition of a set of distributions, such as parking duration, starting SoC, final SoC.
    The iteration is implemented in batches


    Parameters
    ----------
    gdf: GeoDataFrame
        It contains the data coming of the zoning augmented with JRC's ENACT-POP data and the calculated number of EVs
        for each zone.
    behaviour: dict
        It contains a dictionary of a set of distributions which defines the user behaviour.
    max_epoch: int
        Maximum number of epochs
    simulation_days: int
        Number of days for a single step of iteration
    confidence: float (optional)
        Confidence value, needed to calculate the interval. Default 0.95.
    i_confidence_stop: float (optional)
        Relative value at which the simulation must stop. Default 0.05.
    impact_past: OnlineStats
        Previously generated OnlineStats about impact to continue a previous simulation.
    parking_past: OnlineStats
        Previously generated OnlineStats about parking to continue a previous simulation.

    Returns
    -------
    impact_m: OnlineStats
        Impact OnlineStats
    parking_m: OnlineStats
        Parking OnlineStats
    """
    # Calculate Number of Vehicles
    # TODO: feat: manage more days
    total_day_internal_bevs = int(np.around(gdf['day_parking_bevs'].sum() + gdf['day_parking_phevs'].sum() - gdf['day_parking_incoming_bevs'].sum() - gdf['day_parking_incoming_phevs'].sum(), 0))
    total_night_internal_bevs = int(np.around(gdf['night_parking_bevs'].sum()+ gdf['night_parking_phevs'].sum() - gdf['night_parking_outgoing_bevs'].sum() - gdf['night_parking_outgoing_phevs'].sum(), 0))
    #assert total_day_internal_bevs == total_night_internal_bevs, "Something wrong with internal cars"
    n_bevs = total_day_internal_bevs
    # BEVS
    # OK aggiuntina di tot % phev
    # poi questa aggiuntina faccio in modo che abbia il segmento phev
    # mi gioco in qualche modo la ricarica dopo, creando una flag
    # BEVS
    n_bevs_in = int(np.around(gdf['day_parking_incoming_bevs'].sum(), 0))
    n_bevs_out = int(np.around(gdf['night_parking_outgoing_bevs'].sum(), 0))
    zone_dist = {
        "day": gdf['day_parking_bevs'].squeeze() / gdf['day_parking_bevs'].sum(),
        "incoming": gdf['day_parking_incoming_bevs'].squeeze() / gdf['day_parking_incoming_bevs'].sum(),
        "night": gdf['night_parking_bevs'].squeeze() / gdf['night_parking_bevs'].sum(),
        "outgoing": gdf['night_parking_outgoing_bevs'].squeeze() / gdf['night_parking_outgoing_bevs'].sum(),
    }
    impact = OnlineStats() if impact_past is None else impact_past
    parking = OnlineStats() if parking_past is None else parking_past
    power = OnlineStats() if parking_past is None else parking_past
    n_cars = OnlineStats() if parking_past is None else parking_past
    starting_soc = [[[[[] for _ in range(24)] for __ in range(24)] for ___ in range(len(gdf))] for ____ in range(simulation_days)]
    final_soc = [[[[[] for _ in range(24)] for __ in range(24)] for ___ in range(len(gdf))] for ____ in range(simulation_days)]
    n_cars_new = np.zeros(shape=(simulation_days, len(gdf), 24, 24))
    parking_total = np.zeros(shape=(simulation_days, len(gdf), 24, 24))
    parking_same_duration = np.zeros(shape=(simulation_days, len(gdf), 24, 24))
    energy_required = np.zeros(shape=( simulation_days, len(gdf), 24))
    spread_energy_required = np.zeros(shape=( simulation_days, len(gdf), 24))
    mean_t_bev = 0
    mean_t_sim = 0
    mean_t_global = 0
    it_count = 0
    for _ in range(max_epoch):
        it_count += 1
        t = time.time()
        impact_i, parkings_i, powers_i, energy_required, spread_energy_required, n_cars_i, n_cars_new, starting_soc, final_soc, parking_total, parking_same_duration, t_bev, t_sim, tot_in_zones_by_day = single_iteration(n_bevs, n_bevs_in, n_bevs_out,
                                                                                  behaviour, zone_dist,
                                                                                  gdf, simulation_days, energy_required, spread_energy_required, n_cars_new,  starting_soc, final_soc, parking_total, parking_same_duration)
        mean_t_bev += (t_bev - mean_t_bev) / it_count
        mean_t_sim += (t_sim - mean_t_sim) / it_count
        for d in range(simulation_days):
            impact.update(impact_i[:, d, :])
            power.update(powers_i[:, d, :])
            n_cars.update(n_cars_i[:, d, :])
            parking.update(parkings_i[:, d, :] if len(parkings_i.shape) == 3 else parkings_i[:, :, d, :])
        impact_c = impact.get_mean_confidence_interval_relative(confidence)
        parking_c = parking.get_mean_confidence_interval_relative(confidence)
        power_c = power.get_mean_confidence_interval_relative(confidence)
        n_cars_c = n_cars.get_mean_confidence_interval_relative(confidence)
        if timing:
            print(f"{mean_t_bev:.2f}s, {mean_t_sim:.2f}s")
        if impact_c is not None and parking_c is not None and power_c is not None and n_cars_c is not None:
            print(
                f"{it_count}: Impact Confidence: {impact_c.mean():.2f}, Parking Confidence: {parking_c.mean():.2f}, Power Confidence: {power_c.mean():.2f}, Cars Confidence: {n_cars_c.mean():.2f})")
            # TODO: feat: This part has to be rewiewed to find a good stopping criteria
            if (impact_c.mean() + parking_c.mean() + power_c.mean() + n_cars_c.mean()) / 4 < i_confidence_stop:
                break
        t_global = time.time() - t
        mean_t_global += (t_global - mean_t_global) / it_count
        print(f"Iteration time: {mean_t_global:.2f}")
        
    energy_required_last, spread_energy_required_last, n_cars_new_last, starting_soc_new, final_soc_new, parking_total_new, parking_same_duration_new = calculateMatrices(simulation_days, len(gdf), energy_required, spread_energy_required, n_cars_new,  starting_soc, final_soc, parking_total, parking_same_duration, parking_past)

    total_cars_parked_in_zones = get_total_cars_in_zones(tot_in_zones_by_day)
    
    return impact, parking, energy_required_last, spread_energy_required_last, n_cars, n_cars_new_last, starting_soc_new, final_soc_new, parking_total_new, parking_same_duration_new, total_cars_parked_in_zones

def get_total_cars_in_zones(cars_in_days_and_zones: np.ndarray) -> list[int]:
    """
    Sum the total number of charging bevs cars in each zone, by averaging for the simulation days.

    Parameters
    ----------
    cars_in_days_and_zones: np.ndarray
        shape: (n_days, n_zones). for each simulation day, a list of zones with the number of bevs charging

    Return
    ----------
    bevs_in_zones: list[int]
        shape: (n_zones). for each zone, the total number of bevs charging
    """
    avg= (cars_in_days_and_zones.sum(axis=0) / len(cars_in_days_and_zones))
    return [int(n_cars) for n_cars in avg]

def make_soc_compatible(starting_soc: np.ndarray, final_soc: np.ndarray, rng: Generator, starting_choice, final_choice):
    """
    Makes the extraction of SoCs meaningful.

    Parameters
    ----------
    starting_soc: np.ndarray
        Extracted Starting SoC
    final_soc: np.ndarray
        Extracted Final SoC
    rng: Generator
        Numpy Random Generator
    starting_choice: dict
        Starting SoC choice distribution
    final_choice: dict
        Starting SoC choice distribution
    """
    mask = final_soc < starting_soc
    length = np.sum(mask)
    while length > 0:
        starting_soc[mask] = rng.choice(list(starting_choice.keys()), p=list(starting_choice.values()), size=length)
        final_soc[mask] = rng.choice(list(final_choice.keys()), p=list(final_choice.values()), size=length)
        mask = final_soc < starting_soc
        length = np.sum(mask)


def extract_parking_time(rng: Generator, behaviour: dict, charging_place_type: str):
    """
    Extract parking time distribution based on the charge place preference of each car.

    Parameters
    ----------
    rng: Generator
        Numpy Random Generator
    behaviour: dict
        Set of distributions which defines the user behaviour.
    charging_place_type: str
        Charge Place Preference

    Returns
    -------
    parking_time: int
        Parking Time Randomly Sampled from the selected distribution.

    """
    if "home" in charging_place_type:
        parking_dist = behaviour["home_parking_time"]
    elif "work" in charging_place_type:
        parking_dist = behaviour["work_parking_time"]
    else:
        parking_dist = behaviour["other_parking_time"]
    return rng.choice(list(parking_dist.keys()), p=list(parking_dist.values()))


def extract_start_parking_time(rng: Generator, behaviour: dict, charging_place_type: str):
    """
    Extract start parking hour distribution based on the charge place preference of each car.

    Parameters
    ----------
    rng: Generator
        Numpy Random Generator
    behaviour: dict
        Set of distributions which defines the user behaviour.
    charging_place_type: str
        Charge Place Preference

    Returns
    -------
    parking_time: int
        Parking Time Randomly Sampled from the selected distribution.

    """
    if "home" in charging_place_type:
        parking_dist = behaviour["starting_time_night_home"]
    elif "work" in charging_place_type:
        parking_dist = behaviour["starting_time_day_work"]
    else:
        parking_dist = behaviour["starting_time_day_other"]
    return rng.choice(list(parking_dist.keys()), p=list(parking_dist.values()))


def generate_bevs(n_cars, behaviour, zone_dist_day, zone_dist_night, phev_ratio: float, bevs_ratio : float, seed=None, incoming=False, outgoing=False):
    """
    Generate BEVs with their own behaviour.

    Parameters
    ----------
    n_cars: int
        Number of vehicle to generate.
    behaviour: dict
        Set of distributions which defines the user behaviour.
    zone_dist_day: dict
        Population Distribution during the day.
    zone_dist_day: dict
        Population Distribution during the night.
    seed: int
        Seed for reproducibility
    phev_ratio: float 
        The percentage of vehicles that are phevs
    incoming: bool (default False)
        True if the vehicles that you want to generate are Incoming, False otherwise.
    outgoing: bool (default False)
        True if the vehicles that you want to generate are Outgoing, False otherwise.


    Returns
    -------
    bevs: List[BEV]
        List of cars with a specific behaviour.

    """
    assert not (incoming and outgoing), "Impossible state"

    def gen_car(x):
        return BEV(soc=x[0], starting_soc=x[1], final_soc=x[2], km_travelled_per_day=x[3], parking_hours=x[4],
                   day_zone_idx=x[5], night_zone_idx=x[6], charging_place_type=x[7],
                   charging_preference=x[8], start_parking_time=x[9], 
                   avg_consumption_kwh_km=x[10], battery_size=x[11])

    rng = default_rng(seed=seed)
    starting_choice = behaviour["starting_soc_dist"]
    final_choice = behaviour["final_soc_dist"]
    km_choice = behaviour["km_travelled_dist"]
    day_ratio = behaviour["day_ratio"]
    night_ratio = behaviour["night_ratio"]
    soc = [np.around(rng.uniform(10, 100), 0) for _ in np.arange(n_cars)]
    # soc = np.array(rng.choice(list(final_choice.keys()), p=list(final_choice.values()), size=n_cars))
    starting_soc = np.array(
        rng.choice(list(starting_choice.keys()), p=list(starting_choice.values()), size=n_cars))
    final_soc = np.array(rng.choice(list(final_choice.keys()), p=list(final_choice.values()), size=n_cars))
    make_soc_compatible(starting_soc, final_soc, rng, starting_choice, final_choice)
    km_travelled_per_day = rng.choice(list(km_choice.keys()), p=list(km_choice.values()), size=n_cars)
    day_zone_idx = -1 * np.ones(shape=n_cars) if outgoing else rng.choice(list(np.arange(len(zone_dist_day))),
                                                                          p=list(zone_dist_day.apply(lambda x: x[0])),
                                                                          size=n_cars)  # TODO: just index 0
    night_zone_idx = -1 * np.ones(shape=n_cars) if incoming else rng.choice(list(np.arange(len(zone_dist_night))),
                                                                            p=list(
                                                                                zone_dist_night.apply(lambda x: x[0])),
                                                                            size=n_cars)  # TODO: just index 0
    all_ratios = {**day_ratio, **night_ratio}
    charging_place_type = rng.choice(list(all_ratios.keys()), p=list(all_ratios.values()), size=n_cars)
    charging_preference = [0 if "home" in i else 1 for i in charging_place_type]
    parking_hours = [extract_parking_time(rng, behaviour, i) for i in charging_place_type]
    starting_hours = [extract_start_parking_time(rng, behaviour, i) for i in charging_place_type]

    #ADD SPECS 
    segment_ids = list(name_model_percentage_mapping.keys())
    segment_prob = list(name_model_percentage_mapping.values())
    model_names = rng.choice(segment_ids, p=segment_prob, size=n_cars)
    bev_consumption = []
    bev_battery = []
    for model_name in model_names:
      bev_consumption.append(name_model_characteristics_mapping[model_name].avg_consumption_kwh_km)
      bev_battery.append(name_model_characteristics_mapping[model_name].battery_size)
    #ADD SPECS 

    bevs_list = list(map(gen_car,
                    zip(soc, starting_soc, final_soc, km_travelled_per_day, parking_hours, day_zone_idx, night_zone_idx,
                        charging_place_type, charging_preference, starting_hours,
                        bev_consumption, bev_battery)))

    bevs_and_phevs_list = transform_bevs_in_phevs(phevs_ratio=phev_ratio, bevs=bevs_list, bevs_ratio = bevs_ratio)

    return bevs_and_phevs_list

def transform_bevs_in_phevs(phevs_ratio, bevs: list[BEV], bevs_ratio):
    """
        This is not very pretty. Basically we spawn a total number of bev which includes
        also the number of cars that should be phevs instead. For this, after we created all the bevs,
        we transform the phev ratio to actual phevs.
    """
    #print("PHEVRATIO ", phevs_ratio)
    #print("PHEVRATIO sum", phevs_ratio.sum())

    total_cars = len(bevs)
    print("total cars ", total_cars)
    total_total_cars = total_cars if len(phevs_ratio) == 0 and len(bevs_ratio) == 0 else total_cars / (phevs_ratio[0] + bevs_ratio[0])
    print("total total cars ", total_total_cars)
    num_phevs = 0 if len(phevs_ratio) == 0 else int(phevs_ratio[0] * total_total_cars)
    print("num phevs", num_phevs )

    # Get random indices without replacement
    phev_indices = random.sample(range(total_cars), num_phevs)
    #print("phev indices", phev_indices)

    #print("BEVS: \n", len(bevs))
    for i in phev_indices:
        bevs[i].is_phev = True
        bevs[i].avg_consumption_kwh_km = name_model_characteristics_mapping["phev"].avg_consumption_kwh_km
        bevs[i].phev_actual_electrical_batt = name_model_characteristics_mapping["phev"].battery_size
        bevs[i].battery_size = bevs[i].phev_actual_electrical_batt+(bevs[i].phev_actual_electrical_batt*30/100)
    print("BEVS: \n", len(bevs))
    return bevs