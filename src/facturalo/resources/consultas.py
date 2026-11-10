from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import quote

from .._http import HttpClient


class Consultas:
    """Consultas de RUC, DNI, tipo de cambio, placa, SOAT, licencia y código de producto SUNAT."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def dni(self, dni: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/consulta/dni/{quote(dni, safe='')}")

    def ruc(self, ruc: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/consulta/ruc/{quote(ruc, safe='')}")

    def ruc_establecimientos(self, ruc: str) -> Any:
        return self._http.request("GET", f"/consulta/ruc/{quote(ruc, safe='')}/anexos")

    def ruc_representantes(self, ruc: str) -> Any:
        return self._http.request("GET", f"/consulta/ruc/{quote(ruc, safe='')}/representantes")

    def tipo_cambio(self, fecha: Optional[str] = None) -> Dict[str, Any]:
        """Tipo de cambio SUNAT de una fecha (AAAA-MM-DD); sin fecha, el de hoy."""
        return self._http.request("GET", "/consulta/tipo-cambio", query={"fecha": fecha})

    def codigo_producto_sunat(
        self, descripcion: str, *, tipo: Optional[str] = None, limite: Optional[int] = None
    ) -> Dict[str, Any]:
        """Código de producto SUNAT (UNSPSC de 8 dígitos) a partir de una descripción.

        Búsqueda semántica sobre el CUBSO. ``tipo``: bien, servicio, obra o consultoria_obra.
        Devuelve ``{consulta, modo, resultados: [{codigo, nombre, descripcion, tipo, ejemplos, similitud}]}``.
        Úsalo para completar ``codigoProductoSunat`` de cada ítem.
        """
        return self._http.request(
            "GET", "/catalogos/productos-sunat", query={"q": descripcion, "tipo": tipo, "limite": limite}
        )

    def placa(self, placa: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/consulta/placa/{quote(placa, safe='')}")

    def soat(self, placa: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/consulta/placa/{quote(placa, safe='')}/soat")

    def licencia(self, dni: str) -> Dict[str, Any]:
        return self._http.request("GET", f"/consulta/licencia/{quote(dni, safe='')}")
