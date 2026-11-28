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
print(envio["enlaces"]["pdf"])    # PDF A4; también pdfTicket (80 mm), pdfTicket58 (58 mm), xml y cdr
```

El token decide el entorno: `sk_test_` envía a SUNAT Beta (demo) y `sk_live_` a producción. Un rechazo de SUNAT no es una excepción: vuelve con `estado == "RECHAZADA"` y el motivo en `envio["sunat"]`.

## Exonerada en la Amazonía (Ley 27037)

Empresas de la Amazonía que venden para consumo en la misma región: ítems con `tipoIgv` `"20"` y `amazonia`, que agrega la leyenda de SUNAT (`"bienes"` → 2001, `"servicios"` → 2002, `"construccion"` → 2003). Sirve en facturas y boletas.

```python
envio = facturalo.documentos.enviar({
    **documento,
    "amazonia": "bienes",
    "items": [
        {"unidadMedida": "NIU", "descripcion": "ARROZ COSTEÑO 5KG", "cantidad": 10, "precioUnitario": 25, "tipoIgv": "20"},
    ],
})
```

Sin ningún ítem exonerado la API responde 422 (SUNAT lo rechazaría con 3283/3284/3285).

## Percepción, retención, otros cargos y dólares

```python
# Percepción del IGV (51 = 2%, 52 = 1%, 53 = 0.5%): solo al contado, en facturas y boletas.
# Facturalo pone la operación 2001 y calcula la percepción en soles.
facturalo.documentos.enviar({**documento, "percepcion": {"tipo": "51"}})

# Retención del IGV (código 62, 3%): solo facturas a un cliente con RUC.
facturalo.documentos.enviar({**documento, "retencion": {"tipo": "62", "porcentaje": 3}})

# Otros cargos globales (código 50): no forman parte de la base del IGV y se suman al total.
facturalo.documentos.enviar({**documento, "totalOtrosCargos": 15})

# En dólares con bolsas (ICBPER) o percepción, envía el tipo de cambio.
facturalo.documentos.enviar({**documento, "moneda": "USD", "tipoCambio": 3.75})
```

- Percepción, retención y detracción no se combinan entre sí: la API responde 422.
- Al crédito con cliente RUC, las `cuotas` deben sumar total + ICBPER + otros cargos − anticipos − detracción − retención.
- `tipoIgv` `"17"` es IVAP (arroz pilado, 4%): ese comprobante solo lleva ítems con IVAP.
- El ISC todavía no se emite por la API: `totalIsc` mayor a 0 responde 422.
- Un ítem gratuito no lleva `descuento`; el descuento debe ser menor que cantidad × precio y no puede dejar el precio neto en 0.00.
- Una línea gravada o IVAP tan pequeña que su impuesto sería 0 responde 422. Con `icbper` (bolsas) la cantidad es entera.
- La factura (01) va a un cliente con RUC, salvo exportación: los ítems {'node': '`tipoIgv: "40"`', 'php': '`tipoIgv` `40`', 'python': '`tipoIgv` `"40"`'} requieren `sunatTransaccion: "0200"`.
- Notas tipo 11 solo con ítems de exportación (40) y tipo 12 solo con IVAP (17). La nota de crédito 13 solo va sobre una factura, con `formaPago: "CREDITO"` y las `cuotas` del nuevo cronograma (se emite con importe 0).
- Cada anticipo tiene `monto` mayor a 0 y su suma no supera el importe del comprobante.

## Guía remitente (09): compra, venta a terceros y otros

Con serie T... la empresa del token es el remitente. Según el motivo van datos extra: `proveedor` es obligatorio con 02 (Compra) y 07 (Recojo de bienes transformados), `comprador` con 03 (Venta con entrega a terceros), y `descripcionMotivo` (máx. 100) con 13 (Otros) si no hay `observaciones`. Ambos llevan `tipoDocumento` (0, 1, 4, 6, 7 o A), `numeroDocumento` y `denominacion`.

```python
# Compra (02): el destinatario es tu propia empresa y va el proveedor.
guia = {
    "serie": "T001",
    "correlativo": "1",
    "fechaEmision": "2026-11-28",
    "tipoTransporte": "02",
    "motivoTraslado": "02",
    "cliente": {"tipoDocumento": "6", "numeroDocumento": "20600000001", "denominacion": "TU EMPRESA S.A.C."},
    "proveedor": {"tipoDocumento": "6", "numeroDocumento": "20512345678", "denominacion": "PROVEEDOR S.A.C."},
    "datosTraslado": {"fecha": "2026-11-28", "pesoBrutoTotal": 130, "pesoUnidadMedida": "KGM", "numeroBultos": 7},
    "datosTransportista": {"numeroPlaca": "ABC123"},
    "datosChofer": {"tipoDocumento": "1", "numeroDocumento": "45678912", "numeroLicencia": "Q45678912",
                    "nombres": "CARLOS", "apellidos": "RAMOS TORRES"},
    "puntoPartida": {"ubigeo": "150101", "direccion": "AV. ARGENTINA 1234 - LIMA"},
    "puntoLlegada": {"ubigeo": "040101", "direccion": "CALLE MERCADERES 456 - AREQUIPA"},
    "items": [{"codigo": "P001", "descripcion": "CAJA DE PRODUCTOS", "unidadMedida": "NIU", "cantidad": 5}],
}
facturalo.guias.enviar(guia)

