from typing import List
from fastapi import APIRouter, Depends

from dssdm.mongo.input.user import UserInDB
#from app.models.user import UserInDB
from app.services.dcm import dcm_get_charging, dcm_get_ratio
from app.services.users import get_current_active_user
from dssdm.mongo.input.defaults import Defaults
from app.services.defaults import get_latest_defaults
from dssdm.mongo.input.dcm import Charging_DCM_Input, Ratio_DCM_Input

router = APIRouter()

@router.post("/ratio")
async def get_ratio(
          ratio_params: Ratio_DCM_Input,
          current_user: UserInDB = Depends(get_current_active_user),
          current_defaults: Defaults = Depends(get_latest_defaults)
          ):
          return dcm_get_ratio(ratio_params, current_defaults, current_user)

@router.post("/charging")
async def get_charging(
          charging_params: Charging_DCM_Input,
          current_user: UserInDB = Depends(get_current_active_user),
          current_defaults: Defaults = Depends(get_latest_defaults)
          ):
          return dcm_get_charging(charging_params, current_defaults, current_user)
