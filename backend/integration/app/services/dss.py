import pandas as pd
import traceback
from ubm.car_parking import calculate_car_parked
from ubm.charging import charging_behaviour_sim
from ubm.enact_pop import add_enact_pop_stat_to_gdf
from ubm.mobility import get_trips_info, download_datasets
from ubm.surveys import calculate_bevs_phevs_percentage
from ubm.zoning import shapefile_path_to_geodataframe
import P_module_integration_v1 as P
import CI_module_integration_v1 as CI
import base64
from app.core.status import set_running, set_waiting
from app.core.settings import settings
from app.core.auth import authentication
from app.core.logs import Simulation_Log

import dssdm.mongo.output.result as dssdm
import requests

def create_analysis_result(New_CSs, Occupancy, Borders, Stays, RHC, CIY, ECSF, ECSFAC, ECSS, LW, TNP, CPPV, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI, Losses_KPI, ZSCR_KPI, Peak_deviation_KPI, Charging_time=None, SOC=None):
    """It stores the matrices returned by the CI and PI module inside a single MongoModel class. 

    """

    ncs = dssdm.PU(
        fast_cs = New_CSs[0],
        fast_accs = New_CSs[1],
        slow_cs = New_CSs[2])

    occupancy = dssdm.Occupancy(
        fast_cs = list(Occupancy[0]),
        fast_accs = list(Occupancy[1]),
        slow_cs = Occupancy[2])

    borders = dssdm.Borders(
        border_red = list(Borders[0]),
        border_yellow = list(Borders[1]))

    if (Charging_time is not None) and (SOC is not None):

        ct = dssdm.ChargingTime(
            fast = Charging_time[0].values.tolist(),
            medium = Charging_time[1].values.tolist(),
            slow = Charging_time[2].values.tolist())

        res = dssdm.AnalysisResult(
            new_css = ncs,
            occupancy = occupancy,
            borders = borders,
            stays = list(Stays),
            RHC = RHC,
            CIY = CIY,
            ECSF = ECSF,
            ECSFAC = ECSFAC,
            ECSS = ECSS,
            LW = LW,
            TNP = TNP,
            CPPV = CPPV,
            voltage_drop_KPI = Voltage_drop_KPI,
            power_demand_KPI = Power_demand_KPI,
            gr_KPI = GR_KPI,
            voltage_events_KPI = Voltage_events_KPI,
            power_events_KPI = Power_events_KPI,
            losses_KPI = Losses_KPI,
            zscr_KPI = ZSCR_KPI.tolist(),
            peak_deviation_KPI = Peak_deviation_KPI.tolist(),
            charging_time = ct,
            SOC = SOC.values.tolist())

    else:

        res = dssdm.AnalysisResult(
            new_css = ncs,
            occupancy = occupancy,
            borders = borders,
            stays = list(Stays),
            RHC = RHC,
            CIY = CIY,
            ECSF = ECSF,
            ECSFAC = ECSFAC,
            ECSS = ECSS,
            LW = LW,
            TNP = TNP,
            CPPV = CPPV,
            voltage_drop_KPI = Voltage_drop_KPI,
            power_demand_KPI = Power_demand_KPI,
            gr_KPI = GR_KPI,
            voltage_events_KPI = Voltage_events_KPI,
            power_events_KPI = Power_events_KPI,
            losses_KPI = Losses_KPI,
            zscr_KPI = ZSCR_KPI.tolist(),
            peak_deviation_KPI = Peak_deviation_KPI.tolist())

    return res

def create_simulation_result(start_parking_time, start_energy, end_energy, parking_total, parking_total_summed_hourly, parking_total_zones, analysis_result, final_energy_required, final_spread_energy_required):
    """It encapsulates inside a MongoModel class the matrices returned by the UBM module and the
    Analysis Results (outcomes of the CI and PI modules).

    """

    ubm = dssdm.UbmResult(
        start_parking_time = start_parking_time,
        start_energy = start_energy,
        end_energy = end_energy,
        parking_total = parking_total, #mean
        parking_total_summed_hourly = parking_total_summed_hourly,
        parking_total_zones = parking_total_zones,
        energy_required = final_energy_required,
        spread_energy_required = final_spread_energy_required
    )

    res = dssdm.SimulationResult(
        ubm_result = ubm,
        analysis_result = analysis_result if len(analysis_result)>0 else None
    )

    return res

