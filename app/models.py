from sqlmodel import Field, SQLModel
from pydantic import BaseModel
from enum import Enum
from typing import Optional

class EstadoRuleta(str, Enum):
    INICIAL = "inicial"
    CERRADA = "cerrada"
    ABIERTA = "abierta"

class EstadoApuesta(str, Enum):
    PENDIENTE = "pendiente"
    GANADA = "ganada"
    PERDIDA = "perdida"


class TipoApuesta(str, Enum):
    NUMERO = "numero"
    COLOR = "color"

class ColorApuesta(str, Enum):
    ROJO = "rojo"
    NEGRO = "negro"

class Usuario(SQLModel, table=True):
    id: int = Field(primary_key=True)

class Ruleta(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    estado: EstadoRuleta = Field(default=EstadoRuleta.INICIAL)
    numero_ganador: Optional[int] = Field(default=0, nullable=True, ge=0, le=36)
    color_ganador: Optional[ColorApuesta] = Field(default=ColorApuesta.ROJO, nullable=True)

class Apuesta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    ruleta_id: int = Field(foreign_key="ruleta.id")
    tipo_apuesta: TipoApuesta
    numero_apostado: Optional[int] = Field(default=None, nullable=True)
    color_apostado: Optional[ColorApuesta] = Field(default=ColorApuesta.ROJO, nullable=True)
    monto: float = Field(ge=1, le=10000)
    estado: Optional[EstadoApuesta] = Field(default=EstadoApuesta.PENDIENTE, nullable=True)
    ganancia: float = Field(default=0.0)

class CrearApuesta(BaseModel):
    ruleta_id:int
    tipo_apuesta: Optional[TipoApuesta]
    numero_apostado:Optional[int]
    color_apostado:Optional[ColorApuesta]
    monto:float

    