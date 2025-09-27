import threading
import webbrowser
from typing import Optional

from fastapi import FastAPI, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Veiculo
from service import veiculo_service
# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependência do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota principal com filtro seguro

@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    placa: Optional[str] = Query(None),
    id_str: Optional[str] = Query(None),
    page: int = Query(1, ge=1),            # página atual
    per_page: int = Query(10, ge=1, le=100), # registros por página
    db: Session = Depends(get_db)
):
    query = db.query(Veiculo).filter(Veiculo.saida == None)

    if placa:
        query = query.filter(Veiculo.placa.ilike(f"%{placa}%"))

    if id_str and id_str.isdigit():
        query = query.filter(Veiculo.id == int(id_str))

    total = query.count()  # total de registros

    # aplica paginação
    ativos = query.offset((page - 1) * per_page).limit(per_page).all()

    historico = veiculo_service.listar_historico(db)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "ativos": ativos,
        "historico": historico,
        "message": None,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page  # cálculo de páginas
    })

# Registrar entrada
@app.post("/entrada", response_class=HTMLResponse)
def entrada(
    placa: str = Form(...),
    modelo: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    veiculo_service.registrar_entrada(db, placa, modelo)
    ativos = veiculo_service.listar_ativos(db)
    historico = veiculo_service.listar_historico(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ativos": ativos,
        "historico": historico
    })

# Visualizar histórico completo
@app.get("/historico", response_class=HTMLResponse)
def historico(request: Request, db: Session = Depends(get_db)):
    historico = veiculo_service.listar_historico(db)
    return templates.TemplateResponse("historico.html", {
        "request": request,
        "historico": historico
    })

# Registrar saída
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

# Abrir navegador automaticamente
def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
