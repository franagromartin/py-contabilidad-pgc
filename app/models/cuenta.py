from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class CuentaContable(Base):
    """
    Modelo que representa una cuenta contable del PGC.
    Soporta jerarquía mediante relación reflexiva (parent/children).

    Attributes:
        id (int): Identificador único de la cuenta.
        codigo (str): Código de la cuenta (ej. "430", "572"). Único.
        descripcion (str): Nombre o descripción de la cuenta.
        parent_id (int): ID de la cuenta padre (para jerarquía).
    """
    __tablename__ = "cuentas_contables"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    descripcion: Mapped[str] = mapped_column(String(200))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cuentas_contables.id"))

    # Relaciones
    parent: Mapped[Optional["CuentaContable"]] = relationship(
        "CuentaContable", 
        remote_side=[id], 
        back_populates="children"
    )
    children: Mapped[List["CuentaContable"]] = relationship(
        "CuentaContable", 
        back_populates="parent", 
        cascade="all, delete-orphan"
    )
    apuntes: Mapped[List["ApunteContable"]] = relationship(
        back_populates="cuenta"
    )

    def __repr__(self) -> str:
        return f"<CuentaContable(codigo='{self.codigo}', descripcion='{self.descripcion}')>"
