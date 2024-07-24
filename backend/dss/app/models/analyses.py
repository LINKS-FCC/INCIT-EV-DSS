from typing import Optional, List
from datetime import datetime, timezone
from pydantic import Field, BaseModel, validator

from app.models.common.mongodb_utils import OID, MongoModel
from app.models.powerYaml import PowerYaml, PowerYamlUpdate
from app.models.ubmYaml import UbmYaml, UbmYamlUpdate
from app.models.ciYaml import CiYaml, CiYamlUpdate
from app.models.results import SimulationResult

class Outputs(MongoModel):
    LW: int
    TNP: int

class Analyses(MongoModel):
    name: str
    status: str
    ubmY: UbmYaml 
    powerY: PowerYaml
    ciY: CiYaml
    max_epoch: int
    simulation_days: int
    outputsY: Outputs
    default: bool

    @validator('status')
    def status_verify(cls, v):
        if v not in ["running", "pending", "completed", "failed"]:
            raise ValueError('status invalid')
        return v

class AnalysesInDB(Analyses):
    id: OID = Field(alias="_id")
    project_id: OID 
    last_modify: datetime = datetime.now(timezone.utc)
    results: Optional[SimulationResult]    

class AnalysesNotYetInDB(Analyses):
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

    @validator('status')
    def status_verify(cls, v):
        if v not in ["running", "pending", "completed", "failed"]:
            raise ValueError('status invalid')
        return v