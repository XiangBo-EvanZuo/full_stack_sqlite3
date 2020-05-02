from typing import Optional

from pydantic import BaseModel


# Shared properties
class ItemBase(BaseModel):
    cost_money: Optional[int] = 0
    earn_score: Optional[int] = 0


# Properties to receive on item creation
class ItemCreate(ItemBase):
    # admin: bool = False
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Item(ItemInDBBase):
    pass


# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    pass
