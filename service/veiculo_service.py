from database import Veiculo, SessionLocal
from datetime import datetime
from escpos.printer import Usb

# Substitua pelos IDs da sua Bematech 4200
VENDOR_ID = 0x0FE6
PRODUCT_ID = 0x811E

def listar_ativos(db):
    return db.query(Veiculo).filter(Veiculo.saida == None).all()

def listar_historico(db):
    return db.query(Veiculo).all()

def registrar_entrada(db, placa, modelo):
    veiculo = Veiculo(placa=placa, modelo=modelo)
    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)
    imprimir_ticket_entrada(placa, modelo)
    return veiculo

def registrar_saida(db, veiculo_id):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if veiculo:
        veiculo.saida = datetime.now()
        db.commit()
        db.refresh(veiculo)
        imprimir_ticket_saida(veiculo.placa, veiculo.modelo, veiculo.entrada, veiculo.saida)
    return veiculo

# Impressão de entrada
def imprimir_ticket_entrada(placa, modelo):
    try:
        p = Usb(VENDOR_ID, PRODUCT_ID)
        p.text("🚗 Word Parking\n")
        p.text("TICKET DE ENTRADA\n")
        p.text(f"Placa: {placa}\n")
        p.text(f"Modelo: {modelo}\n")
        p.text(f"Entrada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        p.text("-------------------------\n")
        p.text("Obrigado!\n")
        p.cut()
    except Exception as e:
        print("Erro ao imprimir entrada:", e)

# Impressão de saída
def imprimir_ticket_saida(placa, modelo, entrada, saida):
    try:
        p = Usb(VENDOR_ID, PRODUCT_ID)
        p.text("🚗 Word Parking\n")
        p.text("TICKET DE SAÍDA\n")
        p.text(f"Placa: {placa}\n")
        p.text(f"Modelo: {modelo}\n")
        p.text(f"Entrada: {entrada.strftime('%d/%m/%Y %H:%M:%S')}\n")
        p.text(f"Saída: {saida.strftime('%d/%m/%Y %H:%M:%S')}\n")
        p.text("-------------------------\n")
        p.text("Obrigado!\n")
        p.cut()
    except Exception as e:
        print("Erro ao imprimir saída:", e)
