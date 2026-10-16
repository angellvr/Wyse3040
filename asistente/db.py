"""Persistencia local en SQLite (data/asistente.db)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS correos (
    message_id TEXT PRIMARY KEY,
    cuenta TEXT, remitente TEXT, asunto TEXT, fecha TEXT,
    es_factura INTEGER, importante INTEGER, resumen TEXT,
    proveedor TEXT, importe TEXT, drive_url TEXT,
    procesado_en TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS borradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cuenta TEXT, para TEXT, asunto TEXT, cuerpo TEXT,
    estado TEXT DEFAULT 'pendiente',
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tema TEXT, texto TEXT,
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS uso_api (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modelo TEXT, entrada INTEGER, salida INTEGER, cache_lectura INTEGER,
    fecha TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


class DB:
    def __init__(self, ruta: Path) -> None:
        self.con = sqlite3.connect(ruta, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.con.executescript(ESQUEMA)

    def ejecutar(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        cur = self.con.execute(sql, params)
        self.con.commit()
        return cur

    def filas(self, sql: str, params: tuple = ()) -> list[dict]:
        return [dict(r) for r in self.con.execute(sql, params).fetchall()]

    # --- correos ---
    def correo_procesado(self, message_id: str) -> bool:
        return self.con.execute(
            "SELECT 1 FROM correos WHERE message_id = ?", (message_id,)
        ).fetchone() is not None

    def guardar_correo(self, **campos) -> None:
        cols = ", ".join(campos)
        marcas = ", ".join("?" for _ in campos)
        self.ejecutar(f"INSERT OR REPLACE INTO correos ({cols}) VALUES ({marcas})", tuple(campos.values()))

    # --- uso ---
    def registrar_uso(self, modelo: str, usage) -> None:
        self.ejecutar(
            "INSERT INTO uso_api (modelo, entrada, salida, cache_lectura) VALUES (?, ?, ?, ?)",
            (modelo, usage.input_tokens, usage.output_tokens, getattr(usage, "cache_read_input_tokens", 0) or 0),
        )
