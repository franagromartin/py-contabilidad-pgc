import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import date

from app.database import Base
from app.models.empresa import Empresa
from app.models.ejercicio import EjercicioFiscal
from app.models.cuenta import CuentaContable

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    return create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    """Returns a sqlalchemy session, rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def empresa_test(db_session: Session):
    empresa = Empresa(
        cif="B12345678", 
        nombre="Empresa Test S.L.",
        direccion="Calle Test 123"
    )
    db_session.add(empresa)
    db_session.commit()
    db_session.refresh(empresa)
    return empresa

@pytest.fixture
def ejercicio_test(db_session: Session, empresa_test: Empresa):
    ejercicio = EjercicioFiscal(
        empresa_id=empresa_test.id,
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2024, 12, 31),
        estado=True
    )
    db_session.add(ejercicio)
    db_session.commit()
    db_session.refresh(ejercicio)
    return ejercicio

@pytest.fixture
def cuentas_test(db_session: Session):
    # Crear algunas cuentas básicas
    cuentas = [
        CuentaContable(codigo="572", descripcion="Bancos"),
        CuentaContable(codigo="100", descripcion="Capital Social"),
        CuentaContable(codigo="430", descripcion="Clientes"),
        CuentaContable(codigo="400", descripcion="Proveedores"),
        CuentaContable(codigo="700", descripcion="Ventas"),
        CuentaContable(codigo="600", descripcion="Compras"),
        CuentaContable(codigo="472", descripcion="H.P. IVA Soportado"),
        CuentaContable(codigo="477", descripcion="H.P. IVA Repercutido"),
    ]
    db_session.add_all(cuentas)
    db_session.commit()
    return {c.codigo: c for c in cuentas}

@pytest.fixture
def tercero_test(db_session: Session, cuentas_test):
    from app.models.tercero import Tercero
    tercero = Tercero(
        nif="A99999999", 
        nombre="Cliente Test S.A.",
        cuenta_contable_id=cuentas_test["430"].id
    )
    db_session.add(tercero)
    db_session.commit()
    db_session.refresh(tercero)
    return tercero
