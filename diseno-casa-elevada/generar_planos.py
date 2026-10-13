#!/usr/bin/env python3
"""Genera la lámina HTML de la Casa Elevada 200 msnm.

Todas las piezas salen de una sola malla de ejes y de una sola tabla de
niveles, así las cotas de plantas, cortes y elevaciones siempre coinciden.
Unidades: metros. En los dibujos el eje vertical del mundo apunta hacia
arriba; la clase Dwg invierte el signo al escribir el SVG.
"""
import html
import math
import sys

# ---------------------------------------------------------------- datos base
XA, XB, XC, XD = 0.0, 3.0, 6.0, 9.0          # ejes A-D
Y1, Y2, Y3, Y4 = 0.0, 2.4, 5.7, 9.0          # ejes 1-4
XS = [XA, XB, XC, XD]
YS = [Y1, Y2, Y3, Y4]
EJE_X = ["A", "B", "C", "D"]
EJE_Y = ["1", "2", "3", "4"]
COL = 0.30                                    # columna 30x30
VOL = 10.40                                   # borde del mirador en volado
TE, TI = 0.12, 0.10                           # pared exterior / interior

NTN, NPB, FV, TV, NPA, SOL = 0.0, 0.20, 2.60, 3.00, 3.20, 6.20
P_MAIN = math.tan(math.radians(30))          # 30 grados = 57.7 %
P_TERR = 0.15                                 # 15 % sobre la terraza
Z_CUMB = SOL + (Y3 - Y2) * P_MAIN            # fondo de cabio en cumbrera
ALERO_F, ALERO_B, ALERO_L, ALERO_R = -0.90, 10.00, -0.80, 10.50
CUB = 0.24                                    # cabio + correa + panel

# escalera: 17 contrahuellas, 16 huellas de 0.28, descanso de 1.00
CH = (NPA - NPB) / 17
HU = 0.28
ST_X1, ST_X2 = 9.25, 10.35
ST_Y0 = 7.60                                  # primera contrahuella
DESC_Y1, DESC_Y0 = 5.36, 4.36                 # descanso
ST_TOP = 2.40


def riser_y(k):
    """Posición Y de la contrahuella k (1..17)."""
    if k <= 9:
        return ST_Y0 - (k - 1) * HU
    return DESC_Y0 - (k - 10) * HU


def riser_z(k):
    return NPB + k * CH


def roof_under(y):
    """Fondo de cabio en la coordenada Y."""
    if y <= Y2:
        return SOL - (Y2 - y) * P_TERR
    if y <= Y3:
        return SOL + (y - Y2) * P_MAIN
    return Z_CUMB - (y - Y3) * P_MAIN


ROOF_PTS = [(ALERO_F, roof_under(ALERO_F)), (Y2, SOL), (Y3, Z_CUMB), (ALERO_B, roof_under(ALERO_B))]


def fmt(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def offset_poly(pts, d):
    """Desplaza una polilínea d metros hacia su normal izquierda (arriba)."""
    segs = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy)
        nx, ny = -dy / n, dx / n
        if ny < 0:
            nx, ny = -nx, -ny
        segs.append(((x1 + nx * d, y1 + ny * d), (x2 + nx * d, y2 + ny * d)))
    out = [segs[0][0]]
    for (a1, a2), (b1, b2) in zip(segs, segs[1:]):
        # intersección de las dos rectas desplazadas
        x1, y1 = a1; x2, y2 = a2; x3, y3 = b1; x4, y4 = b2
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-9:
            out.append(a2)
            continue
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        out.append((x1 + t * (x2 - x1), y1 + t * (y2 - y1)))
    out.append(segs[-1][1])
    return out


class Dwg:
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.e = []

    def add(self, s):
        self.e.append(s)

    def line(self, x1, y1, x2, y2, c="ln"):
        self.add(f'<line x1="{fmt(x1)}" y1="{fmt(-y1)}" x2="{fmt(x2)}" y2="{fmt(-y2)}" class="{c}"/>')

    def rect(self, xa, ya, xb, yb, c="ln", rx=None):
        x, y = min(xa, xb), max(ya, yb)
        w, h = abs(xb - xa), abs(yb - ya)
        r = f' rx="{fmt(rx)}"' if rx else ""
        self.add(f'<rect x="{fmt(x)}" y="{fmt(-y)}" width="{fmt(w)}" height="{fmt(h)}" class="{c}"{r}/>')

    def poly(self, pts, c="ln", closed=True):
        p = " ".join(f"{fmt(x)},{fmt(-y)}" for x, y in pts)
        self.add(f'<{"polygon" if closed else "polyline"} points="{p}" class="{c}"/>')

    def circle(self, x, y, r, c="ln"):
        self.add(f'<circle cx="{fmt(x)}" cy="{fmt(-y)}" r="{fmt(r)}" class="{c}"/>')

    def ellipse(self, x, y, rx, ry, c="ln"):
        self.add(f'<ellipse cx="{fmt(x)}" cy="{fmt(-y)}" rx="{fmt(rx)}" ry="{fmt(ry)}" class="{c}"/>')

    def path(self, d, c="ln"):
        self.add(f'<path d="{d}" class="{c}"/>')

    def text(self, x, y, s, c="t", size=0.22, anchor="middle", rot=0):
        tr = f' transform="rotate({rot} {fmt(x)} {fmt(-y)})"' if rot else ""
        self.add(f'<text x="{fmt(x)}" y="{fmt(-y)}" font-size="{fmt(size)}" '
                 f'text-anchor="{anchor}" class="{c}"{tr}>{html.escape(s)}</text>')

    def svg(self, label):
        w, h = self.x1 - self.x0, self.y1 - self.y0
        return (f'<svg viewBox="{fmt(self.x0)} {fmt(-self.y1)} {fmt(w)} {fmt(h)}" '
                f'role="img" aria-label="{html.escape(label)}">' + "".join(self.e) + "</svg>")


# ------------------------------------------------------------ utilidades CAD
def arrow(d, x1, y1, x2, y2, c="flecha", head=0.2):
    d.line(x1, y1, x2, y2, c)
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a) + head * 0.45 * math.sin(a), y2 - head * math.sin(a) - head * 0.45 * math.cos(a))
    p2 = (x2 - head * math.cos(a) - head * 0.45 * math.sin(a), y2 - head * math.sin(a) + head * 0.45 * math.cos(a))
    d.poly([(x2, y2), p1, p2], c + "-p")


def dim_h(d, xs, y, labels=None, size=0.2, total=False):
    d.line(xs[0] - 0.12, y, xs[-1] + 0.12, y, "cota")
    for x in xs:
        d.line(x - 0.07, y - 0.07, x + 0.07, y + 0.07, "cota-tick")
        d.line(x, y - 0.16, x, y + 0.16, "cota")
    for i in range(len(xs) - 1):
        lab = labels[i] if labels else f"{xs[i + 1] - xs[i]:.2f}"
        if lab:
            d.text((xs[i] + xs[i + 1]) / 2, y + 0.07, lab, "t-cota t-tot" if total else "t-cota", size)


def dim_v(d, ys, x, labels=None, size=0.2, total=False):
    d.line(x, ys[0] - 0.12, x, ys[-1] + 0.12, "cota")
    for y in ys:
        d.line(x - 0.07, y - 0.07, x + 0.07, y + 0.07, "cota-tick")
        d.line(x - 0.16, y, x + 0.16, y, "cota")
    for i in range(len(ys) - 1):
        lab = labels[i] if labels else f"{ys[i + 1] - ys[i]:.2f}"
        if lab:
            d.text(x - 0.07, (ys[i] + ys[i + 1]) / 2, lab, "t-cota t-tot" if total else "t-cota", size, rot=-90)


def bubble(d, x, y, name, r=0.28):
    d.circle(x, y, r, "burbuja")
    d.text(x, y - 0.095, name, "t-eje", 0.27)


def ejes_planta(d, ytop=11.35, xleft=-2.55, ymin=-1.0, xmax=10.0):
    for x, n in zip(XS, EJE_X):
        d.line(x, ymin, x, ytop - 0.28, "eje")
        bubble(d, x, ytop, n)
    for y, n in zip(YS, EJE_Y):
        d.line(xleft + 0.28, y, xmax, y, "eje")
        bubble(d, xleft, y, n)


