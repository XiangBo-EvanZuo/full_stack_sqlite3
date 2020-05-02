from typing import TYPE_CHECKING
import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
import os
os.sys.path.append(r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app")

from app.db.base_class import Base
# 循环导包问题，没有解决
# if TYPE_CHECKING:
#     from .item import Item  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(50), index=True)
    email = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    scores = Column(Integer, index=True, default=0)
    time = Column(Integer, index=True, default=0)
    # 创建时间
    create_time = Column(DateTime, default=datetime.datetime.now)
    # 更新时间
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    """增加功能： 
    1.用户积分
    2.剩余的次数
    3.创建账户时间
    4.最后登录时间
    """

    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)



    # 循环导包没解决，这个无效
    # items = relationship("Item", back_populates="owner")
