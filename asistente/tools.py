"""Registro de herramientas que los módulos ponen a disposición de Claude."""
from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

Manejador = Callable[..., Any | Awaitable[Any]]


@dataclass
class Tool:
    nombre: str
    descripcion: str
    parametros: dict  # JSON Schema de "properties"
    funcion: Manejador
    obligatorios: tuple[str, ...] = ()

    def definicion(self) -> dict:
        return {
            "name": self.nombre,
            "description": self.descripcion,
            "input_schema": {
                "type": "object",
                "properties": self.parametros,
                "required": list(self.obligatorios),
                "additionalProperties": False,
            },
        }

    async def ejecutar(self, entrada: dict) -> str:
        resultado = self.funcion(**entrada)
        if inspect.isawaitable(resultado):
            resultado = await resultado
        if isinstance(resultado, str):
            return resultado
        return json.dumps(resultado, ensure_ascii=False, default=str)


class Registro:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def añadir(self, tools: list[Tool]) -> None:
        for t in tools:
            self._tools[t.nombre] = t

    def definiciones(self) -> list[dict]:
        # Orden estable para no invalidar la caché de prompts
        return [self._tools[n].definicion() for n in sorted(self._tools)]

    def get(self, nombre: str) -> Tool | None:
        return self._tools.get(nombre)

    def nombres(self) -> list[str]:
        return sorted(self._tools)