def nivel(d, h, z, label, side="left", length=0.9, debajo=False):
    """Marca de nivel: triángulo sobre la línea y rótulo."""
    if side == "left":
        d.line(h - length, z, h + 0.15, z, "fino")
        d.poly([(h - length + 0.18, z), (h - length + 0.06, z + 0.16), (h - length + 0.30, z + 0.16)], "nivel-tri")
        d.text(h - length - 0.06, z - (0.22 if debajo else 0.06), label, "t-nivel", 0.19, "end")
    else:
        d.line(h - 0.15, z, h + length, z, "fino")
        d.poly([(h + length - 0.18, z), (h + length - 0.30, z + 0.16), (h + length - 0.06, z + 0.16)], "nivel-tri")
        d.text(h + length + 0.06, z - 0.06, label, "t-nivel", 0.19, "start")


def llamada(d, x, y, n, tx=None, ty=None):
    """Número de nota en círculo con línea guía opcional al punto (x, y)."""
    if tx is None:
        tx, ty = x, y
    else:
        d.line(tx, ty, x, y, "guia")
        d.circle(x, y, 0.035, "guia-p")
    d.circle(tx, ty, 0.2, "llamada")
    d.text(tx, ty - 0.075, str(n), "t-llamada", 0.21)


def escala_grafica(d, x, y):
    for i in range(5):
        d.rect(x + i, y, x + i + 1, y + 0.1, "esc-a" if i % 2 == 0 else "esc-b")
    for i in (0, 1, 2, 5):
        d.text(x + i, y + 0.2, f"{i}", "t-nota", 0.17)
    d.text(x + 5.15, y - 0.02, "m", "t-nota", 0.17, "start")


def persona(d, h, z0, flip=False):
    s = -1 if flip else 1
    d.circle(h, z0 + 1.58, 0.11, "persona")
    pts = [(h - 0.19, z0 + 1.43), (h + 0.19, z0 + 1.43), (h + 0.15, z0 + 0.86), (h + 0.11, z0 + 0.0),
           (h + 0.02, z0 + 0.0), (h, z0 + 0.72), (h - 0.02, z0), (h - 0.11, z0), (h - 0.15, z0 + 0.86)]
    d.poly(pts, "persona")


def muro_h(d, y, x1, x2, t, vanos=(), c="muro"):
    cuts = sorted(vanos)
    a = x1
    for va, vb in cuts:
        if va > a:
            d.rect(a, y - t / 2, va, y + t / 2, c)
        a = max(a, vb)
    if x2 > a:
        d.rect(a, y - t / 2, x2, y + t / 2, c)


def muro_v(d, x, y1, y2, t, vanos=(), c="muro"):
    cuts = sorted(vanos)
    a = y1
    for va, vb in cuts:
        if va > a:
            d.rect(x - t / 2, a, x + t / 2, va, c)
        a = max(a, vb)
    if y2 > a:
        d.rect(x - t / 2, a, x + t / 2, y2, c)


def ventana_h(d, a, b, y, t, alta=False, code=None, out=-1):
    d.rect(a, y - t / 2, b, y + t / 2, "vano")
    d.line(a, y, b, y, "vidrio-alto" if alta else "vidrio")
    if code:
        d.text((a + b) / 2, y + out * (t / 2 + 0.2) - 0.06, code, "t-vano", 0.17)


def ventana_v(d, a, b, x, t, alta=False, code=None, out=-1):
    d.rect(x - t / 2, a, x + t / 2, b, "vano")
    d.line(x, a, x, b, "vidrio-alto" if alta else "vidrio")
    if code:
        d.text(x + out * (t / 2 + 0.22), (a + b) / 2 - 0.06, code, "t-vano", 0.17)


def puerta_h(d, a, b, y, t, hinge, side, code=None, code_in=False):
    yf = y + side * t / 2
    w = b - a
    h = a if hinge == "a" else b
    o = b if hinge == "a" else a
    ex, ey = h, yf + side * w
    d.line(h, yf, ex, ey, "hoja")
    cross = side * w * (o - h)
    sweep = 1 if cross > 0 else 0
    d.path(f"M {fmt(ex)} {fmt(-ey)} A {fmt(w)} {fmt(w)} 0 0 {sweep} {fmt(o)} {fmt(-yf)}", "arco")
    if code and code_in:
        d.text(o + (0.2 if o > h else -0.2), yf + side * 0.3, code, "t-vano", 0.17)
    elif code:
        d.text((a + b) / 2, y - side * (t / 2 + 0.2) - 0.06, code, "t-vano", 0.17)


def mampara_h(d, a, b, y, t, code=None):
    m = (a + b) / 2
    d.rect(a, y - t / 2, b, y + t / 2, "vano")
    d.line(a, y - 0.025, m + 0.06, y - 0.025, "vidrio")
    d.line(m - 0.06, y + 0.025, b, y + 0.025, "vidrio")
    if code:
        d.text(m, y - t / 2 - 0.26, code, "t-vano", 0.17)


def silla(d, x, y, w=0.42):
    d.rect(x - w / 2, y - w / 2, x + w / 2, y + w / 2, "mueble", rx=0.05)


def cama(d, xa, ya, xb, yb, cab):
    """Cama con cabecera en el lado 'cab' (N, S, E, O)."""
    d.rect(xa, ya, xb, yb, "mueble", rx=0.04)
    if cab in ("E", "O"):
        xc = xb - 0.38 if cab == "E" else xa + 0.04
        ym = (ya + yb) / 2
        if yb - ya > 1.3:
            d.rect(xc, ya + 0.08, xc + 0.34, ym - 0.04, "mueble", rx=0.05)
            d.rect(xc, ym + 0.04, xc + 0.34, yb - 0.08, "mueble", rx=0.05)
        else:
            d.rect(xc, ya + 0.1, xc + 0.34, yb - 0.1, "mueble", rx=0.05)
        xl = xb - 0.62 if cab == "E" else xa + 0.62
        d.line(xl, ya, xl, yb, "mueble")
    else:
        yc = yb - 0.38 if cab == "N" else ya + 0.04
        xm = (xa + xb) / 2
        if xb - xa > 1.3:
            d.rect(xa + 0.08, yc, xm - 0.04, yc + 0.34, "mueble", rx=0.05)
            d.rect(xm + 0.04, yc, xb - 0.08, yc + 0.34, "mueble", rx=0.05)
        else:
            d.rect(xa + 0.1, yc, xb - 0.1, yc + 0.34, "mueble", rx=0.05)
        yl = yb - 0.62 if cab == "N" else ya + 0.62
        d.line(xa, yl, xb, yl, "mueble")


def rotulo(d, x, y, nombre, area=None, size=0.25):
    lines = nombre.split("\n")
    n = len(lines) + (1 if area else 0)
    top = y + (n - 1) * size * 0.55
    for i, ln in enumerate(lines):
        d.text(x, top - i * size * 1.1 - size * 0.35, ln, "t-amb", size)
    if area:
        d.text(x, top - len(lines) * size * 1.1 - size * 0.32, area, "t-area", size * 0.78)


def escalera_planta(d, cortada=False, etiqueta="SUBE", flecha_sube=True, y_label=6.35):
    d.rect(ST_X1, ST_TOP, ST_X2, ST_Y0, "escalera")
    d.rect(ST_X1, DESC_Y0, ST_X2, DESC_Y1, "descanso")
    corte_k = 7
    for k in range(1, 18):
        y = riser_y(k)
        if k in (9, 10):
            continue
        c = "peldano"
        if cortada and k > corte_k:
            c = "peldano oculto"
        d.line(ST_X1, y, ST_X2, y, c)
    if cortada:
        yk = riser_y(corte_k) - 0.14
        d.line(ST_X1, yk - 0.18, ST_X2, yk + 0.18, "ln")
    xm = (ST_X1 + ST_X2) / 2
    if flecha_sube:
        d.circle(xm, ST_Y0 - 0.14, 0.05, "flecha-p")
        arrow(d, xm, ST_Y0 - 0.14, xm, ST_TOP + 0.2, "flecha")
    else:
        d.circle(xm, ST_TOP + 0.2, 0.05, "flecha-p")
        arrow(d, xm, ST_TOP + 0.2, xm, ST_Y0 - 0.14, "flecha")
    d.text(xm + 0.09, y_label, etiqueta, "t-nota", 0.17, rot=-90)


