from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os

os.sys.path.append(
    r"C:\Users\Administrator\Desktop\full-stack-fastapi-postgresql\{{cookiecutter.project_slug}}\backend\app")

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_user_by_name(self, db: Session, name: str):
        return db.query(self.model).filter(self.model.full_name == name).all()

    # 只有视图中的User才能使用 删选除了super用户其他用户信息
    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 10000
    ) -> List[ModelType]:
        return db.query(self.model).filter(self.model.is_superuser == 0).offset(skip).limit(limit).all()

    # 只有视图中的item才能使用， 删选除了super用户其他用户信息
    def get_multi_items(
            self, db: Session, *, skip: int = 0, limit: int = 10000
    ) -> List[ModelType]:
        return db.query(self.model).filter(self.model.own_id != 1).offset(skip).limit(limit).all()

    # 创建必须是全套的CreateSchemaType类型
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # 更新就不用了，可以是字典，字典里面是需要修改的参数信息
    @staticmethod
    def update(
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:

        # ModelType -> 数据库表对象

        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            # 加判断，要兼容传参为dict的情况，也就是部分更新情况
            if field in update_data:
                # setattr(object, name, value)
                # object -- 对象 -> 类的实例对象
                # name -- 字符串 -> 类的实例对象属性
                # value -- 属性值 -> 类的实例属性的值
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
