from datetime import date
from typing import List
from sqlalchemy import ForeignKey, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class EjercicioFiscal(Base):
    """
    Modelo que representa un ejercicio fiscal (año contable).

    Attributes:
        id (int): Identificador único del ejercicio.
        empresa_id (int): ID de la empresa a la que pertenece.
        fecha_inicio (date): Fecha de inicio del ejercicio.
        fecha_fin (date): Fecha de fin del ejercicio.
        estado (bool): Estado del ejercicio (True=Abierto, False=Cerrado).
    """
    __tablename__ = "ejercicios_fiscales"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), index=True)
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    estado: Mapped[bool] = mapped_column(Boolean, default=True, comment="True=Abierto, False=Cerrado")

    # Relaciones
    empresa: Mapped["Empresa"] = relationship(back_populates="ejercicios")
    asientos: Mapped[List["Asiento"]] = relationship(
        back_populates="ejercicio", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<EjercicioFiscal(id={self.id}, inicio='{self.fecha_inicio}', estado={'Abierto' if self.estado else 'Cerrado'})>"
