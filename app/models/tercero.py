from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Tercero(Base):
    """
    Modelo que representa a un Tercero (Cliente, Proveedor, Acreedor, etc.).

    Attributes:
        id (int): Identificador único.
        nif (str): NIF/CIF del tercero. Único.
        nombre (str): Nombre o Razón Social.
        cuenta_contable_id (int): ID de la cuenta contable asociada (ej. 430xxxx, 400xxxx).
    """
    __tablename__ = "terceros"

    id: Mapped[int] = mapped_column(primary_key=True)
    nif: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    cuenta_contable_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cuentas_contables.id"))

    # Relaciones
    cuenta_contable: Mapped[Optional["CuentaContable"]] = relationship()
    # Relación inversa desde Asiento se definirá en asiento.py si es necesaria bidireccionalidad,
    # o simplemente 'asientos' back_populates si se añade allí.

    def __repr__(self) -> str:
        return f"<Tercero(nif='{self.nif}', nombre='{self.nombre}')>"
