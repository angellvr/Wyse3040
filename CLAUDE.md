# CLAUDE.md

Asistente empresarial en Python que corre en un Dell Wyse 3040 (Debian 13 "trixie", 2 GB RAM, Python 3.13)
y se controla por Telegram. Claude (API de Anthropic) es el cerebro; el Wyse solo orquesta.

## Contexto para continuar en cualquier ordenador

- El estado del proyecto vive en este repo: lee `README.md` y `docs/` antes de empezar.
- Decisiones tomadas y pendientes: `docs/decisiones.md` (actualízalo al cerrar cada sesión de trabajo).
- Los secretos (`.env`, `config/cuentas.yaml`, `data/`, `conocimiento/`) NO están en git; solo existen en el Wyse.

## Convenciones

- Código, comentarios, mensajes y documentación en **español**.
- Cada capacidad es un módulo en `asistente/modules/` con `cargar(ctx) -> list[Tool]`; se registra en `modules/__init__.py`.
- Las herramientas son de **solo lectura**. Cualquier acción con efecto externo crea un pendiente que el usuario confirma con un botón en Telegram (patrón `preparar_correo` → `borradores` → `enviar_borrador`).
- Las llamadas síncronas van dentro de `asyncio.to_thread`.
- Las llamadas a Claude pasan por `Contexto.llamar_claude` (fallback del lado del servidor y registro de uso).
- El prompt de sistema y la lista de herramientas deben ser estables para que funcione la caché: nada de fechas ni datos variables en el prompt de sistema.
- El historial de conversación no se recorta (rompería los bloques de razonamiento); se reinicia.

## Comandos

- Ejecutar en local: `python -m asistente` (necesita `.env`).
- Desplegar en el Wyse: `ssh wyse 'sudo bash /opt/asistente/deploy/install.sh'`.
- Logs en el Wyse: `journalctl -u asistente -f` o `/opt/asistente/data/asistente.log`.