def send_result(project_id, analysis_id, result):
    """It physically sends the results to the DSS API.

    Args:
        project_id (str): id of the project to which the analysis belongs
        analysis_id (str): id of the analysis
        result (SimulationResult): outcome of the simulation

    Returns:
        response: HTTP Response
    """

    token = authentication()
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + token
    }

    if result is None:
        response = requests.post(settings.dss_uri + "/results/{}/{}".format(project_id, analysis_id), headers=header)
    else:
        body = result.dict()
        response = requests.post(settings.dss_uri + "/results/{}/{}".format(project_id, analysis_id), headers=header, json=body)
    
    return response

def run_simulation(sim_logs: Simulation_Log, analysis, shape_file):
    """It runs the simulation and, if it ends correctly, it sends back the results to the DSS API.
    Otherwise, it will send back an empty body, as an indication about a failure during the simulation process.

    Args:
        sim_logs (Log): current simulation_log instance to store logs and post them 
        analysis (AnalysesSimulation): simulation parameters
        shape_file (str): the shapefile associated to a single project
    """
    set_running(analysis.id)
    sim_logs.update_log("Set status to running")

    try:
        sim_logs.update_log("Entering try block of run_simulation")
        res = dss(sim_logs, analysis, shape_file)

        sim_logs.update_log("Simulation ENDED")
        print(res) # just print results, without saving them in the logs_data

        sim_logs.update_log("Sending results to API")
        response = send_result(analysis.project_id, analysis.id, res)

        sim_logs.update_log(f"Sent results to api, with answer: {response}")
        # print(response.json()) # this can be used for testing

    except Exception as e:
        sim_logs.update_log("Entered expect block of run_simulation")
        sim_logs.update_log("Simulation FAILED")

        sim_logs.update_log(f"ERROR: \n {str(e)}")
        sim_logs.update_log(f"TRACEBACK: \n {traceback.format_exc()}")

        sim_logs.update_log("Sending results to API")
        response = send_result(analysis.project_id, analysis.id, None)
        sim_logs.update_log(f"Sent results to api, with answer: {response}")

        # print(response.json()) # this can be used for testing
    
    set_waiting()
    sim_logs.update_log("Set status to waiting")
    sim_logs.post_logs()

