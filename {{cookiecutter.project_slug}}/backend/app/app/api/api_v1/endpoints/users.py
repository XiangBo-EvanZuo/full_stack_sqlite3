from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
import os

os.sys.path.append(
    r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app")

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import send_new_account_email

from app.api.api_v1.endpoints.login import red, read

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
        *,
        db: Session = Depends(deps.get_db),
        password: str = Body(None),
        full_name: str = Body(None),
        email: EmailStr = Body(None),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=schemas.User)
def create_user_open(
        *,
        db: Session = Depends(deps.get_db),
        password_1: str = Body(...),
        password_2: str = Body(...),
        email: EmailStr = Body(...),
        full_name: str = Body(None),
        uid: str = Body(...),
        answer: str = Body(...)
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="服务器未开启开放注册功能，请联系统管理员",
        )

    if password_1 != password_2:
        raise HTTPException(
            status_code=403,
            detail="两次输入的密码不一致，请保持一致",
        )
    password = password_2
    # 验证码
    if red.exists(uid):
        true = red.get(uid).decode('ascii')
        if true != answer:
            raise HTTPException(
                status_code=400,
                detail="验证码错误",
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="验证码不存在",
        )

    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )

    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/SearchId/{user_id}", response_model=schemas.User, tags=['search', 'SearchId'])
def read_user_by_id(
        user_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.get("/SearchEmail/{email}", response_model=schemas.User, tags=['search', 'SearchEmail'])
def read_user_by_email(
        email: str,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by email.
    """
    user = crud.user.get_by_email(db, email=email)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="没有权限"
        )
    if user:
        return user
    raise HTTPException(
        status_code=400, detail="没有该用户"
    )


@router.get("/SearchName/{fullname}", response_model=List[schemas.User], tags=['search', 'SearchFullName'])
def read_user_by_fullname(
        fullname: str,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
        Get a specific user by full_name.
        """
    user = crud.user.get_user_by_name(db, name=fullname)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="没有权限"
        )
    if user:
        return user
    raise HTTPException(
        status_code=400, detail="没有该用户"
    )


@router.get('/SearchAll', response_model=List[schemas.User], tags=['search', 'SearchAll'])
def read_user_all(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)

):
    users = crud.user.get_multi(db)
    if users:
        return users
    else:
        raise HTTPException(
            status_code=400, detail="没找到用户"
        )


@router.get('/SearchInactiveUsers', response_model=List[schemas.User], tags=['search', 'SearchInactiveUsers'])
def read_inactive_users(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)

):
    users = crud.user.get_inactive_users(db=db)
    if users:
        return users
    else:
        raise HTTPException(
            status_code=400, detail="没有被封的用户"
        )


@router.put("/{email}", response_model=schemas.User)
def update_user(
        *,
        db: Session = Depends(deps.get_db),
        email: str,
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
