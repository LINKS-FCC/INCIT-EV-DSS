from typing import Optional, List
from dssdm.mongo.mongodb_utils import MongoModel

class PU(MongoModel):
    fast_cs: int
    fast_accs: int
    slow_cs: int

class Occupancy(MongoModel):
    fast_cs: List[float]
    fast_accs: List[float]
    slow_cs: List[float]

class ChargingTime(MongoModel):
    fast: List[List[float]]
    medium: List[List[float]]
    slow: List[List[float]]

class Borders(MongoModel):
    border_red: List[float]
    border_yellow: List[float]

class UbmResult(MongoModel):
    start_parking_time: List[List[float]]
    start_energy: List[List[List[float]]]
    end_energy: List[List[List[float]]]
    parking_total: List[List[List[float]]]
    parking_total_summed_hourly: List[List[float]]
    parking_total_zones: List[int]
    energy_required : List[List[float]]
    spread_energy_required : List[List[float]]

class AnalysisResult(MongoModel):
    new_css: Optional[PU]
    occupancy: Occupancy
    borders: Borders
    stays: List[float]
    RHC: int 
    CIY: int 
    ECSF: int
    ECSFAC: int
    ECSS: int
    LW: Optional[int]
    TNP: int
    CPPV: int
    voltage_drop_KPI: int 
    power_demand_KPI: int
    gr_KPI: str
    voltage_events_KPI: int
    power_events_KPI: int
    charging_time: Optional[ChargingTime]
    SOC: Optional[List[float]]
    losses_KPI: str
    zscr_KPI: List[float]
    peak_deviation_KPI: List[float]

class SimulationResult(MongoModel):
    ubm_result: UbmResult
    analysis_result: Optional[List[AnalysisResult]]