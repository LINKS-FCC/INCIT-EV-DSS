from datetime import timedelta, datetime
from typing import List, Optional
import os

from fastapi import Depends, HTTPException, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from pydantic import ValidationError
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status
from dssdm.mongo.input.project import ProjectInDB
from app.core.db import *
from dssdm.mongo.input.token import TokenData
#from app.models.token import TokenData
from dssdm.mongo.input.user import UserInDB, UserRegistration, UserInfo, PasswordChange, InfoUpdate, UserNotYetInDB
#from app.models.user import UserInDB, UserRegistration, UserInfo, PasswordChange, InfoUpdate, UserNotYetInDB
from dssdm.mongo.input.analysis import AnalysesInDB
from app.services.projects import get_projects

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token", 
    scopes={"user": "Standard users access", "admin": "Access to the whole system", "simulator": "Access to send results of simulation"}
)


def get_user(db: DB, username: str, db_out=True):
    """
    Get information of a specific user (accessible ONLY for the admin)

    Parameters
    ----------
    db: DB
        database with all informations
    username: str
        user username we want to know his informations

        
    Returns
    -------
    UserInDB:
        Informations of a specific user
    None:
        There isn't any user with the specified username

    """
    c = db.instance['users']
    if c.find_one({"username": username}) is None:
        raise HTTPException()
    user = UserInDB.from_mongo(c.find_one({"username": username})).dict()
    if username:
        return UserInfo(**user) if not db_out else UserInDB(**user)
    return None


def create_user(db: DB, user: UserRegistration):
    """
    Sign in a new user account

    Parameters
    ----------
    db: DB
        database with all informations
    user: UserRegistration
        Informations requested for the creation of a new user account
        
    Returns
    -------
    UserInfo:
        User informations used for subscription

    """
    c = db.instance['users']
    if c.count_documents({"email": user.email}) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="There is another user with the same email.")
    if c.count_documents({"username": user.username}) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="There is another user with the same username.")
    hash_pass = get_password_hash(user.password)
    user_db = UserNotYetInDB(**user.dict(), hashed_password=hash_pass, scopes=["user"])
    res = c.insert_one(user_db.mongo())
    return UserInfo(**user_db.dict(), id=res.inserted_id)


def change_password(db: DB, change_password: PasswordChange, current_user: UserInDB):
    """
    Change password of a specific user account

    Parameters
    ----------
    db: DB
        database with all informations
    change_password: PasswordChange
        Object with old password, new password and new password again
    current_user: UserInDB
        current logged user informations
        
    Returns
    -------
    null:
        Check that all fields in change_password are right and update password of logged user

    """
    c = db.instance['users']
    user = authenticate_user(db, current_user.username, change_password.old_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    current_user.hashed_password = get_password_hash(change_password.password)
    c.update_one({"username": current_user.username}, {"$set": {"hashed_password": current_user.hashed_password}})


def update_user(db: DB, info_update: InfoUpdate, current_user: UserInDB):
    """
    Update personal user account information

    Parameters
    ----------
    db: DB
        database with all informations
    info_update: InfoUpdate
        Informations you want to update of personal user account
    user: UserRegistration
        Informations requested for the creation of a new user account
        
    Returns
    -------
    null => everything right

    """
    c = db.instance['users']
    if info_update.email is not None and (c.count_documents({"email": info_update.email}) > 0 and info_update.email != current_user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="There is another user with the same email.")
    if info_update.username is not None and (c.count_documents({"username": info_update.username})> 0 and info_update.username != current_user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="There is another user with the same username.")
    c.update_one({"username": current_user.username}, {"$set": info_update.dict(exclude_none=True)})

def delete_user_admin(username: str, db: DB, current_user: UserInDB):
    """
    Delete a specific user account (accessible ONLY for the admin)

    Parameters
    ----------
    username: str
        username of user account you want to delete
    db: DB
        database with all informations
    info_update: InfoUpdate
        Informations you want to update of personal user account
    current_user:  UserInDB
        Informations about logged user (it should be admin user or the function fails)
        
    Returns
    -------
    null => everything right

    """
    c = db.instance["users"]
    user = UserInDB.from_mongo(c.find_one({"username": username}))
    print(user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user with inserted username")
    if user.username == current_user.username:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="You can't delete your account")
    c.delete_one(user.mongo())

def delete_user_account_service(db: DB, current_user: UserInDB):
    c = db.instance["users"]
    d = db.instance["projects"]
    a = db.instance["analyses"]
    
    # Recupera l'utente
    user = UserInDB.from_mongo(c.find_one({"_id": current_user.id}))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    
    # Recupera i progetti associati all'utente
    projects_list: List[ProjectInDB] = get_projects(db=db, user=user)
    
    for project in projects_list:
        # Recupera le analisi associate al progetto
        analysis_list = [AnalysesInDB.from_mongo(kv) for kv in a.find({"project_id": project.id}, {"results": 0})]
        for analysis in analysis_list:
            # Cancella ogni analisi
            a.delete_one(analysis.mongo())
        
        # Cancella il progetto
        d.delete_one(project.mongo())
        
        # Cancella i file associati al progetto
        file_path = f"shapefile/{project.id}.zip"
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Cancella l'utente
    c.delete_one(user.mongo())
    
    return True

def get_all_users(db: DB):
    return list(map(lambda kv: UserInfo(**UserInDB.from_mongo(kv).dict()), list(db.instance['users'].find())))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: DB, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_private_key, settings.jwt_algorithm)
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: DB = Depends()):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, settings.jwt_public_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(current_user: UserInfo = Security(get_current_user, scopes=["user"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_admin(current_user: UserInfo = Security(get_current_user, scopes=["admin"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_simulator(current_user: UserInfo = Security(get_current_user, scopes=["simulator"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
