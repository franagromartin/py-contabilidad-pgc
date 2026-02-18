from datetime import date
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, Field

class ApunteCreate(BaseModel):
    """Schema for creating a new Apunte."""
    cuenta_codigo: str = Field(..., description="Código de la cuenta contable")
    debe: Decimal = Field(default=Decimal("0.0"), ge=0, decimal_places=2)
    haber: Decimal = Field(default=Decimal("0.0"), ge=0, decimal_places=2)
    descripcion: str = Field(..., max_length=255)

class AsientoCreate(BaseModel):
    """Schema for creating a new Asiento with its Apuntes."""
    fecha: date
    concepto: str = Field(..., max_length=255)
    ejercicio_id: int # Optionally passed, or could be inferred from date
    apuntes: List[ApunteCreate]

    model_config = ConfigDict(from_attributes=True)

class FacturaCreate(BaseModel):
    """Schema para crear un asiento de factura automáticamente."""
    fecha: date
    concepto: str = Field(..., max_length=255)
    ejercicio_id: int
    tercero_id: int
    base_imponible: Decimal = Field(..., gt=0, decimal_places=2)
    tipo_iva: int = Field(..., description="Tipo de IVA (4, 10, 21)")
    cuenta_ingreso_gasto: str = Field(..., description="Código de la cuenta de ingreso o gasto (ej. 700, 600)")
    # El sistema deducirá las cuentas de IVA y Tercero basándose en configuración o parámetros, 
    # por ahora asumiremos cuentas estándar o pasadas explícitamente si se complica.
    # Simplificación: Asumimos IVA Soportado (472) para gastos y Repercutido (477) para ingresos, 
    # pero para este hito el prompt pide "Cuota de IVA (472/477)".
    # Vamos a pedir la cuenta de IVA explícita o deducirla.
    # Para cumplir "Automáticamente los tres apuntes", pediremos cuenta tercero y cuenta base.
    cuenta_tercero: str = Field(..., description="Código de la cuenta del tercero (ej. 430, 400)")
    es_gasto: bool = Field(default=True, description="True=Factura Recibida (Gasto), False=Factura Emitida (Ingreso)")
