from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import quote

from .._http import HttpClient

_FORMATOS = ("pdf", "xml", "cdr")


class Guias:
    """Guías de remisión remitente (09) y transportista (31)."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def enviar(
        self, guia: Dict[str, Any], *, webhook: bool = False, idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        return self._http.request("POST", "/guias/enviar", {"webhook": webhook, "guia": guia}, headers=headers)

    def consultar(self, id: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/guias/{quote(id, safe='')}")

    def consultar_ticket(self, ticket: str) -> Dict[str, Any]:
        return self._http.request("POST", "/guias/ticket", {"ticket": ticket})

    def eventos(self, id: str) -> Any:
        return self._http.request("GET", f"/guias/{quote(id, safe='')}/eventos")

    def listar(
        self,
        *,
        pagina: Optional[int] = None,
        limite: Optional[int] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        estado: Optional[str] = None,
        buscar: Optional[str] = None,
    ) -> Any:
        return self._http.request(
            "GET",
            "/empresas/guias",
            query={
                "page": pagina,
                "limite": limite,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "estado": estado,
                "buscar": buscar,
            },
        )

    def url_archivo(self, id: str, formato: str = "pdf") -> str:
        if formato not in _FORMATOS:
            raise ValueError("Formato no válido. Usa pdf, xml o cdr.")
        return self._http.file_url(f"/guias/{quote(id, safe='')}.{formato}")

    def descargar(self, id: str, formato: str = "pdf") -> bytes:
        return self._http.download(self.url_archivo(id, formato))
