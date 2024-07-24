from dssdm.mongo.mongodb_utils import MongoModel

class NightRatio(MongoModel):
    home_public: float
    home_private: float

class DayRatio(MongoModel):
    work_public: float  # Ofice
    work_private: float  # Office
    other_public: float  # Street
    other_semi_public: float  # Street
    fast: float  #potrebbe anche essere int non lo so