from fastapi import FastAPI
from item import router as item_router
from user import router as user_router

app = FastAPI()

@app.get('/')
async def root():
  return {"message": "Hello World"}

app.include_router(item_router)
app.include_router(user_router)