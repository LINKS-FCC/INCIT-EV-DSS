from datetime import datetime, timezone
import os
from fastapi import HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status
from base64 import b64decode, b64encode
from app.core.db import *
from dssdm.mongo.input.analysis import AnalysesInDB
#from app.models.analyses import AnalysesInDB
from dssdm.mongo.mongodb_utils import OID
#from app.models.common.mongodb_utils import OID
from dssdm.mongo.input.project import Project, ProjectNotYetInDB, ProjectInDB, ProjectInDBAggregated, ProjectUpdate
#from app.models.project import Project, ProjectNotYetInDB, ProjectInDB, ProjectInDBAggregated, ProjectUpdate
from dssdm.mongo.input.user import UserInDB
#from app.models.user import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_projects(db: DB, user: UserInDB):
    """
    Get all projects of the user

    Parameters
    ----------
    db: DB
        database with all informations
    user: UserInDB
        current logged user informations

    Returns
    -------
    projects_list: List[ProjectInDB]
        List with all projects of logged user

    """
    c = db.instance['projects']

    projects_list = list(map(lambda kv: ProjectInDB.from_mongo(kv), list(c.find({"users": user.id}))))
    return projects_list

def get_project(db: DB, user: UserInDB, project_id: OID):
    """
    Get single project of the user

    Parameters
    ----------
    db: DB
        database with all informations
    user: UserInDB
        current logged user informations
    project_id: OID
        project id

    Returns
    -------
    projects: ProjectInDB
        Selected project with all informations

    """
    c = db.instance['projects']
    project = ProjectInDB.from_mongo(c.find_one({"_id": project_id}))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no project with the specified ID.")
    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    project = ProjectInDBAggregated.from_mongo(c.aggregate([{"$match": {"_id": project_id}}, {
        "$lookup": {"from": "users", "localField": "users", "foreignField": "_id", "as": "users"}}]).next())
    return project

def get_shapefile_project(db: DB, user: UserInDB, project_id: OID):
    """
    Get shapefile of a project encoded in base64

    Parameters
    ----------
    db: DB
        database with all informations
    user: UserInDB
        current logged user informations
    project_id: OID
        project id

    Returns
    -------
    shapefile: string
        Shapefile encoded in base64

    """
    c = db.instance['projects']
    project = ProjectInDB.from_mongo(c.find_one({"_id": project_id}))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no project with the specified ID.")
    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    with open("shapefile/{}.zip".format(project_id), "rb") as z:
        return b64encode(z.read())

def post_project(db: DB, user: UserInDB, project: Project, shapefile: UploadFile):
    """
    NOT AVAILABLE
    See "post_project_with_shape(...)"
    """
    c = db.instance['projects']
    project_db = ProjectNotYetInDB(**project.dict(), users=[user.id], last_modify=datetime.now(timezone.utc))
    res = c.insert_one(project_db.mongo())
    with open("shapefile/{}.zip".format(res.inserted_id), "wb") as z:
        z.write(shapefile.file.read())
        z.close()
    return ProjectInDB(**project_db.dict(), id=res.inserted_id)

def post_project_with_shape(db: DB, current_user: UserInDB, project_to_be_created: Project):
    """
    Post a specific project

    Parameters
    ----------
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations
    project_to_be_created: Project
        Object with all informations about project we want to store on DB (also with shapefile encoded in base64 like a string)

    Returns
    -------
    ProjectInDB
        Project object stored on DB

    """
    c = db.instance['projects']
    shape = project_to_be_created.shapefile
    project_to_be_created.shapefile = ""
    
    if c.count_documents({"name": project_to_be_created.name, "users": current_user.id}) > 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="There is already a project with the same name")
    
    project_db = ProjectNotYetInDB(**project_to_be_created.dict(), users=[current_user.id], last_modify=datetime.now(timezone.utc))
    res = c.insert_one(project_db.mongo())
    project_db.shapefile = str(res.inserted_id) + ".zip"
    c.update_one({"_id": res.inserted_id}, {'$set': project_db.dict(exclude_none=True)})

    if not os.path.exists("shapefile/"):
        os.makedirs("shapefile/")
    with open("shapefile/{}.zip".format(res.inserted_id), "wb") as b:
        b.write(b64decode(shape))
        b.close()

    return ProjectInDB(**project_db.dict(), id=res.inserted_id)

def put_project(db: DB, user: UserInDB, project_id: OID, project_updated: ProjectUpdate, shapefile: UploadFile = None):
    """
    NOT AVAILABLE
    See "put_project_with_shape(...)"
    """
    c = db.instance['projects']
    project = ProjectInDB.from_mongo(c.find_one({"_id": project_id}))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no project with the specified ID.")
    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    project_updated.last_modify = datetime.now(timezone.utc)
    c.update_one({"_id": project_id}, {"$set": project_updated.dict(exclude_none=True)})
    if shapefile:
        with open("shapefile/{}.zip".format(project_id), "wb") as z:
            z.write(shapefile.file.read())
            z.close()

def put_project_with_shape(project_id: OID, project_updated: ProjectUpdate, db: DB, user: UserInDB):
    """
    Modify some specific project field already in Database

    Parameters
    ----------
    project_id: OID
        project id
    project_updated: ProjectUpdate
        Project field we want to modify
    db: DB
        database with all informations
    user: UserInDB
        current logged user informations
    
    Returns
    -------
    null => everything right

    """
    c = db.instance['projects']

    if(project_updated.name and c.count_documents({"name": project_updated.name, "users": user.id}) > 0):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="There is already a project with the same name")

    project = ProjectInDB.from_mongo(c.find_one({"_id": project_id}))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no project with the specified ID.")
    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    project_updated.last_modify = datetime.now(timezone.utc)
    if project_updated.shapefile is not None:
        with open("shapefile/{}.zip".format(project.id), "wb") as b:
            b.write(b64decode(project_updated.shapefile))
            b.close() 
        project_updated.shapefile = str(project.id) + ".zip"
    c.update_one({"_id": project_id}, {"$set": project_updated.dict(exclude_none=True)})


def delete_project(db: DB, current_user: UserInDB, project_id: OID):
    """
    Delete specific project from database

    Parameters
    ----------
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations
    project_id: OID
        project id
        
    Returns
    -------
    null => everything right

    """
    c = db.instance['projects']
    d = db.instance["analyses"]
    project = ProjectInDB.from_mongo(c.find_one({"_id": project_id}))
    analyses_list = list(map(lambda kv: AnalysesInDB.from_mongo(kv), list(d.find({"project_id": project_id}))))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no project with the specified ID.")
    if current_user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if analyses_list is not None:
        for analyses_item in analyses_list:
            d.delete_one(analyses_item.mongo())
    c.delete_one(project.mongo())
    os.remove("shapefile/{}.zip".format(project_id))