from typing import Optional, List
from app.models.common.mongodb_utils import MongoModel


class PU(MongoModel):
    fast_cs: int
    fast_accs: int
    slow_cs: int

class Occupancy(MongoModel):
    fast_cs: List[float]
    fast_accs: List[float]
    slow_cs: List[float]

class Borders(MongoModel):
    border_red: List[float]
    border_yellow: List[float]

class SimulationResult(MongoModel):
    new_css: Optional[PU]
    initial_cost_pu: Optional[PU]
    maintenance_costs_pu: Optional[PU]
    initial_costs: Optional[int]
    maintenance_costs: Optional[int]
    occupancy: Occupancy
    borders: Borders
    stays: List[float]
    RHC: int 
    CIY: int 
    ECSF: int
    ECSFAC: int
    ECSS: int
    ROI: int
    LW: Optional[int]
    TNP: int
    CPPV: int
    voltage_drop_KPI: int 
    power_demand_KPI: int
    gr_KPI: str
    voltage_events_KPI: int
    power_events_KPI: int
