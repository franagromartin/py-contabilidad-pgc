import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.cuenta import CuentaContable

def seed_pgc():
    """Inserta los grupos principales del PGC 2007 (1-7)."""
    db = SessionLocal()
    try:
        grupos = [
            {"codigo": "1", "descripcion": "FINANCIACIÓN BÁSICA"},
            {"codigo": "2", "descripcion": "ACTIVO NO CORRIENTE"},
            {"codigo": "3", "descripcion": "EXISTENCIAS"},
            {"codigo": "4", "descripcion": "ACREEDORES Y DEUDORES POR OPERACIONES COMERCIALES"},
            {"codigo": "5", "descripcion": "CUENTAS FINANCIERAS"},
            {"codigo": "6", "descripcion": "COMPRAS Y GASTOS"},
            {"codigo": "7", "descripcion": "VENTAS E INGRESOS"},
        ]

        print("Iniciando carga del PGC 2007 (Grupos 1-7)...")
        
        count = 0
        for data in grupos:
            exists = db.query(CuentaContable).filter_by(codigo=data["codigo"]).first()
            if not exists:
                grupo = CuentaContable(
                    codigo=data["codigo"], 
                    descripcion=data["descripcion"],
                    parent_id=None
                )
                db.add(grupo)
                count += 1
                print(f" + Insertado: {data['codigo']} - {data['descripcion']}")
            else:
                print(f" . Saltado (ya existe): {data['codigo']}")
        
        db.commit()
        print(f"\nCarga completada. {count} grupos insertados.")

    except Exception as e:
        print(f"Error durante el seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_pgc()
