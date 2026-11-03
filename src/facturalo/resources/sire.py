from __future__ import annotations

from typing import Any, Dict, Mapping, Optional
from urllib.parse import quote

from .._http import HttpClient


class LibroSire:
    """Registro de Ventas (RVIE) o de Compras (RCE) del SIRE."""

    def __init__(self, http: HttpClient, libro: str) -> None:
        self._http = http
        self._libro = libro

    def _path(self, periodo: str, accion: str) -> str:
        return f"/sire/{self._libro}/{quote(periodo, safe='')}/{accion}"

    def periodos(self) -> Any:
        return self._http.request("GET", f"/sire/{self._libro}/periodos")

    def resumen(self, periodo: str, query: Optional[Mapping[str, Any]] = None) -> Any:
        return self._http.request("GET", self._path(periodo, "resumen"), query=query)

    def resumen_comprobantes(self, periodo: str, query: Optional[Mapping[str, Any]] = None) -> Any:
        return self._http.request("GET", self._path(periodo, "resumen-comprobantes"), query=query)

    def comprobantes(self, periodo: str, query: Optional[Mapping[str, Any]] = None) -> Any:
        return self._http.request("GET", self._path(periodo, "comprobantes"), query=query)

    def inconsistencias(self, periodo: str, query: Optional[Mapping[str, Any]] = None) -> Any:
        return self._http.request("GET", self._path(periodo, "inconsistencias"), query=query)

    def inconsistencia_por_comprobante(self, periodo: str, query: Mapping[str, Any]) -> Any:
        return self._http.request("GET", self._path(periodo, "inconsistencia-por-comprobante"), query=query)

    def aceptar_propuesta(self, periodo: str, body: Optional[Dict[str, Any]] = None) -> Any:
        return self._http.request("POST", self._path(periodo, "aceptar-propuesta"), body or {})

    def exportar(self, periodo: str, query: Optional[Mapping[str, Any]] = None) -> Any:
        return self._http.request("GET", self._path(periodo, "exportar"), query=query)

    def descargar_ticket(self, num_ticket: str) -> Any:
        return self._http.request("GET", f"/sire/{self._libro}/tickets/{quote(num_ticket, safe='')}/descargar")

    def preliminares(self, periodo: str, query: Optional[Mapping[str, Any]] = None) -> Any:
        return self._http.request("GET", self._path(periodo, "preliminares"), query=query)

    def eliminar_preliminar(self, periodo: str, body: Dict[str, Any]) -> Any:
        return self._http.request("PUT", self._path(periodo, "eliminar-preliminar"), body)

    def eliminar_preliminar_registrado(self, periodo: str, body: Dict[str, Any]) -> Any:
        return self._http.request("PUT", self._path(periodo, "eliminar-preliminar-registrado"), body)

    def conciliar(self, periodo: str, body: Optional[Dict[str, Any]] = None) -> Any:
        return self._http.request("POST", self._path(periodo, "conciliar"), body or {})


class Sire:
    """SIRE: `sire.ventas` (RVIE) y `sire.compras` (RCE)."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self.ventas = LibroSire(http, "ventas")
        self.compras = LibroSire(http, "compras")

    def conciliacion(self, conciliacion_id: str) -> Any:
        return self._http.request("GET", f"/sire/conciliaciones/{quote(conciliacion_id, safe='')}")