def seccion_marca(d, x=7.5, yb=-1.05, yt=10.25):
    for y0, y1 in ((yb, yb + 0.5), (yt - 0.5, yt)):
        d.line(x, y0, x, y1, "corte-linea")
    for y in (yb, yt):
        d.poly([(x - 0.42, y), (x - 0.12, y + 0.13), (x - 0.12, y - 0.13)], "corte-p")
        d.text(x - 0.62, y - 0.08, "A", "t-corte", 0.26)


# ================================================================ PLANTA ALTA
def planta_alta():
    d = Dwg(-3.0, -2.45, 11.85, 11.75)
    ejes_planta(d)
    # proyección de cubierta
    d.rect(ALERO_L, ALERO_F, ALERO_R, ALERO_B, "proyeccion")
    d.text(ALERO_L + 0.1, ALERO_B - 0.25, "proyección de cubierta", "t-nota", 0.16, "start")
    # plataforma y terraza
    plat = [(-0.15, -0.15), (VOL, -0.15), (VOL, 2.525), (9.15, 2.525), (9.15, 9.15), (-0.15, 9.15)]
    d.poly(plat, "piso")
    d.rect(-0.15, -0.15, VOL, Y2, "deck")
    d.poly(plat, "borde")
    # escalera (bajo el nivel del piso alto)
    escalera_planta(d, etiqueta="BAJA", flecha_sube=False)
    # baranda
    d.poly([(-0.10, Y2 - 0.06), (-0.10, -0.10), (VOL - 0.05, -0.10), (VOL - 0.05, 2.475), (ST_X2, 2.475)], "baranda", closed=False)
    d.poly([(-0.05, Y2 - 0.06), (-0.05, -0.05), (VOL - 0.10, -0.05), (VOL - 0.10, 2.43)], "baranda2", closed=False)
    # postes de terraza (madera 15x15)
    for x in (0.0, 3.0, 6.0, 9.0, 10.30):
        d.rect(x - 0.075, -0.075, x + 0.075, 0.075, "poste")
    # muros exteriores
    muro_h(d, Y2, -0.06, 9.06, TE, [(0.60, 2.20), (3.40, 5.20), (6.30, 8.70)])
    muro_h(d, Y4, -0.06, 9.06, TE, [(0.25, 1.15), (4.50, 5.40), (6.60, 8.10)])
    muro_v(d, XA, Y2, Y4, TE, [(3.40, 4.40), (6.60, 7.80)])
    muro_v(d, XD, Y2, Y4, TE, [(3.30, 4.80), (7.70, 8.60)])
    # muros interiores
    muro_h(d, Y3, 0.06, 8.94, TI, [(3.30, 4.10), (4.40, 5.10), (6.20, 7.00)])
    muro_v(d, 4.20, Y3 + 0.05, Y4 - 0.06, TI)
    muro_v(d, 5.70, Y3 + 0.05, Y4 - 0.06, TI)
    # postes de cumbrera dentro del muro del eje 3
    for x in XS:
        d.rect(x - 0.05, Y3 - 0.05, x + 0.05, Y3 + 0.05, "poste-cumbrera")
    # vanos
    ventana_h(d, 0.60, 2.20, Y2, TE, code="V1")
    ventana_h(d, 3.40, 5.20, Y2, TE, code="V2")
    mampara_h(d, 6.30, 8.70, Y2, TE, code="P1")
    ventana_h(d, 0.25, 1.15, Y4, TE, code="V3", out=1)
    ventana_h(d, 4.50, 5.40, Y4, TE, alta=True, code="V4", out=1)
    ventana_h(d, 6.60, 8.10, Y4, TE, code="V5", out=1)
    ventana_v(d, 3.40, 4.40, XA, TE, alta=True, code="V6")
    ventana_v(d, 6.60, 7.80, XA, TE, code="V7")
    ventana_v(d, 3.30, 4.80, XD, TE, alta=True, code="V8", out=1)
    ventana_v(d, 7.70, 8.60, XD, TE, code="V9", out=1)
    puerta_h(d, 3.30, 4.10, Y3, TI, "b", +1, code="P2", code_in=True)
    puerta_h(d, 4.40, 5.10, Y3, TI, "a", +1, code="P3", code_in=True)
    puerta_h(d, 6.20, 7.00, Y3, TI, "a", +1, code="P4", code_in=True)

    # ---- cocina
    d.rect(0.06, 2.46, 2.40, 3.06, "meson")
    d.rect(0.06, 3.06, 0.66, 4.80, "meson")
    d.rect(1.05, 2.56, 1.85, 2.96, "mueble", rx=0.06)
    d.rect(0.12, 3.72, 0.60, 4.28, "mueble")
    for cx, cy in ((0.24, 3.86), (0.48, 3.86), (0.24, 4.14), (0.48, 4.14)):
        d.circle(cx, cy, 0.075, "mueble")
    d.rect(0.06, 4.90, 0.76, 5.62, "mueble")
    d.line(0.06, 4.90, 0.76, 5.62, "mueble")
    d.text(0.98, 5.20, "refri.", "t-nota", 0.15, "start")
    rotulo(d, 1.80, 4.55, "COCINA", "9.4 m²")
    # barra exterior bajo V1
    d.rect(0.60, 2.04, 2.20, 2.34, "meson")
    for cx in (0.90, 1.40, 1.90):
        d.circle(cx, 1.78, 0.17, "mueble")
    # ---- comedor
    d.rect(3.55, 3.40, 5.15, 4.30, "mueble", rx=0.05)
    for cx in (3.88, 4.35, 4.82):
        silla(d, cx, 3.13)
        silla(d, cx, 4.57)
    rotulo(d, 4.35, 5.18, "COMEDOR", "8.6 m²")
    # ---- sala
    d.rect(7.10, 4.80, 8.90, 5.65, "mueble", rx=0.06)
    d.rect(7.10, 5.42, 8.90, 5.65, "mueble")
    d.rect(7.55, 3.95, 8.45, 4.45, "mueble", rx=0.05)
    d.rect(8.12, 2.95, 8.86, 3.69, "mueble", rx=0.08)
    rotulo(d, 7.25, 3.35, "SALA", "10.3 m²")
    # ---- dormitorio principal
    d.rect(0.06, 5.75, 2.66, 6.35, "closet")
    d.line(0.10, 6.05, 1.40, 6.05, "mueble")
    d.line(1.30, 6.10, 2.62, 6.10, "mueble")
    cama(d, 1.70, 7.04, 3.20, 8.94, "N")
    d.rect(1.20, 8.49, 1.65, 8.94, "mueble")
    d.rect(3.25, 8.49, 3.70, 8.94, "mueble")
    rotulo(d, 0.82, 7.45, "DORMITORIO\nPRINCIPAL", "13.0 m²", 0.22)
    # ---- baño
    d.rect(5.20, 6.55, 5.65, 7.15, "mueble")
    d.ellipse(5.43, 6.85, 0.15, 0.2, "mueble")
    d.rect(4.25, 7.20, 4.45, 7.65, "mueble")
    d.ellipse(4.68, 7.425, 0.24, 0.18, "mueble")
    d.rect(4.25, 7.95, 5.65, 8.94, "ducha")
    d.line(4.25, 7.95, 5.10, 7.95, "vidrio")
    d.circle(4.95, 8.45, 0.05, "mueble")
    rotulo(d, 4.78, 6.82, "BAÑO", "4.5 m²", 0.2)
    # ---- dormitorio 2
    d.rect(5.75, 6.70, 6.35, 8.30, "closet")
    d.line(6.05, 6.75, 6.05, 7.55, "mueble")
    d.line(6.10, 7.45, 6.10, 8.25, "mueble")
    cama(d, 7.04, 6.30, 8.94, 7.50, "E")
    d.rect(8.49, 7.55, 8.94, 7.95, "mueble")
    d.rect(6.70, 8.39, 7.90, 8.94, "mueble")
    silla(d, 7.30, 8.10)
    rotulo(d, 7.55, 7.93, "DORMITORIO 2", "10.2 m²", 0.22)
    # ---- terraza
    d.path(f"M 0.2 -0.22 Q 1.5 -0.95 2.8 -0.22 Q 1.5 -0.55 0.2 -0.22 Z", "hamaca")
    d.text(1.5, 0.92, "hamaca", "t-nota", 0.15)
    d.rect(3.60, 0.50, 4.30, 1.20, "mueble", rx=0.08)
    d.rect(5.10, 0.50, 5.80, 1.20, "mueble", rx=0.08)
    d.circle(4.70, 0.85, 0.28, "mueble")
    rotulo(d, 7.45, 1.15, "TERRAZA", "25.0 m²")
    rotulo(d, 9.72, 1.55, "MIRADOR", None, 0.19)
    d.text(9.72, 1.05, "llegada de", "t-nota", 0.15)
    d.text(9.72, 0.85, "la escalera", "t-nota", 0.15)
    d.text(6.05, 1.70, "NPT +3.20", "t-nivel", 0.15)

    seccion_marca(d)
    # cotas
    dim_h(d, [0, 3, 6, 9, VOL], -1.45)
    dim_h(d, [0, VOL], -1.95, ["10.40"], total=True)
    dim_h(d, [0, 4.20, 5.70, 9.0], 10.65)
    dim_v(d, [0, 2.4, 5.7, 9.0], -1.35)
    dim_v(d, [0, 9.0], -1.85, ["9.00"], total=True)
    dim_v(d, [ST_TOP, DESC_Y0, DESC_Y1, ST_Y0], 11.05)
    escala_grafica(d, -2.9, -2.38)
    return d.svg("Planta alta")


