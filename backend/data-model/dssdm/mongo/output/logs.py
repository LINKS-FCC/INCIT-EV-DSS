from typing import List
from pydantic import Field
from dssdm.mongo.mongodb_utils import MongoModel, OID

class LogNotYetInDB(MongoModel):
    date: str
    project_id: str
    analysis_id: str
    logs_data: List[str]

class Log(LogNotYetInDB):
    id: OID = Field(alias="_id")