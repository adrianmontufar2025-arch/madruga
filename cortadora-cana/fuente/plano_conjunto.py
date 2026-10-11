"""Plano 00: conjunto general (alzado, planta, isométrica, detalle del cabezal y lista de materiales)."""
from __future__ import annotations

import math
import os
import sys

from build123d import Compound, Location, scale
from ezdxf.enums import TextEntityAlignment

sys.path.insert(0, os.path.dirname(__file__))
import modelo as MD  # noqa: E402
from planos import DIR_DXF, Cota, Hoja, Plano  # noqa: E402

K = 5.0            # escala 1:5
K_DET = 2.0        # detalle 1:2
GRUPO_CABEZAL = {"P01", "P02", "P03", "P04", "P05", "P07", "P09", "P10", "P12", "P15", "P08"}


def proyectar(forma, origen, arriba):
    vis, hid = forma.project_to_viewport(origen, arriba, look_at=(0, 0, 0))
    return vis, Compound(vis).bounding_box()


def main():
    mundo = MD.a_mundo()
    piezas = MD.construir(0.0)
    colocadas = {p.codigo: mundo * p.ubicacion * p.geometria for p in piezas}
    total = sum(p.masa() for p in piezas)
    conjunto = Compound(list(colocadas.values()))

    plano = Plano("00", "Conjunto general", "Ver lista de materiales", 1, total + 250, conjunto, [],
                  hoja="A2", tratamiento="—")
    h = Hoja(plano)
    h.k = K
    h.ox = h.oy = 0.0
    W, H = 594.0, 420.0

    def vista(forma, origen, arriba, ancla, etiqueta, clave, tipo=None, factor=1.0, rotulo_arriba=False):
        f = scale(forma, factor) if factor != 1 else forma
        vis, b = proyectar(f, origen, arriba)
        ox = ancla[0] * K - b.min.X
        oy = ancla[1] * K - b.min.Y
        h.exp.add_shape([Location((ox, oy, 0)) * e for e in vis], layer="VISIBLE")
        if tipo:
            h.origenes[clave] = (tipo, ox, oy)
        t = h.msp.add_text(etiqueta, height=3.5 * K, dxfattribs={"layer": "TEXTO"})
        if rotulo_arriba:
            t.set_placement(((b.min.X + b.max.X) / 2 + ox, b.max.Y + oy + 6 * K), align=TextEntityAlignment.BOTTOM_CENTER)
        else:
            t.set_placement(((b.min.X + b.max.X) / 2 + ox, b.min.Y + oy - 16 * K), align=TextEntityAlignment.TOP_CENTER)
        return (b.min.X + ox, b.min.Y + oy, b.max.X + ox, b.max.Y + oy)

    caja_alz = vista(conjunto, (0, -5000, 0), (0, 0, 1), (36, 208), "ALZADO  1:5", "alzado", "alzado")
    caja_pla = vista(conjunto, (0, 0, 5000), (0, 1, 0), (36, 152), "PLANTA  1:5", "planta", "planta")
    caja_iso = vista(conjunto, (3000, 4200, 2600), (0, 0, 1), (440, 290), "ISOMÉTRICA  1:10", "iso", factor=0.5,
                     rotulo_arriba=False)
    cabezal = Compound([s for c, s in colocadas.items() if c in GRUPO_CABEZAL])
    f_det = K / K_DET
    caja_det = vista(cabezal, (0, 0, 5000), (0, 1, 0), (62, 22), "", "det", None, f_det, rotulo_arriba=True)
    h.texto("DETALLE A · PLANTA DEL CABEZAL  1:2", 262, 118, 3.5)

    # --- cotas del alzado (coordenadas del mundo)
    gx, _, gz = [v + o for v, o in zip(MD.eje(MD.S_EMP_TRAS), MD.H_A_MUNDO)]
    zf = MD.Z_HORQUILLA + MD.H_A_MUNDO[2]
    b = conjunto.bounding_box()
    for c in [
        Cota("lin", "alzado", (b.min.X, 0, 0), (0, 0, 0), dist=-14, angulo=0, texto="<> hasta el eje del tallo"),
        Cota("lin", "alzado", (gx, 0, 0), (gx, 0, gz), dist=-14, angulo=90, texto="<> eje empuñadura"),
        Cota("lin", "alzado", (0, 0, 0), (0, 0, zf), dist=26, angulo=90, texto="<> guía"),
        Cota("lin", "alzado", (0, 0, 0), (0, 0, MD.ALTURA_CORTE), dist=12, angulo=90, texto="<> corte"),
    ]:
        try:
            h.cota(c)
        except Exception as ex:
            print("cota omitida", ex)
    # eje del tallo
    x0, y0 = h.a_hoja("alzado", 0, 0, -40)
    x1, y1 = h.a_hoja("alzado", 0, 0, zf + 80)
    h.msp.add_line((x0, y0), (x1, y1), dxfattribs={"layer": "EJES"})
    # ángulo de la pértiga
    a = MD.eje(250)
    pa = h.a_hoja("alzado", a[0] + MD.H_A_MUNDO[0], 0, a[2] + MD.H_A_MUNDO[2])
    t = h.msp.add_text("pértiga a 40° sobre la horizontal", height=2.5 * K, dxfattribs={"layer": "COTAS"})
    t.set_placement((pa[0] + 4 * K, pa[1] - 14 * K), align=TextEntityAlignment.TOP_LEFT)

    # --- globos
    def globos(caja, codigos, centro_de, sep_min=11.0):
        cx, cy = (caja[0] + caja[2]) / 2, (caja[1] + caja[3]) / 2
        rx, ry = (caja[2] - caja[0]) / 2 + 16 * K, (caja[3] - caja[1]) / 2 + 14 * K
        items = []
        for cod in codigos:
            px, py = centro_de(cod)
            ang = math.atan2((py - cy) / ry, (px - cx) / rx)
            items.append([ang, cod, px, py])
        items.sort()
        # separación angular mínima medida sobre el perímetro
        n = len(items)
        perim = math.pi * (rx + ry)
        dmin = 2 * math.pi * sep_min * K / perim
        for _ in range(60):
            for i in range(n):
                j = (i + 1) % n
                d = (items[j][0] - items[i][0]) % (2 * math.pi)
                if d < dmin:
                    items[i][0] -= (dmin - d) / 2
                    items[j][0] += (dmin - d) / 2
        for ang, cod, px, py in items:
            bx, by = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
            r = 4.2 * K
            h.msp.add_circle((bx, by), r, dxfattribs={"layer": "COTAS"})
            dx, dy = px - bx, py - by
            d = math.hypot(dx, dy) or 1
            h.msp.add_line((bx + dx / d * r, by + dy / d * r), (px, py), dxfattribs={"layer": "COTAS"})
            h.msp.add_circle((px, py), 0.6 * K, dxfattribs={"layer": "COTAS"})
            tt = h.msp.add_text(cod, height=2.4 * K, dxfattribs={"layer": "TEXTO"})
            tt.set_placement((bx, by), align=TextEntityAlignment.MIDDLE_CENTER)

    def centro_alz(cod):
        c = colocadas[cod].center()
        return h.a_hoja("alzado", c.X, c.Y, c.Z)

    otros = [c for c in colocadas if c not in GRUPO_CABEZAL and not c.startswith("C") and c not in ("P22", "P11B")]
    # globos del alzado: desplazados en perpendicular a la pértiga (arriba-derecha)
    dirp = (-math.cos(math.radians(MD.ANG_PERTIGA)), math.sin(math.radians(MD.ANG_PERTIGA)))
    nor = (dirp[1], -dirp[0])
    nor = (abs(nor[0]), abs(nor[1]))
    lista = []
    for cod in otros:
        px, py = centro_alz(cod)
        if cod in ("P11", "P13", "P14"):
            continue
        lista.append([px * dirp[0] + py * dirp[1], cod, px, py])
    lista.sort()
    ultimo = -1e9
    for item in lista:
        if item[0] < ultimo + 11 * K:
            item[0] = ultimo + 11 * K
        ultimo = item[0]
    def globo(bx, by, px, py, cod):
        r = 4.2 * K
        h.msp.add_circle((bx, by), r, dxfattribs={"layer": "COTAS"})
        dx, dy = px - bx, py - by
        d = math.hypot(dx, dy) or 1
        h.msp.add_line((bx + dx / d * r, by + dy / d * r), (px, py), dxfattribs={"layer": "COTAS"})
        h.msp.add_circle((px, py), 0.6 * K, dxfattribs={"layer": "COTAS"})
        tt = h.msp.add_text(cod, height=2.4 * K, dxfattribs={"layer": "TEXTO"})
        tt.set_placement((bx, by), align=TextEntityAlignment.MIDDLE_CENTER)
    for s_, cod, px, py in lista:
        s0 = px * dirp[0] + py * dirp[1]
        bx = px + (s_ - s0) * dirp[0] + nor[0] * 30 * K
        by = py + (s_ - s0) * dirp[1] + nor[1] * 30 * K
        globo(bx, by, px, py, cod)
    for i, cod in enumerate(("P13", "P14", "P11")):
        px, py = centro_alz(cod)
        globo(px + 34 * K, py + (10 - 12 * i) * K, px, py, cod)
    det = caja_det
    bdet = scale(cabezal, f_det).bounding_box()

    def centro_det(cod):
        c = scale(colocadas[cod], f_det).center()
        ox = det[0] - bdet.min.X
        oy = det[1] - bdet.min.Y
        return (c.X + ox, c.Y + oy)

    globos(caja_det, sorted(GRUPO_CABEZAL), centro_det, sep_min=12)

    # --- marco, cajetín, lista de materiales y notas
    h.marco(W, H)
    h.cajetin(W, H)
    filas = []
    for p in piezas:
        filas.append([p.codigo, p.nombre[:40], p.material[:46], str(p.cantidad), f"{p.masa():.0f}",
                      p.codigo if p.plano else "comercial"])
    filas.append(["C05", "Batería 36 V 4 Ah al cinturón + cable", "Comercial", "1", "1300", "comercial"])
    filas.append(["", "Tornillería, cables, electrónica (estimado)", "", "", "250", ""])
    cols = [("Cód.", 11), ("Denominación", 60), ("Material", 72), ("Cant.", 10), ("Masa g", 14), ("Plano", 22)]
    xt = W - 10 - sum(w for _, w in cols)
    h.tabla(xt, 64 + 6.0 * (len(filas) + 1) + 2, cols, filas, titulo="LISTA DE MATERIALES", h=2.0, fila_h=6.0)
    notas = [
        f"Masa sin batería: {(total + 250) / 1000:.1f} kg (con 0,25 kg estimados de tornillería y cables).".replace(".", ",", 1),
        "Con el patín apoyado, la carga vertical en las manos es de aprox. 1,8 kg.",
        "Corte de tallos hasta %%c55. Altura de corte 15-45 mm (patín P07).",
        "Cuchilla P02 dibujada cerrada. Apertura de trabajo 62°, carrera de la varilla 31 mm.",
        "Motor 36 V 400-500 W + reductor 15:1 + husillo SFU1605 + balancín P15.",
        "Fuerza de corte estimada 2,5-3 kN: confirmar con ensayo en tallos de Pangua.",
    ]
    y = 104
    h.texto("NOTAS", 262, y, 3.0)
    for i, n in enumerate(notas):
        y -= 5.4
        h.texto(f"{i + 1}. {n}", 262, y, 2.0)
    h.doc.header["$LTSCALE"] = K
    ruta = os.path.join(DIR_DXF, "00_conjunto_general.dxf")
    h.exp.write(ruta)
    print(ruta, f"masa {total + 250:.0f} g")


if __name__ == "__main__":
    main()
