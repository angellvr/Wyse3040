"""Bot de Telegram: interfaz de chat, comandos y confirmación de acciones."""
from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .agent import Agente
from .contexto import Contexto
from .modules import correo
from .tools import Registro

log = logging.getLogger(__name__)
LIMITE_TELEGRAM = 4000

AYUDA = """Soy tu asistente. Escríbeme lo que necesites, por ejemplo:
• ¿Cuánto hemos facturado este mes en Odoo?
• ¿Qué cobros ha tenido Stripe esta semana?
• ¿Qué facturas han llegado hoy?
• Busca al cliente X en el CRM
• Escribe a fulano@empresa.com para confirmar la reunión del jueves

Comandos:
/nuevo – empezar conversación nueva
/revisar – revisar el correo ahora
/estado – módulos activos y consumo
/ayuda – este mensaje"""


def _trozos(texto: str) -> list[str]:
    return [texto[i : i + LIMITE_TELEGRAM] for i in range(0, len(texto), LIMITE_TELEGRAM)] or [""]


def crear_app(ctx: Contexto, agente: Agente, registro: Registro) -> Application:
    cfg = ctx.cfg
    app = Application.builder().token(cfg.telegram_token).build()
    permitidos = filters.User(user_id=cfg.telegram_usuarios)

    async def notificar(texto: str) -> None:
        for uid in cfg.telegram_usuarios:
            for t in _trozos(texto):
                await app.bot.send_message(uid, t)

    ctx.notificar = notificar

    async def mostrar_borradores(chat_id: int) -> None:
        """Muestra con botones los borradores de correo pendientes de confirmar."""
        for b in ctx.db.filas("SELECT * FROM borradores WHERE estado = 'pendiente'"):
            ctx.db.ejecutar("UPDATE borradores SET estado = 'mostrado' WHERE id = ?", (b["id"],))
            teclado = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Enviar", callback_data=f"enviar:{b['id']}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"cancelar:{b['id']}"),
            ]])
            texto = (f"📧 Borrador #{b['id']} desde {b['cuenta']}\n"
                     f"Para: {b['para']}\nAsunto: {b['asunto']}\n\n{b['cuerpo']}")
            await app.bot.send_message(chat_id, texto[:LIMITE_TELEGRAM], reply_markup=teclado)

    async def mensaje(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        await update.effective_chat.send_action(ChatAction.TYPING)
        respuesta = await agente.responder(chat_id, update.message.text)
        for t in _trozos(respuesta):
            await update.message.reply_text(t)
        await mostrar_borradores(chat_id)

    async def boton(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        q = update.callback_query
        if q.from_user.id not in cfg.telegram_usuarios:
            await q.answer("No autorizado")
            return
        await q.answer()
        accion, _, id_txt = q.data.partition(":")
        borrador_id = int(id_txt)
        if accion == "enviar":
            try:
                await correo.enviar_borrador(ctx, borrador_id)
                await q.edit_message_reply_markup(None)
                await q.message.reply_text(f"✅ Correo #{borrador_id} enviado.")
            except Exception as e:
                log.exception("Error enviando borrador")
                await q.message.reply_text(f"⚠️ No se pudo enviar: {e}")
        else:
            ctx.db.ejecutar("UPDATE borradores SET estado = 'cancelado' WHERE id = ?", (borrador_id,))
            await q.edit_message_reply_markup(None)
            await q.message.reply_text(f"Borrador #{borrador_id} cancelado.")

    async def cmd_ayuda(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(AYUDA)

    async def cmd_nuevo(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        agente.reiniciar(update.effective_chat.id)
        await update.message.reply_text("Conversación nueva. ¿En qué te ayudo?")

    async def cmd_revisar(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Revisando correo…")
        resumen = await correo.revisar(ctx)
        await update.message.reply_text(resumen)

    async def cmd_estado(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        uso = ctx.db.filas(
            "SELECT modelo, SUM(entrada) entrada, SUM(salida) salida, SUM(cache_lectura) cache "
            "FROM uso_api WHERE fecha >= date('now', 'start of month') GROUP BY modelo"
        )
        lineas = ["Herramientas activas:", ", ".join(registro.nombres()) or "ninguna", "", "Tokens este mes:"]
        lineas += [f"• {u['modelo']}: {u['entrada']} entrada / {u['salida']} salida / {u['cache']} caché" for u in uso]
        await update.message.reply_text("\n".join(lineas))

    async def no_autorizado(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        log.warning("Mensaje de usuario no autorizado: %s", update.effective_user.id if update.effective_user else "?")

    app.add_handler(CommandHandler(["start", "ayuda"], cmd_ayuda, filters=permitidos))
    app.add_handler(CommandHandler("nuevo", cmd_nuevo, filters=permitidos))
    app.add_handler(CommandHandler("revisar", cmd_revisar, filters=permitidos))
    app.add_handler(CommandHandler("estado", cmd_estado, filters=permitidos))
    app.add_handler(MessageHandler(permitidos & filters.TEXT & ~filters.COMMAND, mensaje))
    app.add_handler(CallbackQueryHandler(boton, pattern=r"^(enviar|cancelar):\d+$"))
    app.add_handler(MessageHandler(~permitidos, no_autorizado))
    return app
