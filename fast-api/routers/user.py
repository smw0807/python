from fastapi import APIRouter

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/{user_id}')
async def read_user(user_id):
  return {"user_id": user_id}