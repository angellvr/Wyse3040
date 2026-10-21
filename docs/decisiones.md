# Decisiones y estado

## Decisiones (2026-10-16)

- **Cerebro en la API de Claude**, no un modelo local: el Wyse 3040 no tiene RAM para un LLM.
- **Debian 13 "trixie"** (estable actual; Debian 12 ya solo tiene soporte LTS hasta 2028).
- **Python 3.13 (el de Debian 13) + venv + systemd**, sin Docker, por el poco espacio del eMMC.
- **Telegram** como interfaz: gratis, push y botones, sin abrir puertos.
- **SQLite** para el estado local.
- **Solo lectura por defecto**; las acciones con efecto requieren confirmación por botón.
- **Drive con permiso `drive.file`**: el asistente crea su propia carpeta `Facturas/AAAA/MM`.
- **Correo por IMAP/SMTP con contraseñas de aplicación** (lo más simple para varias cuentas).
- **Modelo `claude-opus-5-5`** para el chat y la clasificación, configurable por `.env`.

## Estado

- [x] v0.1 escrita: núcleo, bot, correo y facturas → Drive, Odoo, Stripe, CRM (genérico) y notas.
- [x] Debian 13 instalado en el Wyse (usuario `angel`); `sudo` y `curl` instalados.
- [ ] Terminar la preparación del Wyse (Tailscale, deploy key) y desplegar. Detalle en [traspaso.md](traspaso.md).
- [ ] Decidir si el clasificador de correos usa `claude-haiku-5-5` (~$1 al mes frente a ~$40).
- [ ] Rellenar credenciales y probar cada módulo contra los servicios reales (todavía no se ha ejecutado nada).
- [ ] Adaptar `crm.py` a la API real del CRM propio.
- [ ] Decidir si las cuentas de Outlook/365 necesitan OAuth.

## Pendiente de saber

- ¿Qué CRM es y cómo se accede: API REST, base de datos u otra cosa?
- ¿Qué proveedores de correo usan las cuentas (Gmail, Workspace, Outlook, otro)?
- ¿Odoo Online (odoo.com) o instalado en un servidor propio? ¿Qué versión?
