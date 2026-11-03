"""Errores del SDK. Misma jerarquía que los SDKs de Node y PHP."""

from __future__ import annotations

from typing import Any, Dict, Optional


class FacturaloError(Exception):
    """Base de todos los errores del SDK."""


class FacturaloConnectionError(FacturaloError):
    """No se pudo conectar con la API (red, DNS, timeout)."""


class FacturaloSignatureVerificationError(FacturaloError):
    """La firma de un webhook falta o no coincide."""


class FacturaloApiError(FacturaloError):
    """La API respondió con un error HTTP. `status`, `errors` (validación) y `body` (respuesta completa)."""

    def __init__(
        self,
        message: str,
        status: int,
        errors: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.errors = errors or {}
        self.body = body

    @staticmethod
    def for_status(
        status: int,
        message: str,
        errors: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> "FacturaloApiError":
        cls = {
            401: FacturaloAuthenticationError,
            403: FacturaloPermissionError,
            404: FacturaloNotFoundError,
            400: FacturaloValidationError,
            422: FacturaloValidationError,
            429: FacturaloRateLimitError,
        }.get(status, FacturaloApiError)
        return cls(message, status, errors, body)


class FacturaloAuthenticationError(FacturaloApiError):
    """401: token ausente, inválido o revocado."""


class FacturaloPermissionError(FacturaloApiError):
    """403: el token no tiene permiso para esta operación."""


class FacturaloNotFoundError(FacturaloApiError):
    """404: el recurso no existe (o es de otra empresa)."""


class FacturaloValidationError(FacturaloApiError):
    """400 / 422: la petición no pasó validación o la operación no procede. Revisa `errors`."""


class FacturaloRateLimitError(FacturaloApiError):
    """429: demasiadas peticiones."""
