from fastapi import HTTPException, status, Depends

from app.core.db import DB
# from app.models.user import UserInDB
from dssdm.mongo.input.user import UserInDB
from dssdm.mongo.input.defaults import Defaults, DefaultsNotInDB

def get_latest_defaults(db: DB = Depends()):
    """
    Get latest defaults saved in database

    Parameters
    ----------
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations

        
    Returns
    -------
    Defaults: Defaults 
        dictionary with a field for every modules that have defaults, with inside all the latest defaults values

    """
    d = db.instance["defaults"]
    defaults = Defaults.from_mongo(d.find_one())
    if defaults is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no defaults")
    return  defaults

def update_single_default(db: DB,  target_module: str, target_field: str, new_default_value):
    """
    Update the value of a single field of a specifc module of the defaults saved in db

    Parameters
    ----------
    db: DB
        database with all informations
    current_user: UserInDB
        current logged user informations
    target_module: str
        string containing the module of which a default value needs to be changed (ub, power, ci)
    target_field: str
        string containing the specific field that needs to be changed
    new_default_value: any
        new value to set to a certain default

        
    Returns
    -------
    has_updated: boolean
        true if updated correctly, false in case of error

    """
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) # TODO: understand how to implement auth to update defaults

    d = db.instance["defaults"] 
    new_value = {"$set": {f"{target_module}.{target_field}": new_default_value}}
    updated = Defaults.from_mongo(d.find_one_and_update({}, new_value))
    if updated is None:
        return False
    return True