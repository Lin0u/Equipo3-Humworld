from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator


class TerminoDiccionarioCrear(BaseModel):
    palabra: str = Field(min_length=1)
    idioma: Literal["es", "en"]
    valor: StrictInt = Field(ge=-10, le=10)

    @field_validator("palabra")
    @classmethod
    def validar_palabra_no_vacia(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("La palabra no puede estar vacía.")
        return value


class TerminoDiccionarioActualizar(TerminoDiccionarioCrear):
    model_config = ConfigDict(extra="forbid")


class TerminoDiccionarioActualizarParcial(BaseModel):
    palabra: str | None = Field(default=None, min_length=1)
    idioma: Literal["es", "en"] | None = None
    valor: StrictInt | None = Field(default=None, ge=-10, le=10)

    model_config = ConfigDict(extra="forbid")

    @field_validator("palabra")
    @classmethod
    def validar_palabra_no_vacia(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("La palabra no puede estar vacía.")
        return value

    @model_validator(mode="after")
    def validar_campos_presentes(self):
        if not self.model_fields_set:
            raise ValueError("PATCH debe incluir al menos un campo modificable.")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Los campos de PATCH no pueden ser nulos.")
        return self


class TerminoDiccionario(BaseModel):
    id: int
    palabra: str
    idioma: Literal["es", "en"]
    valor: int

    model_config = ConfigDict(from_attributes=True)