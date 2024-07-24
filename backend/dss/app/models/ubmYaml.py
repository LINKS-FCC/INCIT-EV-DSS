from typing import Optional, List

from pydantic import BaseModel, validator

from app.models.common.mongodb_utils import MongoModel
from app.models.modules_obj.ubmObject import NightRatio, DayRatio

class UbmInputUpdate(MongoModel):
    total_urban_trips: Optional[List[int]] = None
    total_incoming_trips: Optional[List[int]]= None
    total_outgoing_trips: Optional[List[int]]= None
    average_number_trips: Optional[List[int]]= None
    bevs_ratio: Optional[float]= None
    phevs_ratio: Optional[float]= None

class UbmConfigUpdate(MongoModel):
    night_ratio: Optional[NightRatio]= None
    day_ratio: Optional[DayRatio]= None
    home_parking_time: Optional[dict]= None
    work_parking_time: Optional[dict]= None
    other_parking_time: Optional[dict]= None
    starting_soc_dist: Optional[dict]= None
    final_soc_dist: Optional[dict]= None
    km_travelled_dist: Optional[dict]= None
    starting_time_night: Optional[dict]= None
    starting_time_day: Optional[dict]= None
    starting_time_night_home: Optional[dict]= None
    starting_time_day_work: Optional[dict]= None
    starting_time_day_other: Optional[dict]= None

class UbmInput(MongoModel):
    total_urban_trips: List[int]
    total_incoming_trips: List[int]
    total_outgoing_trips: List[int]
    average_number_trips: List[int]
    bevs_ratio: float
    phevs_ratio: float

class UbmConfig(MongoModel):
    night_ratio: NightRatio
    day_ratio: DayRatio
    home_parking_time: dict
    work_parking_time: dict
    other_parking_time: dict
    starting_soc_dist: dict
    final_soc_dist: dict
    km_travelled_dist: dict
    starting_time_night: dict
    starting_time_day: dict
    starting_time_night_home: dict
    starting_time_day_work: dict
    starting_time_day_other: dict

    @validator('starting_soc_dist')
    def starting_dot(cls, v):
        assert (any(["." in k for k in v.keys()]) == False), "Starting soc keys {} contains .".format([k for k in v.keys() if "." in k])
        return v

    @validator('final_soc_dist')
    def final_dot(cls, v):
        assert (any(["." in k for k in v.keys()]) == False), "Final soc keys {} contains .".format([k for k in v.keys() if "." in k])
        return v

class UbmYaml(MongoModel):
    input: UbmInput
    config: UbmConfig

class UbmYamlUpdate(BaseModel):
    input: Optional[UbmInputUpdate]
    config: Optional[UbmConfigUpdate]