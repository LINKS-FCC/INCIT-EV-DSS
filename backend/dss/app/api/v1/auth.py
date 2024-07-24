from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.config import settings
from app.core.db import DB
from dssdm.mongo.input.token import Token
#from app.models.token import Token
from app.services.users import authenticate_user, create_access_token

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: DB = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.exp_min)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