# ================================================================ PLANTA BAJA
def planta_baja():
    d = Dwg(-3.0, -2.45, 11.85, 11.75)
    ejes_planta(d)
    # contrapiso y vereda
    d.rect(-0.90, -1.00, 10.65, 10.10, "vereda")
    d.rect(-0.15, -0.15, 9.15, 9.15, "contrapiso")
    d.text(-0.82, -0.82, "vereda perimetral +0.20, pendiente 2 % hacia afuera", "t-nota", 0.15, "start")
    # proyección del piso alto
    plat = [(-0.15, -0.15), (VOL, -0.15), (VOL, 2.525), (9.15, 2.525), (9.15, 9.15), (-0.15, 9.15)]
    d.poly(plat, "proyeccion")
    # núcleo de servicio (bloque 15 cm)
    tb = 0.15
    muro_v(d, XA, Y3 + 0.15, Y4 - 0.15, tb, c="muro-bloque")
    muro_h(d, Y3, 0.15, 2.85, tb, [(0.35, 1.05), (1.95, 2.75)], c="muro-bloque")
    muro_v(d, XB, Y3 + 0.15, 7.575, tb, c="muro-bloque")
    muro_h(d, 7.50, 0.075, 3.075, tb, c="muro-bloque")
    muro_v(d, 1.40, Y3 + 0.075, 7.425, TI, c="muro-bloque")
    puerta_h(d, 0.35, 1.05, Y3, tb, "a", +1, code="P5")
    puerta_h(d, 1.95, 2.75, Y3, tb, "b", +1, code="P6")
    # medio baño
    d.rect(0.075, 6.77, 0.30, 7.23, "mueble")
    d.ellipse(0.53, 7.0, 0.24, 0.18, "mueble")
    d.rect(0.95, 6.85, 1.35, 7.35, "mueble")
    d.ellipse(1.15, 7.1, 0.13, 0.17, "mueble")
    rotulo(d, 0.74, 6.62, "½ BAÑO", None, 0.17)
    # bodega
    d.rect(1.45, 6.30, 1.85, 7.425, "closet")
    rotulo(d, 2.40, 7.02, "BODEGA", "2.4 m²", 0.18)
    # lavandería
    d.rect(0.15, 7.575, 0.80, 8.15, "meson")
    d.rect(0.95, 7.575, 1.60, 8.20, "mueble", rx=0.06)
    d.circle(1.275, 7.89, 0.22, "mueble")
    rotulo(d, 1.55, 8.55, "LAVANDERÍA", "techada", 0.18)
    # estar exterior
    d.rect(0.35, 0.35, 2.70, 1.15, "mueble", rx=0.08)
    d.rect(0.35, 1.15, 1.15, 2.70, "mueble", rx=0.08)
    d.rect(1.55, 1.55, 2.35, 2.15, "mueble", rx=0.06)
    d.rect(3.30, 1.40, 4.05, 2.15, "mueble", rx=0.08)
    d.path("M 0.12 -2.6 Q 0.75 -4.05 0.12 -5.5 Q 0.4 -4.05 0.12 -2.6 Z", "hamaca")
    d.text(0.55, 4.05, "hamaca", "t-nota", 0.15, "start")
    rotulo(d, 2.05, 3.55, "ESTAR\nEXTERIOR")
    # comedor exterior
    d.rect(3.60, 3.70, 5.40, 4.60, "mueble", rx=0.05)
    for cx in (3.95, 4.50, 5.05):
        silla(d, cx, 3.42)
        silla(d, cx, 4.88)
    rotulo(d, 4.50, 5.55, "COMEDOR EXTERIOR", None, 0.21)
    # mesón exterior
    d.rect(3.15, 8.40, 5.85, 9.00, "meson")
    d.rect(4.20, 8.48, 4.80, 8.90, "mueble", rx=0.05)
    rotulo(d, 4.50, 7.95, "MESÓN EXTERIOR", "con lavaplatos", 0.18)
    # estacionamiento
    car = "M 6.6 -0.75 Q 6.6 -0.5 6.85 -0.5 L 8.15 -0.5 Q 8.4 -0.5 8.4 -0.75 L 8.4 -4.95 Q 8.4 -5.2 8.15 -5.2 L 6.85 -5.2 Q 6.6 -5.2 6.6 -4.95 Z"
    d.path(car, "auto")
    d.line(6.75, 1.75, 8.25, 1.75, "mueble")
    d.line(6.75, 3.75, 8.25, 3.75, "mueble")
    rotulo(d, 7.50, 2.75, "ESTACIO-\nNAMIENTO", "1 vehículo", 0.2)
    rotulo(d, 7.50, 7.40, "ZONA MULTIUSO", "taller / tendedero", 0.2)
    # columnas y escalera
    for x in XS:
        for y in YS:
            d.rect(x - COL / 2, y - COL / 2, x + COL / 2, y + COL / 2, "columna")
    escalera_planta(d, cortada=True, etiqueta="SUBE 17 CH", y_label=6.95)
    for x in (9.35, 10.25):
        d.rect(x - 0.1, 4.76, x + 0.1, 4.96, "columna")
    d.text(4.30, 0.35, "NPT +0.20", "t-nivel", 0.15)
    seccion_marca(d)
    # cotas
    dim_h(d, [0, 3, 6, 9], -1.45)
    dim_h(d, [9, ST_X1, ST_X2], -1.45, ["", "1.10"])
    dim_h(d, [0, 9.0], -1.95, ["9.00"], total=True)
    dim_h(d, [0, 1.40, 3.0], 10.65)
    dim_v(d, [0, 2.4, 5.7, 9.0], -1.35)
    dim_v(d, [0, 9.0], -1.85, ["9.00"], total=True)
    dim_v(d, [ST_TOP, DESC_Y0, DESC_Y1, ST_Y0], 11.05)
    escala_grafica(d, -2.9, -2.38)
    return d.svg("Planta baja")


