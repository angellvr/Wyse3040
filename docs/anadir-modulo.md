# Cómo añadir una función nueva

1. Crea `asistente/modules/mi_modulo.py` con una función `cargar(ctx) -> list[Tool]`:

```python
from ..contexto import Contexto
from ..tools import Tool


def cargar(ctx: Contexto) -> list[Tool]:
    if not ctx.cfg.algo_necesario:      # devuelve [] si no está configurado
        return []

    async def mi_consulta(cliente: str, dias: int = 30) -> dict:
        ...                              # devuelve str, dict o list (se serializa a JSON)

    return [Tool(
        "mi_consulta",
        "Qué hace y cuándo usarla. Claude decide por esta descripción.",
        {"cliente": {"type": "string"}, "dias": {"type": "integer"}},
        mi_consulta, obligatorios=("cliente",),
    )]
```

2. Añádelo a `MODULOS` en `asistente/modules/__init__.py`.
3. Si necesita credenciales, añádelas a `config.py` y a `.env.example`.

## Reglas

- **Solo lectura por defecto.** Si una herramienta cambia algo fuera (enviar, crear, pagar, borrar),
  debe crear una petición pendiente y que el usuario la confirme con un botón en Telegram,
  igual que `preparar_correo` → `borradores` → `enviar_borrador`.
- Llamadas bloqueantes (librerías síncronas) dentro de `asyncio.to_thread(...)`.
- Limita el tamaño de lo que devuelves (campos concretos, `limit`): todo va al contexto de Claude.
- Para tareas periódicas, añade un `job_queue.run_repeating(...)` en `__main__.py`.

## Ideas para siguientes módulos

- Leer PDFs de facturas (Claude lee PDFs directamente) y extraer base, IVA y total para cuadrar con Odoo.
- Crear facturas de proveedor en Odoo como borrador a partir de lo recibido por correo (con confirmación).
- Avisos de cobros fallidos en Stripe y facturas vencidas en Odoo.
- Notas de voz en Telegram (transcripción) y envío de fotos de tickets.
- Calendario (Google Calendar) para recordatorios y reuniones.
