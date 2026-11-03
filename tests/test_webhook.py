import hashlib
import hmac

import pytest

from facturalo import FacturaloSignatureVerificationError, construir_evento, verificar_firma

SECRET = "whsec_prueba"
CUERPO = b'{"id":"evt_1","evento":"documento.sunat.respuesta"}'
FIRMA = hmac.new(SECRET.encode(), CUERPO, hashlib.sha256).hexdigest()


def test_firma_valida():
    assert construir_evento(CUERPO, FIRMA, SECRET)["evento"] == "documento.sunat.respuesta"
    verificar_firma(CUERPO.decode(), FIRMA.upper(), SECRET)


def test_firma_invalida_o_ausente():
    with pytest.raises(FacturaloSignatureVerificationError):
        verificar_firma(CUERPO, "00" * 32, SECRET)
    with pytest.raises(FacturaloSignatureVerificationError):
        verificar_firma(CUERPO, None, SECRET)
