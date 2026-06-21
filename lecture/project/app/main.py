from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb
from app.models.book import BookModel
from app.book_scraper import NaverBookScraper

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
  '''
  1. 쿼리에서 검색어 추출
  (예외처리)
    - 검색어가 없다면 사용자에게 검색을 요구 return
    - 해당 검색어에 대해 수집된 데이터가 이미 DB에 존재한다면 해당 데이터를 사용자에게 보여준다. return
  2. 데이터 수집기로 해당 검색어에 대해 데이터를 수집한다.
  3. DB에 수집된 데이터를 저장한다.
    - 수집된 각각의 데이터에 대해서 DB에 들어갈 모델 인스턴스를 찍는다.
    - 각 모델 인스턴스를 DB에 저장한다.
  '''
  keyword = q

  naver_book_scraper = NaverBookScraper()
  books = await naver_book_scraper.search(keyword, 10)
  book_models = []
  for book in books:
    book_model = BookModel(
      keyword=keyword,
      publisher=book['publisher'],
      price=int(book['discount']),
      image=book['image'],
    )
    book_models.append(book_model)
    
  await mongodb.engine.save_all(book_models)


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