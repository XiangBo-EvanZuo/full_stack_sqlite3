from datetime import timedelta
from typing import Any
import random

from fastapi.responses import StreamingResponse
import redis
import pymysql
from pydantic import BaseModel

pool = redis.ConnectionPool(host='127.0.0.1')
red = redis.Redis(connection_pool=pool)


def read(num):
    '''读取数据库'''
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='123456',
                           db='identify',
                           charset='utf8')

    # 创建一个游标
    cursor = conn.cursor()
    # 查询数据
    sql = "select code from pics where num = %s "
    cursor.execute(sql, str(num))  # 执行sql
    result_1 = cursor.fetchone()
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接
    return result_1[0]


from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import os

os.sys.path.append(
    r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app")

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.get('/identify/{code}')
async def identify(code):
    n = random.randint(1, 10000 + 1)
    file_path = 'C:/Users/Administrator/Desktop/identify_code/identify/static/{}.png'.format(n)
    img = open(file_path, "rb")
    # n -> true num
    # mysql 储存的
    true_num = read(n)
    # print(true_num)
    # code 与 true num 之间的orm 放到redis之中
    # 验证一下是否有code存在
    identify_code = 'image_code_' + code
    if not red.exists(identify_code):
        try:
            red.setex('image_code_{}'.format(code), settings.EXPIRE_TIME, true_num)
        except Exception as e:
            print(e)
    return StreamingResponse(img)


class ReturnItems(BaseModel):
    status: str
    info: str


class Item(BaseModel):
    uid: str
    answer: str


# @router.post('/code/confirm/', response_model=ReturnItems)
# async def dec(item: Item):
#     if red.exists(item.uid):
#         true = red.get(item.uid).decode('ascii')
#         if true == item.answer:
#             return {'status': '200', 'info': '验证码正确'}
#         return {'status': '403', 'info': '验证码错误'}
#     else:
#         return {'status': '404', 'info': '验证码不存在'}


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
        db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # user = crud.user.authenticate(
    #     db, email=form_data.username, password=form_data.password
    # )
    #
    # return {
    #     "access_token": security.create_access_token(
    #         user.id, expires_delta=access_token_expires
    #     ),
    #     "token_type": "bearer",
    # }

    # 以上为测试

    try:
        uid = form_data.scopes[0]
        answer = form_data.scopes[1]
    except Exception as e:
        raise HTTPException(status_code=400, detail="请添加验证码")

    if red.exists(uid):
        true = red.get(uid).decode('ascii')
        if true == answer:

            user = crud.user.authenticate(
                db, email=form_data.username, password=form_data.password
            )
            print(form_data.username, form_data.password)
            print(form_data.scopes)
            if not user:
                raise HTTPException(status_code=400, detail="账号或密码错误")
            elif not crud.user.is_active(user):
                raise HTTPException(status_code=400, detail="账号已冻结")
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

            return {
                "access_token": security.create_access_token(
                    user.id, expires_delta=access_token_expires
                ),
                "token_type": "bearer",
            }
    raise HTTPException(status_code=400, detail="验证码错误")




@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    # print(password_reset_token)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    print(user.email, email, password_reset_token)
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
        token: str = Body(...),
        new_password: str = Body(...),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}


if __name__ == '__main__':
    c = security.create_access_token('wang')
    print(c)
