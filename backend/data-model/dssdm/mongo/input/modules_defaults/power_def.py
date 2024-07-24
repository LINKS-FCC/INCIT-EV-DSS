from pydantic import BaseModel, Field
from typing import List

class PowerDefaults(BaseModel):
    Expected_EV: float # Ratio of EV (deprecated, leave at 1.0)
    ROIG: int  # ROI Goal [€] (general)
    Solar_PP_profile: List[float]
    Electricity_cost_profile: List[float]
    PPP:  List[float] #P_profile_UL => list of float. if not P_module_generated_profile file => Nicolò
