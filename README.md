# Asistente empresarial en Dell Wyse 3040

Asistente personal para la empresa que corre 24/7 en un **Dell Wyse 3040** (Debian 13, 2 GB RAM)
y se controla desde **Telegram**. El "cerebro" es Claude (API de Anthropic); el Wyse solo
orquesta: lee correos, llama a Odoo/Stripe/CRM, sube facturas a Google Drive y te avisa.

## Qué hace

| Función | Módulo | Estado |
|---|---|---|
| Recoger facturas de varias cuentas de correo y subirlas a Google Drive | `correo` + `drive` | v0.1 |
| Avisar por Telegram cuando llega algo importante | `correo` | v0.1 |
| Consultar facturación y contabilidad en Odoo (solo lectura) | `odoo` | v0.1 |
| Consultar cobros, facturas y saldo en Stripe (solo lectura) | `stripe_mod` | v0.1 |
| Consultar el CRM propio (solo lectura, API REST) | `crm` | v0.1 — adaptar a tu API |
| Preguntas libres sobre la empresa (notas + base de conocimiento) | `notas` | v0.1 |
| Enviar correos **con confirmación** previa en Telegram | `correo` | v0.1 |

Nada se ha probado aún contra los servicios reales: falta poner credenciales (ver abajo).

## Arquitectura en una línea

```
Telegram ⇄ bot.py ⇄ agent.py (Claude + herramientas) ⇄ modules/* ⇄ Gmail/IMAP · Drive · Odoo · Stripe · CRM
                         ↑
                 scheduler (cada X min revisa correo, clasifica, sube facturas, avisa)
```

Detalle en [docs/arquitectura.md](docs/arquitectura.md).

## Puesta en marcha

1. Preparar el Wyse: [docs/despliegue-wyse.md](docs/despliegue-wyse.md)
2. Copiar `.env.example` → `.env` y `config/cuentas.example.yaml` → `config/cuentas.yaml`, y rellenar.
3. Autorizar Google Drive (una vez, en tu PC): `python -m asistente.google_auth`
4. Arrancar: `python -m asistente` (o el servicio systemd `asistente`).

## Añadir funciones nuevas

Cada capacidad es un módulo en `asistente/modules/` que expone una lista `TOOLS`.
Guía: [docs/anadir-modulo.md](docs/anadir-modulo.md).

## Skills y herramientas recomendadas

Ver [docs/skills.md](docs/skills.md).
