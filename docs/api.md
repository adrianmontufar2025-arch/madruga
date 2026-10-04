# API de datos abiertos del SERCOP: qué se verificó

Exploración hecha el **domingo 4 de octubre de 2026, entre las 19:02 y las 19:33 UTC**
(14:02 a 14:33 en Ecuador), con 27 consultas a la API oficial. No se usó el portal web
ni ninguna otra fuente. El detalle de cada consulta está en el
[anexo](#anexo-registro-de-consultas).

Todo lo que sigue sale de respuestas reales. Si algo no se pudo comprobar, se dice.

## Resumen

| Pregunta | Respuesta corta | ¿Sirve para Madruga? |
|---|---|---|
| 1. Frescura | El proceso aparece en la API **1 a 2 días** después de creado, pero **solo como ficha de planificación**: código, entidad, provincia y objeto. Los datos de la convocatoria (tipo, presupuesto, plazos) aparecen **2 a 5 semanas después de publicado**. | **No.** Lo útil llega tarde. |
| 2. ¿Procesos abiertos? | Los que tienen datos de convocatoria y `suppliers` nulo **ya recibieron ofertas** (3 a 14 oferentes) y están en calificación o puja. Los realmente nuevos solo existen como ficha de planificación. | **No**, salvo con datos mínimos. |
| 3. ¿Fecha límite en `record`? | **No.** `tenderPeriod` trae solo `startDate` (publicación). Sí trae `enquiryPeriod` (preguntas) y `awardPeriod` (calificación o puja). | No |
| 4. `internal_type` e Ínfima Cuantía | Valores vistos: `Catálogo electrónico - Compra directa`, `Catálogo electrónico - Mejor oferta`, `Subasta Inversa Electrónica`, `Contratos entre Entidades Públicas o sus subsidiarias` y `null`. Ínfima Cuantía no aparece: buscar "infima" o "ínfima" en 2026 da 0 resultados. | Parcial |

## Acceso y límites

- **Base:** `https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/`
- **Límite del servidor:** 60 consultas por minuto **por IP**. Lo impone Laravel
  (`ThrottleRequests`), y cada respuesta trae `X-RateLimit-Limit: 60` y
  `X-RateLimit-Remaining`.
- **429:** devuelve JSON `{"message": "Too Many Attempts.", "exception": "Illuminate\\Http\\Exceptions\\ThrottleRequestsException", ...}`
  con las cabeceras `Retry-After` (9 y 20 s observados) y `X-RateLimit-Reset`, que es un epoch.
  En esta exploración el cupo se agotó sin que lo causáramos: la IP de salida del
  entorno de pruebas era compartida y `X-RateLimit-Remaining` saltaba entre 3 y 47
  con una consulta por minuto de nuestra parte.
- **302 intermitente:** a veces la respuesta es `HTTP/1.0 302 Object Moved` con `Location: /`
  y sin cuerpo. No viene de Apache/Laravel, porque no trae sus cabeceras, sino de un equipo
  de borde, probablemente un firewall. Pasó con el agente de curl y también con un User-Agent
  propio, y la misma URL que dio 302 respondió 200 poco después (entre 40 s y 6 min). **Hay que tratarlo como un
  429:** esperar y reintentar.
- **Tiempo de respuesta:** entre 0,7 y 27 s.
- **Actualización diaria:** el campo `publishedDate` de `record` muestra un lote por día,
  entre las 14:13 y las 15:04 (hora de Ecuador): 26-sep 15:04, 1-oct 14:36, 2-oct 14:25 y
  3-oct 14:13. Una ejecución a las 06:00 ve lo cargado el día anterior por la tarde.

## `search_ocds`

`GET /search_ocds?year=2026&search=limpieza&page=1`

### Parámetros verificados

| Parámetro | ¿Funciona? | Evidencia |
|---|---|---|
| `year` | Sí | `year=2026` da `total: 104795`; los resultados traen `year: 2026` |
| `search` | Sí | `search=limpieza` da 1 710; `search=SIE` da 15 940 y busca también en el código del proceso; `search=infima` da 0 |
| `page` | Sí | 10 resultados por página; `pages = ceil(total / 10)` |

No se probaron otros parámetros, como mes, tipo o provincia.

### Estructura de la respuesta

```json
{"total": 1710, "page": 171, "pages": 171, "data": [ ... 10 objetos ... ]}
```

Cada elemento de `data`:

| Campo | Tipo observado | Notas |
|---|---|---|
| `id` | entero | Correlativo interno. Crece con la fecha en que el proceso entra a la base: unos 700 por día en 2026. |
| `ocid` | texto | `ocds-5wno2w-<CÓDIGO>-<id entidad>`. El código lleva el tipo de procedimiento como prefijo (`SIE-`, `CE-`, `RE-`...). |
| `year` | entero | |
| `month` | entero | Con datos de convocatoria, es el **mes de publicación** (`tenderPeriod.startDate`); se cumplió en los 3 casos revisados. En las fichas de planificación es el mes de `date`. |
| `method` | texto o `null` | `open`, `selective`, `direct`. |
| `internal_type` | texto o `null` | Ver la pregunta 4. |
| `locality` | texto o `null` | Cantón de la entidad, en mayúsculas. |
| `region` | texto o `null` | Provincia de la entidad, en mayúsculas, sin tildes pero con Ñ (`CAÑAR`, `MANABI`, `GALAPAGOS`, `LOS RIOS`). |
| `suppliers` | texto o `null` | Nombre del proveedor. Es `null` también en procesos **ya adjudicados** (`SIE-DPSO-2026-00001` tiene adjudicación en `record` y aquí `null`). **No sirve para saber si un proceso está abierto.** |
| `buyer` | texto | Entidad contratante. |
| `amount` | texto decimal o `null` | `"0.000000"` en subastas sin adjudicar; en catálogo es el valor de la orden. **No es el presupuesto referencial.** |
| `budget` | texto decimal o `null` | Solo visto en catálogo y régimen especial. `null` en todas las subastas. |
| `date` | ISO 8601 con `-05:00` | **Última actualización**, no la publicación. Ejemplo: `month: 8` con `date: 2026-10-03T14:13:18-05:00`. En las fichas de planificación es el día de creación a las 00:00. |
| `title` | texto o `null` | El código del proceso, o "Orden de compra CE-...". |
| `description` | texto o `null` | Objeto de la contratación. `null` en las fichas de planificación. |

### Tres tipos de fila

1. **Orden de catálogo electrónico** (`CE-`): compra ya hecha, con proveedor y monto. No es una oportunidad para ofertar.
   ```json
   {"id": 3301716, "ocid": "ocds-5wno2w-CE-20260003115291-2419", "year": 2026, "month": 10,
    "method": "direct", "internal_type": "Catálogo electrónico - Compra directa",
    "locality": "QUITO", "region": "PICHINCHA", "suppliers": "<proveedor>",
    "buyer": "MINISTERIO DE INFRAESTRUCTURA Y TECNOLOGIA", "amount": "278227.458000",
    "date": "2026-10-01T00:00:00-05:00", "title": "Orden de compra CE-20260003115291",
    "description": "Orden de compra para adquirir los siguientes productos:  SERVICIOS DE LIMPIEZA ...",
    "budget": "278227.458"}
   ```
2. **Proceso con datos de convocatoria** (`SIE-`, `RE-`...):
   ```json
   {"id": 3291775, "ocid": "ocds-5wno2w-SIE-IDE-2026-0003-95605", "year": 2026, "month": 9,
    "method": "open", "internal_type": "Subasta Inversa Electrónica",
    "locality": "QUITO", "region": "PICHINCHA", "suppliers": null, "buyer": "I-DE \"SHYRIS\"",
    "amount": "0.000000", "date": "2026-10-03T14:13:16-05:00",
    "title": "SIE-IDE-2026-0003-95605",
    "description": "CONTRATACIÓN DEL SERVICIO DE MANTENIMIENTO CORRECTIVO CON REPUESTOS PARA EL VEHÍCULO ...",
    "budget": null}
   ```
3. **Ficha de planificación** (todo `null` salvo ubicación, entidad y fecha):
   ```json
   {"id": 3297538, "ocid": "ocds-5wno2w-SIE-CGPN-2026-00012-2480", "year": 2026, "month": 9,
    "method": null, "internal_type": null, "locality": "QUITO", "region": "PICHINCHA",
    "suppliers": null, "buyer": "COMANDANCIA GENERAL - PLANTA CENTRAL", "amount": null,
    "date": "2026-09-25T00:00:00-05:00", "title": null, "description": null, "budget": null}
   ```
   El objeto del proceso no está aquí; solo aparece en `record`, en `planning.rationale`.

### Orden y paginación

- El orden se parece a "por última actualización, de antigua a reciente": **la última página
  trae lo más reciente**. No es estricto, porque dentro de una página se mezclan días.
- **No es estable:** `CE-20260003115291` apareció en la página 171 y, un minuto después, en la
  170. Hay que deduplicar por `ocid` y contar con que algún registro se salte.
- Para ver lo más reciente hay que pedir primero la página 1, que da `pages`, y luego la
  última. En la consulta sin `search` (10 480 páginas), la última página nunca respondió:
  2 veces 302 y 1 vez 429.

## `record?ocid=...`

`GET /record?ocid=ocds-5wno2w-SIE-IDE-2026-0003-95605`

Paquete OCDS 1.1 con **un** release compilado:

```
uri, license ("https://creativecommons.org/licenses/by/3.0/ec/"), version ("1.1"),
publisher {uid "ocds-5wno2w", name "Servicio Nacional de Contratación Pública (SERCOP)"},
publishedDate (cuándo se cargó a la API), publicationPolicy, extensions[8],
releases[0]:
  id ("<código>-<marca de tiempo UTC>[-compiled]"), tag, date, ocid, language, initiationType,
  buyer {id "EC-RUC-...", name},
  planning {rationale, budget {id}},
  tender {...}        # no existe en las fichas de planificación
  parties [...]       # dirección y contactPoint de entidad, oferentes y proveedores
  awards [...], auctions [...]   # cuando corresponda
```

`tender`, tal como vino en las 3 subastas revisadas:

| Campo | Ejemplo | Uso posible |
|---|---|---|
| `status` | `"active"` en las 3, incluso con oferentes o adjudicación | No indica si recibe ofertas |
| `title` | código del proceso | Código |
| `description` | objeto | Objeto |
| `procurementMethodDetails` | `"Subasta Inversa Electrónica"` | Tipo |
| `mainProcurementCategory` | `"services"` | |
| `lots[].value.amount` | `20119.42` | **Presupuesto referencial** (`tender.value` vino `null`) |
| `items[].classification` | CPC `871410018` y descripción | Filtrar por rubro |
| `tenderPeriod` | `{"startDate": "2026-09-18T16:45:00-05:00"}` | Publicación. **Sin `endDate`.** |
| `enquiryPeriod` | `startDate`, `endDate` (`2026-09-22T16:45`) | Plazo de preguntas |
| `awardPeriod` | `startDate` `2026-10-06T09:00`, `endDate` `2026-10-12T15:30` | Calificación o puja. En SIE-DPSO-2026-00001 su inicio coincidió con el de la puja (`auctions[].period`). |
| `numberOfTenderers` | 3, 6, 14 | Si es mayor que 0, ya hay ofertas |
| `tenderers`, `enquiries` | listas | **Datos personales** (ver abajo) |

Ficha de planificación (`tag: ["planning"]`): solo trae `buyer`, `parties` (dirección de la
entidad) y `planning.rationale` (objeto). Ejemplo: `SIE-CGPN-2026-00012-2480`, con
`date: 2026-09-25`, cargada el 26-sep a las 15:04 y **sin `tender` el 4-oct**.

**Datos personales:** `parties[].contactPoint`, `tender.tenderers` y `tender.enquiries`
pueden traer nombres de personas naturales y hasta números de cédula escritos en el texto de
las preguntas. **No se debe guardar ninguna respuesta cruda de `record` en este repositorio,
que es público.**

## Respuestas con evidencia

### 1. Frescura: ¿cuántos días entre la publicación y la aparición en la API?

- **`month` frente a `date`:** confirmado que `date` es la última actualización.
  `month` coincide con el mes de `tenderPeriod.startDate`, es decir, la publicación:

  | Proceso | Publicado (`tenderPeriod.startDate`) | `month` | `date` (última actualización) | Oferentes |
  |---|---|---|---|---|
  | SIE-DPSO-2026-00001 | 2026-08-31 | 8 | 2026-10-02 | 6, adjudicado el 1-oct |
  | SIE-DPSC-2026-018 | 2026-09-11 | 9 | 2026-10-01 | 14 |
  | SIE-IDE-2026-0003 | 2026-09-18 | 9 | 2026-10-03 | 3 |

- **Ficha de planificación:** llega **1 a 2 días** después de su fecha, según `publishedDate`:
  - SIE-CGPN-2026-00012: fecha 25-sep, cargada el 26-sep a las 15:04.
  - SIE-EPP-2026-180: fecha 1-oct, cargada el 2-oct a las 14:25.

  Comparando el `id` correlativo con la fecha de publicación, la ficha entra a la base entre
  1 y 3 días **antes** de que el proceso se publique. Esto es una estimación por
  interpolación, no un dato directo.
- **Datos de convocatoria:** se completan **2 a 5 semanas** después de la publicación. Evidencia:
  - Se revisaron 89 registros distintos: los más recientes de "limpieza" y "SIE" y una página
    del 25 al 27 de septiembre.
  - Las subastas con datos de convocatoria tienen `id` de entre fines de agosto y el 17-sep,
    según el correlativo. La más reciente verificada en `record` se publicó el 18-sep.
    **Ninguna subasta publicada después tenía datos de convocatoria.**
  - La única fila con datos de convocatoria y `id` cercano al 24-sep es
    `RE-CEP-EMACEP-2026-00006`, un contrato entre entidades públicas. Es régimen especial, así
    que no admite ofertas de proveedores privados, y su publicación no se verificó.
  - Las 38 subastas de la muestra creadas entre el 25-sep y el 2-oct son todas fichas de
    planificación.
  - Las 7 fichas del 25-sep seguían sin datos de convocatoria en `search_ocds` 9 días después.
    En una de ellas, `SIE-CGPN-2026-00012`, se comprobó también en `record`.
- **Veredicto: malo.** La API avisa rápido de que existe un proceso, pero sin presupuesto ni
  plazos. Los datos completos llegan cuando el plazo para ofertar ya pasó.

### 2. ¿Aparecen procesos todavía abiertos a ofertas?

- Con datos de convocatoria y `suppliers: null` aparecen muchos, pero los 3 revisados en
  `record` ya tenían ofertas: `numberOfTenderers` de 3, 14 y 6, este último adjudicado. El plazo
  de preguntas había vencido y la calificación o la puja había empezado o estaba por empezar.
- `suppliers: null` **no** significa abierto: SIE-DPSO-2026-00001 está adjudicado y en
  `search_ocds` muestra `suppliers: null`.
- Los procesos realmente recientes, que deberían estar abiertos, **solo existen como fichas de
  planificación**: código (que incluye el tipo), entidad, provincia, cantón y objeto. Faltan el
  presupuesto, la fecha límite y `internal_type`.
- No se pudo comprobar en el portal si esas fichas ya estaban publicadas o aún en preparación,
  porque eso implicaría usar el portal web.
- **Veredicto: malo** para el formato de aviso pedido, que necesita presupuesto y fecha límite.

### 3. ¿El detalle (`record`) trae la fecha límite para ofertar?

**No.** En las 3 subastas revisadas `tenderPeriod` solo tiene `startDate`. Las fechas que sí
vienen son:
- `enquiryPeriod.endDate`: fin de preguntas.
- `awardPeriod.startDate` y `endDate`: calificación o puja.
- `auctions[].period`: la puja misma.

La fecha límite de entrega de ofertas cae entre el fin de preguntas y el inicio de la
calificación, pero no viene en los datos. En las fichas de planificación no hay `tender`.

### 4. ¿Qué tipos hay en `internal_type`? ¿Se incluye Ínfima Cuantía?

En 89 registros distintos:

| `internal_type` | `method` | Registros |
|---|---|---|
| `null` (ficha de planificación) | `null` | 39 |
| `Catálogo electrónico - Compra directa` | `direct` | 29 |
| `Subasta Inversa Electrónica` | `open` | 19 |
| `Catálogo electrónico - Mejor oferta` | `selective` | 1 |
| `Contratos entre Entidades Públicas o sus subsidiarias` | `direct` | 1 |

- La muestra está sesgada hacia "limpieza" y "SIE". Seguramente existen otros tipos, como
  menor cuantía, cotización o licitación, que no se buscaron para no gastar consultas.
- **Ínfima Cuantía:** `search=infima` y `search=ínfima` con `year=2026` dan `total: 0`. No
  se encontró. Lo único no verificado es si existen con otro texto o código.

## Implicaciones para el diseño

Con los datos actuales, un aviso con "Presupuesto referencial" y "Recibe ofertas hasta"
**no se puede armar** a partir de la API para procesos que sigan abiertos. Queda por decidir:

- **A. Avisar con la ficha de planificación.** Llega 1 a 2 días después de su fecha y quizá
  antes de la publicación. Daría código y tipo (por el prefijo), entidad, provincia y objeto
  (`planning.rationale`, que exige una consulta a `record` por proceso), con presupuesto y plazo
  como "no disponible, ver en el portal". El filtro por rubro tendría que ser por palabras en
  el objeto, porque la ficha no trae CPC.
- **B. Replantear el servicio** con lo que sí trae la API: procesos en calificación o
  adjudicados, sirve para inteligencia de mercado pero no para ofertar.
- **C. No seguir** con esta fuente.

## Anexo: registro de consultas

Hora en UTC. Todas las consultas fueron a `https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/`,
con al menos 5 s entre una y otra; desde las 19:08 se dejó un minuto o más.

| Hora | Estado | Consulta |
|---|---|---|
| 18:44 | — | `search_ocds?year=2026&page=1`: bloqueada por la red del entorno, no llegó al SERCOP |
| 19:02 | 302 | `search_ocds?year=2026&page=1` (curl) |
| 19:02 | 200 | `search_ocds?year=2026&page=1` |
| 19:03 | 302 | `search_ocds?year=2026&page=10480` |
| 19:03 | 200 | `search_ocds?year=2026&search=limpieza&page=1` |
| 19:03 | 200 | `search_ocds?year=2026&search=limpieza&page=171` |
| 19:04 | 200 | `record?ocid=ocds-5wno2w-SIE-DPSO-2026-00001-537258` |
| 19:05 | 200 | `record?ocid=ocds-5wno2w-SIE-EPP-2026-180-253178` |
| 19:05 | 302 | `search_ocds?year=2026&search=limpieza&page=170` |
| 19:05 | 200 | `search_ocds?year=2026&search=limpieza&page=170` (reintento) |
| 19:07 | 200 | `record?ocid=ocds-5wno2w-SIE-DPSC-2026-018-19565` |
| 19:08 | 429 | `search_ocds?year=2026&page=10480` |
| 19:09 | 302 | `search_ocds?year=2026&page=10480` (reintento; se abandonó) |
| 19:10 | 200 | `search_ocds?year=2026&search=SIE&page=1` |
| 19:11 | 200 | `search_ocds?year=2026&search=SIE&page=1594` |
| 19:12 | 200 | `search_ocds?year=2026&search=SIE&page=1593` |
| 19:13 | 200 | `search_ocds?year=2026&search=SIE&page=1592` |
| 19:14 | 302 | `record?ocid=ocds-5wno2w-SIE-IDE-2026-0003-95605` |
| 19:16 | 200 | `record?ocid=ocds-5wno2w-SIE-IDE-2026-0003-95605` (reintento) |
| 19:17 | 302 | `search_ocds?year=2026&search=SIE&page=1530` |
| 19:19 | 302 | `search_ocds?year=2026&search=SIE&page=1530` (reintento 1) |
| 19:23 | 200 | `search_ocds?year=2026&search=SIE&page=1530` (reintento 2) |
| 19:25 | 429 | `search_ocds?year=2026&search=infima&page=1` |
| 19:26 | 429 | `search_ocds?year=2026&search=infima&page=1` (reintento 1) |
| 19:28 | 200 | `search_ocds?year=2026&search=infima&page=1` (reintento 2) |
| 19:29 | 200 | `search_ocds?year=2026&search=%C3%ADnfima&page=1` |
| 19:31 | 429 | `record?ocid=ocds-5wno2w-SIE-CGPN-2026-00012-2480` |
| 19:33 | 200 | `record?ocid=ocds-5wno2w-SIE-CGPN-2026-00012-2480` (reintento) |

Total: 27 consultas al SERCOP, con 16 respuestas 200, 7 de 302 y 4 de 429.

Fuente: SERCOP, datos abiertos, licencia Creative Commons Atribución 3.0 Ecuador.
