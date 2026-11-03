from __future__ import annotations

from typing import Any, Dict
from urllib.parse import quote

from .._http import HttpClient


class Establecimientos:
    """Establecimientos (sucursales) de una empresa."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def _base(self, empresa_id: str) -> str:
        return f"/empresas/{quote(empresa_id, safe='')}/establecimientos"

    def listar(self, empresa_id: str) -> Any:
        return self._http.request("GET", self._base(empresa_id))

    def obtener(self, empresa_id: str, id: str) -> Dict[str, Any]:
        return self._http.request("GET", f"{self._base(empresa_id)}/{quote(id, safe='')}").get("establecimiento", {})

    def crear(self, empresa_id: str, establecimiento: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.request("POST", self._base(empresa_id), {"establecimiento": establecimiento}).get(
            "establecimiento", {}
        )

    def actualizar(self, empresa_id: str, id: str, establecimiento: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.request(
            "PATCH", f"{self._base(empresa_id)}/{quote(id, safe='')}", {"establecimiento": establecimiento}
        ).get("establecimiento", {})

    def eliminar(self, empresa_id: str, id: str) -> None:
        self._http.request("DELETE", f"{self._base(empresa_id)}/{quote(id, safe='')}")
