"""CRM propio: consultas GET de solo lectura a rutas permitidas de su API REST.

Las rutas se declaran en config/cuentas.yaml, sección crm_rutas, por ejemplo:
    crm_rutas:
      clientes: "/api/clientes"          # admite ?q=...
      cliente: "/api/clientes/{id}"
      oportunidades: "/api/oportunidades"
Si tu CRM usa base de datos en vez de API, sustituye consultar() por una consulta SQL de solo lectura.
"""
from __future__ import annotations

import logging
from urllib.parse import quote

import httpx

from ..contexto import Contexto
from ..tools import Tool

log = logging.getLogger(__name__)
MAX_CARACTERES = 30_000


def cargar(ctx: Contexto) -> list[Tool]:
    cfg = ctx.cfg
    if not (cfg.crm_url and cfg.crm_rutas):
        log.info("CRM desactivado (faltan CRM_URL o crm_rutas)")
        return []
    cliente = httpx.AsyncClient(
        base_url=cfg.crm_url.rstrip("/"),
        headers={"Authorization": f"Bearer {cfg.crm_token}"} if cfg.crm_token else {},
        timeout=30,
    )

    async def consultar(recurso: str, id: str = "", parametros: dict | None = None) -> str:
        plantilla = cfg.crm_rutas.get(recurso)
        if plantilla is None:
            raise ValueError(f"Recurso no permitido: {recurso}")
        ruta = plantilla.format(id=quote(id, safe=""))
        r = await cliente.get(ruta, params=parametros or {})
        r.raise_for_status()
        return r.text[:MAX_CARACTERES]

    return [Tool(
        "crm_consultar",
        "Consulta el CRM de la empresa (solo lectura). Recursos: " + ", ".join(cfg.crm_rutas)
        + ". Usa 'id' para los recursos que lo necesitan y 'parametros' para filtros (p. ej. {\"q\": \"nombre\"}).",
        {"recurso": {"type": "string", "enum": list(cfg.crm_rutas)},
         "id": {"type": "string"},
         "parametros": {"type": "object", "additionalProperties": {"type": "string"}}},
        consultar, obligatorios=("recurso",),
    )]
