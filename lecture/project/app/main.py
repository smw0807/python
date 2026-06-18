from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print('BASE_DIR', BASE_DIR)

app = FastAPI()

# html 템플릿
templates_dir = BASE_DIR / "templates"
print('templates_dir', templates_dir)
templates = Jinja2Templates(directory=templates_dir)

@app.get("/item/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
  # 템플릿 렌더링
  return templates.TemplateResponse("./item.html", { "request": request, "id": id , "name": "songminwoo"})