# ========================================================= PLANTA ESTRUCTURAL
def planta_estructural():
    d = Dwg(-3.0, -2.45, 11.85, 11.75)
    ejes_planta(d)
    # plintos
    for x in XS:
        for y in YS:
            d.rect(x - 0.5, y - 0.5, x + 0.5, y + 0.5, "plinto")
    # vigas y riostras sobre ejes
    for y in YS:
        d.rect(-0.15, y - 0.125, 9.15, y + 0.125, "viga")
    for x in XS:
        d.rect(x - 0.125, -0.15, x + 0.125, 9.15, "viga")
    # volado del mirador
    for y in (Y1, Y2):
        d.rect(9.15, y - 0.125, VOL, y + 0.125, "viga-volado")
    d.rect(VOL - 0.25, -0.125, VOL, Y2 + 0.125, "viga-volado")
    # viguetas: muestra en un paño y flechas de dirección
    for i in range(1, 8):
        x = XB + i * 0.40 - 0.1
        d.line(x, Y2 + 0.125, x, Y3 - 0.125, "vigueta")
    for xm in (1.5, 7.5):
        for (ya, yb) in ((Y2, Y3), (Y3, Y4)):
            arrow(d, xm, (ya + yb) / 2 - 1.0, xm, (ya + yb) / 2 + 1.0, "flecha-est", 0.18)
            arrow(d, xm, (ya + yb) / 2 + 1.0, xm, (ya + yb) / 2 - 1.0, "flecha-est", 0.18)
    arrow(d, 9.72, 0.4, 9.72, 2.0, "flecha-est", 0.16)
    arrow(d, 9.72, 2.0, 9.72, 0.4, "flecha-est", 0.16)
    d.text(4.50, 4.35, "viguetas 2\"×8\" @ 0.40", "t-nota-f", 0.18)
    d.text(4.50, 4.10, "(luz 3.30 m)", "t-nota-f", 0.16)
    d.text(1.50, 1.30, "viguetas 2\"×8\" @ 0.40", "t-nota-f", 0.17)
    d.text(1.50, 1.07, "(luz 2.40 m)", "t-nota-f", 0.15)
    # columnas
    for x in XS:
        for y in YS:
            d.rect(x - COL / 2, y - COL / 2, x + COL / 2, y + COL / 2, "columna")
    # postes de madera y de cumbrera
    for x in (0.0, 3.0, 6.0, 9.0):
        d.circle(x, Y3, 0.09, "marca-cumbrera")
    for x in (10.30,):
        d.rect(x - 0.075, -0.075, x + 0.075, 0.075, "poste")
    # escalera: dado de arranque, columnetas y viga de descanso
    d.rect(ST_X1, DESC_Y0, ST_X2, DESC_Y1, "proyeccion")
    d.rect(ST_X1, ST_TOP, ST_X2, ST_Y0, "proyeccion")
    d.rect(ST_X1, 7.40, ST_X2, 7.90, "plinto")
    d.rect(ST_X1, 4.76, ST_X2, 4.96, "viga")
    for x in (9.35, 10.25):
        d.rect(x - 0.3, 4.56, x + 0.3, 5.16, "plinto")
        d.rect(x - 0.1, 4.76, x + 0.1, 4.96, "columna")
    # rótulos de elementos
    d.text(1.50, 9.85, "V 25×40 / R 25×30 en todos los ejes", "t-nota-f", 0.17)
    d.text(VOL - 0.6, -0.55, "volado 1.40", "t-nota-f", 0.16)
    d.text(10.85, 7.72, "dado de", "t-nota-f", 0.15, "start")
    d.text(10.85, 7.52, "arranque", "t-nota-f", 0.15, "start")
    d.text(10.85, 4.80, "columnetas", "t-nota-f", 0.15, "start")
    d.text(10.85, 4.60, "20×20", "t-nota-f", 0.15, "start")
    # cotas
    dim_h(d, [0, 3, 6, 9, VOL], -1.45, ["3.00", "3.00", "3.00", "1.40"])
    dim_h(d, [0, VOL], -1.95, ["10.40"], total=True)
    dim_v(d, [0, 2.4, 5.7, 9.0], -1.35)
    dim_v(d, [0, 9.0], -1.85, ["9.00"], total=True)
    escala_grafica(d, -2.9, -2.38)
    return d.svg("Planta de cimentación y estructura")


# ============================================================ PLANTA DE TECHO
def planta_techo():
    d = Dwg(-3.0, -2.45, 11.85, 11.75)
    ejes_planta(d, ymin=-1.3)
    d.rect(-0.15, Y2, 9.15, 9.15, "proyeccion")
    d.rect(ALERO_L, ALERO_F, ALERO_R, Y2, "techo-terr")
    d.rect(ALERO_L, Y2, ALERO_R, ALERO_B, "techo-main")
    d.line(ALERO_L, Y3, ALERO_R, Y3, "cumbrera")
    d.line(ALERO_L, Y2, ALERO_R, Y2, "quiebre")
    # canalones y bajantes
    for y in (ALERO_F - 0.08, ALERO_B + 0.08):
        d.rect(ALERO_L, y - 0.07, ALERO_R, y + 0.07, "canalon")
    for x, y in ((-0.65, ALERO_F - 0.08), (10.38, ALERO_F - 0.08), (-0.65, ALERO_B + 0.08), (10.38, ALERO_B + 0.08)):
        d.circle(x, y, 0.13, "bajante")
    # flechas de caída del agua
    for x in (1.5, 4.5, 7.5):
        arrow(d, x, 7.0, x, 9.4, "flecha", 0.22)
        arrow(d, x, 5.2, x, 3.0, "flecha", 0.22)
        arrow(d, x, 2.1, x, -0.4, "flecha", 0.22)
    d.text(3.0, 8.15, "30°  (57.7 %)", "t-nota-f", 0.21)
    d.text(3.0, 4.15, "30°  (57.7 %)", "t-nota-f", 0.21)
    d.text(3.0, 0.75, "15 %  (8.5°)", "t-nota-f", 0.21)
    d.text(6.0, Y3 + 0.12, "CUMBRERA VENTILADA  +8.35", "t-amb", 0.2)
    d.text(6.0, Y2 + 0.12, "quiebre de pendiente  +6.20", "t-nota-f", 0.17)
    d.text(4.6, ALERO_B + 0.32, "canalón 15 cm", "t-nota", 0.16)
    d.text(4.6, ALERO_F - 0.48, "canalón 15 cm", "t-nota", 0.16)
    d.text(10.9, ALERO_B + 0.4, "bajante Ø110", "t-nota", 0.15, "start")
    d.text(10.9, ALERO_F - 0.3, "bajante Ø110", "t-nota", 0.15, "start")
    d.rect(ST_X1, ST_TOP, ST_X2, ST_Y0, "proyeccion")
    d.text(9.80, 6.4, "escalera bajo alero", "t-nota", 0.15, rot=-90)
    # cotas
    dim_h(d, [ALERO_L, 0, 9.0, ALERO_R], -1.75, ["0.80", "9.00", "1.50"])
    dim_v(d, [ALERO_F, 0, 2.4, 5.7, 9.0, ALERO_B], -1.35, ["0.90", "2.40", "3.30", "3.30", "1.00"])
    dim_v(d, [ALERO_F, ALERO_B], -1.85, ["10.90"], total=True)
    dim_h(d, [ALERO_L, ALERO_R], -2.15, ["11.30"], total=True)
    return d.svg("Planta de cubierta")


# ================================================================== ELEMENTOS
def techo_corte(d, h0=ALERO_F, h1=ALERO_B):
    U = ROOF_PTS
    R = offset_poly(U, 0.14)
    P = offset_poly(U, CUB)
    d.poly(U + R[::-1], "madera-vista")
    d.poly(R + P[::-1], "cubierta-corte")
    return U, R, P


def tierra(d, h0, h1, z0=-1.65):
    d.rect(h0, z0, h1, NTN, "tierra")
    d.line(h0, NTN, h1, NTN, "terreno")


