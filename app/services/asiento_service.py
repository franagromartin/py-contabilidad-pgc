from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.asiento import Asiento
from app.models.apunte import ApunteContable
from app.models.cuenta import CuentaContable
from app.models.ejercicio import EjercicioFiscal
from app.schemas.asiento import AsientoCreate, FacturaCreate, ApunteCreate
from app.exceptions import (
    AsientoDescuadradoError, 
    CuentaNoEncontradaError,
    EjercicioNoEncontradoError
)

class AsientoService:
    def __init__(self, db: Session):
        self.db = db

    def crear_asiento(self, datos: AsientoCreate) -> Asiento:
        """
        Crea un nuevo asiento contable asegurando que esté cuadrado,
        que las cuentas existan y asignando el número correlativo correspondiente.
        """
        # 1. Validar cuadre (Debe == Haber)
        total_debe = sum(apunte.debe for apunte in datos.apuntes)
        total_haber = sum(apunte.haber for apunte in datos.apuntes)
        
        # Usamos diferencia absoluta menor a un epsilon muy pequeño para "igualdad"
        # aunque con Decimal debería ser exacto.
        if total_debe != total_haber:
            diferencia = total_debe - total_haber
            raise AsientoDescuadradoError(diferencia)

        # 2. Verificar existencia de cuentas y obtener IDs
        cuenta_map = {}
        for apunte_schema in datos.apuntes:
            if apunte_schema.cuenta_codigo not in cuenta_map:
                cuenta = self.db.execute(
                    select(CuentaContable).where(CuentaContable.codigo == apunte_schema.cuenta_codigo)
                ).scalar_one_or_none()
                
                if not cuenta:
                    raise CuentaNoEncontradaError(apunte_schema.cuenta_codigo)
                cuenta_map[apunte_schema.cuenta_codigo] = cuenta.id

        # 3. Validar ejercicio fiscal (si no se proporciona ID, buscar por fecha)
        if not datos.ejercicio_id:
             # Buscar ejercicio abierto que contenga la fecha
             ejercicio = self.db.execute(
                 select(EjercicioFiscal).where(
                     EjercicioFiscal.fecha_inicio <= datos.fecha,
                     EjercicioFiscal.fecha_fin >= datos.fecha,
                     # EjercicioFiscal.estado == True # Opcional: solo permitir en abiertos
                 )
             ).scalar_one_or_none()
             if not ejercicio:
                 raise EjercicioNoEncontradoError(f"No existe ejercicio fiscal para la fecha {datos.fecha}")
             ejercicio_id = ejercicio.id
        else:
            ejercicio_id = datos.ejercicio_id

        # 4. Obtener siguiente número de asiento
        ultimo_numero = self.db.execute(
            select(func.max(Asiento.numero)).where(Asiento.ejercicio_id == ejercicio_id)
        ).scalar() or 0
        nuevo_numero = ultimo_numero + 1

        # 5. Crear Asiento y Apuntes
        nuevo_asiento = Asiento(
            ejercicio_id=ejercicio_id,
            numero=nuevo_numero,
            fecha=datos.fecha,
            concepto=datos.concepto
        )
        self.db.add(nuevo_asiento)
        self.db.flush() # Para obtener nuevo_asiento.id

        for apunte_schema in datos.apuntes:
            # Forzar validación adicional de valores positivos si se requiere 
            # (ya cubierto por pydantic ge=0, pero Decimal permite negativos)
            # Aquí asumimos que pydantic ya filtró los negativos.
            
            apunte = ApunteContable(
                asiento_id=nuevo_asiento.id,
                cuenta_id=cuenta_map[apunte_schema.cuenta_codigo],
                descripcion=apunte_schema.descripcion,
                debe=apunte_schema.debe,
                haber=apunte_schema.haber
            )
            self.db.add(apunte)

        self.db.commit()
        self.db.refresh(nuevo_asiento)
        return nuevo_asiento

    def crear_asiento_factura(self, datos: FacturaCreate) -> Asiento:
        """
        Genera automáticamente un asiento de factura con cálculo de IVA.
        """
        # 1. Validar Tipo de IVA
        if datos.tipo_iva not in [4, 10, 21]:
            raise ValueError(f"Tipo de IVA no válido: {datos.tipo_iva}. Debe ser 4, 10 o 21.")

        # 2. Cálculos (Todo en Decimal)
        # cuota = base * (tipo / 100)
        tipo_decimal = Decimal(datos.tipo_iva) / Decimal(100)
        cuota_iva = (datos.base_imponible * tipo_decimal).quantize(Decimal("0.01"))
        total_factura = datos.base_imponible + cuota_iva

        # 3. Determinar Cuentas de IVA (Simplificado para el Hito)
        # Si es gasto (compra), el IVA es Soportado (472) y va al DEBE.
        # Si es ingreso (venta), el IVA es Repercutido (477) y va al HABER.
        codigo_iva = "472" if datos.es_gasto else "477"
        
        # 4. Construir Apuntes
        apuntes = []

        if datos.es_gasto:
            # Factura Recibida (Compra)
            # Debe: Gasto + IVA
            # Haber: Proveedor (Total)
            apuntes.append(ApunteCreate(
                cuenta_codigo=datos.cuenta_ingreso_gasto,
                descripcion=f"Base {datos.concepto}",
                debe=datos.base_imponible,
                haber=Decimal(0)
            ))
            apuntes.append(ApunteCreate(
                cuenta_codigo=codigo_iva,
                descripcion=f"IVA {datos.tipo_iva}% {datos.concepto}",
                debe=cuota_iva,
                haber=Decimal(0)
            ))
            apuntes.append(ApunteCreate(
                cuenta_codigo=datos.cuenta_tercero,
                descripcion=f"Total {datos.concepto}",
                debe=Decimal(0),
                haber=total_factura
            ))
        else:
            # Factura Emitida (Venta)
            # Debe: Cliente (Total)
            # Haber: Ingreso + IVA
            apuntes.append(ApunteCreate(
                cuenta_codigo=datos.cuenta_tercero,
                descripcion=f"Total {datos.concepto}",
                debe=total_factura,
                haber=Decimal(0)
            ))
            apuntes.append(ApunteCreate(
                cuenta_codigo=datos.cuenta_ingreso_gasto,
                descripcion=f"Base {datos.concepto}",
                debe=Decimal(0),
                haber=datos.base_imponible
            ))
            apuntes.append(ApunteCreate(
                cuenta_codigo=codigo_iva,
                descripcion=f"IVA {datos.tipo_iva}% {datos.concepto}",
                debe=Decimal(0),
                haber=cuota_iva
            ))

        # 5. Delegar en crear_asiento para validación final y persistencia
        asiento_create = AsientoCreate(
            fecha=datos.fecha,
            concepto=datos.concepto,
            ejercicio_id=datos.ejercicio_id,
            apuntes=apuntes
        )
        
        nuevo_asiento = self.crear_asiento(asiento_create)
        
        # 6. Vincular Tercero
        # Esto requiere hacer un update posterior o modificar crear_asiento para aceptar tercero_id.
        # Modificaremos el objeto retornado y haremos commit.
        nuevo_asiento.tercero_id = datos.tercero_id
        self.db.add(nuevo_asiento)
        self.db.commit()
        self.db.refresh(nuevo_asiento)
        
        return nuevo_asiento
