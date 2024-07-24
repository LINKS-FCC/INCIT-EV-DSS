from typing import Dict, List

from pydantic import Field

from app.models.common.mongodb_utils import OID, MongoModel
from app.models.user import UserInfo

class NightRatio(MongoModel):
    home_public: float
    home_private: float

class DayRatio(MongoModel):
    work_public: float  # Office
    work_private: float  # Office
    other_public: float  # Street
    other_semi_public: float  # Street
    fast: float 
