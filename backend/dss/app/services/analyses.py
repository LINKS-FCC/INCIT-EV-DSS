from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status
from datetime import datetime, timezone
from app.core.db import *

from dssdm.mongo.mongodb_utils import OID
from dssdm.mongo.input.analysis import AnalysesInDB, AnalysesFrontedUser, AnalysesUpdate, AnalysesNotYetInDB, AnalysesWithDefaults
from dssdm.mongo.input.powerYaml import PowerYaml
from dssdm.mongo.input.ciYaml import CiYaml
from dssdm.mongo.input.ubmYaml import UbmConfig, UbmYaml, UbmYamlFrontend
from dssdm.mongo.input.user import UserInDB
from dssdm.mongo.input.project import ProjectInDB
from dssdm.mongo.input.defaults import Defaults, AnalysisDefaults
#from app.models.analyses import AnalysesInDB, Analyses, AnalysesNotYetInDB, AnalysesUpdate
#from app.models.common.mongodb_utils import OID
#from app.models.project import ProjectInDB
#from app.models.user import UserInDB

from base64 import b64encode
import requests
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_analyses(project_id: OID, db: DB, user: UserInDB):
    """
    Get all analyses of a specific project

    Parameters
    ----------
    project_id: OID
        project id
    db: DB
        database with all informations
    user: UserInDB
        current logged user informations

    Returns
    -------
    analyses_list: List[AnalysesInDB]
        List with all analyses of a specific project

    """

    d = db.instance["projects"]
    c = db.instance["analyses"]
    analyses_list = list(map(lambda kv: AnalysesInDB.from_mongo(kv), list(c.find({"project_id": project_id}, {"results": 0}))))
    projects = ProjectInDB.from_mongo(d.find_one({"_id": project_id, "users": {"$in": [user.id]}}))
    if analyses_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no projects with the specified ID.")
    if projects is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return analyses_list
    

def get_single_analyses(project_id: OID, analyses_id: OID, db: DB, current_user: UserInDB):
    """
    Get a single analysis of a specific project

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
    analyses: AnalysesInDB
        Single analysis object of a specific project

    """
    c = db.instance["analyses"]
    d = db.instance["projects"]
    analyses = AnalysesInDB.from_mongo(c.find_one({"_id": analyses_id, "project_id": project_id}, {"results": 0}))
    projects = ProjectInDB.from_mongo(d.find_one({"_id": project_id, "users": {"$in": [current_user.id]}}))
    if analyses is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no analyses/projects with the specified ID.")
    if projects is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return analyses

def get_analyses_name_status(project_id: OID, db: DB, current_user: UserInDB):
    """
    Get specific informations about all the analyzes of a project

    Parameters
    ----------
    project_id: OID
        project id
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations

    Returns
    -------
    analyses_list: List[Object] => Generic JSON object
        List of analyzes informations with this shape => {"name": str, "status": str, "last_modify": Date(), "_id": OID} => for every analysis project

    """
    c = db.instance["analyses"]
    d = db.instance["projects"]
    analyses_list = []
    analyses = c.find({"project_id": project_id}, {"name": 1, "status": 1, "last_modify": 1, "_id": 1})
    projects = ProjectInDB.from_mongo(d.find_one({"_id": project_id, "users": {"$in": [current_user.id]}}))
    if analyses_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no projects with the specified ID.")
    if projects is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) 
    for i in analyses:
        i["_id"] = str(i["_id"])
        analyses_list.append(i)
    return analyses_list 


