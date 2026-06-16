from typing import Optional
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
  return {"Hello": "World"}

@app.get('/hello')
def read_fastapi_hello():
  return {"Hello": "Fast API"}

@app.get("/items/{item_id}/{item_name}")
def read_item(item_id: int, item_name: str, q: Optional[str] = None):
  return {"item_id": item_id, "item_name": item_name, "q": q}

@app.get("/item-name/{item_name}")
def read_item_name(item_name: str):
  return {"item_name": item_name}