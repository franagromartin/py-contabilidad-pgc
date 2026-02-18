import pytest
from decimal import Decimal
from datetime import date
from datetime import date
from app.services.asiento_service import AsientoService
from app.schemas.asiento import AsientoCreate, ApunteCreate, FacturaCreate
from app.exceptions import AsientoDescuadradoError, CuentaNoEncontradaError

def test_crear_asiento_correcto(db_session, ejercicio_test, cuentas_test):
    """
    Prueba la creación de un asiento cuadrado correctamente.
    Caso: Bancos (572) a Capital Social (100) por 3000.00€
    """
    service = AsientoService(db_session)

    datos_asiento = AsientoCreate(
        fecha=date(2024, 1, 15),
        concepto="Constitución de la empresa",
        ejercicio_id=ejercicio_test.id,
        apuntes=[
            ApunteCreate(
                cuenta_codigo="572", 
                descripcion="Aportación inicial", 
                debe=Decimal("3000.00"), 
                haber=Decimal("0.00")
            ),
            ApunteCreate(
                cuenta_codigo="100", 
                descripcion="Capital Social", 
                debe=Decimal("0.00"), 
                haber=Decimal("3000.00")
            ),
        ]
    )

    asiento = service.crear_asiento(datos_asiento)

    assert asiento.id is not None
    assert asiento.numero == 1
    assert len(asiento.apuntes) == 2
    assert asiento.apuntes[0].debe == Decimal("3000.00")
    assert asiento.apuntes[1].haber == Decimal("3000.00")

def test_crear_asiento_descuadrado(db_session, ejercicio_test, cuentas_test):
    """
    Prueba que el sistema rechaza un asiento descuadrado.
    Caso: Descuadre de 0.01€
    """
    service = AsientoService(db_session)

    datos_asiento = AsientoCreate(
        fecha=date(2024, 1, 16),
        concepto="Asiento erróneo",
        ejercicio_id=ejercicio_test.id,
        apuntes=[
            ApunteCreate(
                cuenta_codigo="572", 
                descripcion="Cobro parcial", 
                debe=Decimal("100.01"), 
                haber=Decimal("0.00")
            ),
            ApunteCreate(
                cuenta_codigo="430", 
                descripcion="Pago cliente", 
                debe=Decimal("0.00"), 
                haber=Decimal("100.00")
            ),
        ]
    )

    with pytest.raises(AsientoDescuadradoError) as excinfo:
        service.crear_asiento(datos_asiento)
    
    # Verificar mensaje de error aproximado
    assert "descuadrado" in str(excinfo.value)

def test_cuenta_inexistente(db_session, ejercicio_test):
    """
    Prueba que falla si la cuenta no existe.
    """
    service = AsientoService(db_session)
    datos_asiento = AsientoCreate(
        fecha=date(2024, 1, 16),
        concepto="Cuenta fake",
        ejercicio_id=ejercicio_test.id,
        apuntes=[
            ApunteCreate(cuenta_codigo="9999", descripcion="Fake", debe=10, haber=0),
            ApunteCreate(cuenta_codigo="9999", descripcion="Fake", debe=0, haber=10)
        ]
    )
    with pytest.raises(Exception): # Puede ser CuentaNoEncontradaError o error de DB
         service.crear_asiento(datos_asiento)

def test_crear_asiento_factura_iva_21(db_session, ejercicio_test, cuentas_test, tercero_test):
    """
    Prueba la creación automática de un asiento de factura con IVA 21%.
    Caso: Venta de 100€ + 21€ IVA = 121€ Total.
    """
    service = AsientoService(db_session)
    
    datos_factura = FacturaCreate(
        fecha=date(2024, 2, 1),
        concepto="Factura Venta Nº 1",
        ejercicio_id=ejercicio_test.id,
        tercero_id=tercero_test.id,
        base_imponible=Decimal("100.00"),
        tipo_iva=21,
        cuenta_ingreso_gasto="700", # Ventas
        cuenta_tercero="430",       # Clientes
        es_gasto=False              # Es Ingreso (Venta)
    )

    asiento = service.crear_asiento_factura(datos_factura)

    # Verificaciones
    assert asiento.id is not None
    assert asiento.tercero_id == tercero_test.id
    assert len(asiento.apuntes) == 3
    
    # Buscar apuntes por cuenta
    apunte_cliente = next(a for a in asiento.apuntes if a.cuenta.codigo == "430")
    apunte_ingreso = next(a for a in asiento.apuntes if a.cuenta.codigo == "700")
    apunte_iva = next(a for a in asiento.apuntes if a.cuenta.codigo == "477")

    # Verificar importes (Venta: Cliente al Debe, Ingreso/IVA al Haber)
    assert apunte_cliente.debe == Decimal("121.00")
    assert apunte_ingreso.haber == Decimal("100.00")
    assert apunte_iva.haber == Decimal("21.00")
    
    # Verificar cuadre
    total_debe = sum(a.debe for a in asiento.apuntes)
    total_haber = sum(a.haber for a in asiento.apuntes)
    assert total_debe == total_haber == Decimal("121.00")
