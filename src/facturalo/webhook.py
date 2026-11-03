"""Verificación de webhooks: la firma es HMAC-SHA256(secret, cuerpo crudo) en hexadecimal, en X-Facturalo-Firma."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict, Optional, Union

from .errors import FacturaloSignatureVerificationError

Payload = Union[str, bytes]


def verificar_firma(payload: Payload, firma: Optional[str], secret: str) -> None:
    """Recalcula la firma y la compara en tiempo constante con el header X-Facturalo-Firma.

    Usa el cuerpo crudo tal como llegó (`request.body` en Django, `await request.body()` en FastAPI,
    `request.get_data()` en Flask), nunca el JSON ya decodificado.

    :param payload: Cuerpo crudo del request.
    :param firma: Valor del header X-Facturalo-Firma.
    :param secret: El secreto del webhook de la empresa (whsec_...), distinto por entorno.
    :raises FacturaloSignatureVerificationError: si falta la firma o no coincide.
    """
    if firma is None or not firma.strip():
        raise FacturaloSignatureVerificationError("Falta el header X-Facturalo-Firma.")
    cuerpo = payload.encode("utf-8") if isinstance(payload, str) else payload
    esperada = hmac.new(secret.encode("utf-8"), cuerpo, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperada, firma.strip().lower()):
        raise FacturaloSignatureVerificationError("La firma del webhook no coincide.")


def construir_evento(payload: Payload, firma: Optional[str], secret: str) -> Dict[str, Any]:
    """Verifica la firma y devuelve el evento decodificado (id, evento, timestamp, entorno, documento, sunat...)."""
    verificar_firma(payload, firma, secret)
    try:
        evento = json.loads(payload)
    except ValueError as e:
        raise FacturaloSignatureVerificationError("El cuerpo del webhook no es JSON válido.") from e
    if not isinstance(evento, dict):
        raise FacturaloSignatureVerificationError("El cuerpo del webhook no es JSON válido.")
    return evento
