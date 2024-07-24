from fastapi import APIRouter, Depends

from app.core.db import DB
from dssdm.mongo.input.user import UserInDB
#from app.models.user import UserInDB
from app.services.users import get_current_active_user
from app.services.defaults import get_latest_defaults, update_single_default

router = APIRouter()

@router.get("/")
async def get_current_default_values(
          db: DB = Depends(),
          #current_user: UserInDB = Depends(get_current_active_user)
          ):
          return get_latest_defaults(db)

@router.put("/")
async def update_default(
          target_module: str,
          target_field: str,
          new_default_value,
          db: DB = Depends(),
        #current_user: UserInDB = Depends(get_current_active_user)
          ):
          return update_single_default(db, target_module, target_field, new_default_value)