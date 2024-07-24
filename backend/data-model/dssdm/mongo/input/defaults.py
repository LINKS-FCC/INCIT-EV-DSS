from pydantic import BaseModel, Field
from typing import List, Dict

from dssdm.mongo.mongodb_utils import OID, MongoModel

from dssdm.mongo.input.modules_defaults.ci_def import CiDefaults
from dssdm.mongo.input.modules_defaults.power_def import PowerDefaults
from dssdm.mongo.input.modules_defaults.ubm_def import UbmDefaults
from dssdm.mongo.input.modules_defaults.dcm_def import DcmWeights

# ANALYSIS DEFAULTS (CI, P, UBM)
class AnalysisDefaults(BaseModel):
    power: PowerDefaults
    ci: CiDefaults
    ubm: UbmDefaults

# DCM DEFAULTS (dcm weights, ratio and chargin location)
class DcmDefaults(BaseModel):
    weights: DcmWeights
    ratio_sales: Dict[str, float]

# FINAL DEFAULT CLASS (analysis, dcm)
class DefaultsNotInDB(MongoModel):
    analysis: AnalysisDefaults
    dcm: DcmDefaults

class Defaults(DefaultsNotInDB):
    id: OID = Field(alias="_id")