# ====================================================================== CORTE
def corte_aa():
    d = Dwg(-3.9, -2.45, 11.25, 9.0)
    tierra(d, -1.6, 10.9)
    # sub-base y contrapiso
    d.rect(-1.00, -0.10, 10.10, 0.10, "lastre")
    d.rect(-1.00, 0.10, 10.10, NPB, "corte-hormigon")
    # plintos y columnas enterradas (vistas al fondo)
    for y in YS:
        d.rect(y - 0.5, -1.30, y + 0.5, -1.00, "oculto")
        d.rect(y - 0.15, -1.00, y + 0.15, -0.20, "oculto")
        d.rect(y - 0.6, -1.35, y + 0.6, -1.30, "oculto")
    # riostras cortadas
    for y in YS:
        d.rect(y - 0.125, -0.20, y + 0.125, 0.10, "corte-hormigon")
    # columnas vistas, viga vista del eje C y vigas cortadas
    for y in YS:
        d.rect(y - 0.15, NPB, y + 0.15, FV, "col-vista")
    d.rect(-0.15, FV, 9.15, TV, "viga-vista")
    for y in YS:
        d.rect(y - 0.125, FV, y + 0.125, TV, "corte-hormigon")
    # paquete de piso
    d.rect(-0.15, TV, 9.15, NPA - 0.02, "madera-vista")
    d.rect(-0.15, NPA - 0.02, 9.15, NPA, "madera-corte")
    # terraza: baranda, poste visto, viga frontal cortada
    d.rect(-0.15, NPA, -0.05, NPA + 1.0, "madera-vista")
    d.line(-0.15, NPA + 0.12, -0.05, NPA + 0.12, "fino")
    d.rect(-0.075, NPA, 0.075, roof_under(0) - 0.20, "madera-vista")
    d.rect(-0.05, roof_under(0) - 0.20, 0.05, roof_under(0), "madera-corte")
    # muros cortados
    d.rect(Y2 - TE / 2, 5.40, Y2 + TE / 2, SOL, "muro-corte")
    d.rect(Y2 - 0.05, NPA, Y2 + 0.05, 5.40, "marco")
    d.line(Y2, NPA, Y2, 5.40, "vidrio")
    d.rect(Y4 - TE / 2, NPA, Y4 + TE / 2, NPA + 0.90, "muro-corte")
    d.rect(Y4 - TE / 2, NPA + 2.10, Y4 + TE / 2, SOL, "muro-corte")
    d.rect(Y4 - 0.05, NPA + 0.90, Y4 + 0.05, NPA + 2.10, "marco")
    d.line(Y4, NPA + 0.90, Y4, NPA + 2.10, "vidrio")
    d.rect(Y3 - TI / 2, NPA, Y3 + TI / 2, Z_CUMB - 0.25, "muro-corte")
    d.rect(Y3 - 0.05, Z_CUMB - 0.25, Y3 + 0.05, Z_CUMB, "madera-corte")
    # techo
    U, R, P = techo_corte(d)
    cielo = [(Y2 + 0.06, roof_under(Y2 + 0.06) - 0.03), (Y3, Z_CUMB - 0.03), (Y4 - 0.06, roof_under(Y4 - 0.06) - 0.03)]
    d.poly(cielo, "cielo", closed=False)
    # canalones
    for h in (ALERO_F, ALERO_B):
        s = -1 if h < 0 else 1
        z = roof_under(h)
        d.path(f"M {fmt(h)} {fmt(-z)} l {fmt(s*0.02)} 0.16 q {fmt(s*0.08)} 0.06 {fmt(s*0.16)} 0 l {fmt(s*0.02)} -0.18", "canalon-l")
    # muebles, auto, personas
    car_side(d, 0.60, 5.20, NPB)
    persona(d, 6.55, NPB)
    persona(d, 1.20, NPA)
    persona(d, 7.85, NPA)
    # rótulos
    d.text(1.15, NPA + 2.05, "TERRAZA", "t-amb", 0.22)
    d.text(4.05, NPA + 2.85, "SALA", "t-amb", 0.22)
    d.text(7.35, NPA + 2.85, "DORMITORIO 2", "t-amb", 0.22)
    d.text(2.90, 1.95, "ESTACIONAMIENTO", "t-amb", 0.2)
    d.text(7.35, 1.95, "ZONA MULTIUSO", "t-amb", 0.2)
    # llamadas
    llamada(d, 7.6, roof_under(7.6) + 0.22, 1, 7.6, 7.95)
    llamada(d, 3.6, roof_under(3.6) + 0.07, 2, 3.0, 7.55)
    llamada(d, Y3, Z_CUMB - 0.12, 3, 4.75, 8.6)
    llamada(d, 4.5, roof_under(4.5) - 0.03, 4, 4.5, 6.75)
    llamada(d, Y4, 5.8, 5, 9.75, 5.8)
    llamada(d, 6.5, NPA - 0.1, 6, 6.5, 2.45 + 0.0)
    llamada(d, 5.7 + 0.125, 2.8, 7, 5.15, 2.25)
    llamada(d, Y4, 1.4, 8, 9.75, 1.4)
    llamada(d, Y4 + 0.12, 0.0, 9, 9.75, -0.55)
    llamada(d, Y4 + 0.5, -1.15, 10, 10.45, -1.15)
    llamada(d, -0.10, NPA + 0.6, 11, -0.75, NPA + 1.35)
    llamada(d, ALERO_B + 0.08, roof_under(ALERO_B) - 0.1, 12, 10.55, 4.95)
    # niveles
    for z, lab in ((NTN, "NTN ±0.00"), (NPB, "NPT PB +0.20"), (FV, "fondo viga +2.60"),
                   (NPA, "NPT PA +3.20"), (SOL, "solera +6.20"), (Z_CUMB, "cumbrera +8.11")):
        nivel(d, -0.95, z, lab, "left", 0.55, debajo=(z == NTN))
    dim_v(d, [NTN, NPB, FV, NPA, SOL, Z_CUMB], -3.1, ["", "2.40", "0.60", "3.00", "1.91"])
    dim_v(d, [NTN, Z_CUMB + CUB], -3.45, ["8.35"], total=True)
    dim_h(d, [ALERO_F, 0, 2.4, 5.7, 9.0, ALERO_B], -1.75, ["0.90", "2.40", "3.30", "3.30", "1.00"])
    for y, n in zip(YS, EJE_Y):
        bubble(d, y, -2.15, n)
        d.line(y, -1.87, y, -1.55, "eje")
    return d.svg("Corte A-A")


def car_side(d, h0, h1, z0):
    pts = [(h0, z0 + 0.32), (h0, z0 + 0.82), (h0 + 0.15, z0 + 0.95), (h0 + 0.95, z0 + 1.0),
           (h0 + 1.55, z0 + 1.42), (h0 + 3.05, z0 + 1.45), (h0 + 3.75, z0 + 1.0),
           (h1 - 0.10, z0 + 0.92), (h1, z0 + 0.70), (h1, z0 + 0.32)]
    d.poly(pts, "auto")
    d.circle(h0 + 0.85, z0 + 0.32, 0.31, "rueda")
    d.circle(h1 - 0.95, z0 + 0.32, 0.31, "rueda")


