# Traspaso del proyecto a otra cuenta de Claude Code

Documento para continuar el proyecto desde **otra cuenta de Claude Code** (u otro ordenador)
sin perder contexto. Claude Code no comparte memoria ni historial entre cuentas: todo lo que la
nueva sesión necesita saber está en este repositorio.

Última actualización: 2026-10-21.

---

## 1. Qué hay que llevarse

| Qué | Dónde está | Cómo se traspasa |
|---|---|---|
| Código y documentación | GitHub: `https://github.com/angellvr/Wyse3040` (privado) | `git clone` |
| Contexto para Claude | `CLAUDE.md`, `docs/` (este documento incluido) | Va con el repo |
| Secretos (`.env`, `config/cuentas.yaml`) | Solo en el Wyse, en `/opt/asistente/` | **No se traspasan**: se quedan en el Wyse |
| Datos (`data/`, `conocimiento/`) | Solo en el Wyse | Se quedan en el Wyse |
| Memoria e historial de la cuenta anterior | Cuenta antigua de Claude Code | **No se traspasan** (por eso existe este documento) |

**Nunca** pegues claves, contraseñas ni tokens en el chat de Claude Code. Se editan directamente
en el Wyse con `sudo nano /opt/asistente/.env`.

## 2. Pasos en la cuenta nueva

1. **Acceso a GitHub.** Si la cuenta nueva usa otro usuario de GitHub, añádelo como colaborador:
   repo → *Settings → Collaborators → Add people*. Si usa el mismo (`angellvr`), no hace falta nada.
2. **Clonar** en el ordenador donde vayas a trabajar:
   ```bash
   git clone https://github.com/angellvr/Wyse3040.git
   ```
3. **Requisitos del ordenador**: Git. Opcionales pero útiles:
   - Python 3.11 o superior, para ejecutar o probar código en local. El PC original **no tiene Python**,
     así que el código nunca se ha ejecutado allí.
   - GitHub CLI (`gh`), que no estaba instalado en el PC original.
   - Tailscale con la misma cuenta que el Wyse, para conectarse por SSH desde cualquier sitio.
4. **Abrir Claude Code en la carpeta** del repo. Leerá `CLAUDE.md` automáticamente.
5. **Plugins recomendados** (se activan por cuenta): *Finance* (Anthropic), *stripe* (Stripe) y,
   opcionalmente, *telegram* (Anthropic). La skill `claude-api` viene incluida en Claude Code.
6. **Primer mensaje** para la sesión nueva (cópialo tal cual):

   > Continúo el proyecto del asistente empresarial en el Dell Wyse 3040. Lee CLAUDE.md, README.md
   > y todos los ficheros de docs/, especialmente docs/traspaso.md y docs/decisiones.md. Después
   > resúmeme en pocas líneas el estado actual y cuál es el siguiente paso.

## 3. Estado actual (2026-10-21)

### Código: v0.1 escrita y en GitHub, sin ejecutar nunca
- Bot de Telegram con Claude como cerebro (`asistente/agent.py`, `bot.py`).
- Módulos: correo (facturas → Google Drive, avisos, envío con confirmación), Drive, Odoo, Stripe,
  CRM (genérico, por adaptar) y notas.
- Instalador para el Wyse (`deploy/install.sh`) y servicio systemd.
- Ningún módulo se ha probado contra servicios reales. **Lo primero tras desplegar es probarlos uno a uno.**

### Wyse 3040: instalación en curso
- [x] Debian 13 "trixie" instalado. Usuario: `angel`. Hostname: `debian`.
- [x] Instalado `sudo` (el instalador no lo trae si se pone contraseña de root).
- [~] Añadir `angel` al grupo `sudo`: se hizo `usermod`, pero falta confirmar que `groups` muestra `sudo`
  tras volver a iniciar sesión.
- [~] `curl` y Tailscale: `curl` se instaló como root; falta confirmar que `tailscale up` terminó.
- [ ] Ajustes del sistema (zram, actualizaciones automáticas, zona horaria): sección 2 de la guía.
- [ ] Deploy key de GitHub: sección 3 de [despliegue-wyse.md](despliegue-wyse.md). Se estaba haciendo.
- [ ] Clonar en `/opt/asistente` y ejecutar `deploy/install.sh`.
- [ ] Rellenar `.env` y `config/cuentas.yaml` en el Wyse.
- [ ] Autorizar Google Drive (`python -m asistente.google_auth` en un PC con navegador; copiar el token al Wyse).

Para retomarlo, en el Wyse ejecuta `groups`, `tailscale status` y `sudo ls /root/.ssh/` y pásale
el resultado a Claude.

### Lecciones aprendidas en la instalación
- Debian mínimo no trae `sudo` ni `curl`. Ya está reflejado en la guía.
- **Pegar varios comandos a la vez después de `su -` no funciona**: `su -` se queda esperando la contraseña
  y el resto se pierde. Hay que dar los comandos al usuario **de uno en uno**, en bloques separados.
- El usuario sigue la guía en la consola del Wyse y pega aquí la salida; conviene responder con
  comandos cortos y explicar qué debe ver si ha ido bien.

## 4. Decisiones pendientes del usuario

1. **Modelo para clasificar correos.** Hoy es `claude-opus-5-5`. Con `claude-haiku-5-5` el coste baja de
   ~$40 a ~$1 al mes para unos 100 correos diarios. Está propuesto; falta que el usuario decida si se cambia
   el valor por defecto en `.env.example`.
2. **Mostrar coste en dólares en `/estado`.** Propuesto, sin decidir.
3. Datos que faltan para adaptar módulos:
   - Qué **CRM** es y cómo se accede (API REST, base de datos...).
   - Qué **proveedor de correo** tiene cada cuenta (Gmail, Workspace, Outlook/365...).
   - **Odoo Online o instalado en servidor propio**, y versión. Ojo: en Odoo Online la API externa
     suele requerir el plan *Custom*.

## 5. Estimación de costes (referencia)

Con uso normal (10–15 preguntas al día, unos 100 correos al día, Opus para el chat y Haiku para clasificar)
salen **$20–35 al mes** de API de Claude. Si todo va con Opus, $60–75. Telegram, Drive, Stripe y Tailscale son
gratis; la luz del Wyse cuesta menos de 1 € al mes. Recomendado: poner un límite de gasto mensual en
console.anthropic.com.

## 6. Dónde está cada cosa

| Documento | Contenido |
|---|---|
| [../README.md](../README.md) | Qué hace el asistente y cómo se arranca |
| [arquitectura.md](arquitectura.md) | Componentes, flujos, seguridad, modelo y coste |
| [despliegue-wyse.md](despliegue-wyse.md) | Instalación paso a paso en el Wyse |
| [anadir-modulo.md](anadir-modulo.md) | Cómo añadir funciones nuevas |
| [skills.md](skills.md) | Skills y plugins recomendados |
| [decisiones.md](decisiones.md) | Decisiones tomadas y lista de estado |
| [../CLAUDE.md](../CLAUDE.md) | Convenciones que Claude Code debe seguir |

## 7. Al terminar cada sesión de trabajo

Actualiza `docs/decisiones.md` y la sección 3 de este documento, haz commit y `git push`.
Así la siguiente sesión, desde cualquier cuenta u ordenador, parte del estado real.
