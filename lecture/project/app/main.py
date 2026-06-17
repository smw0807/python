from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
#from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()

# 미들웨어
# app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# html 템플릿
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/item/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
  # 템플릿 렌더링
  return templates.TemplateResponse("item.html", { "request": request, "id": id , "name": "songminwoo"})