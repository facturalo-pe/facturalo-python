from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import quote

from .._http import HttpClient


class Webhooks:
    """Webhooks enviados por Facturalo a tu servidor."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def listar(
        self,
        *,
        pagina: Optional[int] = None,
        limite: Optional[int] = None,
        estado: Optional[str] = None,
        evento: Optional[str] = None,
    ) -> Any:
        return self._http.request(
            "GET", "/webhooks", query={"page": pagina, "limite": limite, "estado": estado, "evento": evento}
        )

    def reenviar(self, evento_id: str) -> Dict[str, Any]:
        return self._http.request("POST", f"/webhooks/{quote(evento_id, safe='')}/reenviar")
