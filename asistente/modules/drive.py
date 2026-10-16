"""Google Drive: subir facturas a Facturas/AAAA/MM dentro de la carpeta configurada."""
from __future__ import annotations

import asyncio
import io
import logging

from ..contexto import Contexto
from ..tools import Tool

log = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
MIME_CARPETA = "application/vnd.google-apps.folder"


class Drive:
    def __init__(self, ctx: Contexto) -> None:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        cfg = ctx.cfg
        creds = Credentials.from_authorized_user_file(str(cfg.google_token), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            cfg.google_token.write_text(creds.to_json(), encoding="utf-8")
        self.servicio = build("drive", "v3", credentials=creds, cache_discovery=False)
        self._cache: dict[tuple[str, str], str] = {}
        # Con el permiso drive.file la app solo ve lo que ella crea, así que la carpeta
        # raíz la crea el propio asistente (luego puedes moverla donde quieras en Drive).
        self.raiz = self._carpeta("root", cfg.drive_carpeta_facturas)

    def _carpeta(self, padre: str, nombre: str) -> str:
        clave = (padre, nombre)
        if clave in self._cache:
            return self._cache[clave]
        q = (f"'{padre}' in parents and name = '{nombre}' and mimeType = '{MIME_CARPETA}' "
             "and trashed = false")
        encontrados = self.servicio.files().list(q=q, fields="files(id)").execute().get("files", [])
        if encontrados:
            fid = encontrados[0]["id"]
        else:
            meta = {"name": nombre, "mimeType": MIME_CARPETA, "parents": [padre]}
            fid = self.servicio.files().create(body=meta, fields="id").execute()["id"]
        self._cache[clave] = fid
        return fid

    def _subir(self, contenido: bytes, nombre: str, mime: str, anio: str, mes: str) -> str:
        from googleapiclient.http import MediaIoBaseUpload

        carpeta = self._carpeta(self._carpeta(self.raiz, anio), mes)
        media = MediaIoBaseUpload(io.BytesIO(contenido), mimetype=mime, resumable=False)
        f = self.servicio.files().create(
            body={"name": nombre, "parents": [carpeta]}, media_body=media, fields="id, webViewLink"
        ).execute()
        return f["webViewLink"]

    async def subir_factura(self, contenido: bytes, nombre: str, mime: str, anio: str, mes: str) -> str:
        return await asyncio.to_thread(self._subir, contenido, nombre, mime, anio, mes)


def cargar(ctx: Contexto) -> list[Tool]:
    cfg = ctx.cfg
    if not cfg.google_token.exists():
        log.info("Drive desactivado (falta el token de Google: python -m asistente.google_auth)")
        return []
    ctx.servicios["drive"] = Drive(ctx)
    return []  # Drive no expone herramientas al chat; lo usa el módulo de correo
