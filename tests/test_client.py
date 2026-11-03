import json

import httpx
import pytest

from facturalo import (
    FacturaloClient,
    FacturaloCuentaClient,
    FacturaloNotFoundError,
    FacturaloValidationError,
)


def cliente(handler, token="sk_test_abc"):
    return FacturaloClient(token, http_client=httpx.Client(transport=httpx.MockTransport(handler)))


def ok(data, status=200):
    return httpx.Response(status, json={"success": True, "message": "ok", "data": data})


def test_token_de_empresa_obligatorio():
    with pytest.raises(ValueError):
        FacturaloClient("user_sk_abc")
    with pytest.raises(ValueError):
        FacturaloCuentaClient("sk_test_abc")


def test_entorno_segun_token():
    assert FacturaloClient("sk_test_x").entorno == "demo"
    assert FacturaloClient("sk_live_x").entorno == "prod"


def test_enviar_documento_sin_bearer_y_con_idempotencia():
    visto = {}

    def handler(request: httpx.Request):
        visto["auth"] = request.headers["Authorization"]
        visto["idem"] = request.headers.get("Idempotency-Key")
        visto["url"] = str(request.url)
        visto["body"] = json.loads(request.content)
        return ok({"estado": "ACEPTADA", "enlaces": {"pdf": "https://x/doc.pdf"}})

    r = cliente(handler).documentos.enviar({"serie": "F001"}, idempotency_key="pedido-1")
    assert r["estado"] == "ACEPTADA"
    assert visto["auth"] == "sk_test_abc"
    assert visto["idem"] == "pedido-1"
    assert visto["url"] == "https://api.facturalo.pe/api/v3/documentos/enviar"
    assert visto["body"] == {"webhook": False, "documento": {"serie": "F001"}}


def test_rechazo_sunat_no_es_excepcion():
    r = cliente(lambda req: ok({"estado": "RECHAZADA", "sunat": {"codigo": "2800"}})).documentos.enviar({})
    assert r["estado"] == "RECHAZADA"


def test_errores_mapean_por_status():
    def handler(request):
        return httpx.Response(422, json={"success": False, "message": "Datos inválidos", "errors": {"serie": ["requerido"]}})

    with pytest.raises(FacturaloValidationError) as e:
        cliente(handler).documentos.enviar({})
    assert e.value.status == 422
    assert e.value.errors == {"serie": ["requerido"]}

    with pytest.raises(FacturaloNotFoundError):
        cliente(lambda req: httpx.Response(404, json={"message": "No existe"})).documentos.consultar("x")


def test_post_sin_idempotencia_no_se_reintenta():
    llamadas = []

    def handler(request):
        llamadas.append(1)
        return httpx.Response(503, json={"message": "caído"})

    with pytest.raises(Exception):
        cliente(handler).documentos.enviar({})
    assert len(llamadas) == 1


def test_get_se_reintenta(monkeypatch):
    monkeypatch.setattr("facturalo._http.time.sleep", lambda s: None)
    llamadas = []

    def handler(request):
        llamadas.append(1)
        return httpx.Response(503) if len(llamadas) < 3 else ok({"compra": 3.45})

    assert cliente(handler).consultas.tipo_cambio("2026-10-30") == {"compra": 3.45}
    assert len(llamadas) == 3


def test_query_sin_vacios():
    visto = {}

    def handler(request):
        visto["params"] = dict(request.url.params)
        return ok([])

    cliente(handler).documentos.listar(pagina=2, estado="ACEPTADA")
    assert visto["params"] == {"page": "2", "estado": "ACEPTADA"}


def test_url_archivo():
    c = cliente(lambda req: ok({}))
    assert c.documentos.url_archivo("abc", "ticket") == "https://api.facturalo.pe/api/v3/documentos/abc.ticket.pdf"
    with pytest.raises(ValueError):
        c.documentos.url_archivo("abc", "zip")
