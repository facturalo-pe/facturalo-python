from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import quote

from .._http import HttpClient

_EXTENSION = {"pdf": ".pdf", "ticket": ".ticket.pdf", "xml": ".xml", "cdr": ".cdr"}


def _id(valor: str) -> str:
    return quote(valor, safe="")


class Documentos:
    """Facturas, boletas y notas de crédito y débito."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def enviar(
        self,
        documento: Dict[str, Any],
        *,
        webhook: bool = False,
        establecimiento: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Emite el comprobante y espera la respuesta de SUNAT (o responde EN_PROCESO si `webhook=True`).

        Un rechazo de SUNAT no es una excepción: vuelve con `estado == "RECHAZADA"` y el motivo en `sunat`.
        Con `idempotency_key`, reintentar la misma petición no duplica el comprobante.
        """
        body: Dict[str, Any] = {"webhook": webhook, "documento": documento}
        if establecimiento is not None:
            body["establecimiento"] = establecimiento
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        return self._http.request("POST", "/documentos/enviar", body, headers=headers)

    def generar_xml(self, documento: Dict[str, Any], *, establecimiento: Optional[str] = None) -> Dict[str, Any]:
        """Genera el XML UBL 2.1 sin enviarlo a SUNAT."""
        body: Dict[str, Any] = {"documento": documento}
        if establecimiento is not None:
            body["establecimiento"] = establecimiento
        return self._http.request("POST", "/documentos/xml", body)

    def consultar(self, id: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/documentos/{_id(id)}")

    def buscar(self, tipo_comprobante: str, serie: str, correlativo: str) -> Dict[str, Any]:
        return self._http.request(
            "GET",
            "/documentos/buscar",
            query={"tipo_documento": tipo_comprobante, "serie": serie, "correlativo": correlativo},
        )

    def listar(
        self,
        *,
        pagina: Optional[int] = None,
        limite: Optional[int] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        tipo: Optional[str] = None,
        estado: Optional[str] = None,
        buscar: Optional[str] = None,
        establecimiento: Optional[str] = None,
    ) -> Any:
        return self._http.request(
            "GET",
            "/empresas/documentos",
            query={
                "page": pagina,
                "limite": limite,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "tipo": tipo,
                "estado": estado,
                "buscar": buscar,
                "establecimiento": establecimiento,
            },
        )

    def anular(self, tipo_comprobante: str, serie: str, correlativo: str, motivo: str) -> Dict[str, Any]:
        """Comunicación de baja (facturas) o resumen diario (boletas), dentro del plazo de SUNAT."""
        return self._http.request(
            "POST",
            "/documentos/anular",
            {
                "documento": {
                    "tipoComprobante": tipo_comprobante,
                    "serie": serie,
                    "correlativo": correlativo,
                    "motivo": motivo,
                }
            },
        )

    def reenviar(self, id: str) -> Dict[str, Any]:
        return self._http.request("POST", f"/documentos/{_id(id)}/reenviar")

    def eventos(self, id: str) -> Any:
        return self._http.request("GET", f"/documentos/{_id(id)}/eventos")

    def eliminar(self, id: str) -> None:
        self._http.request("DELETE", f"/documentos/{_id(id)}")

    def url_archivo(self, id: str, formato: str = "pdf") -> str:
        """URL pública del PDF (A4), ticket, XML o CDR."""
        if formato not in _EXTENSION:
            raise ValueError("Formato no válido. Usa pdf, ticket, xml o cdr.")
        return self._http.file_url(f"/documentos/{_id(id)}{_EXTENSION[formato]}")

    def descargar(self, id: str, formato: str = "pdf") -> bytes:
        return self._http.download(self.url_archivo(id, formato))
