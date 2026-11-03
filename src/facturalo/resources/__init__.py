"""Recursos de la API: una clase por recurso, igual que en los SDKs de Node y PHP."""

from .consultas import Consultas
from .documentos import Documentos
from .empresas import Empresas
from .establecimientos import Establecimientos
from .guias import Guias
from .sire import LibroSire, Sire
from .webhooks import Webhooks

__all__ = ["Consultas", "Documentos", "Empresas", "Establecimientos", "Guias", "LibroSire", "Sire", "Webhooks"]
