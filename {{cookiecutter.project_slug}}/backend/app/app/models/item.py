from typing import TYPE_CHECKING
import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import os
os.sys.path.append(r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app")

from app.db.base_class import Base

# 循环导包问题，没有解决
# if TYPE_CHECKING:
from .user import User  # noqa: F401


class Item(Base):
    id = Column(Integer, primary_key=True, index=True)
    # title = Column(String(50), index=True)
    # description = Column(String(50), index=True)

    """增加功能： 
       1.单次消费所获取的用户积分
       2.用户消费的时间
       3.用户消费的金钱
       """
    cost_money = Column(Integer, index=True)
    earn_score = Column(Integer, index=True)
    creat_time = Column(DateTime, default=datetime.datetime.now)

    owner_id = Column(Integer, ForeignKey("user.id"))
    # owner = relationship("User", back_populates="items")
