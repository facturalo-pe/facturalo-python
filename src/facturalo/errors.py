"""Errores del SDK. Misma jerarquía que los SDKs de Node y PHP."""

from __future__ import annotations

from typing import Any, Dict, Optional


class FacturaloError(Exception):
    """Base de todos los errores del SDK."""


class FacturaloConnectionError(FacturaloError):
    """No se pudo conectar con la API (red, DNS, timeout)."""


class FacturaloSignatureVerificationError(FacturaloError):
    """La firma de un webhook falta o no coincide."""


# Códigos (`code`) que la API envía en errores de plan y acceso. Ver `FacturaloApiError.code`.
BILLING_REQUIRED = "BILLING_REQUIRED"  # 402: sin plan activo
BILLING_SUSPENDED = "BILLING_SUSPENDED"  # 402: plan pendiente de pago, suspendido o cancelado
QUOTA_EXCEEDED = "QUOTA_EXCEEDED"  # 402: plan Gratis, se usó el cupo del mes
SALDO_INSUFICIENTE = "SALDO_INSUFICIENTE"  # 402: se pasó el cupo y no hay saldo
PLAN_SIN_GUIAS = "PLAN_SIN_GUIAS"  # 402: el plan no incluye guías de remisión
# 403: el plan Gratis no incluye la API de producción (sk_live_); está incluida en los planes
# Básico, Pro y Negocio. En demo (sk_test_) la API está abierta en todos los planes.
PLAN_SIN_API = "PLAN_SIN_API"
PLAN_SOLO_API = "PLAN_SOLO_API"  # 403: un plan API no incluye los módulos de negocio
CLAVE_SOLO_WOOCOMMERCE = "CLAVE_SOLO_WOOCOMMERCE"  # 403: la clave del plugin solo emite y consulta
PLAN_NO_DISPONIBLE = "PLAN_NO_DISPONIBLE"  # 422: empresa con plan ERP que intenta contratar un plan de Facturalo API (su plan ya incluye la API)


class FacturaloApiError(FacturaloError):
    """La API respondió con un error HTTP. `status`, `code` (p. ej. "PLAN_SIN_API"), `errors` (validación)
    y `body` (respuesta completa)."""

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
        code = (body or {}).get("code")
        self.code: Optional[str] = code if isinstance(code, str) else None

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
    """403: el token no tiene permiso para esta operación. `code` dice por qué (p. ej. "PLAN_SIN_API")."""


class FacturaloNotFoundError(FacturaloApiError):
    """404: el recurso no existe (o es de otra empresa)."""


class FacturaloValidationError(FacturaloApiError):
    """400 / 422: la petición no pasó validación o la operación no procede. Revisa `errors`."""


class FacturaloRateLimitError(FacturaloApiError):
    """429: demasiadas peticiones."""
