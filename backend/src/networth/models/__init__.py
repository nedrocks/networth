from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    id: int
    name: str
    description: str
    status: str

class ItemList(BaseModel):
    items: List[Item]