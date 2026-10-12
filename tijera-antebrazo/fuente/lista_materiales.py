"""Lista de materiales en hoja de cálculo (.xlsx), a partir de visor/piezas.json (lo genera exportar_3d.py)."""
import json
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

import precios_ecuador as PE

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SALIDA = os.path.join(RAIZ, "lista_de_materiales.xlsx")

FABRICACION = {
    "P01": "Corte láser, plasma o chorro de agua desde el DXF (chapa 8 mm). Rectificar el borde de cizalla a escuadra. "
           "Templar a 52-55 HRC.",
    "P02": "Corte por hilo o láser desde el DXF (chapa 5 mm). Afilar bisel de 25-30° por un solo lado, cara plana "
           "contra el gancho. Templar a 56-58 HRC.",
    "P03": "Corte por chorro de agua o CNC (placa 8 mm). Rebaje de media madera y avellanados. Anodizado.",
    "P04": "Corte CNC o a cuchilla desde el DXF (lámina 3 mm). Avellanados para los tornillos.",
    "P05": "Mecanizado CNC desde el STEP. Anodizado.",
    "P06": "Corte láser (chapa 8 mm), escariar los agujeros. Bonificado.",
    "P07": "Corte y taladrado de pletina 16 x 6. Escariar los agujeros.",
    "P08": "Cortar el tubo a medida. Con carbono: disco diamantado y sellar el corte con epoxi.",
    "P09": "Cortar el tubo y mecanizar los extremos.",
    "P10": "Prototipo: impresión 3D en PA-CF. Serie: inyección PA6-GF30.",
    "P11": "Prototipo: impresión 3D. Serie: inyección PA6-GF30 con sobremoldeo TPE de 3 mm.",
    "P12": "Prototipo: impresión 3D. Serie: inyección PA6-GF30.",
    "P13": "Corte láser y plegado (chapa 6 mm de 5052; el 6061-T6 se agrieta al doblar) + ala de 7 mm.",
    "P14": "Impresión 3D, o chapa de aluminio 5052 plegada.",
    "P15": "EVA de 5 mm cortada a cuchilla + correa de velcro cosida con hebilla de liberación rápida.",
    "P16": "Abrazadera impresa en 3D + anilla de acero inoxidable comercial.",
    "P17": "Corte láser o por hilo (chapa 6 mm). Mecanizar la bisagra.",
    "P18": "Impresión 3D con recubrimiento de TPE.",
    "P19": "Patas: tubo de aluminio cortado a 311 mm. Abrazadera impresa en 3D. Puntas de acero torneadas y templadas "
           "(Ø8 x 25 mm) + disco de caucho.",
}
COMPRA = {
    "C01": "Motor sin escobillas (BLDC) de 36 V y 300-400 W, con sensores Hall. Controlador con freno eléctrico.",
    "C02": "Reductor planetario 15:1 que acople al eje del motor.",
    "C03": "Husillo de bolas SFU1605 (Ø16 mm, paso 5 mm) con soporte de rodamiento. Largo según el plano de conjunto.",
    "C04": "Tuerca SFU1605 + horquilla de tiro mecanizada.",
    "C05": "Batería de herramienta de 36 V. Con 2,5 Ah pesa unos 0,9 kg y con 4 Ah unos 1,3 kg. Va al cinturón con "
           "cable espiral.",
    "C06": "Perno con hombro ISO 7379 de Ø12 x 25 mm (rosca M10, clase 12.9) + 2 arandelas Belleville DIN 2093 12,2 x 25 (mantienen el juego de 0,05-0,1 mm).",
    "C07": "Pasador Ø6 + separador + resorte de torsión de 0,3 N·m.",
    "C08": "Arnés simple de desbrozadora, con mosquetón de liberación rápida.",
    "C09": "Palanca de pulgar + cable de freno de bicicleta con funda.",
}

FUENTE = "Arial"
GRIS = PatternFill("solid", start_color="E7E9EC")
GRIS_CLARO = PatternFill("solid", start_color="F3F4F6")
FINO = Side(style="thin", color="B5BAC1")
BORDE = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)


