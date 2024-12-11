from fastapi import APIRouter, Depends

from app.core.db import DB
from dssdm.mongo.input.user import User, UserRegistration, PasswordChange, UserInDB, InfoUpdate, UserInfo
#from app.models.user import User, UserRegistration, PasswordChange, UserInDB, InfoUpdate, UserInfo
from app.services.users import delete_user_account_service, get_current_active_user, create_user, get_all_users, change_password, update_user, get_current_active_admin, delete_user_admin

router = APIRouter()


@router.get("")
async def get_users(db: DB = Depends()):
    return get_all_users(db)

@router.post("", response_model=UserInfo)
async def post_user(user: UserRegistration, db: DB = Depends()):
    return create_user(db, user)

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/password")
async def put_password(password_change: PasswordChange, current_user: UserInDB = Depends(get_current_active_user),
                       db: DB = Depends()):
    change_password(db, password_change, current_user)

@router.put("/me")
async def update_user_me(info_update: InfoUpdate, current_user: UserInDB = Depends(get_current_active_user),
                         db: DB = Depends()):
    update_user(db, info_update, current_user)


@router.delete("/delete-account")
async def delete_user_account( current_user: UserInDB = Depends(get_current_active_user),
                        db: DB = Depends()):
    return delete_user_account_service( db=db, current_user=current_user)

@router.delete("/{username}")
async def delete_user(username: str, current_user: UserInDB = Depends(get_current_active_admin),
                        db: DB = Depends()):
    return delete_user_admin(username, db, current_user)

