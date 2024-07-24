from fastapi import HTTPException
from typing import List
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status
from app.core.db import *

from dssdm.mongo.mongodb_utils import OID
from dssdm.mongo.input.analysis import AnalysesResults
from dssdm.mongo.input.user import UserInDB
from dssdm.mongo.input.project import ProjectInDB
from dssdm.mongo.output.result import SimulationResult
#from app.models.analyses import AnalysesInDB
#from app.models.common.mongodb_utils import OID
#from app.models.project import ProjectInDB
#from app.models.results import SimulationResult
#from app.models.user import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_results(project_id: OID, analyses_id: OID, db: DB, current_user: UserInDB):
    """
    Get results of a specific simulation analysis

    Parameters
    ----------
    project_id: OID
        project id   
    analyses_id: OID
        analysis id 
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations

        
    Returns
    -------
    analyses: AnalysisInDB
        All informations about analysis and his results

    """
    a = db.instance["analyses"]
    p = db.instance["projects"]
    analyses = AnalysesResults.from_mongo(a.find_one({"_id": analyses_id, "project_id": project_id}))
    projects = ProjectInDB.from_mongo(p.find_one({"_id": project_id, "users": {"$in": [current_user.id]}}))
    if analyses is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no analyses/projects with the specified ID.")
    if projects is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if analyses.results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Results are not available now")
    if analyses.status != "completed":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Results not available")
    return analyses


def post_results(project_id: OID, analyses_id: OID, results: SimulationResult, db: DB, current_user: UserInDB):
    """
    Post results of a specific simulation analysis on database (accessible ONLY for the simulator machine)

    Parameters
    ----------
    project_id: OID
        project id   
    analyses_id: OID
        analysis id 
    results: SimulationResult
        All informations about simulation analysis results
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations

        
    Returns
    -------
    null => everything right

    """
    a = db.instance["analyses"]
    if(results is not None):
        #p = db.instance["projects"]
        analyses = AnalysesResults.from_mongo(a.find_one({"_id": analyses_id, "project_id": project_id}))
        if analyses is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no analyses/projects with the specified ID.")
        analyses.results = results
        analyses.status = "completed"
        analyses.last_modify = datetime.now(timezone.utc)
        a.update_one({"_id": analyses_id, "project_id": project_id}, {"$set": analyses.dict(exclude_none=True)})
    else:
        a.update_one({"_id": analyses_id, "project_id": project_id}, {"$set": {"status": "failed"}})
