"""Configuración: variables de entorno (.env) + config/cuentas.yaml."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


def _lista_ints(valor: str) -> list[int]:
    return [int(x) for x in valor.replace(" ", "").split(",") if x]


@dataclass
class CuentaCorreo:
    nombre: str
    usuario: str
    password: str
    imap_host: str
    imap_puerto: int = 993
    smtp_host: str | None = None
    smtp_puerto: int = 587
    carpetas: list[str] = field(default_factory=lambda: ["INBOX"])
    puede_enviar: bool = False


@dataclass
class Config:
    # Claude
    modelo: str = os.getenv("MODELO", "claude-opus-5-5")
    modelo_clasificador: str = os.getenv("MODELO_CLASIFICADOR", "claude-opus-5-5")
    esfuerzo: str = os.getenv("ESFUERZO", "medium")

    # Telegram
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")
    telegram_usuarios: list[int] = field(
        default_factory=lambda: _lista_ints(os.getenv("TELEGRAM_USUARIOS_PERMITIDOS", ""))
    )

    # Tareas periódicas
    intervalo_correo_min: int = int(os.getenv("INTERVALO_CORREO_MIN", "15"))
    hora_resumen_diario: str = os.getenv("HORA_RESUMEN_DIARIO", "08:30")
    zona_horaria: str = os.getenv("ZONA_HORARIA", "Europe/Madrid")

    # Google Drive
    drive_carpeta_facturas: str = os.getenv("DRIVE_CARPETA_FACTURAS", "Facturas")
    google_token: Path = RAIZ / os.getenv("GOOGLE_TOKEN", "data/google_token.json")
    google_cliente: Path = RAIZ / os.getenv("GOOGLE_CLIENTE", "data/google_client_secret.json")

    # Odoo
    odoo_url: str = os.getenv("ODOO_URL", "")
    odoo_db: str = os.getenv("ODOO_DB", "")
    odoo_usuario: str = os.getenv("ODOO_USUARIO", "")
    odoo_api_key: str = os.getenv("ODOO_API_KEY", "")

    # Stripe (usar clave restringida de solo lectura: rk_live_...)
    stripe_key: str = os.getenv("STRIPE_API_KEY", "")

    # CRM propio
    crm_url: str = os.getenv("CRM_URL", "")
    crm_token: str = os.getenv("CRM_TOKEN", "")

    # Rutas
    datos: Path = RAIZ / "data"
    conocimiento: Path = RAIZ / "conocimiento"

    cuentas: list[CuentaCorreo] = field(default_factory=list)
    crm_rutas: dict[str, str] = field(default_factory=dict)
    contexto_empresa: str = ""


def cargar() -> Config:
    cfg = Config()
    cfg.datos.mkdir(exist_ok=True)
    fichero = RAIZ / "config" / "cuentas.yaml"
    if fichero.exists():
        datos = yaml.safe_load(fichero.read_text(encoding="utf-8")) or {}
        for c in datos.get("correo", []):
            # La contraseña se lee de una variable de entorno, nunca del YAML
            c["password"] = os.getenv(c.pop("password_env"), "")
            cfg.cuentas.append(CuentaCorreo(**c))
        cfg.crm_rutas = datos.get("crm_rutas", {})
        cfg.contexto_empresa = datos.get("empresa", "")
    return cfg
