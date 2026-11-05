"""Transporte HTTP compartido por FacturaloClient y FacturaloCuentaClient. Uso interno."""

from __future__ import annotations

import time
from typing import Any, Dict, Mapping, Optional

import httpx

from .errors import FacturaloApiError, FacturaloConnectionError

DEFAULT_BASE_URL = "https://api.facturalo.pe/api/v3"
#: El envío síncrono espera la respuesta de SUNAT: puede tardar varios segundos.
DEFAULT_TIMEOUT_SECONDS = 90.0
_MAX_RETRIES = 2
_RETRYABLE_STATUS = {429, 502, 503, 504}

Json = Dict[str, Any]


class HttpClient:
    def __init__(
        self,
        token: str,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._token = token
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._http = http_client or httpx.Client(timeout=timeout)
        self._timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        body: Optional[Json] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Devuelve `data` del sobre `{ success, message, data }`: un dict, o una lista en los listados."""
        envelope = self._send(method, path, body, query or {}, dict(headers or {}))
        data = envelope.get("data")
        return data if isinstance(data, (dict, list)) else {}

    def file_url(self, path: str) -> str:
        return self._base_url + path

    def download(self, url: str) -> bytes:
        """Descarga binaria (PDF, XML, CDR). Las URLs de archivos son públicas: no envía el token."""
        try:
            response = self._http.get(url, timeout=self._timeout)
        except httpx.HTTPError as e:
            raise FacturaloConnectionError("No se pudo conectar con la API de Facturalo.") from e
        if not 200 <= response.status_code < 300:
            raise FacturaloApiError.for_status(response.status_code, f"No se pudo descargar {url}")
        return response.content

    def _send(
        self,
        method: str,
        path: str,
        body: Optional[Json],
        query: Mapping[str, Any],
        extra_headers: Dict[str, str],
    ) -> Json:
        headers = {
            # Facturalo no usa el esquema Bearer: el token va tal cual.
            "Authorization": self._token,
            "Accept": "application/json",
            # Facturalo registra desde dónde se emite cada comprobante (consola, API, SDK…).
            "X-Facturalo-Origen": "sdk-python",
            **extra_headers,
        }
        params = {
            k: ("true" if v else "false") if isinstance(v, bool) else v
            for k, v in query.items()
            if v is not None and v != ""
        }

        # GET siempre. POST solo con Idempotency-Key (el servidor deduplica): nunca se emite dos veces.
        can_retry = method == "GET" or "Idempotency-Key" in extra_headers
        attempts = _MAX_RETRIES + 1 if can_retry else 1

        last_error: Optional[Exception] = None
        for attempt in range(attempts):
            if attempt > 0:
                time.sleep((2**attempt) * 0.2)
            try:
                response = self._http.request(
                    method,
                    self._base_url + path,
                    json=body,
                    params=params or None,
                    headers=headers,
                    timeout=self._timeout,
                )
            except (httpx.ConnectError, httpx.ConnectTimeout) as e:
                last_error = FacturaloConnectionError("No se pudo conectar con la API de Facturalo.")
                last_error.__cause__ = e
                if can_retry:
                    continue
                raise last_error from e
            except httpx.HTTPError as e:
                raise FacturaloConnectionError("No se pudo conectar con la API de Facturalo.") from e

            try:
                decoded = response.json()
            except ValueError:
                decoded = {}
            if not isinstance(decoded, dict):
                decoded = {}

            if 200 <= response.status_code < 300:
                return decoded

            message = decoded.get("message") if isinstance(decoded.get("message"), str) else response.reason_phrase
            errors = decoded.get("errors") if isinstance(decoded.get("errors"), dict) else {}
            error = FacturaloApiError.for_status(response.status_code, message, errors, decoded or None)
            if can_retry and response.status_code in _RETRYABLE_STATUS and attempt < _MAX_RETRIES:
                last_error = error
                continue
            raise error

        raise last_error or FacturaloConnectionError("No se pudo conectar con la API de Facturalo.")

    def close(self) -> None:
        self._http.close()
