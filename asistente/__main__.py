"""Arranque: python -m asistente"""
from __future__ import annotations

import logging
from datetime import time as hora
from logging.handlers import RotatingFileHandler
from zoneinfo import ZoneInfo

import anthropic

from . import config
from .agent import Agente
from .bot import crear_app
from .contexto import Contexto
from .db import DB
from .modules import MODULOS, correo
from .tools import Registro

RESUMEN_DIARIO = (
    "Prepárame el resumen de la mañana: correos importantes y facturas recibidas en las "
    "últimas 24 h, cobros de Stripe de ayer y facturas de cliente vencidas sin cobrar en Odoo. "
    "Sé breve; si algún sistema no está disponible, sáltalo."
)


def main() -> None:
    cfg = config.cargar()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(),
                  RotatingFileHandler(cfg.datos / "asistente.log", maxBytes=2_000_000, backupCount=3)],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    log = logging.getLogger("asistente")

    if not cfg.telegram_token or not cfg.telegram_usuarios:
        raise SystemExit("Faltan TELEGRAM_TOKEN o TELEGRAM_USUARIOS_PERMITIDOS en .env")

    ctx = Contexto(cfg=cfg, db=DB(cfg.datos / "asistente.db"), claude=anthropic.AsyncAnthropic())
    registro = Registro()
    for modulo in MODULOS:
        nombre = modulo.__name__.rsplit(".", 1)[-1]
        try:
            tools = modulo.cargar(ctx)
            registro.añadir(tools)
            log.info("Módulo %s: %d herramientas", nombre, len(tools))
        except Exception:
            # Un módulo mal configurado no debe tumbar el resto
            log.exception("No se pudo cargar el módulo %s", nombre)

    agente = Agente(ctx, registro)
    app = crear_app(ctx, agente, registro)
    zona = ZoneInfo(cfg.zona_horaria)

    if cfg.cuentas:
        async def tarea_correo(_):
            log.info(await correo.revisar(ctx))
        app.job_queue.run_repeating(tarea_correo, interval=cfg.intervalo_correo_min * 60, first=30)

    if cfg.hora_resumen_diario:
        h, m = map(int, cfg.hora_resumen_diario.split(":"))

        async def tarea_resumen(_):
            # Conversación aparte (id 0) para no mezclarla con el chat del usuario
            agente.reiniciar(0)
            await ctx.notificar("☀️ " + await agente.responder(0, RESUMEN_DIARIO))

        app.job_queue.run_daily(tarea_resumen, time=hora(h, m, tzinfo=zona), days=(1, 2, 3, 4, 5))

    log.info("Asistente arrancado con %d herramientas", len(registro.nombres()))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
