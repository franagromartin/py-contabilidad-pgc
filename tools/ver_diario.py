import sys
import os
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.asiento import Asiento
from app.models.apunte import ApunteContable
from app.models.cuenta import CuentaContable

def ver_diario():
    db = SessionLocal()
    try:
        print("\n=== LIBRO DIARIO ===\n")
        asientos = db.query(Asiento).order_by(Asiento.fecha, Asiento.numero).all()
        
        # Header
        print(f"{'FECHA':<12} {'Nº':<5} {'CUENTA':<12} {'DESCRIPCIÓN':<45} {'DEBE':>12} {'HABER':>12}")
        print("=" * 105)
        
        for asiento in asientos:
            first_line = True
            for apunte in asiento.apuntes:
                fecha_str = str(asiento.fecha) if first_line else ""
                numero_str = str(asiento.numero) if first_line else ""
                cuenta_cod = apunte.cuenta.codigo if apunte.cuenta else "???"
                desc_cortada = (apunte.descripcion[:42] + '..') if len(apunte.descripcion) > 42 else apunte.descripcion
                
                print(f"{fecha_str:<12} {numero_str:<5} {cuenta_cod:<12} {desc_cortada:<45} {apunte.debe:>12.2f} {apunte.haber:>12.2f}")
                first_line = False
            print("-" * 105)

        # Saldos
        print("\n=== SALDOS ESPECÍFICOS ===\n")
        cuentas_interes = ['477', '430']
        
        for codigo_busqueda in cuentas_interes:
            # Buscar cuentas que empiecen por el código (para incluir subcuentas como 430.0)
            cuentas = db.query(CuentaContable).filter(CuentaContable.codigo.like(f"{codigo_busqueda}%")).all()
            
            if not cuentas:
                print(f"No se encontraron cuentas para el código base '{codigo_busqueda}'")
                continue
                
            for cuenta in cuentas:
                apuntes = db.query(ApunteContable).filter_by(cuenta_id=cuenta.id).all()
                total_debe = sum(a.debe for a in apuntes)
                total_haber = sum(a.haber for a in apuntes)
                saldo = total_debe - total_haber
                
                print(f"Cuenta {cuenta.codigo} - {cuenta.descripcion}")
                print(f"  Debe: {total_debe:>10.2f} €")
                print(f"  Haber:{total_haber:>10.2f} €")
                print(f"  Saldo:{saldo:>10.2f} € (Deudor)" if saldo >= 0 else f"  Saldo:{abs(saldo):>10.2f} € (Acreedor)")
                print("-" * 40)

    except Exception as e:
        print(f"Error consultando diario: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ver_diario()