def dss(sim_logs: Simulation_Log, analysis, shape_file):
    """It executes the analysis by calling all the modules involved in the simulation process.
    Then, it assemblies the results by calling the appropriate function and it and returns them.

    Args:
        sim_logs (Log): current simulation_log instance to store logs and post them 
        analysis (AnalysesSimulation): simulation parameters
        shape_file (str): the shapefile associated to a single project

    Returns:
        result (SimulationResult): outcome of the simulation
    """

    ## UB&M Modules
    sim_logs.update_log("UBM - User Behaviour & Mobility Module")
    sim_logs.update_log("UBM - Extracting user input")
    input_data = analysis.ubmY.input.dict()
    behaviour = analysis.ubmY.config.dict()
    sim_logs.update_log("UBM - Extracting user input")
    behaviour["starting_soc_dist"] = {k.replace(",","."): v for k, v in behaviour["starting_soc_dist"].items()}
    behaviour["final_soc_dist"] = {k.replace(",","."): v for k, v in behaviour["final_soc_dist"].items()}

    ## Dataset
    sim_logs.update_log("UBM - Downloading datasets")
    download_datasets()
    sim_logs.update_log("UBM - Finished downloading datasets")

    # Loading Zoning and augmenting it with JRC's ENACT-POP data
    sim_logs.update_log("UBM - Loading Zoning and augmenting it with JRC's ENACT-POP data")
    with open("shapefile.zip", "wb") as zip:
        decode = base64.b64decode(shape_file)
        zip.write(decode)
        zip.close()
    gdf = shapefile_path_to_geodataframe("shapefile.zip")
    gdf_UL = gdf.copy()
    gdf = add_enact_pop_stat_to_gdf(gdf)
    sim_logs.update_log("UBM - Finished augmentation")

    # Get Information about Trips and Vehicles
    sim_logs.update_log("UBM - Get Information about Trips and Vehicles")
    urban_trips, in_trips, out_trips, avg_n_trips = get_trips_info(input_data)
    sim_logs.update_log(f"UBM - DATA -> urban_trips: {urban_trips}, avg_n_trips: {avg_n_trips}")
    sim_logs.update_log(f"UBM - DATA -> in_trips: {urban_trips}, out_trips: {out_trips}")
    
    # Calculate behv
    sim_logs.update_log("UBM - Exctractinh behv based on user choice") 
    gdf = calculate_bevs_phevs_percentage(gdf, input_data)
    sim_logs.update_log( f"UBM - DATA -> bevs_ratio: {gdf['bevs_ratio']}, phevs_ratio: {gdf['phevs_ratio']}") 

    # Calculate car parked
    gdf = calculate_car_parked(gdf, urban_trips, in_trips, out_trips, avg_n_trips)
    sim_logs.update_log( f"UBM - DATA -> day_parking: {gdf['day_parking']}, day_parking_incoming: {gdf['day_parking_incoming']}, day_parking_bevs: {gdf['day_parking_bevs']}, day_parking_incoming_bevs: {gdf['day_parking_incoming_bevs']}") 
    sim_logs.update_log( f"UBM - DATA -> night_parking: {gdf['night_parking']}, night_parking_outgoing: {gdf['night_parking_outgoing']}, night_parking_bevs: {gdf['night_parking_bevs']}, night_parking_outgoing_bevs: {gdf['night_parking_outgoing_bevs']}") 


    # Simulate Charging Behaviour
    sim_logs.update_log("UBM - Simulating Charging Behaviour")
    impact, parking, energy_required, spread_energy_required, _, n_cars_new, starting_soc, final_soc, parking_total, parking_same_duration, parking_total_zones  = charging_behaviour_sim(gdf, behaviour, max_epoch=analysis.max_epoch, simulation_days=analysis.simulation_days)
    sim_logs.update_log( f"UBM - Finished simulation of charging behavior")
    
    parking_total_summed_hourly= []
    parking_total_mean = []
    start_parking_time = []
    start_energy = []
    end_energy = []
    analysis_result = []
    final_energy_required = []
    final_spread_energy_required = []
    for zone_id in range(len(gdf)):
        sim_logs.update_log(f"Starting CI and P simulation for zone: {zone_id}/{len(gdf)}") 
    
        impact_matrix = impact.mean[zone_id, :]# Shape: (n_zones, 24)
        parking_short_matrix = parking.mean[0, zone_id, :]# Shape: (n_zones, 24)
        parking_medium_matrix = parking.mean[1, zone_id, :]# Shape: (n_zones, 24)
        parking_long_matrix = parking.mean[2, zone_id, :]# Shape: (n_zones, 24)
        parking_short_matrix = pd.DataFrame(parking_short_matrix).T
        parking_medium_matrix = pd.DataFrame(parking_medium_matrix).T
        parking_long_matrix = pd.DataFrame(parking_long_matrix).T
        start_parking_time_zone = pd.DataFrame(n_cars_new[zone_id].mean)#n_cars_new ---> OnlineStats() (days, n_zones, 24, 24); n_cars_new[zone_id].mean ---> matrix (24, 24)
        start_energy_zone = pd.DataFrame(starting_soc[zone_id].mean)#starting_soc ---> OnlineStats() (days, n_zones, 24, 24); starting_soc[zone_id].mean ---> matrix (24, 24)
        end_energy_zone = pd.DataFrame(final_soc[zone_id].mean)#final_soc ---> OnlineStats() (days, n_zones, 24, 24); final_soc[zone_id].mean ---> matrix (24, 24)

        parking_total_matrix = pd.DataFrame(parking_same_duration[zone_id].mean)#last matrix about parking with same duration requested from UL of a single zone (24, 24)

        parking_total_matrix_for_sum = pd.DataFrame(parking_total[zone_id].mean)  # Shape: (n_zones, 24)

        final_energy_required_1 = pd.DataFrame(energy_required[zone_id].mean)
        final_energy_required.append(final_energy_required_1.sum(axis=1).values.tolist())
        final_spread_energy_required_1 = pd.DataFrame(spread_energy_required[zone_id].mean)
        final_spread_energy_required.append(final_spread_energy_required_1.sum(axis=1).values.tolist())
        
      
        parking_total_summed_hourly.append(parking_total_matrix_for_sum.sum(axis=1).values.tolist()) #axis 1 = one element for each row (sum of the durations); shape: (n_zones, 24, 1) 
        start_parking_time.append(start_parking_time_zone.sum(axis=1).values.tolist())
        start_energy.append(start_energy_zone.values.tolist())
        end_energy.append(end_energy_zone.values.tolist())
        parking_total_mean.append(parking_total_matrix.values.tolist())

        if analysis.powerY is not None and 'FCS' in gdf_UL.columns and 'FACCS' in gdf_UL.columns and 'SCS' in gdf_UL.columns and 'Zone_type' in gdf_UL.columns and 'TNP' in gdf_UL.columns and 'ML' in gdf_UL.columns:
            ## CI module
            sim_logs.update_log("CI - Starting computation")
            input_data_ci = analysis.ciY.dict()
            Expected_EV = input_data_ci['Expected_EV'] 
            #ECSF = input_data_ci.get("ECSF", 0)
            #ECSFAC = input_data_ci.get("ECSFAC", 0)
            #ECSS = input_data_ci.get("ECSS", 0)
            ECSF = gdf_UL['FCS'][zone_id]
            ECSFAC = gdf_UL['FACCS'][zone_id]
            ECSS = gdf_UL['SCS'][zone_id]
            CIY = input_data_ci['CIY']
            ROIG = input_data_ci['ROIG']
            CI_database = input_data_ci["CI_database"]
            
            try:
                if int(CIY) == 1:
                    [New_CSs, Number_of_CS, VP_matrix_short, VP_matrix_medium, VP_matrix_long, CPPV, Charging_time, SOC] = CI.CI_module(CI_database, parking_total_matrix,  parking_short_matrix, parking_medium_matrix, parking_long_matrix, Expected_EV, ECSF, ECSFAC, ECSS, CIY, start_parking_time_zone, start_energy_zone, end_energy_zone)
                else:
                    [Number_of_CS, VP_matrix_short, VP_matrix_medium, VP_matrix_long, CPPV] = CI.CI_module(CI_database, parking_total_matrix,  parking_short_matrix,parking_medium_matrix, parking_long_matrix, Expected_EV, ECSF, ECSFAC, ECSS, CIY, start_parking_time_zone, start_energy_zone, end_energy_zone)
                sim_logs.update_log("CI - Finished computation")
            except Exception as e:
                sim_logs.update_log("Error inside CI MODULE")
                raise Exception(e)

            ## P Module
            sim_logs.update_log("P - Starting computation")
            input_data_p = analysis.powerY.dict()
            Expected_EV = input_data_p['Expected_EV']
            Solar_pp = input_data_p["Solar_PP_profile"]
            #Zone_type = input_data_p['Zone_type']
            #TRNP = input_data_p['TRNP']
            #ML = input_data_p['ML']
            Zone_type = gdf_UL['Zone_type'][zone_id]
            TRNP = gdf_UL['TNP'][zone_id]
            ML = gdf_UL['ML'][zone_id]
            #PP = input_data_p['PP']
            #PPP = input_data_p['PPP']
            #SPP = input_data_p['SPP']
            #SPPP = input_data_p['SPPP']
            TDP = input_data_p['TDP']
            AY = input_data_p['AY']
            #CIY = input_data_p['CIY']

            try:
                [Occupancy, Borders, Stays, RHC, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI, Losses_KPI, ZSCR_KPI, Peak_deviation_KPI] = P.P_module(Solar_pp, Number_of_CS, VP_matrix_short, VP_matrix_medium, VP_matrix_long, impact_matrix, Zone_type, Expected_EV, TRNP, ML, _, _, _, _, TDP, AY, CIY)
            except Exception as e:
                sim_logs.update_log("Error inside P MODULE")
                raise Exception(e)
            sim_logs.update_log("P - Finished computation")

            if (parking_total_matrix.iloc[:, 1:].sum(axis=1) < 10)[0]:
                Voltage_events_KPI = 0
                Power_events_KPI = 0
                Peak_deviation_KPI = pd.Series([0] * 24)
                Voltage_drop_KPI = 0
                Power_demand_KPI =  0
                GR_KPI = 'N/A'


            ## Outputs for p and ci
            #input_data_outputs = analysis.outputsY.dict()
            #LW = input_data_outputs['LW']
            #TNP = input_data_outputs['TNP']
            LW = 0
            TNP = TRNP

            sim_logs.update_log("Saving results for the zone")
            if int(CIY) == 1:
                result = create_analysis_result(New_CSs, Occupancy, Borders, Stays, RHC, CIY, ECSF, ECSFAC, ECSS, LW, TNP, CPPV, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI, Losses_KPI, ZSCR_KPI, Peak_deviation_KPI, Charging_time, SOC)
            else:
                Charging_time = None 
                SOC = None
                result = create_analysis_result([0, 0, 0], Occupancy, Borders, Stays, RHC, CIY, ECSF, ECSFAC, ECSS,
                    0, TNP, CPPV, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI, Losses_KPI, ZSCR_KPI, Peak_deviation_KPI, Charging_time, SOC)
            
            analysis_result.append(result)

            sim_logs.update_log("Finished saving results for the p and ci modules")

    sim_logs.update_log("Finished computations for all zones")
    sim_logs.update_log("SAVING FINAL SIMULATION RESULT")
    return create_simulation_result(start_parking_time, start_energy, end_energy, parking_total_mean,parking_total_summed_hourly, parking_total_zones, analysis_result, final_energy_required, final_spread_energy_required)