# ======================================================== ELEVACIÓN LATERAL
def elevacion_lateral():
    d = Dwg(-3.1, -1.45, 11.25, 9.0)
    d.rect(-1.6, -0.35, 10.9, NTN, "tierra-e")
    d.line(-1.6, NTN, 10.9, NTN, "terreno")
    d.rect(-1.00, NTN, 10.10, NPB, "vereda-e")
    # núcleo de servicio al fondo
    d.rect(Y3 + 0.15, NPB, Y4 - 0.15, FV, "fondo")
    d.text(8.1, 2.32, "núcleo de servicio", "t-nota", 0.15)
    d.text(8.1, 2.12, "(al fondo)", "t-nota", 0.15)
    # columnas y vigas de borde
    for y in YS:
        d.rect(y - 0.15, NPB, y + 0.15, FV, "columna-e")
    d.rect(-0.15, FV, 9.15, TV, "viga-e")
    d.rect(-0.15, TV, 9.15, NPA, "madera-e")
    # pared lateral (hastial) con zócalo y caña
    gable = [(Y2 - 0.06, NPA), (Y4 + 0.06, NPA), (Y4 + 0.06, SOL), (Y3, Z_CUMB), (Y2 - 0.06, SOL)]
    d.poly(gable, "cana-e")
    d.rect(Y2 - 0.06, NPA, Y4 + 0.06, NPA + 1.0, "tabla-e")
    for i in range(1, 7):
        z = NPA + i * 0.15
        d.line(Y2 - 0.06, z, Y4 + 0.06, z, "tabla-l")
    for y in (Y2, 4.05, Y3, 7.35, Y4):
        top = roof_under(y)
        d.rect(y - 0.05, NPA + 1.0, y + 0.05, min(top, SOL) if y in (Y2, Y4) else top, "marco-e")
    d.rect(Y2 - 0.06, NPA + 0.95, Y4 + 0.06, NPA + 1.05, "marco-e")
    d.rect(Y2 - 0.06, SOL - 0.10, Y4 + 0.06, SOL, "marco-e")
    # ventanas
    for (a, b, z0, z1) in ((3.30, 4.80, NPA + 2.0, NPA + 2.6), (7.70, 8.60, NPA + 0.9, NPA + 2.1)):
        d.rect(a - 0.06, z0 - 0.06, b + 0.06, z1 + 0.06, "marco-e")
        d.rect(a, z0, b, z1, "vidrio-e")
        d.line((a + b) / 2, z0, (a + b) / 2, z1, "fino")
    # celosía del hastial
    d.rect(5.10, 6.55, 6.30, 7.30, "marco-e")
    d.rect(5.16, 6.61, 6.24, 7.24, "celosia-e")
    for i in range(1, 6):
        z = 6.61 + i * 0.105
        d.line(5.16, z, 6.24, z, "fino")
    # mirador en volado: viga de borde, baranda y poste
    d.rect(-0.15, FV, Y2 + 0.125, TV, "viga-e")
    d.rect(-0.15, TV, Y2 + 0.125, NPA, "madera-e")
    d.rect(-0.15, NPA, Y2, NPA + 1.0, "baranda-e")
    for i in range(0, 21):
        y = -0.10 + i * 0.125
        d.line(y, NPA + 0.08, y, NPA + 0.92, "balaustre")
    d.rect(-0.15, NPA + 0.92, Y2, NPA + 1.0, "madera-e")
    d.rect(-0.15, NPA, Y2, NPA + 0.08, "madera-e")
    d.rect(-0.075, NPA, 0.075, roof_under(0) - 0.20, "madera-e")
    d.rect(-0.05, roof_under(0) - 0.20, 0.05, roof_under(0), "madera-e")
    # techo: tapa del alero lateral (frontis)
    U = ROOF_PTS
    T = offset_poly(U, 0.30)
    d.poly(U + T[::-1], "frontis")
    P = offset_poly(U, 0.30)
    d.poly(P, "cubierta-borde", closed=False)
    # bajantes
    for h in (ALERO_F - 0.08, ALERO_B + 0.08):
        d.rect(h - 0.055, NPB, h + 0.055, roof_under(ALERO_F if h < 0 else ALERO_B) - 0.05, "bajante-e")
    # escalera
    pts = [(ST_Y0, NPB)]
    for k in range(1, 18):
        y = riser_y(k)
        z = riser_z(k)
        pts.append((y, z))
        if k == 9:
            pts.append((DESC_Y0, z))
        elif k < 17:
            pts.append((y - HU, z))
    m = CH / HU
    w = 0.15 * math.sqrt(1 + m * m)
    z_desc = riser_z(9)
    f2 = lambda y: (z_desc - w) + (DESC_Y0 - y) * m          # fondo tramo 2
    f1 = lambda y: (NPB - w) + (ST_Y0 - y) * m               # fondo tramo 1
    y_f2_land = DESC_Y0 - ((z_desc - 0.15) - (z_desc - w)) / m
    y_f1_land = ST_Y0 - ((z_desc - 0.15) - (NPB - w)) / m
    y_f1_ground = ST_Y0 - (NPB - (NPB - w)) / m
    pts += [(ST_TOP, f2(ST_TOP)), (y_f2_land, z_desc - 0.15), (y_f1_land, z_desc - 0.15), (y_f1_ground, NPB)]
    d.poly(pts, "escalera-e")
    # columneta bajo descanso
    d.rect(4.76, NPB, 4.96, z_desc - 0.15, "columna-e")
    # pasamanos
    hand = [(ST_Y0 + 0.05, riser_z(1) + 0.90), (DESC_Y1, riser_z(9) + 0.90), (DESC_Y0, riser_z(9) + 0.90),
            (DESC_Y0, riser_z(10) + 0.90), (ST_TOP, NPA + 0.90)]
    d.poly(hand, "pasamanos", closed=False)
    for k in range(1, 18, 2):
        y = riser_y(k) - HU / 2
        z = riser_z(k)
        zt = z + 0.90 + (HU / 2) * m if k != 9 else z + 0.90
        d.line(y, z, y, zt, "balaustre")
    # personas
    persona(d, 4.85, z_desc)
    persona(d, 8.35, NPB)
    # llamadas
    llamada(d, 9.6, roof_under(9.6) + 0.15, 1, 10.55, 6.7)
    llamada(d, 5.7, 6.9, 2, 7.0, 7.85)
    llamada(d, 8.2, NPA + 0.45, 3, 10.55, NPA + 0.45)
    llamada(d, 8.2, 5.75, 4, 10.55, 5.75)
    llamada(d, 6.6, riser_z(5), 5, 6.6, 2.15)
    llamada(d, 4.86, 1.2, 6, 3.75, 0.85)
    llamada(d, 1.2, NPA + 0.5, 7, 1.2, 4.95)
    for z, lab in ((NPB, "NPT PB +0.20"), (NPA, "NPT PA +3.20"), (SOL, "solera +6.20"), (Z_CUMB + CUB, "cumbrera +8.35")):
        nivel(d, -1.15, z, lab, "left", 0.55)
    dim_h(d, [0, 2.4, 5.7, 9.0], -0.55)
    for y, n in zip(YS, EJE_Y):
        bubble(d, y, -1.05, n)
    return d.svg("Elevación lateral derecha")


# ======================================================== ELEVACIÓN FRONTAL
def elevacion_frontal():
    d = Dwg(-3.1, -1.45, 11.65, 9.0)
    d.rect(-1.5, -0.35, 11.2, NTN, "tierra-e")
    d.line(-1.5, NTN, 11.2, NTN, "terreno")
    d.rect(-0.90, NTN, 10.65, NPB, "vereda-e")
    # fondo: núcleo y mobiliario de PB
    d.rect(0.15, NPB, 2.85, FV, "fondo")
    for a, b in ((0.35, 1.05), (1.95, 2.75)):
        d.rect(a, NPB, b, NPB + 2.10, "puerta-fondo")
    d.rect(3.15, NPB, 5.85, NPB + 0.90, "fondo")
    d.rect(0.35, NPB, 2.70, NPB + 0.75, "mueble-e", rx=0.06)
    d.rect(3.60, NPB + 0.72, 5.40, NPB + 0.77, "mueble-e")
    for x in (3.70, 5.30):
        d.line(x, NPB, x, NPB + 0.72, "mueble-e")
    car = [(6.62, NPB + 0.30), (6.62, NPB + 0.90), (6.82, NPB + 1.0), (7.05, NPB + 1.42), (7.95, NPB + 1.42),
           (8.18, NPB + 1.0), (8.38, NPB + 0.90), (8.38, NPB + 0.30)]
    d.poly(car, "auto")
    d.poly([(7.12, NPB + 1.02), (7.2, NPB + 1.36), (7.8, NPB + 1.36), (7.88, NPB + 1.02)], "fino")
    for x in (6.70, 8.05):
        d.rect(x, NPB, x + 0.25, NPB + 0.32, "rueda")
    # escalera vista de frente: contrahuellas
    for k in range(1, 18):
        z = riser_z(k)
        d.line(ST_X1, z, ST_X2, z, "peldano")
    d.rect(ST_X1, NPB, ST_X2, NPA, "escalera-f")
    for x in (9.35, 10.25):
        d.rect(x - 0.1, NPB, x + 0.1, riser_z(9) - 0.15, "columna-e")
    # columnas, vigas, borde de piso
    for x in XS:
        d.rect(x - 0.15, NPB, x + 0.15, FV, "columna-e")
    d.rect(-0.15, FV, VOL, TV, "viga-e")
    d.rect(-0.15, TV, VOL, NPA, "madera-e")
    # pared frontal con vanos
    d.rect(-0.06, NPA, 9.06, SOL, "cana-e")
    d.rect(-0.06, NPA, 9.06, NPA + 1.0, "tabla-e")
    for x in (0.0, 3.0, 6.0, 9.0):
        d.rect(x - 0.05, NPA, x + 0.05, SOL, "marco-e")
    for (a, b, z0, z1) in ((0.60, 2.20, NPA + 1.0, NPA + 2.0), (3.40, 5.20, NPA + 0.8, NPA + 2.2)):
        d.rect(a - 0.06, z0 - 0.06, b + 0.06, z1 + 0.06, "marco-e")
        d.rect(a, z0, b, z1, "vidrio-e")
        d.line((a + b) / 2, z0, (a + b) / 2, z1, "fino")
    d.rect(6.24, NPA, 8.76, NPA + 2.26, "marco-e")
    d.rect(6.30, NPA, 8.70, NPA + 2.20, "vidrio-e")
    d.line(7.50, NPA, 7.50, NPA + 2.20, "fino")
    d.rect(0.60, NPA + 0.92, 2.20, NPA + 1.0, "madera-e")
    # baranda
    d.rect(-0.15, NPA, VOL, NPA + 0.08, "madera-e")
    d.rect(-0.15, NPA + 0.92, VOL, NPA + 1.0, "madera-e")
    n = int((VOL + 0.15) / 0.125)
    for i in range(n + 1):
        x = -0.12 + i * 0.125
        d.line(x, NPA + 0.08, x, NPA + 0.92, "balaustre")
    # postes y viga frontal
    zb = roof_under(0) - 0.20
    for x in (0.0, 3.0, 6.0, 9.0, 10.30):
        d.rect(x - 0.075, NPA, x + 0.075, zb, "madera-e")
    d.rect(-0.15, zb, VOL, zb + 0.20, "madera-e")
    # cubierta vista: faldón de terraza + faldón principal
    z_eave = roof_under(ALERO_F)
    z_q = SOL + CUB / math.cos(math.atan(P_TERR))
    z_top = Z_CUMB + CUB / math.cos(math.radians(30))
    d.rect(ALERO_L, z_eave + 0.02, ALERO_R, z_q, "panel-terr")
    d.rect(ALERO_L, z_q, ALERO_R, z_top, "panel-main")
    x = ALERO_L + 0.25
    while x < ALERO_R - 0.05:
        d.line(x, z_eave + 0.25, x, z_q, "nervio")
        d.line(x, z_q, x, z_top, "nervio")
        x += 0.25
    d.rect(ALERO_L, z_eave - 0.05, ALERO_R, z_eave + 0.25, "frontis")
    d.rect(ALERO_L, z_eave - 0.17, ALERO_R, z_eave - 0.03, "canalon-e")
    for x in (-0.65, 10.44):
        d.rect(x - 0.055, NPB, x + 0.055, z_eave - 0.17, "bajante-e")
    persona(d, 4.6, NPA)
    persona(d, 4.55, NPB)
    llamada(d, 3.0, 4.95, 1, 3.0 + 0.0, 4.95)
    llamada(d, 7.5, zb + 0.1, 2, 7.5, 6.85)
    llamada(d, 7.0, NPA + 1.5, 3)
    llamada(d, 1.4, NPA + 1.5, 4)
    llamada(d, 1.5, 1.7, 5)
    llamada(d, 10.44, 1.2, 6, 11.05, 1.2)
    for z, lab in ((NPB, "NPT PB +0.20"), (NPA, "NPT PA +3.20"), (z_eave, "alero +5.70"), (z_top, "cumbrera +8.35")):
        nivel(d, -1.05, z, lab, "left", 0.55)
    dim_h(d, [0, 3, 6, 9, VOL], -0.55, ["3.00", "3.00", "3.00", "1.40"])
    for x, n in zip(XS, EJE_X):
        bubble(d, x, -1.05, n)
    return d.svg("Elevación frontal")


