from fastapi import APIRouter, Depends
from pydantic.class_validators import List
from typing import Optional

from app.core.db import DB
from dssdm.mongo.mongodb_utils import OID
#from app.models.common.mongodb_utils import OID
from dssdm.mongo.input.user import UserInDB
#from app.models.user import UserInDB
from dssdm.mongo.output.result import SimulationResult
from dssdm.mongo.input.analysis import AnalysesResults
#from app.models.results import SimulationResult
from app.services.users import get_current_active_user, get_current_active_simulator
from app.services.results import post_results, get_results

router = APIRouter()

@router.get("/{project_id}/{analyses_id}", response_model=AnalysesResults)
async def get_results_for_single_analyses(project_id: OID, analyses_id: OID, db: DB = Depends(), 
            current_user: UserInDB = Depends(get_current_active_user)):
    return get_results(project_id, analyses_id, db, current_user)

@router.post("/{project_id}/{analyses_id}")
async def edit_results_for_single_analyses(project_id: OID, analyses_id: OID, results: Optional[SimulationResult] = None, db: DB = Depends(), 
            current_user: UserInDB = Depends(get_current_active_simulator)):
    post_results(project_id, analyses_id, results, db, current_user)


