from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import quote

from .._http import HttpClient


def _id(valor: str) -> str:
    return quote(valor, safe="")


class Empresas:
    """Empresas de la cuenta (token de usuario user_sk_...)."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def listar(self) -> Any:
        return self._http.request("GET", "/empresas")

    def obtener(self, id: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/empresas/{_id(id)}").get("empresa", {})

    def verificar_ruc(self, ruc: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/empresas/verificar-ruc/{_id(ruc)}")

    def crear(self, empresa: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.request("POST", "/empresas", {"empresa": empresa}).get("empresa", {})

    def actualizar(self, id: str, empresa: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.request("PATCH", f"/empresas/{_id(id)}", {"empresa": empresa}).get("empresa", {})

    def actualizar_webhook(self, id: str, webhook: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.request("PATCH", f"/empresas/{_id(id)}/webhook", {"webhook": webhook}).get("empresa", {})

    def eventos_webhook(self, id: str) -> Any:
        return self._http.request("GET", f"/empresas/{_id(id)}/webhook/eventos")

    def actualizar_eventos_webhook(self, id: str, entorno: str, eventos: List[str]) -> Any:
        return self._http.request(
            "PATCH", f"/empresas/{_id(id)}/webhook/eventos", {"entorno": entorno, "eventos": eventos}
        )

    def regenerar_token(self, id: str, entorno: str) -> Dict[str, Any]:
        return self._http.request("POST", f"/empresas/{_id(id)}/regenerar-token", {"entorno": entorno}).get(
            "empresa", {}
        )

    def regenerar_secret_webhook(self, id: str, entorno: str) -> Dict[str, Any]:
        return self._http.request(
            "POST", f"/empresas/{_id(id)}/webhook/regenerar-secret", {"entorno": entorno}
        ).get("empresa", {})

    def certificado(self, id: str) -> Optional[Dict[str, Any]]:
        certificado = self._http.request("GET", f"/empresas/{_id(id)}/certificado").get("certificado")
        return certificado if isinstance(certificado, dict) else None
