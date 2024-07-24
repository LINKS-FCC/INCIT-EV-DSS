from typing import List

from dssdm.mongo.mongodb_utils import MongoModel

class CIDatabase(MongoModel):
    manufacturer: str
    max_output_power: float
    installation_cost: int
    maintenance_cost: int
    authorization: str # example: PIN code, RFID
    EV_communication: str # example: IEC 61851 & IEC15118