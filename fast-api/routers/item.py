from fastapi import APIRouter, Query, HTTPException
from enum import Enum
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix='/items', tags=['items'])

class ModelName(str, Enum):
  alexnet = "alexnet"
  lcnet = "lcnet"
  resnet = "resnet"

class Item(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
  tax: Optional[float] = None

# @router.get('/{item_id}')
# async def read_item(item_id):
#   return {"item_id": item_id}

@router.get('/models/{model_name}')
async def get_model(model_name: ModelName, nickname: Optional[str] = None):
  return {"model_name": model_name, "nickname": nickname}

@router.get('/')
async def read_items(skip: int = 0, limit: int = 10):
  return {"skip": skip, "limit": limit}

@router.get('/search')
async def search_items(keyword: str = Query(default=None), skip: int = 0, limit: int = 10):
  if keyword is None:
    raise HTTPException(status_code=400, detail="Keyword is required")

  return {"keyword": keyword, "skip": skip, "limit": limit}

@router.post('/create_item/')
async def create_item(item: Item):
  return item