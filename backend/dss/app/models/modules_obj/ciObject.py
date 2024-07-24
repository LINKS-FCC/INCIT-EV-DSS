from typing import Dict, List

from pydantic import Field

from app.models.common.mongodb_utils import OID, MongoModel
from app.models.user import UserInfo

class CIDatabase(MongoModel):
    manufacturer: str
    max_output_power: float
    installation_cost: int
    maintenance_cost: int
    authorization: str # example: PIN code, RFID
    EV_communication: str # example: IEC 61851 & IEC15118