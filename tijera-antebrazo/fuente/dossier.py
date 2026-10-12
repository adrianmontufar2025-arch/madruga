"""Dossier de fabricación en un solo PDF para imprimir: portada, cómo funciona, imágenes 3D, orden de
construcción, lista de materiales, presupuesto en Ecuador, proveedores y los planos a escala."""
import io
import json
import os
from urllib.parse import urlparse

from PIL import Image as PILImage
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

import lista_materiales as LM
import precios_ecuador as PE

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SALIDA = os.path.join(RAIZ, "dossier_fabricacion.pdf")
IMG = os.path.join(RAIZ, "imagenes", "sin_rotulo")
PLANOS = os.path.join(RAIZ, "planos_cortadora.pdf")

import matplotlib  # noqa: E402  (trae las fuentes DejaVu en cualquier sistema)

FUENTES = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
pdfmetrics.registerFont(TTFont("Texto", os.path.join(FUENTES, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Texto-Negrita", os.path.join(FUENTES, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Texto-Negrita", italic="Texto", boldItalic="Texto-Negrita")

TINTA = colors.HexColor("#1d2125")
SUAVE = colors.HexColor("#5b636b")
ACENTO = colors.HexColor("#c8561f")
FONDO = colors.HexColor("#eef0f2")
LINEA = colors.HexColor("#b5bac1")
CONF = {"alta": colors.HexColor("#1e7b34"), "media": colors.HexColor("#8a6d00"), "baja": colors.HexColor("#b42318")}

PAG = landscape(A4)
MARGEN = 14 * mm
TITULO_DOC = "Tijera de caña con apoyo de antebrazo"


def estilo(nombre, **kw):
    base = dict(fontName="Texto", fontSize=10, leading=13.5, textColor=TINTA, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(nombre, **base)


E = {
    "h1": estilo("h1", fontName="Texto-Negrita", fontSize=20, leading=24, spaceAfter=6),
    "h2": estilo("h2", fontName="Texto-Negrita", fontSize=13, leading=17, spaceBefore=8, spaceAfter=4),
    "p": estilo("p", spaceAfter=5),
    "pq": estilo("pq", fontSize=8.5, leading=11.5, textColor=SUAVE),
    "lista": estilo("lista", leftIndent=12, bulletIndent=2, spaceAfter=3),
    "paso": estilo("paso", fontSize=9.2, leading=11.8, leftIndent=14, bulletIndent=2, spaceAfter=1.6),
    "celda": estilo("celda", fontSize=7.6, leading=9.6),
    "celda_n": estilo("celda_n", fontName="Texto-Negrita", fontSize=7.6, leading=9.6),
    "cab": estilo("cab", fontName="Texto-Negrita", fontSize=7.8, leading=10),
    "pie": estilo("pie", fontSize=9.5, leading=13, textColor=SUAVE),
}

IMAGENES = [
    ("armada.png", "Conjunto armado",
     "Tijera de una mano con cuna de antebrazo, correa de hombro en el centro de gravedad y pata de apoyo plegada. "
     "El brazo en color piel es solo referencia."),
    ("en_la_mata.png", "En la mata",
     "La mano libre sostiene la caña y decide hacia dónde cae; la tijera corta al ras entre los retoños."),
    ("lateral_medidas.png", "Vista lateral y medidas de uso",
     "Postura parecida a la del machete: mano a 0,43 m del suelo y a 0,64 m del tallo. Corte a 11 mm del suelo, con "
     "el tubo a 45° y el patín apoyado."),
    ("cabezal_detalle.png", "Cabezal de corte al ras",
     "Fondo plano: gancho y placa base al mismo nivel, patín de UHMW de 3 mm debajo."),
    ("cabezal_abierto.png", "Cabezal con la cuchilla abierta",
     "Cuchilla abierta 62°. Entra una caña de hasta Ø65 mm en la garganta."),
    ("cabezal_planta.png", "Planta del cabezal",
     "Vista desde arriba con la cuchilla abierta. El círculo marca la capacidad de Ø65 mm."),
    ("corte_parcial.png", "Corte parcial en mata apretada",
     "Caña Ø60 con más de la mitad afuera de la garganta: la cuchilla corta un 62 % del diámetro (naranja). El resto "
     "(verde) se parte con un leve tirón hacia el lado contrario al corte."),
    ("empunadura.png", "Mango ergonómico",
     "Gatillo largo de cuatro dedos, como el de la rozadora. Arriba atrás, un tope donde apoya el arco entre pulgar e "
     "índice para levantar la herramienta. Palanca de pulgar opcional y guardamonte amplio para guantes."),
    ("motor.png", "Dónde va el motor",
     "Dentro de la carcasa naranja, encima de la muñeca. Motor, reductor, husillo y tuerca tiran de la varilla, que "
     "baja por dentro del tubo hasta el balancín del cabezal."),
    ("reposo.png", "Reposo: parada sola junto a la mata",
     "Mientras las dos manos llevan la caña al pilo, la tijera queda parada sobre el patín y la pata, con las puntas "
     "clavadas en la tierra y la cuchilla cerrada. Se vuelca recién a los 27° de pendiente."),
    ("despiece.png", "Despiece",
     "Códigos P: piezas a fabricar, con plano. Códigos C: componentes comerciales."),
]


def jpeg(ruta):
    """Imagen en JPEG (calidad 90) para que el PDF pese menos; para imprimir no se nota la diferencia."""
    buf = io.BytesIO()
    PILImage.open(ruta).convert("RGB").save(buf, "JPEG", quality=90)
    buf.seek(0)
    return buf


def dominio(url):
    if not url:
        return "—"
    return urlparse(url).netloc.replace("www.", "") or url


def numero(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class Dossier(BaseDocTemplate):
    def __init__(self, ruta, paginas_planos_desde):
        super().__init__(ruta, pagesize=PAG, leftMargin=MARGEN, rightMargin=MARGEN, topMargin=MARGEN,
                         bottomMargin=MARGEN + 4 * mm, title="Dossier de fabricación · " + TITULO_DOC,
                         author="Diseño conceptual Rev. B", subject="Prototipo de tijera de caña")
        self.planos_desde = paginas_planos_desde
        marco = Frame(MARGEN, MARGEN + 4 * mm, PAG[0] - 2 * MARGEN, PAG[1] - 2 * MARGEN - 4 * mm, id="cuerpo",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        portada = Frame(0, 0, PAG[0], PAG[1], id="portada", leftPadding=0, rightPadding=0, topPadding=0,
                        bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="Portada", frames=[portada], onPage=self.dibujar_portada),
                               PageTemplate(id="Cuerpo", frames=[marco], onPage=self.pie)])

    def pie(self, c, doc):
        c.saveState()
        c.setStrokeColor(LINEA)
        c.setLineWidth(0.5)
        c.line(MARGEN, MARGEN, PAG[0] - MARGEN, MARGEN)
        c.setFont("Texto", 7.5)
        c.setFillColor(SUAVE)
        c.drawString(MARGEN, MARGEN - 9, f"{TITULO_DOC} · Dossier de fabricación · Rev. B, conceptual")
        c.drawRightString(PAG[0] - MARGEN, MARGEN - 9, f"pág. {doc.page}")
        c.restoreState()

    def dibujar_portada(self, c, doc):
        with open(os.path.join(RAIZ, "visor", "piezas.json"), encoding="utf-8") as f:
            datos = json.load(f)
        W, H = PAG
        c.saveState()
        c.setFillColor(colors.HexColor("#e3e6e1"))
        c.rect(0, 0, W, H, stroke=0, fill=1)
        # imagen principal a la derecha
        ruta = os.path.join(IMG, "en_la_mata.png")
        iw, ih = 1600, 1000
        alto = H
        ancho = alto * iw / ih
        c.drawImage(ImageReader(jpeg(ruta)), W - ancho + 70 * mm, 0, ancho, alto)
        # banda de texto
        c.setFillColor(colors.white)
        c.rect(0, 0, 128 * mm, H, stroke=0, fill=1)
        c.setFillColor(ACENTO)
        c.rect(0, H - 6 * mm, 128 * mm, 6 * mm, stroke=0, fill=1)
        x = 14 * mm
        y = H - 30 * mm
        c.setFillColor(SUAVE)
        c.setFont("Texto-Negrita", 9)
        c.drawString(x, y, "DOSSIER DE FABRICACIÓN DEL PROTOTIPO")
        y -= 14 * mm
        c.setFillColor(TINTA)
        c.setFont("Texto-Negrita", 25)
        for linea in ("Tijera de caña", "con apoyo", "de antebrazo"):
            c.drawString(x, y, linea)
            y -= 10.5 * mm
        y -= 2 * mm
        c.setFont("Texto", 10.5)
        c.setFillColor(SUAVE)
        for linea in ("Corte selectivo al ras de cañas de hasta 6 cm,",
                      "con una mano, entre matas cerradas y retoños.",
                      "Pangua, Cotopaxi · Ecuador"):
            c.drawString(x, y, linea)
            y -= 5.4 * mm
        y -= 8 * mm
        cifras = [("Ø65 mm", "capacidad de corte"), ("11 mm", "altura de corte"),
                  (f"{datos['masa_total_g'] / 1000:.1f} kg".replace(".", ","), "masa sin batería"),
                  ("36 V", "batería al cinturón")]
        for i, (v, t) in enumerate(cifras):
            cx = x + (i % 2) * 52 * mm
            cy = y - (i // 2) * 16 * mm
            c.setFillColor(ACENTO)
            c.setFont("Texto-Negrita", 15)
            c.drawString(cx, cy, v)
            c.setFillColor(SUAVE)
            c.setFont("Texto", 8.5)
            c.drawString(cx, cy - 5 * mm, t)
        y -= 40 * mm
        c.setFillColor(TINTA)
        c.setFont("Texto-Negrita", 9)
        c.drawString(x, y, "Contenido")
        y -= 5.5 * mm
        c.setFont("Texto", 8.8)
        for t in ("1. Cómo funciona y cómo imprimir", "2. Imágenes 3D", "3. Orden de construcción",
                  "4. Lista de materiales", "5. Presupuesto en Ecuador y proveedores",
                  f"6. Planos a escala (desde la pág. {self.planos_desde})"):
            c.drawString(x, y, t)
            y -= 5 * mm
        c.setFont("Texto", 7.5)
        c.setFillColor(SUAVE)
        c.drawString(x, 14 * mm, "Rev. B · diseño conceptual para prototipo · octubre de 2026")
        c.drawString(x, 10 * mm, "Confirmar la fuerza de corte con un ensayo antes de fabricar las piezas de acero.")
        c.restoreState()


def tabla(filas, anchos, cabecera=1, estilos_extra=()):
    t = Table(filas, colWidths=anchos, repeatRows=cabecera)
    est = [("FONT", (0, 0), (-1, -1), "Texto", 7.6),
           ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("BACKGROUND", (0, 0), (-1, cabecera - 1), FONDO),
           ("LINEBELOW", (0, 0), (-1, -1), 0.3, LINEA),
           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
           ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2)]
    t.setStyle(TableStyle(est + list(estilos_extra)))
    return t


def P(texto, e="celda"):
    return Paragraph(texto, E[e])


def seccion_intro(datos):
    h = []
    h.append(Paragraph("1. Cómo funciona", E["h1"]))
    h.append(Paragraph(
        "Herramienta eléctrica de una mano para cortar caña de hasta 6 cm de diámetro al ras del suelo, en matas "
        "cerradas y con retoños. Se trabaja igual que con el machete: <b>la mano libre sostiene la caña</b> y decide "
        "hacia dónde cae; la otra corta sin fuerza ni puntería. El antebrazo descansa en una cuna y una correa de "
        "hombro, como la de la rozadora, sostiene el resto del peso.", E["p"]))
    pasos = [
        "Se mete la punta del gancho (P01) entre las cañas, junto a la caña elegida. Si hay espacio, la punta "
        "envolvente con resorte (P17) rodea la caña; si está apretada, la punta cede y la tijera corta la parte que "
        "alcanza.",
        "El cabezal se apoya en el suelo sobre el patín (P04). El corte queda a 11 mm del suelo.",
        "Con la mano en el mango se aprieta el gatillo de cuatro dedos (P12). El motor tira de la varilla (P09), la "
        "varilla gira el balancín (P06) y la biela (P07) cierra la cuchilla (P02) contra el gancho.",
        "Para usar las dos manos, el pulgar baja la pata (P19): la tijera queda parada sola con la cuchilla cerrada "
        "mientras la caña se lleva al pilo.",
        "Para una caña virada, se gira el antebrazo y el cabezal queda de canto.",
    ]
    for i, t in enumerate(pasos, 1):
        h.append(Paragraph(t, E["lista"], bulletText=f"{i}."))
    a = datos
    h.append(Paragraph("Cifras del modelo", E["h2"]))
    filas = [[P("Concepto", "cab"), P("Valor", "cab")]]
    for k, v in [
        ("Capacidad de corte", "tallos de hasta Ø65 mm; corte parcial de más de la mitad del diámetro si la caña está apretada"),
        ("Masa sin batería", f"≈ {a['masa_total_g'] / 1000:.1f} kg".replace(".", ",")),
        ("Accionamiento", "motor sin escobillas 36 V 300–400 W, reductor 15:1, husillo de bolas SFU1605, balancín y biela"),
        ("Muñeca", f"{numero(a['momento_muneca_Nm'])[:-1]} N·m sin apoyo; {numero(a['aire_cuna']['muneca_Nm'])[:-1]} N·m con la cuna; "
                   f"{numero(a['apoyado']['muneca_Nm'])[:-1]} N·m con el patín apoyado".replace(",0 ", " ")),
        ("Parada sola (pata abajo)", f"se vuelca recién a los {a['reposo']['pendiente_max_grados']}° de pendiente"),
        ("Fuerza de corte supuesta", "3–3,5 kN para cañas de 6 cm: confirmar con el ensayo"),
    ]:
        filas.append([P(k, "celda_n"), P(v)])
    h.append(tabla(filas, [55 * mm, 200 * mm]))
    h.append(Paragraph("Cómo imprimir este documento", E["h2"]))
    for t in [
        f"Las páginas 1 a {DOSSIER_PAGINAS[0]} son A4 horizontal y se imprimen en cualquier impresora.",
        "Los planos van en su tamaño original para conservar la escala: el conjunto en A2 y las piezas en A3. Para "
        "medir sobre el papel hay que imprimirlos al 100 % (tamaño real) en una imprenta.",
        "Si se imprimen en A4 salen reducidos: sirven para leer, pero no hay que medir sobre el papel; se usan las "
        "cotas.",
        "Para el corte láser se entregan los archivos DXF del paquete (escala 1:1), no el papel. El plano del patín "
        "P04 impreso al 100 % sirve como plantilla para cortarlo a mano.",
    ]:
        h.append(Paragraph(t, E["lista"], bulletText="•"))
    h.append(PageBreak())
    return h


def seccion_imagenes():
    h = [Paragraph("2. Imágenes 3D", E["h1"])]
    ancho = PAG[0] - 2 * MARGEN
    alto_max = PAG[1] - 2 * MARGEN - 40 * mm
    for i, (archivo, titulo, texto) in enumerate(IMAGENES, 1):
        w = ancho
        hgt = w * 1000 / 1600
        if hgt > alto_max:
            hgt = alto_max
            w = hgt * 1600 / 1000
        bloque = [Paragraph(f"Fig. {i}. {titulo}", E["h2"]),
                  Image(jpeg(os.path.join(IMG, archivo)), width=w, height=hgt),
                  Spacer(1, 3 * mm), Paragraph(texto, E["pie"])]
        h.append(KeepTogether(bloque))
        h.append(PageBreak())
    return h


def seccion_construccion():
    h = [Paragraph("3. Orden de construcción", E["h1"]),
         Paragraph("Una propuesta de orden para el primer prototipo. Los detalles de cada pieza están en las notas de "
                   "su plano.", E["p"])]
    etapas = [
        ("Antes de fabricar", [
            "Medir la fuerza de corte en unas 20 cañas de 6 cm, con una gata hidráulica y una celda de carga. El diseño "
            "supone 3–3,5 kN.",
            "Pedir las cotizaciones de la hoja de presupuesto: aceros y temple a Böhler (Quito), corte láser, torre "
            "CNC, UHMW. Importar juntos el motor con reductor y el husillo, en un solo envío por courier.",
        ]),
        ("Fabricar las piezas", [
            "Corte láser desde los DXF (borrar antes las capas COTAS, TEXTO, EJES y MARCO): P01, P02, P03, P06, P13, P17. "
            "P07 de platina 16 x 6. El patín P04 a mano o con router, con la plantilla.",
            "Temple: P01 a 52–55 HRC, P02 a 56–58 HRC (el D2 se templa a 1.010–1.040 °C), P17. P06 se compra ya "
            "bonificado (V320).",
            "Afilar la cuchilla P02 con bisel de 25–30° de un solo lado, con la cara plana contra el gancho. Rectificar "
            "el borde del gancho P01 a escuadra, sin filo.",
            "Mecanizar la torre P05 desde el STEP. En el torno: horquilla de tiro (C04), extremos del tubo P08 y de la "
            "varilla P09, perno pivote si no se importa (hombro Ø12, rosca M10). Escariar los agujeros de P06 y P07.",
            "Plegar P13 en aluminio 5052-H32 con radio interior de 9 mm o más.",
            "Imprimir en 3D P10, P11, P12, P14, P16, P18 y la abrazadera de P19, en PETG o nylon (el PLA se ablanda al "
            "sol).",
        ]),
        ("Montar", [
            "Cabezal: placa base P03 y gancho P01 a media madera, con tornillos M6 avellanados desde abajo; patín P04 "
            "debajo; torre P05 encima.",
            "Cuchilla P02 en el perno pivote C06 con las arandelas Belleville: dejar un juego de 0,05–0,1 mm entre "
            "cuchilla y gancho. Punta P17 con su pasador y resorte (C07).",
            "Balancín P06, biela P07 y varilla P09. Tubo P08: entra 40 mm en la torre y 20 mm en la carcasa, con epoxi "
            "estructural y pasador Ø4.",
            "Motor, reductor, husillo y tuerca dentro de la carcasa P10; unir la tuerca con la varilla.",
            "Mango P11 con gatillo P12 y palanca P18; cuna P13, P14 y P15; anilla P16; pata P19 con su cable (C09).",
            "Electrónica: controlador, sensor Hall del gatillo, sensor de presencia en el mango, batería al cinturón "
            "con cable espiral.",
        ]),
        ("Probar", [
            "Sin batería: mover el mecanismo a mano. La cuchilla debe barrer toda la garganta sin rozar.",
            "Con batería y sin caña: el freno al soltar el gatillo y el modo reposo (al quitar la mano, la cuchilla se "
            "cierra y queda bloqueada).",
            "Cortar cañas de 2, 4 y 6 cm midiendo la corriente del motor; probar el corte parcial en una mata apretada.",
            "Probar en la ladera la postura, la correa y la pata, con tierra suelta, mojada y con piedras.",
            "Regla de trabajo: la mano que sostiene la caña siempre a unos 40 cm o más del corte, y usar botas.",
        ]),
    ]
    n = 1
    for titulo, pasos in etapas:
        h.append(Paragraph(titulo, E["h2"]))
        for t in pasos:
            h.append(Paragraph(t, E["paso"], bulletText=f"{n}."))
            n += 1
    h.append(PageBreak())
    return h


def seccion_lista(datos):
    piezas = {p["codigo"]: p for p in datos["piezas"]}
    piezas.setdefault("C09", dict(codigo="C09", nombre="Botón de pulgar + cable de la pata P19", material="Comercial",
                                  cantidad=1, masa_g=0, plano=False))
    codigos = sorted(piezas, key=lambda c: (c[0] != "P", c))
    planos = sorted(os.listdir(os.path.join(RAIZ, "planos_dxf")))
    h = [Paragraph("4. Lista de materiales", E["h1"]),
         Paragraph("Masas calculadas del modelo 3D. Las piezas P se fabrican (tienen plano); las C se compran.", E["p"])]
    filas = [[P(t, "cab") for t in ("Cód.", "Denominación", "Material / especificación", "Cant.", "Masa (g)",
                                     "Cómo se fabrica / qué comprar", "Plano")]]
    total = 0
    for c in codigos:
        p = piezas[c]
        masa = 900 if c == "C05" else p["masa_g"]
        if c != "C05":
            total += masa * p["cantidad"]
        nota = LM.FABRICACION.get(c) or LM.COMPRA.get(c, "")
        plano = next((n[:3] for n in planos if n.startswith(c + "_")), "comercial")
        filas.append([P(c, "celda_n"), P(p["nombre"]), P(p["material"]), P(str(p["cantidad"])),
                      P(f"{masa:,}".replace(",", ".") if masa else "—"), P(nota), P(plano)])
    total += datos["tornilleria_cables_g"]
    filas.append([P(""), P("Tornillería, cables y electrónica (estimado)"), P("Comercial"), P("1"),
                  P(str(datos["tornilleria_cables_g"])), P("No está dibujado en el modelo 3D."), P("—")])
    filas.append([P(""), P("<b>Masa sin batería</b>"), P(""), P(""), P(f"<b>{total:,}</b>".replace(",", ".")),
                  P("La batería (C05) va al cinturón y no se cuenta."), P("")])
    h.append(tabla(filas, [11 * mm, 44 * mm, 52 * mm, 11 * mm, 14 * mm, 118 * mm, 18 * mm]))
    h.append(PageBreak())
    return h


def seccion_presupuesto():
    h = [Paragraph("5. Presupuesto en Ecuador", E["h1"]),
         Paragraph(f"Consulta web del {PE.FECHA_CONSULTA}. Casi ningún proveedor ecuatoriano publica precios: la "
                   "mayoría de las filas son rangos estimados o precios de importación y hay que confirmarlos con "
                   "cotización. Confianza <font color='#1e7b34'><b>alta</b></font>: precio publicado en Ecuador; "
                   "<font color='#8a6d00'><b>media</b></font>: importación u otra presentación; "
                   "<font color='#b42318'><b>baja</b></font>: estimado. Los enlaces completos están en "
                   "lista_de_materiales.xlsx.", E["p"])]
    cab = [P(t, "cab") for t in ("Código(s)", "Qué comprar o encargar", "Proveedor · ciudad", "Cant.", "Mín. USD",
                                  "Máx. USD", "Conf.", "Fuente", "Nota")]
    filas = [cab]
    extra = []
    totales = {}
    for grupo in PE.GRUPOS:
        letra = grupo[0]
        filas.append([P(f"<b>{grupo}</b>")] + [""] * 8)
        extra.append(("SPAN", (0, len(filas) - 1), (-1, len(filas) - 1)))
        extra.append(("BACKGROUND", (0, len(filas) - 1), (-1, len(filas) - 1), colors.HexColor("#f6f7f8")))
        smin = smax = 0.0
        for (g, cod, que, medida, prov, ciudad, cant, pmin, pmax, conf, fuente, nota) in PE.LINEAS:
            if g != letra:
                continue
            smin += cant * pmin
            smax += cant * pmax
            filas.append([P(cod), P(f"{que}<br/><font color='#5b636b'>{medida}</font>"), P(f"{prov}<br/>{ciudad}"),
                          P(str(cant)), P(numero(cant * pmin)), P(numero(cant * pmax)),
                          P(f"<font color='{CONF[conf].hexval().replace('0x', '#')}'><b>{conf}</b></font>"),
                          P(dominio(fuente)), P(nota)])
        totales[letra] = (smin, smax)
    h.append(tabla(filas, [17 * mm, 50 * mm, 42 * mm, 11 * mm, 15 * mm, 15 * mm, 13 * mm, 30 * mm, 76 * mm],
                   estilos_extra=extra))
    sub = [sum(totales[g][i] for g in "ABCD") for i in (0, 1)]
    imp = 0.15
    filas = [[P("Resumen", "cab"), P("Mínimo (USD)", "cab"), P("Máximo (USD)", "cab")]]
    for g in PE.GRUPOS[:-1]:
        filas.append([P(g), P(numero(totales[g[0]][0])), P(numero(totales[g[0]][1]))])
    filas.append([P("<b>Subtotal (A a D)</b>"), P(f"<b>{numero(sub[0])}</b>"), P(f"<b>{numero(sub[1])}</b>")])
    filas.append([P("Imprevistos (15 %)"), P(numero(sub[0] * imp)), P(numero(sub[1] * imp))])
    filas.append([P("<b>Total estimado del prototipo</b>"), P(f"<b>{numero(sub[0] * (1 + imp))}</b>"),
                  P(f"<b>{numero(sub[1] * (1 + imp))}</b>")])
    filas.append([P(PE.GRUPOS[-1]), P(numero(totales['E'][0])), P(numero(totales['E'][1]))])
    h.append(Spacer(1, 5 * mm))
    h.append(KeepTogether([tabla(filas, [90 * mm, 30 * mm, 30 * mm])]))
    h.append(Paragraph("Importación por courier", E["h2"]))
    for t in PE.IMPORTACION:
        h.append(Paragraph(t.replace("https://", ""), E["lista"], bulletText="•"))
    h.append(PageBreak())
    h.append(Paragraph("Proveedores y talleres encontrados", E["h1"]))
    h.append(Paragraph("Confirmar dirección, existencias y precio antes de viajar.", E["p"]))
    filas = [[P(t, "cab") for t in ("Proveedor", "Ciudad", "Qué ofrece", "Web")]]
    for nombre, ciudad, que, web in PE.PROVEEDORES:
        filas.append([P(f"<b>{nombre}</b>"), P(ciudad), P(que), P(web.replace("https://", "").replace("http://", ""))])
    h.append(tabla(filas, [70 * mm, 45 * mm, 95 * mm, 59 * mm]))
    return h


DOSSIER_PAGINAS = [0]


def construir(ruta, planos_desde):
    with open(os.path.join(RAIZ, "visor", "piezas.json"), encoding="utf-8") as f:
        datos = json.load(f)
    doc = Dossier(ruta, planos_desde)
    historia = [NextPageTemplate("Cuerpo"), PageBreak()]
    historia += seccion_intro(datos) + seccion_imagenes() + seccion_construccion() + seccion_lista(datos)
    historia += seccion_presupuesto()
    doc.build(historia)
    return len(PdfReader(ruta).pages)


def main():
    tmp = SALIDA + ".tmp"
    n = construir(tmp, 0)                 # primera pasada: contar las páginas del dossier
    DOSSIER_PAGINAS[0] = n
    n = construir(tmp, n + 1)
    escritor = PdfWriter()
    for pagina in PdfReader(tmp).pages:
        escritor.add_page(pagina)
    for pagina in PdfReader(PLANOS).pages:
        escritor.add_page(pagina)
    escritor.add_metadata({"/Title": "Dossier de fabricación · " + TITULO_DOC})
    with open(SALIDA, "wb") as f:
        escritor.write(f)
    os.remove(tmp)
    print(SALIDA, f"{n} páginas de dossier + {len(PdfReader(PLANOS).pages)} planos")


if __name__ == "__main__":
    main()
