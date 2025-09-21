import threading
import webbrowser
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn

from database import Base, engine, SessionLocal
from service import veiculo_service

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    ativos = veiculo_service.listar_ativos(db)
    historico = veiculo_service.listar_historico(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ativos": ativos,
        "historico": historico
    })

@app.post("/entrada", response_class=HTMLResponse)
def entrada(placa: str = Form(...), modelo: str = Form(...), request: Request = None, db: Session = Depends(get_db)):
    veiculo_service.registrar_entrada(db, placa, modelo)
    ativos = veiculo_service.listar_ativos(db)
    historico = veiculo_service.listar_historico(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ativos": ativos,
        "historico": historico
    })

@app.post("/saida/{veiculo_id}", response_class=HTMLResponse)
def saida(veiculo_id: int, request: Request = None, db: Session = Depends(get_db)):
    veiculo_service.registrar_saida(db, veiculo_id)
    ativos = veiculo_service.listar_ativos(db)
    historico = veiculo_service.listar_historico(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ativos": ativos,
        "historico": historico
    })

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