def post_analyses(analyses_frontend: AnalysesFrontedUser, project_id: OID, db: DB, current_user: UserInDB, current_defaults: Defaults):
    """
    Post a new analysis of a specific project

    Parameters
    ----------
    analyses: AnalysesFrontendUser
        Analyses object with all user input of all modules (but no defaults)
    project_id: OID
        project id
    analyses_id: OID
        analysis id
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations
    current_defaults: Defaults
        latest defaults present in the database

    Returns
    -------
    AnalysesInDB
        Single analysis object posted on database

    """
    c = db.instance["analyses"]
    d = db.instance["projects"]

    if current_defaults is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No defaults have been found, they must be seeded and present in the database.")
    
    if(c.count_documents({"name": analyses_frontend.name, "project_id": project_id}) > 0):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="There is already an analyses with the same name")

    analyses_sim = merge_analyses_frontend_with_defaults(analyses_frontend, current_defaults)

    analyses_db = AnalysesNotYetInDB(**analyses_sim.dict(), project_id=project_id, last_modify=datetime.now(timezone.utc))

    projects_existence = ProjectInDB.from_mongo(d.find_one({"_id": project_id}))
    projects = ProjectInDB.from_mongo(d.find_one({"_id": project_id, "users": {"$in": [current_user.id]}}))

    if projects_existence is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no projects with the specified ID.")
    if projects is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        projects.last_modify = datetime.now(timezone.utc)
        d.update_one({"_id": project_id}, {"$set": projects.dict(exclude_none=True)})
        res = c.insert_one(analyses_db.mongo())

        if analyses_db.status == "running":
            sim_status = run_simulation(AnalysesInDB(**analyses_db.dict(), id=res.inserted_id), projects)
            c.update_one({"_id": res.inserted_id, "project_id": project_id}, {"$set": {"status": sim_status}})
        return AnalysesInDB(**analyses_db.dict(), id=res.inserted_id)


def put_analyses(project_id: OID, analyses_id: OID, analyses_updated: AnalysesUpdate, db: DB, current_user: UserInDB):
    """
    Modify some specific fields of an already existing analysis

    Parameters
    ----------
    project_id: OID
        project id
    analyses_id: OID
        analysis id
    analyses_updated: AnalysesUpdate
        Informations we want to modify of a specific analysis
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations

    Returns
    -------
    null => everything right

    """
    c = db.instance["analyses"]
    d = db.instance["projects"]

    if(analyses_updated.name and c.count_documents({"name": analyses_updated.name, "project_id": project_id}) > 0):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="There is already an analyses with the same name")

    analyses = AnalysesInDB.from_mongo(c.find_one({"_id": analyses_id, "project_id": project_id}))
    projects = ProjectInDB.from_mongo(d.find_one({"_id": project_id, "users": {"$in": [current_user.id]}}))
    if analyses is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no analyses/projects with the specified ID.")
    if projects is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    analyses_updated.last_modify = datetime.now(timezone.utc)
    projects.last_modify = datetime.now(timezone.utc)
    d.update_one({"_id": project_id}, {"$set": projects.dict(include={"last_modify"})})
    c.update_one({"_id": analyses_id, "project_id": project_id}, {"$set": analyses_updated.dict(exclude_none=True)})
    if analyses_updated.status == "running" and analyses.status != "running":#faccio richiesta a Nico solo se l'utente fa Save&Run
        sim_status = run_simulation(AnalysesInDB.from_mongo(c.find_one({"_id": analyses_id, "project_id": project_id})), projects)
        c.update_one({"_id": analyses_id, "project_id": project_id}, {"$set": {"status": sim_status}})
    return
    


def delete_analyses(project_id: OID, analyses_id: OID, db: DB, current_user: UserInDB):
    """
    Delete an analysis of a specific project

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
    null => everything right

    """
    c = db.instance['analyses']
    d = db.instance["projects"]
    analyses = AnalysesInDB.from_mongo(c.find_one({"_id": analyses_id, "project_id": project_id}))
    projects = ProjectInDB.from_mongo(d.find_one({"_id": project_id, "users": {"$in": [current_user.id]}}))
    if analyses is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no analyses/projects with the specified ID.")
    if projects is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    projects.last_modify = datetime.now(timezone.utc)
    d.update_one({"_id": project_id}, {"$set": projects.dict(exclude_none=True)})
    c.delete_one(analyses.mongo())

