from fastapi import APIRouter, Depends
from pydantic.class_validators import List
from typing import Union

from app.core.db import DB
#from app.models.common.mongodb_utils import OID
from dssdm.mongo.mongodb_utils import OID
from dssdm.mongo.input.analysis import AnalysesInDB, AnalysesFrontedUser, AnalysesUpdate
from dssdm.mongo.input.user import UserInDB
#from app.models.user import UserInDB
#from app.models.analyses import AnalysesInDB, Analyses, AnalysesUpdate
from app.services.analyses import get_analyses, post_analyses, get_single_analyses, put_analyses, delete_analyses, get_analyses_name_status
from app.services.users import get_current_active_user
from dssdm.mongo.input.defaults import Defaults
from app.services.defaults import get_latest_defaults

router = APIRouter()

@router.get("/status/{project_id}")
async def show_analyses_name_status(project_id: OID, db: DB = Depends(),
          current_user: UserInDB = Depends(get_current_active_user)):
          return get_analyses_name_status(project_id, db, current_user)

@router.get("/{project_id}", response_model=List[AnalysesInDB])
async def list_all_analyses_of_project(project_id: OID, db: DB = Depends(), 
            current_user: UserInDB = Depends(get_current_active_user)):
            return get_analyses(project_id, db, current_user)

@router.get("/{project_id}/{analyses_id}", response_model=AnalysesInDB)
async def open_single_analyses_of_project(project_id: OID, analyses_id: OID, db: DB = Depends(), 
            current_user: UserInDB = Depends(get_current_active_user)):
            return get_single_analyses(project_id, analyses_id, db, current_user)

@router.post("/{project_id}", response_model = AnalysesInDB)
async def create_analyses(analyses: AnalysesFrontedUser, project_id: OID, db: DB = Depends(), 
            current_user: UserInDB = Depends(get_current_active_user),
            current_defaults: Defaults = Depends(get_latest_defaults)):
            return post_analyses(analyses, project_id, db, current_user, current_defaults)

@router.put("/{project_id}/{analyses_id}")
async def edit_a_single_analyses(project_id: OID, analyses_id: OID, analyses_updated: AnalysesUpdate, db: DB = Depends(), 
            current_user: UserInDB = Depends(get_current_active_user)):
            return put_analyses(project_id, analyses_id, analyses_updated, db, current_user)

@router.delete("/{project_id}/{analyses_id}")
async def delete_single_analyses(project_id: OID, analyses_id: OID, db: DB = Depends(),
            current_user: UserInDB = Depends(get_current_active_user)):
            return delete_analyses(project_id, analyses_id, db, current_user)  