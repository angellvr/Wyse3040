# Despliegue en el Dell Wyse 3040

## 1. Instalar Debian 13 (trixie)

1. Descarga `debian-13.x-amd64-netinst.iso` (debian.org → Descargar) y grábala en un USB (Rufus o balenaEtcher).
2. En el Wyse pulsa **F2** al arrancar para entrar en la BIOS (contraseña de fábrica habitual: `Fireport`).
   - *General → Boot Sequence*: modo **UEFI**, activa el arranque por USB.
   - *Secure Boot*: **desactivado**.
   - *Power Management → AC Recovery*: **Power On** (que arranque solo tras un corte de luz).
3. Arranca desde el USB (**F12**) e instala:
   - Particionado: todo el disco eMMC, sin swap aparte (usaremos zram).
   - Software: solo **servidor SSH** y **utilidades estándar** (sin escritorio).
4. Tras reiniciar, desde tu PC: `ssh usuario@IP-del-wyse`.

Si el instalador no ve el eMMC, actualiza la BIOS del Wyse desde la web de Dell.

## 2. Ajustes del sistema

Si en el instalador pusiste contraseña de root, `sudo` no viene instalado. Actívalo primero
(sustituye `angel` por tu usuario) y vuelve a iniciar sesión:

```bash
su -                      # contraseña de root; el guion es necesario
apt install -y sudo
usermod -aG sudo angel
exit
```

```bash
sudo apt install -y zram-tools unattended-upgrades curl
echo -e "ALGO=zstd\nPERCENT=50" | sudo tee /etc/default/zramswap
sudo systemctl restart zramswap
sudo dpkg-reconfigure -plow unattended-upgrades   # actualizaciones de seguridad automáticas
sudo timedatectl set-timezone Europe/Madrid
```

Recomendado: instala **Tailscale** para administrarlo desde fuera sin abrir puertos:
`curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up`.

## 3. Acceso al repositorio privado de GitHub

En el Wyse genera una clave de despliegue de solo lectura:

```bash
sudo -u root ssh-keygen -t ed25519 -f /root/.ssh/github_asistente -N ""
cat /root/.ssh/github_asistente.pub
```

Añádela en GitHub → repo → *Settings → Deploy keys* (sin permiso de escritura) y crea `/root/.ssh/config`:

```
Host github.com
  IdentityFile /root/.ssh/github_asistente
```

## 4. Instalar el asistente

```bash
sudo apt install -y git
sudo git clone git@github.com:USUARIO/REPO.git /opt/asistente
sudo bash /opt/asistente/deploy/install.sh
```

Después rellena los secretos (el servicio fallará hasta que estén):

```bash
sudo nano /opt/asistente/.env
sudo nano /opt/asistente/config/cuentas.yaml
sudo systemctl restart asistente
journalctl -u asistente -f
```

## 5. Credenciales que necesitas

| Servicio | Dónde se obtiene |
|---|---|
| Claude | console.anthropic.com → API Keys (pon un límite de gasto mensual) |
| Telegram | @BotFather → `/newbot`; tu ID numérico con @userinfobot |
| Gmail / Workspace | Verificación en 2 pasos + *Contraseñas de aplicación* |
| Outlook / Microsoft 365 | Contraseña de aplicación o, si tu organización la bloquea, habrá que añadir OAuth (pendiente) |
| Google Drive | Google Cloud Console → proyecto → habilitar *Drive API* → credenciales OAuth tipo *Aplicación de escritorio* → descargar JSON como `data/google_client_secret.json`. Luego en tu PC: `python -m asistente.google_auth` y copia `data/google_token.json` al Wyse con `scp` |
| Odoo | Usuario con permisos de solo lectura → Preferencias → Seguridad de la cuenta → Nueva clave API |
| Stripe | Developers → API keys → *Create restricted key* con permisos **Read** en Charges, Customers, Invoices, Payouts, Balance, Subscriptions, Refunds |

## 6. Actualizar

Cuando subas cambios a GitHub desde cualquier ordenador:

```bash
sudo bash /opt/asistente/deploy/install.sh
```

## 7. Copias de seguridad

Lo único que no está en GitHub es `/opt/asistente/data`, `.env`, `config/cuentas.yaml` y `conocimiento/`.
Cópialos de vez en cuando a otro sitio (p. ej. `tar czf` + subirlo a Drive cifrado).
