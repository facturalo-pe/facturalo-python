# Facturalo para Python

SDK oficial de [Facturalo](https://www.facturalo.pe) para Python: emite facturas, boletas, notas de crédito y débito y guías de remisión ante SUNAT, consulta RUC, DNI y tipo de cambio, trabaja el SIRE y verifica los webhooks. Cliente delgado sobre la [API REST v3](https://docs.facturalo.pe), con la misma superficie que los SDKs de [Node.js](https://www.npmjs.com/package/@facturalo-pe/node) y [PHP](https://packagist.org/packages/facturalo-pe/facturalo-php).

```bash
pip install facturalo-pe
```

Requiere Python 3.9 o superior.

## Tu primera factura

```python
import os
from facturalo import FacturaloClient

facturalo = FacturaloClient(os.environ["FACTURALO_TOKEN"])  # sk_test_... (demo) o sk_live_...

envio = facturalo.documentos.enviar(
    {
        "sunatTransaccion": "0101",
        "tipoComprobante": "01",
        "serie": "F001",
        "correlativo": "1",
        "fechaEmision": "2026-11-03",
        "moneda": "PEN",
        "formaPago": "CONTADO",
        "cliente": {
            "tipoDocumento": "6",
            "numeroDocumento": "20000000001",
            "denominacion": "EMPRESA S.A.C.",
            "direccion": "AV. LIMA 123 - LIMA - LIMA - LIMA",
        },
        "items": [
            {"unidadMedida": "NIU", "descripcion": "SERVICIO DE CONSULTORÍA", "cantidad": 1, "precioUnitario": 118, "tipoIgv": "10"},
        ],
    },
    idempotency_key="pedido-1001",
)

print(envio["estado"])            # ACEPTADA o RECHAZADA
print(envio["enlaces"]["pdf"])    # PDF A4; también pdfTicket, xml y cdr
```

El token decide el entorno: `sk_test_` envía a SUNAT Beta (demo) y `sk_live_` a producción. Un rechazo de SUNAT no es una excepción: vuelve con `estado == "RECHAZADA"` y el motivo en `envio["sunat"]`.

## Recursos

| Cliente | Token | Recursos |
|---|---|---|
| `FacturaloClient` | `sk_test_...` / `sk_live_...` | `documentos` (enviar, generar_xml, consultar, buscar, listar, anular, reenviar, eventos, eliminar, url_archivo, descargar), `guias` (enviar, consultar, consultar_ticket, eventos, listar, descargar), `consultas` (ruc, dni, tipo_cambio, placa, soat, licencia…), `webhooks` (listar, reenviar), `sire.ventas` / `sire.compras` |
| `FacturaloCuentaClient` | `user_sk_...` | `empresas` (listar, obtener, verificar_ruc, crear, actualizar, webhook, regenerar_token…), `establecimientos`, `consultas` |

```python
facturalo.consultas.ruc("20100006538")
facturalo.consultas.tipo_cambio("2026-10-30")
facturalo.documentos.anular("01", "F001", "1", motivo="Error en los datos del cliente")
pdf = facturalo.documentos.descargar(envio["documento"]["id"], "pdf")  # bytes
```

## Errores

Todas heredan de `FacturaloError`. Los errores HTTP son `FacturaloApiError` con `status`, `errors` y `body`:

| Excepción | Cuándo |
|---|---|
| `FacturaloValidationError` | 400 / 422: datos inválidos (revisa `e.errors`) |
| `FacturaloAuthenticationError` | 401: token inválido o revocado |
| `FacturaloPermissionError` | 403 |
| `FacturaloNotFoundError` | 404 |
| `FacturaloRateLimitError` | 429 |
| `FacturaloConnectionError` | Red, DNS o timeout |

## Reintentos e idempotencia

- Timeout por defecto de 90 s: el envío síncrono espera la respuesta de SUNAT.
- Los `GET` se reintentan ante 429, 502, 503, 504 o fallos de conexión.
- Los envíos solo se reintentan si llevan `idempotency_key`: el servidor deduplica y nunca se emite dos veces el mismo comprobante.

## Webhooks

```python
from facturalo import construir_evento, FacturaloSignatureVerificationError

# Django: request.body · Flask: request.get_data() · FastAPI: await request.body()
try:
    evento = construir_evento(cuerpo_crudo, request.headers.get("X-Facturalo-Firma"), os.environ["FACTURALO_WEBHOOK_SECRET"])
except FacturaloSignatureVerificationError:
    ...  # responde 400

if evento["evento"] == "documento.sunat.respuesta":
    ...
```

La firma es `HMAC-SHA256(secret, cuerpo crudo)` en hexadecimal y se compara en tiempo constante.

## Desarrollo

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Documentación completa: [docs.facturalo.pe](https://docs.facturalo.pe). Licencia MIT · © Consultia Digital S.A.C. (Facturalo).
