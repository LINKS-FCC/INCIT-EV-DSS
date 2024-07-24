from typing import List, Optional
from pydantic import BaseModel

from dssdm.mongo.mongodb_utils import MongoModel
from dssdm.mongo.input.defaults import PowerDefaults

class PowerYamlFrontend(MongoModel):
    #abs_path: str #credo non sia necessario dal momento che gli passiamo direttamente i campi
    CIY: bool  # 0-1 (false-true) to trigger the analysis of a new CI (general)
    AY: int  # Year to be examined to scale values (general)
    TDP: str  # ['Weekdays', 'Weekends'] (general)
    ## ZONE-SPECIFIC
    #Zone_type: str  # ['Commercial', 'Residential', 'Industrial (?)'] (zone-specific)
    #PP: bool  # 0-1 (false-true) Power Demand Profile activation specified by user (zone-specific)
    #PPP:  Optional[List[float]] #P_profile_UL => list of float. #USER OPTIONAL VALUE
    #TRNP: int  # Transformer Nominal Power [kW] (zone-specific)
    #ML: float  # Maximal Loading [%] (zone-specific)
    #SPP: int  # Number of existing Solar Power Plants (zone-specific)
    #SPPP: float  # Solar Power Plants Nominal Power [kW] (zone-specific)

class PowerYaml(PowerYamlFrontend, PowerDefaults):
    pass

class PowerYamlUpdate(BaseModel):
    CIY: Optional[bool]= None  
    AY: Optional[int] = None 
    TDP: Optional[str] = None 

    #Zone_type: Optional[str] = None 
    #PP: Optional[bool] = None 
    #PPP:  Optional[List[float]]= None 
    #TRNP: Optional[int] = None 
    #ML: Optional[float] = None 
    #SPP: Optional[int] = None 
    #SPPP: Optional[float] = None 