def main():
    with open(os.path.join(RAIZ, "visor", "piezas.json"), encoding="utf-8") as f:
        datos = json.load(f)
    piezas = {p["codigo"]: p for p in datos["piezas"]}
    piezas.setdefault("C09", dict(codigo="C09", nombre="Botón de pulgar + cable de la pata P19", grupo="Brazo",
                                  material="Comercial", cantidad=1, masa_g=0, plano=False))
    codigos = sorted((c for c in piezas if c != "C05"), key=lambda c: (c[0] != "P", c))
    planos = set(os.listdir(os.path.join(RAIZ, "planos_dxf")))
    steps = set(os.listdir(os.path.join(RAIZ, "modelo_3d", "piezas_step")))

    def archivo(lista, cod):
        return next((n for n in sorted(lista) if n.startswith(cod + "_")), "—")

    wb = Workbook()
    ws = wb.active
    ws.title = "Lista de materiales"
    ws["A1"] = "Tijera de caña con apoyo de antebrazo · Lista de materiales (Rev. B, conceptual)"
    ws["A1"].font = Font(name=FUENTE, size=14, bold=True)
    ws["A2"] = ("Masas calculadas del modelo 3D (fuente/modelo.py). Diseño para prototipo: confirmar la fuerza de corte "
                "con un ensayo antes de fabricar las piezas de acero.")
    ws["A2"].font = Font(name=FUENTE, size=10, italic=True, color="555B63")

    cab = ["Código", "Denominación", "Grupo", "Material / especificación", "Cant.", "Masa unit. (g)", "Masa total (g)",
           "Cómo se fabrica / qué comprar", "Plano DXF", "Modelo 3D (STEP)"]
    fila_cab = 4
    for j, t in enumerate(cab, 1):
        c = ws.cell(row=fila_cab, column=j, value=t)
        c.font = Font(name=FUENTE, size=10, bold=True)
        c.fill = GRIS
        c.border = BORDE
        c.alignment = Alignment(vertical="center", wrap_text=True)

    def fila(r, p, nota):
        cod = p["codigo"]
        es_pieza = cod.startswith("P")
        valores = [cod, p["nombre"], p["grupo"], p["material"], p["cantidad"], p["masa_g"], f"=E{r}*F{r}", nota,
                   archivo(planos, cod) if es_pieza else "comercial", archivo(steps, cod) if es_pieza else "—"]
        for j, v in enumerate(valores, 1):
            c = ws.cell(row=r, column=j, value=v)
            c.font = Font(name=FUENTE, size=10)
            c.border = BORDE
            c.alignment = Alignment(vertical="top", wrap_text=j in (2, 4, 8))
            if j in (6, 7):
                c.number_format = "#,##0"

    r = fila_cab + 1
    for cod in codigos:
        p = piezas[cod]
        nota = FABRICACION.get(cod) or COMPRA.get(cod, "")
        if cod == "C09":
            nota += " Masa incluida en la fila de tornillería."
        fila(r, p, nota)
        r += 1
    fila(r, dict(codigo="—", nombre="Tornillería, cables y electrónica (controlador, sensor Hall del gatillo, "
                 "sensor de presencia)", grupo="Varios", material="Comercial", cantidad=1,
                 masa_g=datos["tornilleria_cables_g"]), "Estimado; no está dibujado en el modelo 3D.")
    ws.cell(row=r, column=9, value="—")
    ultima = r
    r += 1
    ws.cell(row=r, column=6, value="Masa sin batería (g)").font = Font(name=FUENTE, size=10, bold=True)
    c = ws.cell(row=r, column=7, value=f"=SUM(G{fila_cab + 1}:G{ultima})")
    c.font = Font(name=FUENTE, size=10, bold=True)
    c.number_format = "#,##0"
    c.border = BORDE
    fila_sin = r
    r += 2
    ws.cell(row=r, column=1, value="Al cinturón (no pesa en el brazo)").font = Font(name=FUENTE, size=10, bold=True)
    r += 1
    bat = dict(piezas["C05"])
    bat["masa_g"] = 900
    fila(r, bat, COMPRA["C05"])
    ws.cell(row=r, column=6).comment = None
    fila_bat = r
    r += 1
    ws.cell(row=r, column=6, value="Total con batería (g)").font = Font(name=FUENTE, size=10, bold=True)
    c = ws.cell(row=r, column=7, value=f"=G{fila_sin}+G{fila_bat}")
    c.font = Font(name=FUENTE, size=10, bold=True)
    c.number_format = "#,##0"
    c.border = BORDE
    r += 2
    notas = [
        "Notas",
        "Masa de la batería: 900 g para 2,5 Ah (estimado de catálogo). Con 4 Ah, unos 1.300 g.",
        "Los DXF están a escala 1:1: las piezas de chapa (P01, P02, P03, P04, P06, P07, P13, P17) van directo a corte;"
        " antes, borrar las capas COTAS, TEXTO, EJES y MARCO.",
        "Las piezas plásticas (P10, P11, P12, P14, P16, P18) se pueden imprimir en 3D desde el STEP para el prototipo.",
    ]
    for k, t in enumerate(notas):
        c = ws.cell(row=r + k, column=1, value=t)
        c.font = Font(name=FUENTE, size=10, bold=(k == 0))

    for col, ancho in zip("ABCDEFGHIJ", (8, 34, 16, 40, 6, 12, 12, 58, 42, 42)):
        ws.column_dimensions[col].width = ancho
    ws.freeze_panes = ws.cell(row=fila_cab + 1, column=3)
    ws.print_title_rows = f"{fila_cab}:{fila_cab}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    hoja_presupuesto(wb)
    hoja_proveedores(wb)
    wb.save(SALIDA)
    print(SALIDA)


