from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# html 템플릿
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
  # 템플릿 렌더링
  return templates.TemplateResponse("./index.html", { "request": request, "title":"콜렉터 북북이" })

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
  return templates.TemplateResponse("./index.html", { "request": request, "title":"콜렉터 북북이", "keyword": q })