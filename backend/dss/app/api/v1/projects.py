from typing import Optional
from pydantic.class_validators import List
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.core.db import DB
from dssdm.mongo.mongodb_utils import OID
#from app.models.common.mongodb_utils import OID
from dssdm.mongo.input.project import Project, ProjectInDB, ProjectInDBAggregated, ProjectUpdate
#from app.models.project import Project, ProjectInDB, ProjectInDBAggregated, ProjectUpdate
from dssdm.mongo.input.user import UserInDB
#from app.models.user import UserInDB
from app.services.projects import get_projects, post_project, delete_project, get_project, put_project, post_project_with_shape, put_project_with_shape, get_shapefile_project
from app.services.users import get_current_active_user
import json

router = APIRouter()


@router.get("/", response_model=List[ProjectInDB])
async def list_all_user_projects(db: DB = Depends(), current_user: UserInDB = Depends(get_current_active_user)):
    return get_projects(db, current_user)


@router.post("/", response_model=ProjectInDB) #not available. You should use the one under
async def create_a_user_project(project_to_be_created: str = Form(...), shapefile: UploadFile = File(...), db: DB = Depends(),
                                current_user: UserInDB = Depends(get_current_active_user)):
    return post_project(db, current_user, Project(**(json.loads(project_to_be_created))), shapefile)

@router.post("/shapefile", response_model=ProjectInDB)
async def create_a_user_project(project_to_be_created: Project, db: DB = Depends(),
                            current_user: UserInDB = Depends(get_current_active_user)):
    return post_project_with_shape(db, current_user, project_to_be_created)


@router.get("/{project_id}", response_model=ProjectInDBAggregated)
async def open_a_user_project(project_id: OID, db: DB = Depends(),
                              current_user: UserInDB = Depends(get_current_active_user)):
    return get_project(db, current_user, project_id)


@router.get("/{project_id}/shapefile")
async def get_shapefile_encoded(project_id: OID, db: DB=Depends(),
                              current_user: UserInDB = Depends(get_current_active_user)):
    return get_shapefile_project(db, current_user, project_id)


@router.put("/{project_id}") #not available. you should use the one under
async def edit_a_single_project(project_id: OID, project_updated: str = Form(...), file: Optional[UploadFile] = File(None), db: DB = Depends(),
                                current_user: UserInDB = Depends(get_current_active_user)):
    return put_project(db, current_user, project_id, ProjectUpdate(**json.loads(project_updated)), file)

@router.put("/shapefile/{project_id}")
async def edit_a_single_project_with_shape(project_id: OID, project_updated: ProjectUpdate, db: DB = Depends(),
                                current_user: UserInDB = Depends(get_current_active_user)):
    return put_project_with_shape(project_id, project_updated, db, current_user)


@router.delete("/{project_id}")
async def delete_a_user_project_and_all_his_analyses(project_id: OID, db: DB = Depends(),
                                current_user: UserInDB = Depends(get_current_active_user)):
    delete_project(db, current_user, project_id)
