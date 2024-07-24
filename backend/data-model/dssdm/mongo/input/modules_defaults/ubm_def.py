from pydantic import BaseModel, Field
from dssdm.mongo.input.ubmObject import NightRatio, DayRatio

# UBM-INPUT fields
class UbmInputDefault(BaseModel):
    bevs_ratio: float #suggestion not hidden default
    phevs_ratio: float #suggestion, not hidden default

# UBM-CONFIG fields
class UbmConfigDefault(BaseModel):
    night_ratio: NightRatio #suggestion, not hidden default + dcm option
    day_ratio: DayRatio #suggestion, not hidden default + dcm option
    km_travelled_dist: dict #suggestion, not hidden default
    starting_time_day_other: dict #hidden default
    starting_time_day_work: dict #hidden default
    starting_time_night_home: dict #hidden default
    starting_time_day: dict #hidden default
    starting_time_night: dict #hidden default
    home_parking_time: dict #hidden default
    work_parking_time: dict #hidden default
    other_parking_time: dict #hidden default
    starting_soc_dist: dict #hidden default
    final_soc_dist: dict #hidden default

class UbmDefaults(BaseModel):
    input: UbmInputDefault
    config: UbmConfigDefault