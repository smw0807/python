from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb
from app.models.book import BookModel

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# html 템플릿
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
  # 테스트 데이터 저장
  # book = BookModel(keyword="test", publisher="test", price=10000, image="test.png")
  # await mongodb.engine.save(book)

  # 템플릿 렌더링
  return templates.TemplateResponse("./index.html", { "request": request, "title":"콜렉터 북북이" })

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
  return templates.TemplateResponse("./index.html", { "request": request, "title":"콜렉터 북북이", "keyword": q })

# 이벤트 등록 - 서버 시작 시 실행
@app.on_event("startup")
def on_app_start():
  print('-------------------------------- S')
  print('서버 시작')
  mongodb.connect()
  print('-------------------------------- E')

@app.on_event("shutdown")
def on_app_shutdown():
  print('-------------------------------- S')
  print('서버 종료')
  mongodb.close()
  print('-------------------------------- E')