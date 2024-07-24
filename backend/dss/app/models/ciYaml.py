from typing import List, Optional

from pydantic import BaseModel
from app.models.modules_obj.ciObject import CIDatabase
from app.models.common.mongodb_utils import MongoModel

class CiYaml(MongoModel):
    ## GENERAL
    Expected_EV: float  # Ratio of EV (deprecated, leave at 1.0)
    #abs_path: 'datasets' credo non sia necessario. Sarebbe il percorso in cui prende dei file di input ----> corrispondono a delle matrici che sono l'output dell'ubm
    CIY: bool  # 0-1 (false-true) to trigger the analysis of a new CI (general)
    ROIG: int  # ROI Goal [€] (general)
    CI_database: List[CIDatabase]
    ## ZONE-SPECIFIC
    ECSF: Optional[int]  # Existing Charging Stations Fast (zone-specific)
    ECSFAC: Optional[int]  # Existing Charging Stations Fast AC (zone-specific)
    ECSS: Optional[int]  # Existing Charging Stations Slow (zone-specific)

class CiYamlUpdate(BaseModel):
    ## GENERAL Optional[]
    Expected_EV: Optional[float] = None 
    CIY: Optional[bool] = None 
    ROIG: Optional[int] = None 
    CI_database: Optional[List[CIDatabase]] = None
    
    ECSF: Optional[int] = None 
    ECSFAC: Optional[int] = None 
    ECSS: Optional[int] = None 