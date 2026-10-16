# Arquitectura

## Por qué así

- **El Wyse 3040 no puede ejecutar un modelo de IA local** (2 GB RAM, Atom de 4 núcleos).
  Por eso el razonamiento lo hace Claude vía API y el Wyse solo hace de orquestador:
  consume ~80–150 MB de RAM y unos 5 W.
- **Los datos se quedan en local**: base SQLite, adjuntos temporales, credenciales y logs
  viven en el Wyse. A la API solo viaja lo que hace falta para cada pregunta.
- **Python 3.11** (el de Debian 12): hay librerías maduras para todo (Odoo es Python,
  Stripe, Google, IMAP, Telegram).
- **Sin Docker** de inicio: el eMMC de 8/16 GB va justo. Un `venv` + `systemd` basta.

## Componentes

```
asistente/
├── __main__.py      Arranque: carga config, módulos, bot y tareas programadas
├── config.py        Lee .env y config/cuentas.yaml
├── db.py            SQLite: correos procesados, borradores, notas, eventos
├── agent.py         Bucle de Claude con herramientas (tool use)
├── bot.py           Bot de Telegram: chat, comandos, botones de confirmación
├── __main__.py      (también programa las tareas: revisar correo, resumen diario)
├── tools.py         Registro de herramientas (Tool) que exponen los módulos
├── google_auth.py   Asistente de autorización OAuth para Drive/Gmail
└── modules/
    ├── correo.py    IMAP multi-cuenta, clasificación, facturas → Drive, envío SMTP
    ├── drive.py     Subida de archivos a carpetas por año/mes
    ├── odoo.py      Consultas XML-RPC de solo lectura
    ├── stripe_mod.py Consultas de solo lectura (clave restringida)
    ├── crm.py       Consultas GET al CRM propio (rutas permitidas)
    └── notas.py     Memoria de la empresa: notas y base de conocimiento
```

## Flujos

### 1. Recogida de facturas (automático, cada `INTERVALO_CORREO_MIN`)
1. Para cada cuenta de `config/cuentas.yaml` se leen por IMAP los correos nuevos
   (sin marcarlos como leídos).
2. Se descartan los ya procesados (Message-ID guardado en SQLite).
3. Claude clasifica cada correo con salida estructurada:
   `es_factura`, `importante`, `proveedor`, `importe`, `fecha`, `resumen`.
4. Si es factura y trae PDF/imagen → se sube a Drive en `Facturas/AAAA/MM/`
   con nombre `AAAA-MM-DD_proveedor_importe.pdf`.
5. Si es importante → aviso por Telegram con el resumen.

### 2. Conversación (Telegram)
1. Solo responde a los IDs de Telegram autorizados (`TELEGRAM_USUARIOS_PERMITIDOS`).
2. El mensaje entra al bucle del agente con todas las herramientas de los módulos activos.
3. Claude decide qué consultar (Odoo, Stripe, CRM, correo, notas) y responde.

### 3. Acciones con efecto (enviar correo, etc.)
El modelo **nunca** ejecuta directamente una acción irreversible. La herramienta
`preparar_correo` solo crea un borrador; el bot te lo muestra con botones
**Enviar / Cancelar** y solo tu pulsación lo envía. Cualquier acción futura con efecto
(crear factura en Odoo, reembolso en Stripe...) debe seguir este mismo patrón.

## Seguridad

- Claves de **solo lectura** siempre que se pueda: clave restringida de Stripe, usuario de
  Odoo con permisos de solo lectura, token del CRM de solo lectura.
- `.env`, `config/cuentas.yaml`, `data/` y tokens de Google **nunca** se suben a GitHub.
- El contenido de los correos se trata como datos, no como órdenes (un correo no puede
  hacer que el asistente envíe nada: todo envío pasa por tu confirmación).
- Acceso remoto al Wyse: Tailscale o WireGuard; no abrir puertos al exterior.
  El bot de Telegram funciona por *polling*, no necesita puertos abiertos.

## Modelo y coste

- Modelo por defecto: `claude-opus-5-5` (configurable con `MODELO` y `MODELO_CLASIFICADOR`).
- Para abaratar la clasificación de correos, puedes poner `MODELO_CLASIFICADOR=claude-haiku-5-5`.
- El prompt de sistema y las herramientas se cachean (prompt caching) para reducir coste.
- Fallback del lado del servidor activado (`fallbacks: "default"`) en el modelo principal:
  si un clasificador de seguridad rechaza una petición legítima, la API la reintenta con
  el modelo recomendado en vez de fallar.