# Venta con entrega a terceros (03): `cliente` es quien recibe y va el comprador.
base = {k: v for k, v in guia.items() if k != "proveedor"}
facturalo.guias.enviar({
    **base,
    "correlativo": "2",
    "motivoTraslado": "03",
    "cliente": {"tipoDocumento": "6", "numeroDocumento": "20605302379", "denominacion": "ALMACEN DESTINO S.A.C."},
    "comprador": {"tipoDocumento": "6", "numeroDocumento": "20111111111", "denominacion": "COMPRADOR S.A.C."},
})

# Otros (13): describe el motivo.
facturalo.guias.enviar({**base, "correlativo": "3", "motivoTraslado": "13",
                        "descripcionMotivo": "TRASLADO A TALLER DE REPARACION"})
```

- `proveedor` y `comprador` solo se aceptan en sus motivos. Con 02, 04, 07 y 18 el destinatario (`cliente`) es la propia empresa.
- Los motivos 08 (Importación) y 09 (Exportación) aún no se emiten por la API: responden 422.
- `observaciones` hasta 250 caracteres; la fecha de traslado no puede ser anterior a `fechaEmision`; `pesoBrutoTotal` y cada `cantidad` mayores a 0; `numeroBultos` entero.
- Con transporte público el transportista no puede tener el RUC de tu empresa. Con el indicador `TrasladoVehiculoM1L` no se exigen la placa ni `datosChofer`.

## Guía transportista (31)

La empresa del token es el transportista: van el remitente (dueño de la carga), el destinatario, la placa con su TUC, el conductor y el registro MTC. Si la guía remitente (09) relacionada es electrónica, `items` va vacío: SUNAT toma el detalle de esa guía. `indicadores` acepta `remitente` o `subcontratador` (quién paga el flete) y `traslado_total`.

```python
facturalo.guias.enviar({
    "serie": "V001",
    "correlativo": "1",
    "fechaEmision": "2026-11-24",
    "motivoTraslado": "01",
    "remitente": {"tipoDocumento": "6", "numeroDocumento": "20512345678", "denominacion": "COMERCIAL REMITENTE S.A.C."},
    "destinatario": {"tipoDocumento": "6", "numeroDocumento": "20605302379", "denominacion": "DISTRIBUIDORA DESTINO S.A.C."},
    "datosTransportista": {"numeroMTC": "1500123456"},
    "datosTraslado": {"fecha": "2026-11-24", "pesoBrutoTotal": 50, "pesoUnidadMedida": "KGM", "numeroBultos": 5,
                      "indicadores": ["remitente"]},
    "datosVehiculo": {"numeroPlaca": "ABC123", "numeroTUC": "15M21012345678"},
    "datosChofer": {"tipoDocumento": "1", "numeroDocumento": "45678912", "numeroLicencia": "Q45678912",
                    "nombres": "CARLOS", "apellidos": "RAMOS TORRES"},
    "puntoPartida": {"ubigeo": "150101", "direccion": "AV. ARGENTINA 1234 - LIMA"},
    "puntoLlegada": {"ubigeo": "040101", "direccion": "CALLE MERCADERES 456 - AREQUIPA"},
    "documentosRelacionados": [{"tipoDocumento": "09", "numeroDocumento": "T001-00000123"}],
    "items": [],
})
```

- `datosVehiculo.numeroTUC` es obligatorio: TUC, constancia de inscripción vehicular o certificado de habilitación vehicular (10 a 15 letras y números).
- Con una factura relacionada y `traslado_total`, `items` también puede ir vacío.
- Un indicador que no existe responde 422. Lista completa: [docs.facturalo.pe](https://docs.facturalo.pe).

## Validar una guía sin emitirla

`validar` recibe lo mismo que `enviar` (remitente o transportista) y responde si SUNAT la aceptaría: aplica las reglas de la API (422 como `enviar`), arma el XML y corre las reglas de SUNAT, sin usar el correlativo, guardar ni enviar nada.

```python
validacion = facturalo.guias.validar(guia)
if validacion["prediccion"] == "RECHAZADA":
    for e in validacion["errores"]:
        print(e["codigo"], e["mensaje"])
