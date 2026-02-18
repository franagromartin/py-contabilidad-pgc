from typing import List, Optional, Any
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Empresa(Base):
    """
    Modelo que representa una empresa en el sistema contable.
    
    Attributes:
        id (int): Identificador único de la empresa.
        cif (str): Código de Identificación Fiscal (CIF/NIF).
        nombre (str): Razón social o nombre de la empresa.
        direccion (str): Dirección fiscal.
        configuracion (dict): Configuración específica de la empresa (JSON).
    """
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True)
    cif: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    direccion: Mapped[Optional[str]] = mapped_column(String(500))
    configuracion: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)

    # Relaciones
    ejercicios: Mapped[List["EjercicioFiscal"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Empresa(id={self.id}, nombre='{self.nombre}', cif='{self.cif}')>"
