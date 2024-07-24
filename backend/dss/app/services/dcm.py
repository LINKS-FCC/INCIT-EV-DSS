# from app.models.user import UserInDB
from dssdm.mongo.input.user import UserInDB
from dssdm.mongo.input.dcm import Ratio_DCM_Input, Charging_DCM_Input
from dssdm.mongo.output.dcm import Ratio_DCM_Output, Charging_DCM_Output
from dssdm.mongo.input.defaults import Defaults,  DcmDefaults
from dssdm.mongo.input.modules_defaults.dcm_def import ChargingWeights, RatioWeights, DcmWeights
import math


def dcm_get_ratio(ratio_params: Ratio_DCM_Input, current_defaults: Defaults, _: UserInDB):
    """
    Query the dcm-ratio model, to get the right ratios of bevs and phevs,
    based on the ratio_params sent.

    Parameters
    ----------
    ratio_params: Ratio_DCM_Input
        ratio parameters to be used in the dcm-ratio model
    current_defaults: Defaults
        latest defaults present in the database
    _: UserInDB
        current user reaching the endpoint

    Returns
    -------
    ratio_output: Ratio_DCM_Output
    error: bool
    message: str

    """
    try:
        ratio_weights = current_defaults.dcm.weights.ratio
        ratio_sales = DcmDefaults( weights=DcmWeights(ratio = current_defaults.dcm.weights.ratio, charging=current_defaults.dcm.weights.charging ), ratio_sales = current_defaults.dcm.ratio_sales)
        ratio_output = ratio_model( ratio_params, ratio_sales, ratio_weights)
        return {
            "output": ratio_output,
            "error": False,
            "message": "DCM returned bev and phev ratios without error"
        }
    except Exception as e:
        return {
            "output": None,
            "error": True,
            "message": str(e)
        }


def dcm_get_charging(charging_params: Charging_DCM_Input, current_defaults: Defaults, _: UserInDB):
    """
    Query the dcm-charging model, to get the right distribution for the charging
    behavior, based on the charging_params sent.

    Parameters
    ----------
    charging_params: Charging_DCM_Input
        charging parameters (values) to be used in the dcm model
    current_defaults: Defaults
        latest defaults present in the database
    current_user: UserInDB
        current user reaching the endpoint

    Returns
    -------
    charging_output: Charging_DCM_Output
    error: bool
    message: str

    """
    try:
        charging_weights = current_defaults.dcm.weights.charging
        charging_output = charging_location_model(charging_params, charging_weights)
        return {
            "output": charging_output,
            "error": False,
            "message": "DCM returned charging location distribution without error"
        }
    except Exception as e:
        return {
            "output": None,
            "error": True,
            "message": str(e)
        }
        
# CALCULATE BEV RATIO:

def calc_ratio_bev(P_BEV, ratio_sales_obj: DcmDefaults, vehicle_imm_t0, bev_vehicle_t0 , forecast_year, total_stock_vehicle, average_scarp) :
    bev_t = 0
    imm_t = 0
    stock = 0
    new_ratio = {y : r for y,r in ratio_sales_obj.ratio_sales.items() if y <= forecast_year }
    for index, (y,r) in enumerate(new_ratio.items()):
        if index == 0 :
            imm_t = vehicle_imm_t0 * (1 + (r/100))
            bev_t = bev_vehicle_t0 + ((P_BEV) * imm_t)
            stock = total_stock_vehicle + imm_t - ( total_stock_vehicle * (average_scarp / 100 ))
        else :
            imm_t = imm_t * (1+ (r/100) )
            bev_t = bev_t + ((P_BEV) * imm_t)
            stock = stock + imm_t - ( stock * (average_scarp / 100 ))
            
    return bev_t/stock

# CALCULATE BEV RATIO:

def calc_ratio_phev(P_PHEV, ratio_sales_obj: DcmDefaults, vehicle_imm_t0, phev_vehicle_t0, forecast_year, total_stock_vehicle, average_scarp ) :
    phev_t = 0
    imm_t = 0
    stock = 0
    new_ratio = {y : r for y,r in ratio_sales_obj.ratio_sales.items() if y <= forecast_year }
    for index, (y,r) in enumerate(new_ratio.items()):
        if index == 0 :
            imm_t = vehicle_imm_t0 * (1 + (r/100))
            phev_t = phev_vehicle_t0 + ((P_PHEV) * imm_t)
            stock = total_stock_vehicle + imm_t - ( total_stock_vehicle * (average_scarp / 100 ))
        else :
            imm_t = imm_t * (1+ (r/100))
            phev_t = phev_t + ((P_PHEV) * imm_t)
            stock = stock + imm_t - ( stock * (average_scarp / 100 )) 
            
    return phev_t/stock


