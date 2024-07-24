from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, validator, Field

from dssdm.mongo.mongodb_utils import OID, MongoModel

class User(MongoModel):
    username: str
    email: EmailStr

class UserInfo(User):
    id: OID = Field(alias="_id")
    # TODO: change to True when the activation part will be implemented
    disabled: Optional[bool] = False

class UserInDB(UserInfo):
    hashed_password: str
    scopes: List[str]

class UserNotYetInDB(User):
    hashed_password: str
    disabled: Optional[bool] = False
    scopes: List[str]

class PasswordChange(BaseModel):
    old_password: str
    password: constr(regex=r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}")
    password_again: constr(regex=r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}")

    @validator('password_again')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

class InfoUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v

class UserRegistration(User):
    gdpr_accepted: bool = False
    password: constr(regex=r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}")
    password_again: constr(regex=r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}")

    @validator('password_again')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

    @validator('gdpr_accepted')
    def gdpr_accepted_true(cls, v):
        if not v:
            raise ValueError('gdpr_accepted must be True')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v