else:
    facturalo.guias.enviar(guia)
```

Si las reglas de SUNAT no están disponibles lanza `FacturaloApiError` con `status` 503: la guía se puede enviar igual.

## Recursos

| Cliente | Token | Recursos |
|---|---|---|
| `FacturaloClient` | `sk_test_...` / `sk_live_...` | `documentos` (enviar, generar_xml, consultar, buscar, listar, anular, reenviar, eventos, eliminar, url_archivo, descargar), `guias` (enviar, validar, consultar, consultar_ticket, eventos, listar, descargar), `consultas` (ruc, dni, tipo_cambio, placa, soat, licencia, codigo_producto_sunat…), `webhooks` (listar, reenviar), `sire.ventas` / `sire.compras` |
| `FacturaloCuentaClient` | `user_sk_...` | `empresas` (listar, obtener, verificar_ruc, crear, actualizar, webhook, regenerar_token…), `establecimientos`, `consultas` |

```python
facturalo.consultas.ruc("20100006538")
facturalo.consultas.tipo_cambio("2026-10-30")
# Código de producto SUNAT para un ítem, por su descripción
facturalo.consultas.codigo_producto_sunat("laptop core i5", limite=3)
facturalo.documentos.anular("01", "F001", "1", motivo="Error en los datos del cliente")
pdf = facturalo.documentos.descargar(envio["documento"]["id"], "pdf")  # bytes
```

## Errores

Todas heredan de `FacturaloError`. Los errores HTTP son `FacturaloApiError` con `status`, `code`, `errors` y `body`:

| Excepción | Cuándo |
|---|---|
| `FacturaloValidationError` | 400 / 422: datos inválidos (revisa `e.errors`) |
| `FacturaloAuthenticationError` | 401: token inválido o revocado |
| `FacturaloPermissionError` | 403: el token no puede hacer esto. `e.code` dice por qué (p. ej. `PLAN_SIN_API`) |
| `FacturaloNotFoundError` | 404 |
| `FacturaloRateLimitError` | 429 |
| `FacturaloConnectionError` | Red, DNS o timeout |

Los 402 de plan llegan como `FacturaloApiError`. Códigos de plan (`e.code`, constantes en `facturalo.errors`):

| Código | HTTP | Qué significa |
|---|---|---|
| `PLAN_SIN_API` | 403 | El plan Gratis no incluye la API de producción (`sk_live_`). Está incluida en los planes de pago de Facturalo ERP (Básico, Pro, Negocio) y en los de Facturalo API. En demo (`sk_test_`) la API funciona en todos los planes |
| `PLAN_SOLO_API` | 403 | Tu plan API no incluye los módulos de negocio (inventario, compras, cajas...) |
| `CLAVE_SOLO_WOOCOMMERCE` | 403 | La clave del plugin de WooCommerce solo sirve para emitir y consultar un comprobante |
| `BILLING_REQUIRED` / `BILLING_SUSPENDED` | 402 | Sin plan activo, o pendiente de pago |
| `QUOTA_EXCEEDED` / `SALDO_INSUFICIENTE` | 402 | Se usó el cupo del mes y no hay saldo |
| `PLAN_SIN_GUIAS` | 402 | El plan no incluye guías de remisión |
| `PLAN_NO_DISPONIBLE` | 422 | Una empresa con plan de Facturalo ERP intentó contratar un plan de Facturalo API (su plan de pago ya incluye la API) |

```python
from facturalo import FacturaloPermissionError
from facturalo.errors import PLAN_SIN_API

try:
    facturalo.documentos.enviar(documento)
except FacturaloPermissionError as e:
    if e.code == PLAN_SIN_API:
        ...  # Elige un plan Básico, Pro o Negocio en console.facturalo.pe/plan/planes
    raise
```

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