COLOR_CONFIANZA = {"alta": "1E7B34", "media": "8A6D00", "baja": "B42318"}


def _celda(ws, r, c, v, negrita=False, formato=None, envolver=False, color=None, borde=True, relleno=None):
    celda = ws.cell(row=r, column=c, value=v)
    celda.font = Font(name=FUENTE, size=10, bold=negrita, color=color)
    celda.alignment = Alignment(vertical="top", wrap_text=envolver)
    if borde:
        celda.border = BORDE
    if formato:
        celda.number_format = formato
    if relleno:
        celda.fill = relleno
    return celda


def hoja_presupuesto(wb):
    ws = wb.create_sheet("Presupuesto Ecuador")
    ws["A1"] = "Presupuesto estimado del prototipo en Ecuador (USD)"
    ws["A1"].font = Font(name=FUENTE, size=14, bold=True)
    ws["A2"] = (f"Consulta web del {PE.FECHA_CONSULTA}. Casi ningún proveedor publica precios: la mayoría son rangos "
                "estimados o de importación, así que hay que confirmarlos con cotización. Algunos precios incluyen IVA "
                "(15 %) y otros no.")
    ws["A2"].font = Font(name=FUENTE, size=10, italic=True, color="555B63")
    cab = ["Grupo", "Código(s)", "Qué comprar o encargar", "Medida / cantidad", "Proveedor sugerido", "Ciudad", "Cant.",
           "Precio mín. (USD)", "Precio máx. (USD)", "Subtotal mín. (USD)", "Subtotal máx. (USD)", "Confianza",
           "Fuente", "Nota"]
    fila_cab = 4
    for j, t in enumerate(cab, 1):
        c = _celda(ws, fila_cab, j, t, negrita=True, envolver=True, relleno=GRIS)
        c.alignment = Alignment(vertical="center", wrap_text=True)
    usd = "#,##0.00"
    r = fila_cab + 1
    primera = r
    for grupo in PE.GRUPOS:
        letra = grupo[0]
        for j in range(1, len(cab) + 1):
            _celda(ws, r, j, grupo if j == 1 else None, negrita=True, relleno=GRIS_CLARO)
        r += 1
        for (g, cod, que, medida, prov, ciudad, cant, pmin, pmax, conf, fuente, nota) in PE.LINEAS:
            if g != letra:
                continue
            valores = [g, cod, que, medida, prov, ciudad, cant, pmin, pmax, f"=G{r}*H{r}", f"=G{r}*I{r}", conf,
                       fuente or "—", nota]
            for j, v in enumerate(valores, 1):
                c = _celda(ws, r, j, v, envolver=j in (2, 3, 4, 5, 6, 13, 14),
                           formato=usd if j in (8, 9, 10, 11) else None,
                           color=COLOR_CONFIANZA.get(conf) if j == 12 else None)
                if j == 13 and fuente:
                    c.hyperlink = fuente
                    c.font = Font(name=FUENTE, size=9, color="1F5FAD", underline="single")
            r += 1
    ultima = r - 1
    r += 1
    _celda(ws, r, 3, "Resumen", negrita=True, borde=False)
    _celda(ws, r, 10, "Mínimo (USD)", negrita=True, relleno=GRIS)
    _celda(ws, r, 11, "Máximo (USD)", negrita=True, relleno=GRIS)
    r += 1
    filas_grupo = []
    for grupo in PE.GRUPOS[:-1]:
        letra = grupo[0]
        _celda(ws, r, 3, grupo, borde=False)
        _celda(ws, r, 10, f'=SUMIF($A${primera}:$A${ultima},"{letra}",J${primera}:J${ultima})', formato=usd)
        _celda(ws, r, 11, f'=SUMIF($A${primera}:$A${ultima},"{letra}",K${primera}:K${ultima})', formato=usd)
        filas_grupo.append(r)
        r += 1
    _celda(ws, r, 3, "Subtotal (A a D)", negrita=True, borde=False)
    _celda(ws, r, 10, f"=SUM(J{filas_grupo[0]}:J{filas_grupo[-1]})", negrita=True, formato=usd)
    _celda(ws, r, 11, f"=SUM(K{filas_grupo[0]}:K{filas_grupo[-1]})", negrita=True, formato=usd)
    fila_sub = r
    r += 1
    _celda(ws, r, 3, "Imprevistos (porcentaje editable)", borde=False)
    _celda(ws, r, 9, 0.15, formato="0%", color="0000FF", relleno=PatternFill("solid", start_color="FFF6BF"))
    _celda(ws, r, 10, f"=J{fila_sub}*$I${r}", formato=usd)
    _celda(ws, r, 11, f"=K{fila_sub}*$I${r}", formato=usd)
    fila_imp = r
    r += 1
    _celda(ws, r, 3, "Total estimado del prototipo", negrita=True, borde=False)
    _celda(ws, r, 10, f"=J{fila_sub}+J{fila_imp}", negrita=True, formato=usd, relleno=GRIS_CLARO)
    _celda(ws, r, 11, f"=K{fila_sub}+K{fila_imp}", negrita=True, formato=usd, relleno=GRIS_CLARO)
    r += 1
    _celda(ws, r, 3, PE.GRUPOS[-1], borde=False)
    _celda(ws, r, 10, f'=SUMIF($A${primera}:$A${ultima},"E",J${primera}:J${ultima})', formato=usd)
    _celda(ws, r, 11, f'=SUMIF($A${primera}:$A${ultima},"E",K${primera}:K${ultima})', formato=usd)
    r += 2
    notas = ["Cómo leer la confianza",
             "alta: precio publicado en una tienda de Ecuador.",
             "media: precio de importación, de otro país o de otra presentación.",
             "baja: estimado; la nota de cada fila explica cómo se calculó.",
             "La celda amarilla (imprevistos) se puede cambiar; los totales se recalculan solos.",
             "",
             "Importación por courier"] + PE.IMPORTACION
    for k, t in enumerate(notas):
        _celda(ws, r + k, 1, t, negrita=t in ("Cómo leer la confianza", "Importación por courier"), borde=False)
    for col, ancho in zip("ABCDEFGHIJKLMN", (7, 14, 38, 26, 34, 18, 6, 11, 11, 12, 12, 10, 40, 60)):
        ws.column_dimensions[col].width = ancho
    ws.freeze_panes = ws.cell(row=fila_cab + 1, column=4)
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0


