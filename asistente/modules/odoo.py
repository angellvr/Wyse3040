"""Odoo: consultas de solo lectura por XML-RPC (facturas, pagos, contabilidad, contactos)."""
from __future__ import annotations

import asyncio
import logging
import xmlrpc.client

from ..contexto import Contexto
from ..tools import Tool

log = logging.getLogger(__name__)

# Modelos que el asistente puede leer. Añade aquí los que necesites.
MODELOS_PERMITIDOS = {
    "account.move": "Facturas de cliente/proveedor y asientos (move_type: out_invoice, in_invoice, out_refund, in_refund, entry)",
    "account.move.line": "Apuntes contables",
    "account.payment": "Pagos y cobros",
    "account.account": "Plan de cuentas",
    "account.journal": "Diarios",
    "account.tax": "Impuestos",
    "res.partner": "Contactos: clientes y proveedores",
    "sale.order": "Pedidos de venta y presupuestos",
    "purchase.order": "Pedidos de compra",
    "product.product": "Productos",
}
METODOS_LECTURA = {"search_read", "read_group", "search_count", "fields_get"}
MAX_REGISTROS = 200


class Odoo:
    def __init__(self, url: str, db: str, usuario: str, api_key: str) -> None:
        self.url, self.db, self.api_key = url.rstrip("/"), db, api_key
        comun = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = comun.authenticate(db, usuario, api_key, {})
        if not self.uid:
            raise RuntimeError("Autenticación en Odoo fallida")

    def ejecutar(self, modelo: str, metodo: str, args: list, kwargs: dict):
        if modelo not in MODELOS_PERMITIDOS:
            raise ValueError(f"Modelo no permitido: {modelo}")
        if metodo not in METODOS_LECTURA:
            raise ValueError(f"Método no permitido: {metodo}")
        # Un ServerProxy por llamada: no es seguro compartirlo entre hilos
        obj = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)
        return obj.execute_kw(self.db, self.uid, self.api_key, modelo, metodo, args, kwargs)


def cargar(ctx: Contexto) -> list[Tool]:
    cfg = ctx.cfg
    if not (cfg.odoo_url and cfg.odoo_db and cfg.odoo_usuario and cfg.odoo_api_key):
        log.info("Odoo desactivado (faltan ODOO_URL/ODOO_DB/ODOO_USUARIO/ODOO_API_KEY)")
        return []
    odoo = Odoo(cfg.odoo_url, cfg.odoo_db, cfg.odoo_usuario, cfg.odoo_api_key)

    async def buscar(modelo: str, dominio: list | None = None, campos: list | None = None,
                     limite: int = 50, orden: str = "") -> list:
        kwargs = {"fields": campos or [], "limit": min(limite, MAX_REGISTROS)}
        if orden:
            kwargs["order"] = orden
        return await asyncio.to_thread(odoo.ejecutar, modelo, "search_read", [dominio or []], kwargs)

    async def agrupar(modelo: str, dominio: list, campos: list, agrupar_por: list) -> list:
        return await asyncio.to_thread(
            odoo.ejecutar, modelo, "read_group", [dominio, campos, agrupar_por], {"lazy": False}
        )

    async def campos(modelo: str) -> dict:
        res = await asyncio.to_thread(odoo.ejecutar, modelo, "fields_get", [], {"attributes": ["string", "type"]})
        return {k: f"{v['string']} ({v['type']})" for k, v in res.items()}

    modelos = "\n".join(f"- {m}: {d}" for m, d in MODELOS_PERMITIDOS.items())
    p_modelo = {"type": "string", "enum": list(MODELOS_PERMITIDOS)}
    p_dominio = {"type": "array", "items": {}, "description": "Dominio Odoo, p. ej. [[\"state\",\"=\",\"posted\"],[\"invoice_date\",\">=\",\"2026-01-01\"]]"}

    return [
        Tool("odoo_buscar",
             f"Lee registros de Odoo (solo lectura). Modelos disponibles:\n{modelos}\n"
             "Indica siempre 'campos' para no traer datos de más. Usa odoo_campos si dudas del nombre de un campo.",
             {"modelo": p_modelo, "dominio": p_dominio,
              "campos": {"type": "array", "items": {"type": "string"}},
              "limite": {"type": "integer"},
              "orden": {"type": "string", "description": "p. ej. 'invoice_date desc'"}},
             buscar, obligatorios=("modelo",)),
        Tool("odoo_agrupar",
             "Totales agrupados en Odoo (read_group), ideal para facturación por mes, cliente o estado. "
             "Ejemplo campos: ['amount_total:sum'], agrupar_por: ['invoice_date:month'].",
             {"modelo": p_modelo, "dominio": p_dominio,
              "campos": {"type": "array", "items": {"type": "string"}},
              "agrupar_por": {"type": "array", "items": {"type": "string"}}},
             agrupar, obligatorios=("modelo", "dominio", "campos", "agrupar_por")),
        Tool("odoo_campos", "Lista los campos de un modelo de Odoo con su etiqueta y tipo.",
             {"modelo": p_modelo}, campos, obligatorios=("modelo",)),
    ]