# ========================================================= DETALLE ESCALERA
def detalle_escalera():
    d = Dwg(1.40, -1.0, 8.95, 4.75)
    d.rect(1.45, -0.6, 8.7, NTN, "tierra")
    d.line(1.45, NTN, 8.7, NTN, "terreno")
    d.rect(1.45, NTN, 8.7, NPB, "vereda-e")
    m = CH / HU
    w = 0.15 * math.sqrt(1 + m * m)
    z_desc = riser_z(9)
    pts = [(ST_Y0, NPB)]
    for k in range(1, 18):
        y, z = riser_y(k), riser_z(k)
        pts.append((y, z))
        if k == 9:
            pts.append((DESC_Y0, z))
        elif k < 17:
            pts.append((y - HU, z))
    f2 = lambda y: (z_desc - w) + (DESC_Y0 - y) * m
    y_f2_land = DESC_Y0 - ((z_desc - 0.15) - (z_desc - w)) / m
    y_f1_land = ST_Y0 - ((z_desc - 0.15) - (NPB - w)) / m
    y_f1_ground = ST_Y0 - w / m
    pts += [(ST_TOP, f2(ST_TOP)), (y_f2_land, z_desc - 0.15), (y_f1_land, z_desc - 0.15), (y_f1_ground, NPB)]
    d.poly(pts, "corte-hormigon")
    # viga del eje 2 (llegada), piso del mirador y su baranda
    d.rect(ST_TOP - 0.25, FV, ST_TOP, TV, "corte-hormigon")
    d.rect(1.45, TV, ST_TOP, NPA, "madera-vista")
    d.rect(1.45, NPA - 0.02, ST_TOP, NPA, "madera-corte")
    d.rect(1.45, NPA + 0.92, ST_TOP, NPA + 1.0, "madera-e")
    y = 1.55
    while y < ST_TOP - 0.02:
        d.line(y, NPA, y, NPA + 0.92, "balaustre")
        y += 0.125
    # dado de arranque
    d.rect(7.30, -0.50, 8.00, NPB, "oculto")
    # columneta y viga de descanso
    d.rect(4.76, NPB, 4.96, z_desc - 0.15, "col-vista")
    d.rect(4.76, -0.5, 4.96, NPB, "oculto")
    d.rect(4.46, -0.6, 5.26, -0.5, "oculto")
    # pasamanos y balaustres
    hand = [(ST_Y0 + 0.05, riser_z(1) + 0.90), (DESC_Y1, z_desc + 0.90), (DESC_Y0, z_desc + 0.90),
            (DESC_Y0, riser_z(10) + 0.90), (ST_TOP, NPA + 0.90)]
    d.poly(hand, "pasamanos", closed=False)
    for k in range(1, 17):
        if k == 9:
            continue
        y = riser_y(k) - HU / 2
        z = riser_z(k)
        d.line(y, z, y, z + 0.90 + (HU / 2) * m, "balaustre")
    # números de contrahuella
    for k in range(1, 18):
        y, z = riser_y(k), riser_z(k)
        d.text(y - HU / 2, z + 0.04, str(k), "t-paso", 0.1)
    # cotas de un peldaño
    k = 4
    y, z = riser_y(k), riser_z(k)
    dim_h(d, [y - HU, y], z + 0.30, ["0.28"], 0.12)
    dim_v(d, [NPB, riser_z(1)], 7.95, ["0.176"], 0.11)
    # cotas generales
    dim_h(d, [ST_TOP, DESC_Y0, DESC_Y1, ST_Y0], -0.8, ["1.96 (7 huellas)", "1.00", "2.24 (8 huellas)"], 0.13)
    dim_v(d, [NPB, z_desc, NPA], 8.45, ["1.59 (9 CH)", "1.41 (8 CH)"], 0.13)
    dim_v(d, [NPB, NPA], 8.8, ["3.00"], 0.13, total=True)
    d.text(6.55, 3.05, "pasamanos h = 0.90 m", "t-nota", 0.12)
    d.text(3.30, 1.10, "losa H.A. e = 0.15 m", "t-nota", 0.12)
    d.text(4.86, 2.10, "descanso +1.79", "t-nota", 0.12)
    d.text(1.50, 4.36, "baranda del mirador h = 1.00", "t-nota", 0.12, "start")
    d.text(1.95, 2.38, "viga eje 2", "t-nota", 0.12)
    d.text(7.65, -0.30, "dado", "t-nota", 0.11)
    return d.svg("Detalle de escalera")


# ======================================================================= HTML
def main(out):
    tpl = open(sys.argv[1], encoding="utf-8").read()
    rep = {
        "{{PLANTA_BAJA}}": planta_baja(),
        "{{PLANTA_ALTA}}": planta_alta(),
        "{{PLANTA_TECHO}}": planta_techo(),
        "{{PLANTA_EST}}": planta_estructural(),
        "{{CORTE}}": corte_aa(),
        "{{ELEV_LAT}}": elevacion_lateral(),
        "{{ELEV_FRONT}}": elevacion_frontal(),
        "{{ESCALERA}}": detalle_escalera(),
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    open(out, "w", encoding="utf-8").write(tpl)
    print("ok", out, len(tpl))
    print("cumbrera fondo", round(Z_CUMB, 3), "alero frontal", round(roof_under(ALERO_F), 3),
          "alero post", round(roof_under(ALERO_B), 3), "viga frontal fondo", round(roof_under(0) - 0.2, 3),
          "CH", round(CH, 4), "descanso", round(riser_z(9), 3))


if __name__ == "__main__":
    main(sys.argv[2])