def hoja_proveedores(wb):
    ws = wb.create_sheet("Proveedores")
    ws["A1"] = "Proveedores y talleres encontrados en Ecuador"
    ws["A1"].font = Font(name=FUENTE, size=14, bold=True)
    ws["A2"] = f"Consulta web del {PE.FECHA_CONSULTA}. Confirmar dirección, existencias y precio antes de viajar."
    ws["A2"].font = Font(name=FUENTE, size=10, italic=True, color="555B63")
    for j, t in enumerate(["Proveedor", "Ciudad", "Qué ofrece", "Web"], 1):
        _celda(ws, 4, j, t, negrita=True, relleno=GRIS)
    for i, (nombre, ciudad, que, web) in enumerate(PE.PROVEEDORES, 5):
        _celda(ws, i, 1, nombre, envolver=True)
        _celda(ws, i, 2, ciudad, envolver=True)
        _celda(ws, i, 3, que, envolver=True)
        c = _celda(ws, i, 4, web)
        if web.startswith("http"):
            c.hyperlink = web
            c.font = Font(name=FUENTE, size=10, color="1F5FAD", underline="single")
    for col, ancho in zip("ABCD", (42, 28, 70, 42)):
        ws.column_dimensions[col].width = ancho
    ws.freeze_panes = "A5"


if __name__ == "__main__":
    main()
