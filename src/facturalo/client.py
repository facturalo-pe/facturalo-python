from __future__ import annotations

from typing import Optional

import httpx

from ._http import DEFAULT_TIMEOUT_SECONDS, HttpClient
from .resources import Consultas, Documentos, Empresas, Establecimientos, Guias, Sire, Webhooks


class FacturaloClient:
    """Cliente con el token de una empresa (sk_test_... demo / sk_live_... producción).

    Emite y consulta comprobantes y guías, consulta RUC/DNI, revisa los webhooks enviados y trabaja el SIRE::

        facturalo = FacturaloClient(os.environ["FACTURALO_TOKEN"])
        envio = facturalo.documentos.enviar({...})
    """

    _PREFIJOS = ("sk_test_", "sk_live_")

    def __init__(
        self,
        token: str,
        *,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        if not token.startswith(self._PREFIJOS):
            raise ValueError(
                "FacturaloClient espera el token de una empresa (sk_test_... / sk_live_...). "
                "Para el token de usuario (user_sk_...) usa FacturaloCuentaClient."
            )
        self._http = HttpClient(token, base_url, http_client, timeout)
        #: "demo" o "prod", según el token.
        self.entorno = "prod" if token.startswith("sk_live_") else "demo"
        self.documentos = Documentos(self._http)
        self.guias = Guias(self._http)
        self.consultas = Consultas(self._http)
        self.webhooks = Webhooks(self._http)
        self.sire = Sire(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "FacturaloClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class FacturaloCuentaClient:
    """Cliente con el token de usuario (user_sk_...): administra empresas, sus tokens, webhooks y establecimientos.

    Útil para software que da de alta las empresas de sus clientes.
    """

    def __init__(
        self,
        token: str,
        *,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        if not token.startswith("user_sk_"):
            raise ValueError(
                "FacturaloCuentaClient espera el token de usuario (user_sk_...). "
                "Para emitir comprobantes usa FacturaloClient con el token de la empresa."
            )
        self._http = HttpClient(token, base_url, http_client, timeout)
        self.empresas = Empresas(self._http)
        self.establecimientos = Establecimientos(self._http)
        self.consultas = Consultas(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "FacturaloCuentaClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
