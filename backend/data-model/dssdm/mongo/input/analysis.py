import string
from typing import Optional
from datetime import datetime, timezone
from pydantic import Field, BaseModel

from dssdm.mongo.mongodb_utils import OID, MongoModel
from dssdm.mongo.input.powerYaml import PowerYamlFrontend, PowerYamlUpdate, PowerYaml
from dssdm.mongo.input.ubmYaml import UbmYaml, UbmYamlUpdate, UbmYamlFrontend
from dssdm.mongo.input.ciYaml import CiYamlFrontend, CiYamlUpdate, CiYaml
from dssdm.mongo.output.result import SimulationResult

#class Outputs(MongoModel):
#    LW: int
#    TNP: int

class Analyses(MongoModel):
    name: str
    status: str
    max_epoch: int
    simulation_days: int
#    outputsY: Outputs
    default: bool

class AnalysesFrontedUser(Analyses):
    powerY: Optional[PowerYamlFrontend]
    ciY: Optional[CiYamlFrontend]
    ubmY: UbmYamlFrontend

class AnalysesWithDefaults(AnalysesFrontedUser):
    powerY: Optional[PowerYaml]
    ciY: Optional[CiYaml]
    ubmY: UbmYaml

class AnalysesInDB(AnalysesWithDefaults):
    id: OID = Field(alias="_id")
    project_id: OID 
    last_modify: datetime = datetime.now(timezone.utc)
    
class AnalysesResults(AnalysesInDB):
    results: Optional[SimulationResult]

class AnalysesSimulation(AnalysesWithDefaults):
    id: str
    project_id: str
    
class AnalysesNotYetInDB(AnalysesWithDefaults):
    project_id: OID
    last_modify: datetime = datetime.now(timezone.utc)

class AnalysesUpdate(BaseModel):  
    name: Optional[str] = None
    status: Optional[str] = None
    ubmY: Optional[UbmYamlUpdate] = None
    powerY: Optional[PowerYamlUpdate] = None
    ciY: Optional[CiYamlUpdate] = None
    default: Optional[bool] = None
    last_modify: datetime = datetime.now(timezone.utc)