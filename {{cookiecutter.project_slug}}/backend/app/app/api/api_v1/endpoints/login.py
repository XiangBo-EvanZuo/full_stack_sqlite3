from datetime import timedelta
from typing import Any
import random
import json
import requests

from fastapi.responses import StreamingResponse
import redis
import pymysql
from pydantic import BaseModel

# 放在这个db里面
pool = redis.ConnectionPool(host='127.0.0.1')
red = redis.Redis(connection_pool=pool)


# 放在这个db里面
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


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
        db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # form_data.username

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


@router.post("/password-recovery/", response_model=schemas.Msg)
def recover_password(
        email: str = Body(...),
        identify_code: str = Body(...),
        answer: str = Body(...),
        db: Session = Depends(deps.get_db)
) -> Any:
    """
    Password Recovery
    """
    # 验证码阶段
    if red.exists(identify_code):
        true = red.get(identify_code).decode('ascii')
        if true != answer:
            raise HTTPException(status_code=400, detail="验证码错误")
    else:
        raise HTTPException(status_code=400, detail="验证码不存在")

    # 验证用户是否存在
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )

    # 用户存在，验证短信验证码
    password_reset_token = generate_password_reset_token(email=email)
    message_code = generate_verification_code()
    codes = {message_code: password_reset_token}

    if not red.exists(email):
        try:
            red.setex(email, settings.EMAIL_RESET_TOKEN_EXPIRE_SECONDS, json.dumps(codes))
            try:
                # 暂未开启API接口
                if settings.USERS_OPEN_RESET_PASSWORD:
                    send_result = send_message(message_code, email)
                    print(send_result)
                print(message_code)
                print(email)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
    else:
        raise HTTPException(
            status_code=404,
            detail="请等60秒",
        )
    # 放弃发邮件，选择短信
    # send_reset_password_email(
    #     email_to=user.email, email=email, token=password_reset_token
    # )

    return {"msg": "Password recovery email sent"}


# 放在这个utils里面
def send_message(message_code, phone):
    """
    :param phone: 手机号
    :param message_code: 验证码
    :return: dict 发送结果
    """

    # 调用api
    data = {
        "content": '您的验证码是：{message}。请不要把验证码泄露给其他人。'.format(message=message_code),
        "account": settings.MESSAGE_SEND_ACCOUNT,
        "password": settings.MESSAGE_SEND_PASSWORD,
        "mobile": phone
    }
    c = requests.post(url=settings.MESSAGE_SEND_URL, data=data)
    code = c.text.split('code>')[1][0]
    msg = c.text.split('msg>')[1].split('<')[0]
    smsid = c.text.split('smsid>')[1].split('<')[0]
    return {
        "code": code,
        "msg": msg,
        "smsid": smsid
    }


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
        # message_email 前端绑定值
        message_code: str = Body(...),
        message_email: str = Body(...),
        new_password: str = Body(...),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    user = crud.user.get_by_email(db, email=message_email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在与系统中",
        )
    try:
        key = red.get(message_email).decode('ascii')
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="请先点击发送验证码",
        )

    token = json.loads(key).get(message_code)
    if not token:
        raise HTTPException(
            status_code=404,
            detail="短信验证码错误",
        )
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    if not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    # 是否允许修改管理员找回自己的密码 默认允许
    # if crud.user.is_superuser(user):
    #     raise HTTPException(status_code=400, detail="管理员更改？？？")

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}


# 放在这个utils里面
def generate_verification_code(len=4):
    ''' 随机生成6位的验证码 '''
    # 注意： 这里我们生成的是0-9A-Za-z的列表，当然你也可以指定这个list，这里很灵活
    # 比如： code_list = ['P','y','t','h','o','n','T','a','b'] # PythonTab的字母
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    # for i in range(65, 91):  # 对应从“A”到“Z”的ASCII码
    #     code_list.append(chr(i))
    # for i in range(97, 123):  # 对应从“a”到“z”的ASCII码
    #     code_list.append(chr(i))
    myslice = random.sample(code_list, len)  # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(myslice).upper()  # list to string
    return verification_code


if __name__ == '__main__':
    # c = security.create_access_token('wang')
    # print(c)
    pass
