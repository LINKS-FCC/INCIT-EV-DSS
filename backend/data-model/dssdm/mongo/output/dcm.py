from pydantic import BaseModel


class Ratio_DCM_Output(BaseModel):
    bev: float
    phevs: float


class Charging_Night(BaseModel):
    home_public: float
    home_private: float


class Charging_Day(BaseModel):
    work_public: float
    work_private: float
    other_public: float
    other_semi_public: float
    fast: float


class Charging_DCM_Output(BaseModel):
    night_ratio: Charging_Night
    day_ratio: Charging_Day
