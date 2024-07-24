from typing import Optional, List
from pydantic import BaseModel, validator

from dssdm.mongo.mongodb_utils import MongoModel
from dssdm.mongo.input.ubmObject import NightRatio, DayRatio

class UbmInputUpdate(MongoModel):
    total_urban_trips: Optional[int] = None
    total_incoming_trips: Optional[int]= None
    total_outgoing_trips: Optional[int]= None
    average_number_trips: Optional[int]= None
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

# FINAL INPUTS FOR THE ANALYSIS, WITH ALL VALUES FROM USER + DEFAULT ONES
class UbmInput(MongoModel):
    total_urban_trips: List[int] #no default
    total_incoming_trips: List[int] #no default
    total_outgoing_trips: List[int] #no default
    average_number_trips: List[int] #no default
    bevs_ratio: float #default suggestion (not hidden) + with dcm option 
    phevs_ratio: float #default suggestion (not hidden) + with dcm option

class UbmConfig(MongoModel):
    night_ratio: NightRatio #default optional + dcm option
    day_ratio: DayRatio #default optional + dcm option 
    km_travelled_dist: dict #default suggestion
    starting_time_night: dict #default hidden
    starting_time_day: dict #default hidden
    starting_time_night_home: dict #default hidden
    starting_time_day_work: dict #default hidden
    starting_time_day_other: dict #default hidden
    home_parking_time: dict #default hidden
    work_parking_time: dict #default hidden
    other_parking_time: dict #default hidden
    starting_soc_dist: dict #default hidden
    final_soc_dist: dict #default hidden

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
    starting_time_day_work: Optional[dict]= None
    starting_time_day_other: Optional[dict]= None

# FRONTEND WITHOUT DEFAULTS
class UbmConfigFrontend(MongoModel):
    night_ratio: NightRatio #default suggestion + dcm
    day_ratio: DayRatio #default suggestion + dcm
    km_travelled_dist: dict #default suggestion
    # + hidden defaults that get merged during the creation of the analysis

class UbmYamlFrontend(MongoModel):
    input: UbmInput #no hidden defaults, all fields from user
    config: UbmConfigFrontend