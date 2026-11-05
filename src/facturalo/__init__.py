"""SDK oficial de Facturalo para Python: facturación electrónica SUNAT por API.

    from facturalo import FacturaloClient

    facturalo = FacturaloClient(os.environ["FACTURALO_TOKEN"])
    envio = facturalo.documentos.enviar(documento, idempotency_key="pedido-1001")
"""

from .client import FacturaloClient, FacturaloCuentaClient
from .errors import (
    FacturaloApiError,
    FacturaloAuthenticationError,
    FacturaloConnectionError,
    FacturaloError,
    FacturaloNotFoundError,
    FacturaloPermissionError,
    FacturaloRateLimitError,
    FacturaloSignatureVerificationError,
    FacturaloValidationError,
)
from .webhook import construir_evento, verificar_firma

__version__ = "1.1.0"

__all__ = [
    "FacturaloClient",
    "FacturaloCuentaClient",
    "FacturaloError",
    "FacturaloApiError",
    "FacturaloAuthenticationError",
    "FacturaloConnectionError",
    "FacturaloNotFoundError",
    "FacturaloPermissionError",
    "FacturaloRateLimitError",
    "FacturaloSignatureVerificationError",
    "FacturaloValidationError",
    "construir_evento",
    "verificar_firma",
]
