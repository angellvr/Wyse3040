"""Objeto compartido que reciben todos los módulos."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

import anthropic

from .config import Config
from .db import DB


@dataclass
class Contexto:
    cfg: Config
    db: DB
    claude: anthropic.AsyncAnthropic
    # Envía un aviso por Telegram a los usuarios autorizados (lo rellena bot.py)
    notificar: Callable[[str], Awaitable[None]] | None = None
    # Servicios que unos módulos ofrecen a otros (p. ej. "drive")
    servicios: dict[str, Any] = field(default_factory=dict)

    async def llamar_claude(self, modelo: str, **kwargs):
        """Llamada a la API con fallback del lado del servidor y registro de uso."""
        extra = {}
        if not modelo.startswith("claude-haiku"):
            # Si un clasificador de seguridad rechaza una petición legítima,
            # la API la reintenta con el modelo recomendado.
            extra = {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}
        respuesta = await self.claude.beta.messages.create(model=modelo, **extra, **kwargs)
        self.db.registrar_uso(modelo, respuesta.usage)
        return respuesta
