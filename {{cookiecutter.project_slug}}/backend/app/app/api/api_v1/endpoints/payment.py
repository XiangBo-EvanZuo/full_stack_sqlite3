import os
os.sys.path.append(r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app")

from fastapi import APIRouter, Body, Depends, HTTPException


from app import models, schemas
from app.api import deps
from app.utils import OpenidUtils


router = APIRouter()


@router.get('/openid/')
def get_openid(code):
    try:
        openidutils = OpenidUtils(code)
        openid = openidutils.get_openid()
    except Exception as e:
        raise HTTPException(status_code=400, detail="获取openid失败")
    return openid


def get_openid_wechat(code):
    try:
        openidutils = OpenidUtils(code)
        openid = openidutils.get_openid()
    except Exception as e:
        raise HTTPException(status_code=400, detail="获取openid失败")
    return openid

if __name__ == '__main__':
    pass
