from fastapi import APIRouter
from enum import Enum
from typing import Optional

router = APIRouter(prefix='/items', tags=['items'])

class ModelName(str, Enum):
  alexnet = "alexnet"
  lcnet = "lcnet"
  resnet = "resnet"

@router.get('/{item_id}')
async def read_item(item_id):
  return {"item_id": item_id}

@router.get('/models/{model_name}')
async def get_model(model_name: ModelName, nickname: Optional[str] = None):
  return {"model_name": model_name, "nickname": nickname}