def run_simulation(analyses: AnalysesInDB, projects: ProjectInDB):
    """
    Start simulation of a specific analysis

    Parameters
    ----------
    analyses: AnalysesInDB
        Analysis object of a specific project (with all modules inputs)
    projects: ProjectInDB
        Project object with all his information

    Returns
    -------
    response.json()["result"]
        - Generic Object with the status of the simulation request
        - Status: running (simulation is running), failed (simulation is failed), pending (simulation is not in running because simulator is full of request)

    """

    with open("shapefile/{}".format(projects.shapefile), "rb") as b:
        data = b.read()
        shapefile = b64encode(data).decode("ascii")
        b.close()

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    analysis = analyses.dict()
    analysis["id"] = str(analyses.id)
    analysis["project_id"] = str(analyses.project_id)
    analysis.pop("last_modify")
    # analysis.pop("results")

    private_key = RSA.importKey(settings.jwt_private_key)
    signer = PKCS1_v1_5.new(private_key)
    
    digest = SHA256.new()
    digest.update(json.dumps(analysis).encode())
    analysis_signed = b64encode(signer.sign(digest)).decode("ascii")

    digest = SHA256.new()
    digest.update(shapefile.encode())
    shapefile_signed = b64encode(signer.sign(digest)).decode("ascii")
    
    body = {
        "analysis": analysis,
        "shape_file": shapefile,
        "analysis_hash": analysis_signed,
        "shape_file_hash": shapefile_signed
    }
    
    response = requests.post(url=settings.simulator_uri, headers=header, json=body)
    return response.json()["result"]

def merge_analyses_frontend_with_defaults(analysis_frontend: AnalysesFrontedUser, current_defaults: Defaults) -> AnalysesWithDefaults:
    defaults_for_analyses = current_defaults.analysis #pick defaults of analysis, ignoring dcm defaults
    analysis_with_defaults = analysis_frontend.dict() 
    #add UBM defaults (change only config, input is ok)
    ubm_frontend = UbmYamlFrontend(**analysis_frontend.ubmY.dict())
    ubm_config_frontend = ubm_frontend.config.dict()
    ubm_config_default = defaults_for_analyses.ubm.config.dict()
    ubm_config_default.pop("night_ratio") #suggestion field
    ubm_config_default.pop("day_ratio") #suggestion field
    ubm_config_default.pop("km_travelled_dist") #suggestion field
    ubm_config_with_def = UbmConfig(**ubm_config_default, **ubm_config_frontend) #keys conflict: use keys from right dict=fronten
    ubm_with_def = UbmYaml(input=ubm_frontend.input, config=ubm_config_with_def)
    analysis_with_defaults["ubmY"] = ubm_with_def
    print("ANALYSIS FRONTEND POWER Y IS NONE: ", analysis_frontend.powerY is None)
    if analysis_frontend.powerY is None:
        analysis_sim = AnalysesWithDefaults(**analysis_with_defaults)
        return analysis_sim
    else: 
        #add POWER defaults (handle ppp as optional from frontend)
        power_frontend = analysis_frontend.powerY.dict()
        power_defaults = defaults_for_analyses.power.dict()
        #if power_frontend["PPP"] and power_frontend["PPP"] is not None: #keys conflict
        #    power_defaults.pop("PPP")
        #    power_with_def = PowerYaml(**power_defaults, **power_frontend) 
        #else: 
        #    power_frontend.pop("PPP")
        power_with_def = PowerYaml(**power_frontend, **power_defaults) 
        analysis_with_defaults["powerY"] = power_with_def
        #add CI defaults
        ci_with_def = CiYaml(**analysis_frontend.ciY.dict(), **defaults_for_analyses.ci.dict()) #no key conflicts
        analysis_with_defaults["ciY"] = ci_with_def
        #merge frontend analyses with defaults
        analysis_sim = AnalysesWithDefaults(**analysis_with_defaults)
        return analysis_sim