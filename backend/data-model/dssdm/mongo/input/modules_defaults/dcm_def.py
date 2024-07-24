from pydantic import BaseModel, Field

class RatioWeights(BaseModel):
    asc_1: float
    asc_2: float
    asc_3: float
    asc_4: float
    asc_5: float
    b_diffusion: float
    b_opercost: float
    b_price: float
    b_purchincent: float
    b_range: float
    b_utilincent: float
    mu_bev: float
    mu_noevs: float
    mu_phev: float
    average_price_U3 : float
    average_price_U4 : float
    average_range_U3 : float
    average_range_U4 : float
    average_scarp: float
    default_price_ice : float
    default_range_ice: float

class ChargingWeights(BaseModel):
    asc_1: float
    asc_2: float
    asc_3: float
    asc_4: float
    asc_5: float
    b_ancillary_services: float
    b_charging_price: float
    b_charging_time: float
    b_renewable_energy: float
    b_waiting_time: float
    mu_home: float
    mu_work: float

class DcmWeights(BaseModel):
    ratio: RatioWeights
    charging: ChargingWeights