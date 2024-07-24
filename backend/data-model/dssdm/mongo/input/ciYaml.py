from typing import List, Optional
from pydantic import BaseModel

from dssdm.mongo.input.ciObject import CIDatabase
from dssdm.mongo.mongodb_utils import MongoModel
from dssdm.mongo.input.defaults import CiDefaults

class CiYamlFrontend(MongoModel):
    ## GENERAL
    #abs_path: 'datasets' credo non sia necessario. Sarebbe il percorso in cui prende dei file di input ----> corrispondono a delle matrici che sono l'output dell'ubm
    CIY: bool  # 0-1 (false-true) to trigger the analysis of a new CI (general)
    CI_database: List[CIDatabase]
    ## ZONE-SPECIFIC
    #ECSF: Optional[int]  # Existing Charging Stations Fast (zone-specific)
    #ECSFAC: Optional[int]  # Existing Charging Stations Fast AC (zone-specific)
    #ECSS: Optional[int]  # Existing Charging Stations Slow (zone-specific)

class CiYaml(CiYamlFrontend, CiDefaults):
    pass

class CiYamlUpdate(BaseModel):
    ## GENERAL Optional[]
    #abs_path: 'datasets' credo non sia necessario. Sarebbe il percorso in cui prende dei file di input ----> corrispondono a delle matrici che sono l'output dell'ubm
    CIY: Optional[bool] = None # 0-1 (false-true) to trigger the analysis of a new CI (general)
    CI_database: Optional[List[CIDatabase]] = None
    ## ZONE-SPECIFIC
    #ECSF: Optional[int] = None # Existing Charging Stations Fast (zone-specific)
    #ECSFAC: Optional[int] = None # Existing Charging Stations Fast AC (zone-specific)
    #ECSS: Optional[int] = None # Existing Charging Stations Slow (zone-specific)