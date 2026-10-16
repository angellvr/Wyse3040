"""Módulos del asistente. Para añadir uno nuevo: crea el fichero y añádelo a MODULOS."""
from . import correo, crm, drive, notas, odoo, stripe_mod

# El orden importa: drive antes que correo (correo usa el servicio de drive)
MODULOS = [drive, correo, odoo, stripe_mod, crm, notas]
