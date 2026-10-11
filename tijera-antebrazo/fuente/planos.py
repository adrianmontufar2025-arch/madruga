"""
Genera los planos DXF pieza por pieza (y el plano de conjunto) a partir de modelo.py.

Cada plano lleva la geometría a escala real 1:1 en el espacio modelo (sirve
directo para corte láser, plasma o CNC), con el marco y el cajetín escalados
según la escala de la hoja. Proyección: método europeo (ISO-E, primer diedro).
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field

import ezdxf
from ezdxf.enums import TextEntityAlignment
from build123d import (Compound, ExportDXF, GeomType, LineType, Location, Pos, Rot, Unit)

sys.path.insert(0, os.path.dirname(__file__))
import modelo as MD  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_DXF = os.path.join(RAIZ, "planos_dxf")
os.makedirs(DIR_DXF, exist_ok=True)

HOJAS = {"A3": (420.0, 297.0), "A2": (594.0, 420.0)}
ESCALAS = [0.5, 1, 2, 5, 10]          # denominador (0.5 = escala 2:1)
FECHA = "2026-10-11"
PROYECTO = "Tijera de caña con apoyo de antebrazo"

VIEWPORTS = {
    "planta": ((0, 0, 5000), (0, 1, 0)),
    "alzado": ((0, -5000, 0), (0, 0, 1)),
    "perfil": ((-5000, 0, 0), (0, 0, 1)),      # vista lateral izquierda (ISO-E: a la derecha del alzado)
}
NOMBRE_VISTA = {"planta": "PLANTA", "alzado": "ALZADO", "perfil": "PERFIL IZQUIERDO"}


def proy(tipo, x, y, z):
    if tipo == "planta":
        return x, y
    if tipo == "alzado":
        return x, z
    if tipo == "perfil":
        return -y, z
    raise ValueError(tipo)


def esc_txt(k):
    if k < 1:
        return f"{int(round(1 / k))}:1"
    return f"1:{int(k)}"


@dataclass
class Cota:
    tipo: str            # lin | dia | rad | ang
    vista: str
    a: tuple = ()
    b: tuple = ()
    dist: float = 10.0
    angulo: float = 0.0  # para lin: 0 horizontal, 90 vertical; para dia/rad: ángulo de la línea
    texto: str = "<>"
    r: float = 0.0


@dataclass
class Plano:
    codigo: str
    titulo: str
    material: str
    cantidad: int
    masa_g: float
    forma: object
    vistas: list
    cotas: list = field(default_factory=list)
    notas: list = field(default_factory=list)
    agujeros: list = field(default_factory=list)     # (id, x, y, Ø, descripción)  en la vista planta o alzado
    vista_agujeros: str = "planta"
    tratamiento: str = "—"
    hoja: str = "A3"
    escala: float | None = None
    extra: list = field(default_factory=list)        # (forma, tipo_vista, etiqueta, dx, dy) vistas adicionales
    marcas_centro: bool = True
    origen: str = "eje del pivote" 


# ---------------------------------------------------------------------------
# Dibujo
# ---------------------------------------------------------------------------
class Hoja:
    def __init__(self, plano: Plano):
        self.p = plano
        self.exp = ExportDXF(version=ezdxf.DXF2013, unit=Unit.MM)
        self.exp.add_layer("VISIBLE", line_weight=0.5)
        self.exp.add_layer("OCULTAS", line_weight=0.25, line_type=LineType.ISO_DASH)
        self.exp.add_layer("EJES", line_weight=0.18, line_type=LineType.ISO_LONG_DASH_DOT)
        self.exp.add_layer("COTAS", line_weight=0.18)
        self.exp.add_layer("TEXTO", line_weight=0.25)
        self.exp.add_layer("MARCO", line_weight=0.7)
        self.doc = self.exp._document
        self.msp = self.exp._modelspace
        lay = self.doc.layers
        lay.get("OCULTAS").color = 8
        lay.get("EJES").color = 1
        lay.get("COTAS").color = 4
        lay.get("TEXTO").color = 7
        lay.get("MARCO").color = 7
        std = self.doc.styles.get("Standard")
        std.dxf.font = "arial.ttf"
        self.origenes = {}

    # -- utilidades de texto y líneas en coordenadas de hoja (mm de papel)
    def P(self, x, y):
        return (self.ox + x * self.k, self.oy + y * self.k)

    def texto(self, s, x, y, h=3.5, alin=TextEntityAlignment.LEFT, capa="TEXTO", papel=True):
        pos = self.P(x, y) if papel else (x, y)
        t = self.msp.add_text(s, height=h * self.k, dxfattribs={"layer": capa, "style": "Standard"})
        t.set_placement(pos, align=alin)
        return t

    def linea(self, a, b, capa="MARCO", papel=True):
        pa = self.P(*a) if papel else a
        pb = self.P(*b) if papel else b
        self.msp.add_line(pa, pb, dxfattribs={"layer": capa})

    def rect(self, x0, y0, x1, y1, capa="MARCO"):
        for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            self.linea(a, b, capa)

    # -- vistas
    def bbox2d(self, forma, tipo):
        bb = forma.bounding_box()
        xs, ys = [], []
        for x in (bb.min.X, bb.max.X):
            for y in (bb.min.Y, bb.max.Y):
                for z in (bb.min.Z, bb.max.Z):
                    u, v = proy(tipo, x, y, z)
                    xs.append(u)
                    ys.append(v)
        return min(xs), min(ys), max(xs), max(ys)

    def dibujar_vista(self, forma, tipo, ox, oy, etiqueta=None, clave=None):
        org, up = VIEWPORTS[tipo]
        vis, hid = forma.project_to_viewport(org, up, look_at=(0, 0, 0))
        mover = Location((ox, oy, 0))
        if vis:
            self.exp.add_shape([mover * e for e in vis], layer="VISIBLE")
        if hid:
            self.exp.add_shape([mover * e for e in hid], layer="OCULTAS")
        self.origenes[clave or tipo] = (tipo, ox, oy)
        # marcas de centro en agujeros
        if self.p.marcas_centro:
            vistos = set()
            for e in vis + hid:
                if e.geom_type == GeomType.CIRCLE and e.is_closed and e.radius <= 22:
                    c = e.arc_center
                    key = (round(c.X, 1), round(c.Y, 1))
                    if key in vistos:
                        continue
                    vistos.add(key)
                    L = e.radius + 2.5 * min(self.k, 2)
                    cx, cy = c.X + ox, c.Y + oy
                    self.msp.add_line((cx - L, cy), (cx + L, cy), dxfattribs={"layer": "EJES"})
                    self.msp.add_line((cx, cy - L), (cx, cy + L), dxfattribs={"layer": "EJES"})
        if etiqueta:
            x0, y0, x1, y1 = self.bbox2d(forma, tipo)
            t = self.msp.add_text(etiqueta, height=3.5 * self.k, dxfattribs={"layer": "TEXTO"})
            t.set_placement(((x0 + x1) / 2 + ox, y0 + oy - 27 * self.k), align=TextEntityAlignment.TOP_CENTER)

    def a_hoja(self, clave, x, y, z):
        tipo, ox, oy = self.origenes[clave]
        u, v = proy(tipo, x, y, z)
        return (u + ox, v + oy)

    # -- cotas
    def ds(self):
        if "ISO25" not in self.doc.dimstyles:
            d = self.doc.dimstyles.new("ISO25")
            for kk, vv in dict(dimtxt=2.5, dimasz=2.5, dimexe=1.25, dimexo=0.8, dimgap=0.8, dimtad=1,
                               dimdec=1, dimzin=8, dimtih=0, dimtoh=0, dimclrd=4, dimclre=4, dimclrt=7,
                               dimscale=self.k, dimdsep=44, dimlunit=2, dimtxsty="Standard",
                               dimjust=0, dimtix=0, dimatfit=3).items():
                setattr(d.dxf, kk, vv)
        return "ISO25"

    def cota(self, c: Cota):
        st = self.ds()
        at = {"layer": "COTAS"}
        if c.tipo == "lin":
            a = self.a_hoja(c.vista, *c.a)
            b = self.a_hoja(c.vista, *c.b)
            if c.angulo == 0:
                base = ((a[0] + b[0]) / 2, max(a[1], b[1]) + c.dist * self.k if c.dist >= 0 else min(a[1], b[1]) + c.dist * self.k)
            else:
                base = (max(a[0], b[0]) + c.dist * self.k if c.dist >= 0 else min(a[0], b[0]) + c.dist * self.k, (a[1] + b[1]) / 2)
            self.msp.add_linear_dim(base=base, p1=a, p2=b, angle=c.angulo, text=c.texto, dimstyle=st,
                                    dxfattribs=at).render()
        elif c.tipo == "dia":
            ctr = self.a_hoja(c.vista, *c.a)
            self.msp.add_diameter_dim(center=ctr, radius=c.r, angle=c.angulo, text=c.texto, dimstyle=st,
                                      override={"dimtmove": 0}, dxfattribs=at).render()
        elif c.tipo == "rad":
            ctr = self.a_hoja(c.vista, *c.a)
            self.msp.add_radius_dim(center=ctr, radius=c.r, angle=c.angulo, text=c.texto, dimstyle=st,
                                    dxfattribs=at).render()
        elif c.tipo == "ang":
            ctr = self.a_hoja(c.vista, *c.a)
            a0, a1 = c.b
            self.msp.add_angular_dim_cra(center=ctr, radius=c.r, start_angle=a0, end_angle=a1, distance=c.dist * self.k,
                                         text=c.texto, dimstyle=st, dxfattribs=at).render()
        elif c.tipo == "nota":
            a = self.a_hoja(c.vista, *c.a)
            dx, dy = c.b
            b = (a[0] + dx * self.k, a[1] + dy * self.k)
            self.msp.add_line(a, b, dxfattribs={"layer": "COTAS"})
            ang = math.atan2(a[1] - b[1], a[0] - b[0])
            s = 2.5 * self.k
            p1 = (a[0] - s * math.cos(ang - 0.25), a[1] - s * math.sin(ang - 0.25))
            p2 = (a[0] - s * math.cos(ang + 0.25), a[1] - s * math.sin(ang + 0.25))
            self.msp.add_solid([a, p1, p2], dxfattribs={"layer": "COTAS"})
            fin = (b[0] + (6 if dx >= 0 else -6) * self.k, b[1])
            self.msp.add_line(b, fin, dxfattribs={"layer": "COTAS"})
            t = self.msp.add_text(c.texto, height=2.5 * self.k, dxfattribs={"layer": "TEXTO"})
            t.set_placement((fin[0] + (1 if dx >= 0 else -1) * self.k, fin[1] + 0.8 * self.k),
                            align=TextEntityAlignment.BOTTOM_LEFT if dx >= 0 else TextEntityAlignment.BOTTOM_RIGHT)

    # -- tabla genérica (en coordenadas de papel)
    def tabla(self, x, y, columnas, filas, titulo=None, h=2.5, fila_h=6.0):
        """x, y: esquina superior izquierda en papel. columnas: [(titulo, ancho)]."""
        ancho = sum(w for _, w in columnas)
        yy = y
        if titulo:
            self.texto(titulo, x, yy + 2, 3.0, TextEntityAlignment.BOTTOM_LEFT)
        todas = [[c for c, _ in columnas]] + filas
        for i, fila in enumerate(todas):
            self.linea((x, yy), (x + ancho, yy), "MARCO" if i == 0 else "TEXTO")
            xx = x
            for (col, w), val in zip(columnas, fila):
                self.texto(str(val), xx + 1.5, yy - fila_h / 2, h, TextEntityAlignment.MIDDLE_LEFT)
                xx += w
            yy -= fila_h
        self.linea((x, yy), (x + ancho, yy), "MARCO")
        xx = x
        for _, w in columnas:
            self.linea((xx, y), (xx, yy), "TEXTO")
            xx += w
        self.linea((xx, y), (xx, yy), "TEXTO")
        return y - yy

    def cajetin(self, W, H):
        k = self.k
        x1, y0 = W - 10, 10
        x0 = x1 - 180
        alto = 48
        self.rect(x0, y0, x1, y0 + alto)
        filas = [y0 + 8, y0 + 16, y0 + 24, y0 + 34]
        for yy in filas:
            self.linea((x0, yy), (x1, yy), "TEXTO")
        self.linea((x0 + 90, y0), (x0 + 90, y0 + 24), "TEXTO")
        self.linea((x0 + 135, y0), (x0 + 135, y0 + 24), "TEXTO")
        self.linea((x0 + 135, y0 + 34), (x0 + 135, y0 + alto), "TEXTO")
        p = self.p
        lab = 1.8
        def campo(x, y, etiqueta, valor, h=2.6):
            self.texto(etiqueta, x + 1.2, y + 5.6, lab)
            self.texto(valor, x + 1.2, y + 1.3, h)
        self.texto(PROYECTO, x0 + 2, y0 + 42, 3.0)
        self.texto(p.titulo, x0 + 2, y0 + 36, 4.2)
        campo(x0 + 135, y0 + 34, "PLANO N.º", p.codigo, 4.0)
        self.texto("Material", x0 + 1.2, y0 + 30.6, lab)
        self.texto(p.material[:95], x0 + 1.2, y0 + 26.0, 2.4)
        campo(x0, y0 + 16, "Tratamiento / acabado", p.tratamiento[:52], 2.2)
        campo(x0 + 90, y0 + 16, "Cantidad", str(p.cantidad))
        campo(x0 + 135, y0 + 16, "Masa aprox.", f"{p.masa_g:,.0f} g".replace(",", "."))
        campo(x0, y0 + 8, "Tolerancias generales", "ISO 2768-mK · medidas en mm", 2.2)
        campo(x0 + 90, y0 + 8, "Escala", esc_txt(self.k))
        campo(x0 + 135, y0 + 8, "Hoja", p.hoja)
        campo(x0, y0, "Dibujó / Fecha", f"Claude (asistente IA) · {FECHA}", 2.2)
        campo(x0 + 90, y0, "Proyección", "ISO-E (europea)", 2.2)
        campo(x0 + 135, y0, "Revisión", "A · conceptual", 2.2)
        # símbolo de primer diedro
        sx, sy = x0 + 120, y0 + 30
        self.linea((sx - 9, sy - 2.5), (sx - 9, sy + 2.5), "TEXTO")
        self.linea((sx - 9, sy + 2.5), (sx - 3, sy + 4), "TEXTO")
        self.linea((sx - 3, sy + 4), (sx - 3, sy - 4), "TEXTO")
        self.linea((sx - 3, sy - 4), (sx - 9, sy - 2.5), "TEXTO")
        c = self.msp.add_circle(self.P(sx + 4, sy), 3.5 * k, dxfattribs={"layer": "TEXTO"})
        self.msp.add_circle(self.P(sx + 4, sy), 1.5 * k, dxfattribs={"layer": "TEXTO"})
        return x0, y0 + alto

    def marco(self, W, H):
        self.rect(0, 0, W, H, "TEXTO")
        self.rect(20, 10, W - 10, H - 10, "MARCO")
        self.texto("Diseño conceptual para prototipo. Validar fuerzas y medidas con ensayos de campo antes de fabricar en serie.",
                   22, H - 7.5, 2.2)


def colocar_vistas(hoja: Hoja, plano: Plano, area):
    """Distribuye las vistas (ISO-E) dentro de 'area' (x0, y0, x1, y1 en papel) eligiendo la escala."""
    forma = plano.forma
    bb = {t: hoja.bbox2d(forma, t) for t in ("planta", "alzado", "perfil")}
    extras = [(f, t, et, dx, dy) for (f, t, et, dx, dy) in plano.extra]

    def disposicion(k):
        gap = 40.0  # papel
        pos = {}
        # alzado en (0,0) relativo; planta debajo; perfil a la derecha
        w = lambda t: (bb[t][2] - bb[t][0]) / k
        h = lambda t: (bb[t][3] - bb[t][1]) / k
        tiene = set(plano.vistas)
        ancho = 0.0
        alto = 0.0
        if "alzado" in tiene:
            ax, ay = 0.0, (h("planta") + gap if "planta" in tiene else 0.0)
            pos["alzado"] = (ax, ay)
            ancho = w("alzado")
            alto = ay + h("alzado")
            if "planta" in tiene:
                pos["planta"] = (0.0, 0.0)
                ancho = max(ancho, w("planta"))
            if "perfil" in tiene:
                pos["perfil"] = (ancho + gap, ay)
                ancho = ancho + gap + w("perfil")
                alto = max(alto, ay + h("perfil"))
        else:
            pos["planta"] = (0.0, 0.0)
            ancho, alto = w("planta"), h("planta")
            if "perfil" in tiene:
                pos["perfil"] = (ancho + gap, 0.0)
                ancho += gap + w("perfil")
                alto = max(alto, h("perfil"))
        # vistas extra a la derecha
        for f, t, et, dx, dy in extras:
            b = hoja.bbox2d(f, t)
            pos[et] = (ancho + gap, 0.0)
            ancho += gap + (b[2] - b[0]) / k
            alto = max(alto, (b[3] - b[1]) / k)
        return pos, ancho, alto

    x0, y0, x1, y1 = area
    W, H = x1 - x0, y1 - y0 - 30
    if plano.escala:
        k = plano.escala
        pos, ancho, alto = disposicion(k)
    else:
        for k in ESCALAS:
            pos, ancho, alto = disposicion(k)
            if ancho <= W and alto <= H:
                break
    return k, pos, ancho, alto


def generar(plano: Plano):
    hoja = Hoja(plano)
    W, H = HOJAS[plano.hoja]
    # reserva para la tabla de agujeros
    ancho_tabla = 104.0 if plano.agujeros else 0.0
    area = (24, 66, W - 14 - (ancho_tabla + 6 if ancho_tabla else 0), H - 16)
    hoja.k = 1.0
    k, pos, ancho, alto = colocar_vistas(hoja, plano, area)
    hoja.k = k
    hoja.ox, hoja.oy = 0.0, 0.0
    # centrar el grupo en el área
    gx = area[0] + (area[2] - area[0] - ancho) / 2
    gy = area[1] + 30 + (area[3] - area[1] - 30 - alto) / 2
    for t in plano.vistas:
        b = hoja.bbox2d(plano.forma, t)
        px, py = pos[t]
        ox = (gx + px) * k - b[0]
        oy = (gy + py) * k - b[1]
        hoja.dibujar_vista(plano.forma, t, ox, oy, NOMBRE_VISTA[t])
    for f, t, et, _, _ in plano.extra:
        b = hoja.bbox2d(f, t)
        px, py = pos[et]
        ox = (gx + px) * k - b[0]
        oy = (gy + py) * k - b[1]
        hoja.dibujar_vista(f, t, ox, oy, et, clave=et)
    hoja.marco(W, H)
    cx0, cy1 = hoja.cajetin(W, H)
    for c in plano.cotas:
        try:
            hoja.cota(c)
        except Exception as ex:  # una cota mala no debe tumbar el plano
            print("  cota omitida", plano.codigo, c.tipo, ex)
    # notas
    if plano.notas:
        y = 56
        hoja.texto("NOTAS", 24, y, 3.0)
        i = 0
        for n in plano.notas:
            y -= 5.2
            if n.startswith("   "):
                hoja.texto("    " + n.strip(), 24, y, 2.4)
            else:
                i += 1
                hoja.texto(f"{i}. {n}", 24, y, 2.4)
    # tabla de agujeros
    if plano.agujeros:
        cols = [("Ag.", 9), ("X", 15), ("Y", 15), ("Diám.", 13), ("Tipo", 48)]
        filas = [[a, f"{x:.1f}".replace(".", ","), f"{y:.1f}".replace(".", ","), f"{d:g}".replace(".", ","), t]
                 for a, x, y, d, t in plano.agujeros]
        tx = W - 10 - sum(w for _, w in cols) - 4
        ty = H - 22
        alto_t = hoja.tabla(tx, ty, cols, filas, titulo="TABLA DE AGUJEROS")
        hoja.texto(f"Origen de coordenadas: {plano.origen}", tx, ty - alto_t - 4, 2.2)
        # etiquetas de agujero en la vista
        for a, x, y, d, t in plano.agujeros:
            px, py = hoja.a_hoja(plano.vista_agujeros, x, y, 0) if plano.vista_agujeros == "planta" else hoja.a_hoja(plano.vista_agujeros, x, 0, y)
            tt = hoja.msp.add_text(a, height=2.2 * k, dxfattribs={"layer": "COTAS"})
            tt.set_placement((px + (d / 2 + 1.2 * k), py + (d / 2 + 0.6 * k)), align=TextEntityAlignment.BOTTOM_LEFT)
    hoja.doc.header["$LTSCALE"] = k
    hoja.doc.header["$INSUNITS"] = 4
    ruta = os.path.join(DIR_DXF, f"{plano.codigo}_{slug(plano.titulo)}.dxf")
    hoja.exp.write(ruta)
    return ruta, k


def slug(s):
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
