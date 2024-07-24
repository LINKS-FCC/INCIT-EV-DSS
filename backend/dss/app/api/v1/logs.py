from typing import List
from fastapi import APIRouter, Depends

from app.core.db import DB
from dssdm.mongo.input.user import UserInDB
from dssdm.mongo.mongodb_utils import OID
from dssdm.mongo.output.logs import LogNotYetInDB
#from app.models.user import UserInDB
from app.services.users import get_current_active_user
from app.services.logs import get_logs_of_analysis, create_log_of_analysis, unstuck_analysis

router = APIRouter()

@router.get("/{analysis_id}")
async def get_all_logs_of_analysis(
          analysis_id: str,
          db: DB = Depends(),
          #current_user: UserInDB = Depends(get_current_active_user)
          ):
          return get_logs_of_analysis(analysis_id, db)

@router.post("/")
async def create_log(
          log: LogNotYetInDB,
          db: DB = Depends(),
        #current_user: UserInDB = Depends(get_current_active_user)
          ):
          return create_log_of_analysis(log, db)

@router.put("/unstuck/{analyses_id}")
async def unstuck_single_analysis(analyses_id: OID, db: DB = Depends(), 
            # _: UserInDB = Depends(get_current_active_simulator)
            ):
            return unstuck_analysis(analyses_id, db)