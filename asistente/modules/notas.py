"""Memoria de la empresa: notas que el asistente guarda y consulta.

Además, todo fichero .md en la carpeta conocimiento/ se carga en el prompt de sistema
(datos fijos: servicios, tarifas, proveedores habituales, procedimientos...).
"""
from __future__ import annotations

from ..contexto import Contexto
from ..tools import Tool


def cargar(ctx: Contexto) -> list[Tool]:
    def guardar_nota(tema: str, texto: str) -> str:
        cur = ctx.db.ejecutar("INSERT INTO notas (tema, texto) VALUES (?, ?)", (tema, texto))
        return f"Nota #{cur.lastrowid} guardada."

    def buscar_notas(texto: str = "") -> list[dict]:
        patron = f"%{texto}%"
        return ctx.db.filas(
            "SELECT id, tema, texto, creado_en FROM notas WHERE tema LIKE ? OR texto LIKE ? "
            "ORDER BY id DESC LIMIT 50", (patron, patron),
        )

    def borrar_nota(id: int) -> str:
        ctx.db.ejecutar("DELETE FROM notas WHERE id = ?", (id,))
        return f"Nota #{id} borrada."

    return [
        Tool("guardar_nota", "Guarda un dato duradero sobre la empresa (cliente, proveedor, precio, acuerdo, preferencia).",
             {"tema": {"type": "string", "description": "Etiqueta corta, p. ej. 'cliente:Acme' o 'tarifas'"},
              "texto": {"type": "string"}},
             guardar_nota, obligatorios=("tema", "texto")),
        Tool("buscar_notas", "Busca en las notas guardadas de la empresa. Sin texto devuelve las últimas.",
             {"texto": {"type": "string"}}, buscar_notas),
        Tool("borrar_nota", "Borra una nota por su id (cuando el usuario indica que ya no es válida).",
             {"id": {"type": "integer"}}, borrar_nota, obligatorios=("id",)),
    ]
