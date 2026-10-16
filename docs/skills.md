# Skills, plugins y herramientas recomendadas

Hay dos sitios donde las "skills" ayudan, y conviene no mezclarlos:

1. **Para desarrollar el proyecto**: Claude Code en tu PC, cuando trabajas en este repositorio.
2. **Para el asistente en marcha** en el Wyse: lo que el bot sabe hacer, que son los módulos de `asistente/modules/`.

## 1. Para desarrollar (Claude Code)

### Ya disponibles en tu Claude Code

| Skill | Para qué en este proyecto |
|---|---|
| `claude-api` | Referencia actualizada de la API de Claude (modelos, tool use, caché, coste). Úsala al tocar `agent.py` o `contexto.py`. Su subcomando `cost-optimize` sirve para revisar el gasto cuando el bot ya esté en uso |
| `pdf` | Probar la extracción de datos de facturas en PDF antes de meterla en un módulo |
| `xlsx` | Generar informes de facturación o conciliación en Excel a partir de Odoo/Stripe |
| `security-review` | Revisar los cambios antes de desplegarlos (el bot maneja credenciales y dinero) |
| `code-review` | Revisar bugs en un cambio o en una rama |
| `schedule` | Programar tareas en la nube (p. ej. una revisión semanal del código) |
| `skill-creator` | Crear las skills propias del proyecto (ver abajo) |

### Plugins del directorio que encajan

| Plugin | Por qué |
|---|---|
| **Finance** (Anthropic) | Skills de conciliación, cierre mensual, asientos y análisis de desviaciones. Sirven de guía para los módulos contables que añadas después |
| **stripe** (Stripe) | Buenas prácticas y documentación de Stripe al ampliar `stripe_mod.py` |
| **telegram** (Anthropic) | Canal para hablar con una sesión de Claude Code desde Telegram. Es una alternativa para *programar* desde el móvil, no para sustituir al bot |

En esta sesión de Claude Code también tienes conectados **Stripe** y **Google Drive** como conectores MCP.
Sirven para consultar tus datos reales mientras desarrollas, por ejemplo para ver la forma de los objetos.

### Skills propias que conviene crear en `.claude/skills/`

Se guardan en el repositorio, así que están en todos tus ordenadores:

- **`desplegar-wyse`**: hace `git push` y luego, por SSH, `sudo bash /opt/asistente/deploy/install.sh`, y comprueba los logs.
- **`nuevo-modulo`**: crea un módulo siguiendo [anadir-modulo.md](anadir-modulo.md), con su entrada en `.env.example`.
- **`probar-herramienta`**: ejecuta una herramienta concreta contra el servicio real, para depurar sin pasar por Telegram.

## 2. Para el asistente en marcha

Las capacidades del bot son sus módulos, no skills de Claude Code. Estas son las siguientes que recomiendo, por orden de utilidad:

1. **Lectura de PDFs de facturas**: Claude lee PDFs directamente desde la API y puede extraer base imponible, IVA, total y NIF para cuadrar con Odoo.
2. **Facturas de proveedor en Odoo como borrador**, con confirmación por botón.
3. **Alertas**: facturas de cliente vencidas, cobros fallidos en Stripe y gastos fuera de lo normal.
4. **Notas de voz y fotos de tickets** desde Telegram.
5. **Google Calendar** para recordatorios.

## ¿Por qué Telegram?

- Es gratis, tiene app en todos los dispositivos y notificaciones push fiables.
- Los bots funcionan por *polling*, así que no hay que abrir puertos en la red.
- Tiene botones (para confirmar acciones), archivos, notas de voz y grupos (por si un día lo usa más gente del equipo).
- Alternativas: **Slack** (si el equipo ya lo usa; integración parecida) o **WhatsApp Business API** (de pago y con plantillas obligatorias para iniciar conversaciones; no lo recomiendo para esto).
