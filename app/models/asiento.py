from datetime import date
from typing import List, Optional
from sqlalchemy import ForeignKey, Date, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Asiento(Base):
    """
    Modelo que representa un asiento contable.
    Agrupa varios apuntes (partida doble).

    Attributes:
        id (int): Identificador único del asiento.
        ejercicio_id (int): ID del ejercicio fiscal al que pertenece.
        numero (int): Número secuencial del asiento dentro del ejercicio.
        fecha (date): Fecha del asiento.
        concepto (str): Descripción general del asiento.
    """
    __tablename__ = "asientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    ejercicio_id: Mapped[int] = mapped_column(ForeignKey("ejercicios_fiscales.id"), index=True)
    tercero_id: Mapped[Optional[int]] = mapped_column(ForeignKey("terceros.id"), nullable=True, index=True)
    numero: Mapped[int] = mapped_column(Integer, index=True)
    fecha: Mapped[date] = mapped_column(Date, index=True)
    concepto: Mapped[str] = mapped_column(String(255))

    # Relaciones
    ejercicio: Mapped["EjercicioFiscal"] = relationship(back_populates="asientos")
    tercero: Mapped[Optional["Tercero"]] = relationship()
    apuntes: Mapped[List["ApunteContable"]] = relationship(
        back_populates="asiento", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Asiento(numero={self.numero}, fecha='{self.fecha}', concepto='{self.concepto[:20]}...')>"