# THE ACTUAL MODELS TO COMPUTE THE REAL VALUES:

def ratio_model(
        ratio_params: Ratio_DCM_Input,
        ratio_sales: DcmDefaults,
        ratio_weights: RatioWeights, 
        ) -> Ratio_DCM_Output:
    """
    The actual DCM-ratio model that executes the computation with the
    parameters (values) inserted by the user and the weights stored in the defaults.

    Parameters
    ----------
    ratio_params: Ratio_DCM_Input
        ratio parameters (values) to be used in the dcm model
    ratio_weights: RatioWeights
        latest ratio weights defaults present in the database

    Returns
    -------
    ratio_output: Ratio_DCM_Output
    """

    #TOTAL STOCK VEHICLE
    total_vehicle_in_city = ratio_params.total_urban_trips[0] + ratio_params.total_outgoing_trips[0]
    total_stock_vehicle = total_vehicle_in_city / ratio_params.average_number_trips[0]
    #utility functions
    U1=ratio_weights.asc_1 + ratio_weights.b_price * ratio_params.price_ice + ratio_weights.b_opercost * 0 + ratio_weights.b_purchincent * 0 + ratio_weights.b_range * ratio_params.range_ice
    U2=ratio_weights.asc_2 + ratio_weights.b_price * ratio_params.price_ice + ratio_weights.b_opercost * 0 + ratio_weights.b_purchincent * 0 + ratio_weights.b_range * ratio_params.range_ice
    U3=ratio_weights.asc_3 + ratio_weights.b_price * ratio_params.price_ice * ratio_weights.average_price_U3 + ratio_weights.b_opercost * 0 + ratio_weights.b_purchincent * 0 + ratio_weights.b_range * ratio_params.range_ice * ratio_weights.average_range_U3
    U4=ratio_weights.asc_4 + ratio_weights.b_price * ratio_params.price_ice * ratio_weights.average_price_U4 + ratio_weights.b_opercost * 0 + ratio_weights.b_purchincent * 0 + ratio_weights.b_range * ratio_params.range_ice * ratio_weights.average_range_U4
    U5=ratio_weights.asc_5 + ratio_weights.b_price * ratio_params.price_ice * ratio_params.coef_price_phev +  ratio_weights.b_opercost * ratio_params.cost_phev + ratio_weights.b_purchincent*ratio_params.purchase_incentives_phev + ratio_weights.b_utilincent*ratio_params.utilization_incentives_phev +ratio_weights.b_range * ratio_params.range_ice * ratio_params.coef_range_phev + ratio_weights.b_diffusion*ratio_params.diffusion
    U6=ratio_weights.b_price * ratio_params.price_ice * ratio_params.coef_price_bev +  ratio_weights.b_opercost * ratio_params.cost_bev + ratio_weights.b_purchincent*ratio_params.purchase_incentives_bev + ratio_weights.b_utilincent*ratio_params.utilization_incentives_bev + ratio_weights.b_range * ratio_params.range_ice * ratio_params.coef_range_bev + ratio_weights.b_diffusion*ratio_params.diffusion

    #inclusive utility functions
    '''
    1.	ICE: Internal Combustion Engine
    2.	BIOICE: Biofuel Internal combustion Engine
    3.	LPG-NG V: Liquefied Petrol Gas / Natural Gas Vehicle
    4.	HEV: Hybrid Electric Vehicle (NON plug-in)
    5.	BEV: Battery Electric Vehicle
    6.	PHEV: Plug-in Electric Vehicle'''
    
    sum_exp_NOBEV=math.exp(U1)+math.exp(U2)+math.exp(U3)+math.exp(U4)

    I_NOBEV=math.log(sum_exp_NOBEV)
    I_PHEV=math.log(math.exp(U5))
    I_BEV=math.log(math.exp(U6))

    #P(G)
    den=math.exp(I_BEV*ratio_weights.mu_bev)+math.exp(I_PHEV*ratio_weights.mu_phev)+math.exp(I_NOBEV*ratio_weights.mu_noevs) 
    PBEV= math.exp(ratio_weights.mu_bev*I_BEV)/den
    PPHEV=math.exp(ratio_weights.mu_phev*I_PHEV)/den
    PNOBEV=math.exp(ratio_weights.mu_noevs*I_NOBEV)/den


    #P(i/G)
    P_BEV_BEV=1
    P_PHEV_PHEV=1
    P_ICE_NOBEV=math.exp(U1)/sum_exp_NOBEV
    P_BIOICE_NOBEV=math.exp(U2)/sum_exp_NOBEV
    P_LPGNPG_NOBEV=math.exp(U3)/sum_exp_NOBEV
    P_HEV_NOBEV=math.exp(U4)/sum_exp_NOBEV

    #P(i)
    P_BEV=PBEV*P_BEV_BEV
    P_PHEV=PPHEV*P_PHEV_PHEV
    P_ICE=PNOBEV*P_ICE_NOBEV
    P_BIOICE=PNOBEV*P_BIOICE_NOBEV
    P_LPGNPG=PNOBEV*P_LPGNPG_NOBEV
    P_HEV=PNOBEV*P_HEV_NOBEV
    #output
    bev_ratio= P_BEV 
    phev_ratio= P_PHEV 
    
    #TODO
    #@LUCIO: add here the change, before returning the actual output.
    #NB: remember that we need the percentage of vehicles that are bevs/phevs,
    #not the number of them. The final output should be two values between 0 and 1.

    bev_ratio = calc_ratio_bev(P_BEV, ratio_sales, ratio_params.vehicle_imm_t0, ratio_params.bev_vehicle_t0, ratio_params.forecast_year, total_stock_vehicle, ratio_weights.average_scarp)
    phev_ratio = calc_ratio_phev(P_PHEV, ratio_sales, ratio_params.vehicle_imm_t0, ratio_params.phev_vehicle_t0, ratio_params.forecast_year, total_stock_vehicle, ratio_weights.average_scarp)


    

    ratio_output = Ratio_DCM_Output(bev=bev_ratio, phevs=phev_ratio)
    return ratio_output


