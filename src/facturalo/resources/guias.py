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
        """Emite la guía: la serie decide el tipo (T... remitente 09, V... transportista 31).

        Remitente (09): `proveedor` {tipoDocumento, numeroDocumento, denominacion} es obligatorio con
        motivo 02 y 07; `comprador` (mismos campos) con motivo 03; `descripcionMotivo` (máx. 100) con
        motivo 13 si no hay `observaciones`. Los motivos 08 y 09 aún no se emiten (422).
        Transportista (31): `datosVehiculo.numeroTUC` es obligatorio (10 a 15 letras y números).
        """
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        return self._http.request("POST", "/guias/enviar", {"webhook": webhook, "guia": guia}, headers=headers)

    def validar(self, guia: Dict[str, Any]) -> Dict[str, Any]:
        """Valida la guía con el mismo cuerpo que `enviar`, sin usar el correlativo, guardar ni enviar.

        Aplica las reglas de la API (422 como `enviar`), arma el XML y corre las reglas de SUNAT.
        Devuelve `valido`, `prediccion` (ACEPTADA o RECHAZADA), `guia` {tipo, serie, correlativo},
        `errores` y `observaciones` ({codigo, mensaje, detalle}). Si las reglas de SUNAT no están
        disponibles lanza `FacturaloApiError` con `status` 503: la guía se puede enviar igual.
        """
        return self._http.request("POST", "/guias/validar", {"guia": guia})

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
