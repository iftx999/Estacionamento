from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, index=True)
    modelo = Column(String)
    entrada = Column(DateTime, default=datetime.utcnow)
    saida = Column(DateTime, nullable=True)
