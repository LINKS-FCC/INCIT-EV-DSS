from pydantic import BaseModel, validator
from typing import List

class Ratio_DCM_Input(BaseModel):
    # necessary for dcm
    diffusion: float #0, 2.5, 5, 7.5, 10 
    cost_phev: float #-2.5, 0, 2.5
    cost_bev: float #-2.5, 0, 2.5
    coef_price_phev: float #0.5, 0.8, 1, 1.2, 1.5, 2, 3
    coef_price_bev: float #0.5, 0.8, 1, 1.2, 1.5, 2, 3
    coef_range_phev: float #0.5, 0.8, 1, 1.2, 1.5, 2
    coef_range_bev: float #0.5, 0.8, 1, 1.2, 1.5, 2
    purchase_incentives_phev: float #-1, 0, 1, 2, 3
    purchase_incentives_bev: float #-1, 0, 1, 2, 3 
    utilization_incentives_phev: float #0, 1, 2
    utilization_incentives_bev: float #0, 1, 2
    price_ice : float #1 <= x <= 10
    range_ice : float # 1<= x <= 10
    # these are to find the right percentages
    vehicle_imm_t0: float 
    bev_vehicle_t0: float
    phev_vehicle_t0: float
    forecast_year: str #2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030 , 2031, 2032, 2033, 2034, 2035
    #Scrap Model
    total_urban_trips: List[int]
    total_outgoing_trips: List[int]
    average_number_trips: List[int]
    
    
    @validator("diffusion")
    def diff(cls, v):
        if v not in [0, 2.5, 5, 7.5, 10]:
            raise ValueError("diffusion value must be 0, 2.5, 5, 7.5 or 10")
        return v

    @validator("cost_phev")
    def cost_validator_phev(cls, v):
        if v not in [-2.5, 0, 2.5]:
            raise ValueError("cost value must be -2.5, 0 or 2.5")
        return v
    
    @validator("cost_bev")
    def cost_validator_bev(cls, v):
        if v not in [-2.5, 0, 2.5]:
            raise ValueError("cost value must be -2.5, 0 or 2.5")
        return v
    
    @validator("coef_price_phev")
    def coefficient_price_phev(cls, v):
        if v not in [0.5, 0.8, 1, 1.2, 1.5, 2, 3]:
            raise ValueError("purchase_incentives value must be 0.5, 1, 2, 3")
        return v
    
    @validator("coef_price_bev")
    def coefficient_price_bev(cls, v):
        if v not in [0.5, 0.8, 1, 1.2, 1.5, 2, 3]:
            raise ValueError("purchase_incentives value must be 0.5, 1, 2, 3")
        return v
    
    @validator("coef_range_phev")
    def coefficient_range_phev(cls, v):
        if v not in [0.5, 0.8, 1, 1.2, 1.5, 2]:
            raise ValueError("purchase_incentives value must be 0.5, 1, 2, 3")
        return v
    
    @validator("coef_range_bev")
    def coefficient_range_bev(cls, v):
        if v not in [0.5, 0.8, 1, 1.2, 1.5, 2]:
            raise ValueError("purchase_incentives value must be 0.5, 1, 2, 3")
        return v

    @validator("purchase_incentives_phev")
    def purchase_phev(cls, v):
        if v not in [-1, 0, 1, 2, 3]:
            raise ValueError("purchase_incentives value must be -1, 0, 1, 2 or 3")
        return v
    
    @validator("purchase_incentives_bev")
    def purchase_bev(cls, v):
        if v not in [-1, 0, 1, 2, 3]:
            raise ValueError("purchase_incentives value must be -1, 0, 1, 2 or 3")
        return v

    @validator("utilization_incentives_phev")
    def utilization_phev(cls, v):
        if v not in [0, 1, 2]:
            raise ValueError("utilization_incentives value must be 0, 1 or 2")
        return v
    
    @validator("utilization_incentives_bev")
    def utilization_bev(cls, v):
        if v not in [0, 1, 2]:
            raise ValueError("utilization_incentives value must be 0, 1 or 2")
        return v
    
    @validator("price_ice")
    def price_ice_f(cls, v):
        if not (1 <= v <= 10): 
            raise ValueError("price ice value must be between 1 and 10")
        return v
    
    @validator("range_ice")
    def range_ice_f(cls, v):
        if not (1 <= v <= 10): 
            raise ValueError("range ice value must be between 1 and 1o")
        return v
    
    @validator("forecast_year")
    def forecast_year_f(cls, v):
        if v not in ["2023","2024", "2025", "2026", "2027", "2028", "2029", "2030", "2031", "2032", "2033", "2034", "2035"]: 
            raise ValueError("year value must be : 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035")
        return v
    
    @validator("total_urban_trips")
    def total_urban_trips_f(cls, v):
        if (len(v) == 0):
            raise ValueError("There must be a value for: daily urban trips by car")
        return v
    
    @validator("total_outgoing_trips")
    def total_outgoing_trips_f(cls, v):
        if (len(v) == 0):
            raise ValueError("There must be a value for: daily outgoing trips by car")
        return v
    
    @validator("average_number_trips")
    def average_number_trips_f(cls, v):
        if (len(v) == 0 or v[0] == 0):
            raise ValueError("There must be a value for: daily average number of trips")
        return v

class Charging_DCM_Input(BaseModel):
    charging_price: float #0.5, 1, 2, 6
    renewable_energy: float # 0 <= x <= 1
    waiting_time: float #1, 3, 5
    charging_time: float  #0.5, 1, 2, 4 


    @validator("charging_price")
    def charging(cls, v):
        if v not in [0.5, 1, 2, 6]:
            raise ValueError("charging price value must be 0.5, 1, 2 or 6")
        return v

    @validator("renewable_energy")
    def renewable(cls, v):
        if not (0 <= v <= 1): 
            raise ValueError("renewable energy value must be between 0 and 1")
        return v

    @validator("waiting_time")
    def waiting(cls, v):
        if v not in [1, 3, 5]:
            raise ValueError("waiting time value must be 1, 3 or 5")
        return v
    
    @validator("charging_time")
    def charging_tim(cls, v):
        if v not in [0.5, 1, 2, 4 ]:
            raise ValueError("Charging Time value must be 0.5, 1, 2, 4")
        return v