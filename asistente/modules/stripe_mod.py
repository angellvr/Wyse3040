"""Stripe: consultas de solo lectura. Usa una clave restringida (rk_...) con permisos de lectura."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from ..contexto import Contexto
from ..tools import Tool

log = logging.getLogger(__name__)

RECURSOS = {
    "charges": "Cobros",
    "payment_intents": "Intentos de pago",
    "invoices": "Facturas de Stripe",
    "customers": "Clientes",
    "subscriptions": "Suscripciones",
    "payouts": "Transferencias al banco",
    "refunds": "Reembolsos",
    "balance_transactions": "Movimientos de saldo (incluye comisiones)",
}
# Campos que se devuelven de cada objeto para no saturar el contexto
CAMPOS = ["id", "amount", "amount_paid", "amount_due", "amount_refunded", "currency", "status", "paid",
          "created", "description", "customer", "customer_email", "customer_name", "email", "name",
          "number", "fee", "net", "type", "arrival_date", "current_period_end", "hosted_invoice_url"]


def _epoch(fecha: str) -> int:
    return int(datetime.fromisoformat(fecha).replace(tzinfo=timezone.utc).timestamp())


def _limpiar(obj: dict) -> dict:
    res = {k: obj[k] for k in CAMPOS if k in obj and obj[k] is not None}
    for k in ("created", "arrival_date", "current_period_end"):
        if k in res:
            res[k] = datetime.fromtimestamp(res[k], timezone.utc).strftime("%Y-%m-%d")
    for k in ("amount", "amount_paid", "amount_due", "amount_refunded", "fee", "net"):
        if k in res:
            res[k] = res[k] / 100  # Stripe usa céntimos
    return res


def cargar(ctx: Contexto) -> list[Tool]:
    if not ctx.cfg.stripe_key:
        log.info("Stripe desactivado (falta STRIPE_API_KEY)")
        return []
    import stripe

    cliente = stripe.StripeClient(ctx.cfg.stripe_key)

    def _listar(recurso: str, desde: str, hasta: str, estado: str, limite: int) -> list:
        params: dict = {"limit": min(limite, 100)}
        if desde or hasta:
            params["created"] = {}
            if desde:
                params["created"]["gte"] = _epoch(desde)
            if hasta:
                params["created"]["lt"] = _epoch(hasta)
        if estado and recurso in ("invoices", "subscriptions"):
            params["status"] = estado
        servicio = getattr(cliente.v1, recurso)
        return [_limpiar(o.to_dict()) for o in servicio.list(params=params).data]

    async def listar(recurso: str, desde: str = "", hasta: str = "", estado: str = "", limite: int = 50) -> list:
        return await asyncio.to_thread(_listar, recurso, desde, hasta, estado, limite)

    async def saldo() -> dict:
        b = (await asyncio.to_thread(cliente.v1.balance.retrieve)).to_dict()
        return {
            "disponible": [{"importe": x["amount"] / 100, "moneda": x["currency"]} for x in b["available"]],
            "pendiente": [{"importe": x["amount"] / 100, "moneda": x["currency"]} for x in b["pending"]],
        }

    return [
        Tool("stripe_listar",
             "Lista objetos de Stripe (solo lectura, máx. 100). Importes ya en unidades (no céntimos). "
             "Recursos: " + "; ".join(f"{k} = {v}" for k, v in RECURSOS.items()),
             {"recurso": {"type": "string", "enum": list(RECURSOS)},
              "desde": {"type": "string", "description": "AAAA-MM-DD inclusive"},
              "hasta": {"type": "string", "description": "AAAA-MM-DD exclusivo"},
              "estado": {"type": "string", "description": "Solo invoices/subscriptions: paid, open, void, active..."},
              "limite": {"type": "integer"}},
             listar, obligatorios=("recurso",)),
        Tool("stripe_saldo", "Saldo actual de Stripe: disponible y pendiente.", {}, saldo),
    ]
