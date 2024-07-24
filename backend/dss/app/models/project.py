from typing import List, Optional
from datetime import datetime, timezone
from pydantic import Field

from app.models.common.mongodb_utils import OID, MongoModel, BaseModel
from app.models.user import UserInfo


class Project(MongoModel):
    name: str
    city: str
    shapefile: str

class ProjectInDB(Project):
    id: OID = Field(alias="_id")
    users: List[OID]
    last_modify: datetime = datetime.now(timezone.utc)

class ProjectInDBAggregated(Project):
    _id: OID = Field()
    users: List[UserInfo]
    last_modify: datetime = datetime.now(timezone.utc)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    users: Optional[List[OID]] = None
    shapefile: Optional[str] = None
    last_modify: datetime = datetime.now(timezone.utc)

class ProjectNotYetInDB(Project):
    users: List[OID]
    last_modify: datetime = datetime.now(timezone.utc)