from typing import List, Optional

from pydantic import BaseModel

from app.models.common.mongodb_utils import MongoModel

class PowerYaml(MongoModel):
    #abs_path: str #credo non sia necessario dal momento che gli passiamo direttamente i campi
    Expected_EV: float # Ratio of EV (deprecated, leave at 1.0)
    ROIG: int  # ROI Goal [€] (general)
    CIY: bool  # 0-1 (false-true) to trigger the analysis of a new CI (general)
    AY: int  # Year to be examined to scale values (general)
    TDP: str  # ['Weekdays', 'Weekends'] (general)
    Solar_PP_profile: List[float]
    Electricity_cost_profile: List[float]
    ## ZONE-SPECIFIC
    Zone_type: str  # ['Commercial', 'Residential', 'Industrial (?)'] (zone-specific)
    PP: bool  # 0-1 (false-true) Power Demand Profile activation specified by user (zone-specific)
    PPP:  Optional[List[float]] #P_profile_UL => list of float. if not P_module_generated_profile file => Nicolò
    TRNP: int  # Transformer Nominal Power [kW] (zone-specific)
    ML: float  # Maximal Loading [%] (zone-specific)
    SPP: int  # Number of existing Solar Power Plants (zone-specific)
    SPPP: float  # Solar Power Plants Nominal Power [kW] (zone-specific)

class PowerYamlUpdate(BaseModel):
    Expected_EV: Optional[float]= None
    ROIG: Optional[int]= None 
    CIY: Optional[bool]= None  
    AY: Optional[int] = None 
    TDP: Optional[str] = None 
    Solar_PP_profile: Optional[List[float]] = None
    Electricity_cost_profile: Optional[List[float]] = None

    Zone_type: Optional[str] = None 
    PP: Optional[bool] = None 
    PPP:  Optional[List[float]]= None 
    TRNP: Optional[int] = None 
    ML: Optional[float] = None 
    SPP: Optional[int] = None 
    SPPP: Optional[float] = None 