def charging_location_model(
        charging_params: Charging_DCM_Input,
        charging_weights: ChargingWeights, 
        ) -> Charging_DCM_Output:
    """
    The actual DCM-charging model that executes the computation with the
    parameters (values) inserted by the user and the weights stored in the defaults.

    Parameters
    ----------
    charging_params: Charging_DCM_Input
        charging parameters (values) to be used in the dcm model
    charging_weights: ChargingWeights
        latest charging weights defaults present in the database

    Returns
    -------
    charging_output: Charging_DCM_Output
    """
    #utility functions
    common_part_home = charging_weights.b_charging_price * charging_params.charging_price + \
                       charging_weights.b_renewable_energy * charging_params.renewable_energy 
                          
    common_part_not_home =  charging_weights.b_waiting_time * charging_params.waiting_time + \
                            charging_weights.b_charging_time * charging_params.charging_time
                            
    common_part_private = charging_weights.b_charging_price * 2 + \
                       charging_weights.b_renewable_energy * 0.36 
                            
    U_HPUB = charging_weights.asc_3 + common_part_home + common_part_not_home
    U_HPRIV = charging_weights.asc_2 + common_part_private 
    U_WPUB =  common_part_home +  common_part_not_home
    U_WPRIV = charging_weights.asc_4 + common_part_private 
    U_EB = charging_weights.asc_1 + common_part_home + common_part_not_home + charging_weights.b_ancillary_services * 0
    #inclusive utility functions
    sum_e_H = math.exp(U_HPUB)+math.exp(U_HPRIV) #sum of the exponential of Utility relatives to Home
    sum_e_W = math.exp(U_WPUB)+math.exp(U_WPRIV)+math.exp(U_EB)#sum of the exponential of Utility relatives to Work
    I_H=math.log(sum_e_H)
    I_W=math.log(sum_e_W)
    # P(G)
    den = math.exp(charging_weights.mu_home * I_H) + math.exp(charging_weights.mu_work * I_W)
    P_H = (math.exp(charging_weights.mu_home * I_H)) / den
    P_W = (math.exp(charging_weights.mu_work * I_W)) / den
    # P(i/G)
    P_HPUB_H = math.exp(U_HPUB) / sum_e_H
    P_HPRIV_H = math.exp(U_HPRIV) / sum_e_H
    P_WPUB_W = math.exp(U_WPUB) / sum_e_W
    P_WPRIV_W = math.exp(U_WPRIV) / sum_e_W
    P_EP_W = math.exp(U_EB) / sum_e_W
    # P(i)
    P_HPUB = P_H * P_HPUB_H
    P_HPRIV = P_H * P_HPRIV_H
    P_WPUB = P_W * P_WPUB_W
    P_WPRIV = P_W * P_WPRIV_W
    P_EP = P_W * P_EP_W
    #output
    day = {
            "work_public": P_WPUB,
            "work_private": P_WPRIV,
            "other_public": P_EP,
            "other_semi_public": 0,
            "fast": 0
    }
    night= {
            "home_public": P_HPUB,
            "home_private": P_HPRIV
    }
    charging_output = Charging_DCM_Output(day_ratio=day, night_ratio=night)
    return charging_output
