from decimal import Decimal
from typing import Optional
from sqlalchemy import ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.database import Base

class ApunteContable(Base):
    """
    Modelo que representa un apunte contable (una línea del asiento).

    Attributes:
        id (int): Identificador único del apunte.
        asiento_id (int): ID del asiento al que pertenece.
        cuenta_id (int): ID de la cuenta contable asociada.
        descripcion (str): Descripción del apunte.
        debe (Decimal): Importe al Debe.
        haber (Decimal): Importe al Haber.
    """
    __tablename__ = "apuntes_contables"

    id: Mapped[int] = mapped_column(primary_key=True)
    asiento_id: Mapped[int] = mapped_column(ForeignKey("asientos.id"), index=True)
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas_contables.id"), index=True)
    descripcion: Mapped[str] = mapped_column(String(255))
    debe: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    haber: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Relaciones
    asiento: Mapped["Asiento"] = relationship(back_populates="apuntes")
    cuenta: Mapped["CuentaContable"] = relationship(back_populates="apuntes")

    @validates("debe", "haber")
    def validate_importe(self, key: str, value: Any) -> Decimal:
        """
        Valida que el importe no sea nulo. 
        SQLAlchemy convierte None a NULL en la DB, pero aquí forzamos que sea un valor numérico (o 0).
        """
        if value is None:
            raise ValueError(f"El campo '{key}' no puede ser nulo.")
        return value

    def __repr__(self) -> str:
        return f"<ApunteContable(cuenta_id={self.cuenta_id}, debe={self.debe}, haber={self.haber})>"
