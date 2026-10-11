"""
Cortadora selectiva de caña en pértiga — modelo paramétrico conceptual (Rev. A).

Todas las medidas en mm. Este archivo define la geometría de cada pieza y su
posición en el conjunto. Lo usan:
  - exportar_3d.py  -> STEP, GLB y STL del conjunto
  - planos.py       -> planos DXF pieza por pieza

Sistema de coordenadas del cabezal (H):
  origen en el eje del perno pivote, z = 0 en la cara inferior de la
  contracuchilla-gancho, X hacia adelante (hacia la caña), Y a la izquierda,
  Z hacia arriba. El plano de corte está en z = 8 (cara superior del gancho).
Sistema del mundo (W): suelo en z = 0 y la caña cortada centrada en x = y = 0.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from build123d import (
    Align, Axis, Box, CenterArc, Circle, Color, Compound, Cone, Cylinder, Face,
    Line, Location, Plane, Polygon, Pos, Rectangle, RectangleRounded, Rot,
    SlotCenterToCenter, Sphere, Spline, Torus, Wire, extrude, fillet,
)

# ---------------------------------------------------------------------------
# Parámetros principales
# ---------------------------------------------------------------------------
C_GARGANTA = (62.0, 12.0)      # centro de la garganta (tallo) en H
D_TALLO_MAX = 55.0             # capacidad de corte
R_GANCHO_INT = 30.0            # radio interior del gancho
R_GANCHO_EXT = 52.0            # radio exterior del gancho
ESP_GANCHO = 8.0               # espesor contracuchilla-gancho
ESP_CUCHILLA = 5.0             # espesor cuchilla móvil
Z_CORTE = ESP_GANCHO           # plano de corte en H
ALTURA_CORTE = 30.0            # altura de corte sobre el suelo (ajustable 15–45)
H_A_MUNDO = (-C_GARGANTA[0], -C_GARGANTA[1], ALTURA_CORTE - Z_CORTE)

ANG_APERTURA = 62.0            # apertura de la cuchilla (grados)
COLA_R = 60.0                  # brazo de la cola de la cuchilla
COLA_ANG = 100.0               # ángulo de la cola con la cuchilla cerrada

ANG_PERTIGA = 40.0             # inclinación de la pértiga sobre la horizontal
U = (-math.cos(math.radians(ANG_PERTIGA)), 0.0, math.sin(math.radians(ANG_PERTIGA)))
N_ARRIBA = (math.sin(math.radians(ANG_PERTIGA)), 0.0, math.cos(math.radians(ANG_PERTIGA)))

# Palanca angular (balancín) que cambia la dirección del tiro de la varilla
BRAZO_B = 45.0                 # brazo hacia la biela
BRAZO_A = 35.0                 # brazo hacia la varilla
Z_BIELA = 23.0                 # plano medio de la biela en H
Y_EJE = 45.0                   # plano medio del balancín y de la pértiga
Y_BIELA = Y_EJE + 11.5         # la biela trabaja al lado del balancín

D_TUBO = 32.0                  # pértiga de carbono Ø32 x 2


def _rot2(v, ang_deg):
    a = math.radians(ang_deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def punta_cola(theta):
    """Centro del agujero de la cola de la cuchilla (x, y) para apertura theta."""
    return _rot2((COLA_R * math.cos(math.radians(COLA_ANG)), COLA_R * math.sin(math.radians(COLA_ANG))), theta)


# Pivote del balancín: se elige para que, a media carrera, el brazo B quede
# vertical y la biela horizontal.
_t_mid = punta_cola(ANG_APERTURA / 2)
L_BIELA = 90.0
Q_BALANCIN = (_t_mid[0] - math.sqrt(L_BIELA ** 2 - (_t_mid[1] - Y_BIELA) ** 2), Y_EJE, Z_BIELA + BRAZO_B)


def angulo_balancin(theta):
    """Ángulo phi del balancín (0 = brazo B vertical) para la apertura theta."""
    tx, ty = punta_cola(theta)
    dy = ty - Y_EJE
    lo, hi = -80.0, 80.0
    for _ in range(80):
        mid = (lo + hi) / 2
        bx = Q_BALANCIN[0] + BRAZO_B * math.sin(math.radians(mid))
        bz = Q_BALANCIN[2] - BRAZO_B * math.cos(math.radians(mid))
        d = math.sqrt((tx - bx) ** 2 + (ty - Y_BIELA) ** 2 + (Z_BIELA - bz) ** 2)
        if d > L_BIELA:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def punto_b(phi, y=Y_EJE):
    return (Q_BALANCIN[0] + BRAZO_B * math.sin(math.radians(phi)), y,
            Q_BALANCIN[2] - BRAZO_B * math.cos(math.radians(phi)))


_A0 = (BRAZO_A * N_ARRIBA[0], BRAZO_A * N_ARRIBA[2])   # brazo A ⟂ a la varilla


def punto_a(phi):
    ax, az = _rot2(_A0, phi)
    return (Q_BALANCIN[0] + ax, Y_EJE, Q_BALANCIN[2] + az)


A_MEDIO = punto_a(0.0)


def eje(s):
    """Punto del eje de la pértiga (H) a la distancia s desde el brazo A medio."""
    return (A_MEDIO[0] + s * U[0], A_MEDIO[1], A_MEDIO[2] + s * U[2])


def plano_eje(s):
    """Plano local de una pieza de la pértiga: X a lo largo del eje, Z 'arriba'."""
    return Plane(origin=eje(s), x_dir=U, z_dir=N_ARRIBA)


# Estaciones a lo largo del eje (s, mm)
S_CODO = (40.0, 150.0)
S_COLLAR = (140.0, 185.0)
S_TUBO_INF = (170.0, 620.0)
S_FUNDA = (190.0, 410.0)
S_ACOPLE = (605.0, 685.0)
S_TUBO_SUP = (670.0, 1000.0)
S_EMP_DEL = (700.0, 860.0)
S_CARCASA = (990.0, 1250.0)
S_EMP_TRAS = 1190.0
S_VARILLA = (0.0, 1030.0)
S_ANILLA = 430.0               # en el centro de gravedad (ver exportar_3d.py)


# ---------------------------------------------------------------------------
# Utilidades de geometría
# ---------------------------------------------------------------------------
def sector(c, ri, ro, a0, barrido):
    o = CenterArc(c, ro, a0, barrido)
    i = CenterArc(c, ri, a0, barrido)
    return Face(Wire([o, Line(o @ 1, i @ 1), i, Line(i @ 0, o @ 0)]))


def poly(*pts):
    return Polygon(*pts, align=None)


def circ(x, y, r):
    return Pos(x, y) * Circle(r)


def tubo(largo, d_ext, d_int):
    t = Cylinder(d_ext / 2, largo, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if d_int > 0:
        t = t - Cylinder(d_int / 2, largo, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Rot(0, 90, 0) * t       # eje a lo largo de +X local


def safe_fillet(shape, edges, r):
    try:
        return fillet(edges, r)
    except Exception:
        return shape


# ---------------------------------------------------------------------------
# Piezas del cabezal (definidas en el sistema H)
# ---------------------------------------------------------------------------
def p01_gancho():
    cx, cy = C_GARGANTA
    mandibula = sector(C_GARGANTA, R_GANCHO_INT, R_GANCHO_EXT, 250, 115)
    rp = (R_GANCHO_INT + R_GANCHO_EXT) / 2
    pico = circ(cx + rp * math.cos(math.radians(5)), cy + rp * math.sin(math.radians(5)),
                (R_GANCHO_EXT - R_GANCHO_INT) / 2)
    a_in = (cx + R_GANCHO_INT * math.cos(math.radians(250)), cy + R_GANCHO_INT * math.sin(math.radians(250)))
    a_out = (cx + R_GANCHO_EXT * math.cos(math.radians(250)), cy + R_GANCHO_EXT * math.sin(math.radians(250)))
    cuello = poly((-45, -37), (a_out[0], -37), a_out, a_in, (18, -10), (18, 20), (-45, 20))
    perfil = mandibula + pico + cuello
    perfil = perfil - circ(0, 0, 6.25)                  # pivote M12
    for x, y in AGUJEROS_GANCHO:
        perfil = perfil - circ(x, y, 4.25)              # M8 avellanado
    for x, y in AGUJEROS_UNA:
        perfil = perfil - circ(x, y, 2.5)               # roscado M6 (broca 5)
    pieza = extrude(perfil, ESP_GANCHO)
    return pieza


AGUJEROS_GANCHO = [(-35.0, -25.0), (-38.0, -8.0), (-12.0, -28.0)]
R_UNA = 47.0
UNA_ANG = (292.0, 12.0)        # tramo frontal de la mandíbula
AGUJEROS_UNA = [
    (C_GARGANTA[0] + R_UNA * math.cos(math.radians(a)), C_GARGANTA[1] + R_UNA * math.sin(math.radians(a)))
    for a in (300.0, 4.0)
]


def _perfil_cuchilla():
    """Perfil de la cuchilla en posición cerrada (H)."""
    cx, cy = C_GARGANTA
    r_filo = R_GANCHO_INT + 4.0
    a_ini, a_fin = 251.0, 335.0
    filo = CenterArc(C_GARGANTA, r_filo, a_ini, a_fin - a_ini)
    p_ini = filo @ 0
    p_fin = filo @ 1
    lomo = Spline((p_fin.X, p_fin.Y), (p_fin.X - 6, p_fin.Y + 14), (62, 21.5), (6, 19.5),
                  tangents=[(0.15, 1), (-1, 0)])
    cuerpo = Face(Wire([Line((6, 19.5), (9, -16)), Line((9, -16), p_ini), filo, lomo]))
    cubo = circ(0, 0, 20)
    tx, ty = punta_cola(0)
    ang = math.degrees(math.atan2(ty, tx))
    brazo = Rot(0, 0, ang) * Pos(COLA_R / 2, 0) * Rectangle(COLA_R, 22)
    ojo = circ(tx, ty, 11)
    perfil = cuerpo + cubo + brazo + ojo
    perfil = perfil - circ(0, 0, 6.25) - circ(tx, ty, 4.0)
    return perfil


def p02_cuchilla():
    return Pos(0, 0, Z_CORTE) * extrude(_perfil_cuchilla(), ESP_CUCHILLA)


def p03_una():
    cx, cy = C_GARGANTA
    a0, a1 = UNA_ANG
    barrido = (a1 - a0) % 360
    pared = extrude(sector(C_GARGANTA, R_UNA - 1.5, R_UNA + 1.5, a0, barrido), 40)
    pestanas = None
    for x, y in AGUJEROS_UNA:
        ang = math.degrees(math.atan2(y - cy, x - cx))
        p = Pos(x, y) * Rot(0, 0, ang) * (Pos(1.5, 0) * Rectangle(14, 14))
        p = p - circ(x, y, 3.25)
        pestanas = p if pestanas is None else pestanas + p
    pest = extrude(pestanas, 3)
    una = Pos(0, 0, Z_CORTE) * (pared + pest)
    return una


CHASIS_X = (-182.0, 0.0)
CHASIS_Y = (-37.0, 74.0)
ESP_CHASIS = 8.0


def p05_chasis():
    x0, x1 = CHASIS_X
    y0, y1 = CHASIS_Y
    base = Pos((x0 + x1) / 2, (y0 + y1) / 2) * RectangleRounded(x1 - x0, y1 - y0, 8)
    frente = circ(0, 0, 24) + poly((0, -24), (0, 24), (-30, 24), (-30, -24))
    perfil = base + frente
    perfil = perfil - circ(0, 0, 6.25)
    for x, y in AGUJEROS_GANCHO:
        perfil = perfil - circ(x, y, 3.4)                     # roscado M8 (broca 6.8)
    for x, y in AGUJEROS_TORRE:
        perfil = perfil - circ(x, y, 3.4)
    # aligeramientos
    perfil = perfil - Pos(-70, -8) * RectangleRounded(40, 42, 10)
    perfil = perfil - Pos(-70, 46) * RectangleRounded(40, 26, 8)
    perfil = perfil - Pos(-126, 8) * RectangleRounded(44, 18, 6)
    perfil = perfil - Pos(-126, 47) * RectangleRounded(44, 18, 6)
    return Pos(0, 0, -ESP_CHASIS) * extrude(perfil, ESP_CHASIS)


TORRE_X = (-162.0, -90.0)
TORRE_Y = (Y_EJE - 14.0, Y_EJE + 28.0)
TORRE_Z = (0.0, 124.0)
AGUJEROS_TORRE = [(-154.0, 34.0), (-154.0, 68.5), (-98.0, 34.0), (-98.0, 68.5)]


def p04_torre():
    x0, x1 = TORRE_X
    y0, y1 = TORRE_Y
    z0, z1 = TORRE_Z
    caja = Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN))
    caja = safe_fillet(caja, caja.edges().filter_by(Axis.Y), 8)
    jefe = plano_eje(-10) * tubo(80, 48, 0)
    torre = caja + jefe
    # cavidad del balancín y de la biela (abierta hacia adelante)
    cy0, cy1 = TORRE_CAV_Y
    cav = Pos(x0 + 10, cy0, 6) * Box(x1 - x0 - 10, cy1 - cy0, z1 - 12, align=(Align.MIN, Align.MIN, Align.MIN))
    paso_biela = Pos(x1 - 40, 27, 6) * Box(60, cy1 - 27, 44, align=(Align.MIN, Align.MIN, Align.MIN))
    torre = torre - cav - paso_biela
    torre = torre - plano_eje(-30) * tubo(70, 30, 0)          # carrera del brazo A
    torre = torre - plano_eje(30) * tubo(50, 32.2, 0)         # alojamiento del codo
    # eje del balancín y tornillos de fijación
    torre = torre - Pos(Q_BALANCIN[0], Y_EJE, Q_BALANCIN[2]) * Rot(90, 0, 0) * Cylinder(5, 80)
    for x, y in AGUJEROS_TORRE:
        torre = torre - Pos(x, y, 0) * Cylinder(3.3, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x, z in AGUJEROS_GANCHO_TRAS:
        torre = torre - Pos(x, y1, z) * Rot(90, 0, 0) * Cylinder(2.5, 20)
    return torre


TORRE_CAV_Y = (Y_EJE - 8.0, Y_EJE + 19.0)
AGUJEROS_GANCHO_TRAS = [(-150.0, 52.0), (-122.0, 52.0)]


def p15_balancin():
    """Palanca angular en su posición media (phi = 0), plano XZ, centrada en Y_EJE."""
    qx, _, qz = Q_BALANCIN
    bx, _, bz = punto_b(0)
    ax, _, az = punto_a(0)
    pl = Plane.XZ
    def c2(x, z, r):
        return pl * Pos(x, z) * Circle(r)
    def barra(p, q, w):
        dx, dz = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dz)
        ang = math.degrees(math.atan2(dz, dx))
        return pl * Pos((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) * Rot(0, 0, ang) * Rectangle(L, w)
    perfil = c2(qx, qz, 12) + c2(bx, bz, 9) + c2(ax, az, 9) + barra((qx, qz), (bx, bz), 14) + barra((qx, qz), (ax, az), 14)
    perfil = perfil - c2(qx, qz, 5.0) - c2(bx, bz, 4.0) - c2(ax, az, 4.0)
    sol = extrude(perfil, 4, both=True)
    return Pos(0, Y_EJE, 0) * sol


def p09_biela():
    """Biela recta de 90 mm entre centros, de canto, en su sistema local (eje X)."""
    perfil = Pos(L_BIELA / 2, 0) * SlotCenterToCenter(L_BIELA, 16) - circ(0, 0, 4) - circ(L_BIELA, 0, 4)
    return Plane.XZ * extrude(perfil, 3, both=True)


def loc_biela(theta):
    phi = angulo_balancin(theta)
    b = punto_b(phi, Y_BIELA)
    tx, ty = punta_cola(theta)
    t = (tx, ty, Z_BIELA)
    d = (t[0] - b[0], t[1] - b[1], t[2] - b[2])
    n = (0.0, 0.0, 1.0)
    dl = math.sqrt(sum(c * c for c in d))
    xd = tuple(c / dl for c in d)
    dot = sum(a * b for a, b in zip(n, xd))
    zd = tuple(a - dot * b for a, b in zip(n, xd))
    return Location(Plane(origin=b, x_dir=xd, z_dir=zd))


def p07_patin():
    largo = 180.0
    x0 = -180.0
    y0, y1 = CHASIS_Y[0] - 3, CHASIS_Y[1] + 3
    zs = -(ALTURA_CORTE - Z_CORTE)          # suelo en H
    suela = Pos(x0, y0, zs) * Box(largo, y1 - y0, 6, align=(Align.MIN, Align.MIN, Align.MIN))
    r = 20.0

    def punta(xc, a0):
        sec = sector((0, 0), r - 6, r, a0, 70)
        return Pos(xc, y0, zs + r) * Rot(90, 0, 0) * extrude(sec, -(y1 - y0))

    suela = suela + punta(x0 + largo, 270) + punta(x0, 200)
    # alas laterales con colisos de regulación de altura
    for yy in (y0, CHASIS_Y[1]):
        ala = Pos(-170, yy, zs) * Box(140, 3, -zs + 6, align=(Align.MIN, Align.MIN, Align.MIN))
        for xs in PATIN_COLISOS_X:
            col = Pos(xs, yy + 1.5, -8) * Rot(90, 0, 0) * extrude(Rot(0, 0, 90) * SlotCenterToCenter(18, 6.5), 3, both=True)
            ala = ala - col
        suela = suela + ala
    return suela


PATIN_COLISOS_X = (-150.0, -50.0)


def p10_gancho_trasero():
    """Gancho de arrastre en forma de C abierta hacia el operario (plano XZ)."""
    pl = Plane.XZ
    y_cara = TORRE_Y[1]
    c = (-218.0, 52.0)
    arco = sector(c, 26, 36, -120, 240)
    brazo = poly((-162, 40), (-112, 40), (-112, 64), (-162, 64))
    union = poly((-186, 72), (-162, 64), (-162, 40), (-194, 30))
    perfil = arco + brazo + union
    for x, z in AGUJEROS_GANCHO_TRAS:
        perfil = perfil - circ(x, z, 3.4)
    sol = pl * extrude(perfil, -5)
    return Pos(0, y_cara, 0) * sol


# Guía superior
MASTIL_BASE = (-5.0, -56.0)
Z_BISAGRA = 14.0
Z_HORQUILLA = 600.0
OREJAS_Y = ((-70.0, -65.0), (-47.0, -42.0))


def p12_bisagra():
    x, y = MASTIL_BASE
    yc = CHASIS_Y[0]
    base = Pos(x, yc, -ESP_CHASIS) * Box(40, 5, 30, align=(Align.CENTER, Align.MAX, Align.MIN))
    fondo = Pos(x, yc, -ESP_CHASIS) * Box(40, yc - OREJAS_Y[0][0], 6, align=(Align.CENTER, Align.MAX, Align.MIN))
    b = base + fondo
    for ya, yb in OREJAS_Y:
        o = Pos(x, yb, Z_BISAGRA) * Rot(90, 0, 0) * Cylinder(11, yb - ya, align=(Align.CENTER, Align.CENTER, Align.MIN))
        o = o + Pos(x, ya, -ESP_CHASIS) * Box(22, yb - ya, Z_BISAGRA + ESP_CHASIS, align=(Align.CENTER, Align.MIN, Align.MIN))
        b = b + o
    b = b - Pos(x, 0, Z_BISAGRA) * Rot(90, 0, 0) * Cylinder(3.1, 200)
    for dx in (-13.0, 13.0):
        b = b - Pos(x + dx, yc, -ESP_CHASIS / 2) * Rot(90, 0, 0) * Cylinder(2.75, 20)
    return b


def p11_mastil():
    x, y = MASTIL_BASE
    z0, z1 = Z_BISAGRA + 16, Z_HORQUILLA - 20
    t = Pos(x, y, z0) * Cylinder(8, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    t = t - Pos(x, y, z0) * Cylinder(6.5, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return t


def p11b_terminales():
    x, y = MASTIL_BASE
    ya, yb = OREJAS_Y[0][1], OREJAS_Y[1][0]
    inf = Pos(x, yb, Z_BISAGRA) * Rot(90, 0, 0) * Cylinder(9, yb - ya, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inf = inf + Pos(x, y, Z_BISAGRA) * Cylinder(9, 45, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inf = inf - Pos(x, 0, Z_BISAGRA) * Rot(90, 0, 0) * Cylinder(3.1, 200)
    sup = Pos(x, y, Z_HORQUILLA - 40) * Cylinder(9, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return inf + sup


HORQ_RI, HORQ_RO = 34.0, 46.0
HORQ_BOCA = (342.0, 102.0)     # sector abierto (boca) de la horquilla


def p13_horquilla():
    cx, cy = C_GARGANTA
    a_fin, a_ini = HORQ_BOCA
    anillo = sector(C_GARGANTA, HORQ_RI, HORQ_RO, a_ini, (a_fin - a_ini) % 360)
    mx, my = MASTIL_BASE
    ang = math.degrees(math.atan2(cy - my, cx - mx))
    brazo_l = math.hypot(cx - mx, cy - my) - HORQ_RI - 4
    brazo = Pos(mx, my) * Rot(0, 0, ang) * Pos(brazo_l / 2, 0) * Rectangle(brazo_l, 22)
    ojo = circ(mx, my, 13)
    perfil = anillo + brazo + ojo - circ(mx, my, 8.1)
    # eje de la compuerta
    gx = cx + (HORQ_RI + HORQ_RO) / 2 * math.cos(math.radians(a_ini))
    gy = cy + (HORQ_RI + HORQ_RO) / 2 * math.sin(math.radians(a_ini))
    perfil = perfil - circ(gx, gy, 2.6)
    return Pos(0, 0, Z_HORQUILLA) * extrude(perfil, 6)


def p14_compuerta():
    cx, cy = C_GARGANTA
    a_fin, a_ini = HORQ_BOCA
    barrido = (a_ini - a_fin) % 360
    dedo = sector(C_GARGANTA, HORQ_RI + 1, HORQ_RI + 9, a_fin + 4, barrido - 4)
    gx = cx + (HORQ_RI + HORQ_RO) / 2 * math.cos(math.radians(a_ini))
    gy = cy + (HORQ_RI + HORQ_RO) / 2 * math.sin(math.radians(a_ini))
    ojo = circ(gx, gy, 7)
    brazo = poly((gx, gy - 4), (gx, gy + 4),
                 (cx + (HORQ_RI + 9) * math.cos(math.radians(a_ini - 6)), cy + (HORQ_RI + 9) * math.sin(math.radians(a_ini - 6))),
                 (cx + (HORQ_RI + 1) * math.cos(math.radians(a_ini - 6)), cy + (HORQ_RI + 1) * math.sin(math.radians(a_ini - 6))))
    perfil = dedo + ojo + brazo - circ(gx, gy, 2.6)
    return Pos(0, 0, Z_HORQUILLA + 6) * extrude(perfil, 3)


# ---------------------------------------------------------------------------
# Pértiga y accionamiento (definidas en su sistema local, eje +X)
# ---------------------------------------------------------------------------
def p08_codo():
    return tubo(S_CODO[1] - S_CODO[0], 32, 26)


def p06_collar():
    L = S_COLLAR[1] - S_COLLAR[0]
    c = tubo(L, 46, 32.2)
    # 8 muescas de indexado cada 45°
    for k in range(8):
        c = c - Rot(k * 45, 0, 0) * Pos(L / 2 - 4, 0, 23) * Box(8, 6, 6)
    c = c + Pos(L / 2 + 4, 0, 23) * Rot(0, 0, 0) * Cylinder(5, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return c


def p16_tubo_inf():
    return tubo(S_TUBO_INF[1] - S_TUBO_INF[0], D_TUBO, D_TUBO - 4)


def p17_funda():
    return tubo(S_FUNDA[1] - S_FUNDA[0], 37, D_TUBO)


def p18_acople():
    L = S_ACOPLE[1] - S_ACOPLE[0]
    a = tubo(L, 42, D_TUBO + 0.2)
    a = a + Pos(L / 2, 0, 0) * Rot(0, 90, 0) * Torus(21, 2.5)
    palanca = Pos(L / 2 - 20, 0, 21) * Box(52, 12, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    palanca = palanca + Pos(L / 2 + 6, 0, 21) * Rot(90, 0, 0) * Cylinder(6, 16)
    return a + palanca


def p19_tubo_sup():
    return tubo(S_TUBO_SUP[1] - S_TUBO_SUP[0], D_TUBO, D_TUBO - 4)


def p20_empunadura_del():
    L = S_EMP_DEL[1] - S_EMP_DEL[0]
    g = tubo(L, 40, D_TUBO)
    for k in range(1, 8):
        g = g + Pos(k * L / 8, 0, 0) * Rot(0, 90, 0) * Torus(20, 1.4)
    caja = Pos(L - 46, 0, 18) * Box(44, 26, 18, align=(Align.CENTER, Align.CENTER, Align.MIN))
    caja = safe_fillet(caja, caja.edges(), 4)
    gatillo_pres = Pos(L - 64, 0, 20) * Rot(0, -20, 0) * Box(36, 14, 6, align=(Align.MAX, Align.CENTER, Align.MIN))
    palanca_guia = Pos(L - 30, 12, 34) * Rot(0, 0, 0) * Box(10, 6, 16, align=(Align.CENTER, Align.MIN, Align.MIN))
    return g + caja + gatillo_pres + palanca_guia


def p21_anilla():
    a = tubo(24, 42, D_TUBO)
    a = a + Pos(12, 0, 21) * Box(18, 10, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    a = a + Pos(12, 0, 42) * Rot(90, 0, 0) * Torus(12, 3)
    return a


def p23_carcasa():
    L = S_CARCASA[1] - S_CARCASA[0]
    cono = Rot(0, 90, 0) * Cone(20, 32, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cuerpo = Pos(40, 0, 0) * tubo(L - 60, 64, 0)
    tapa = Pos(L - 20, 0, 0) * Rot(0, 90, 0) * Cone(32, 26, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c = cono + cuerpo + tapa
    # ranuras de ventilación
    for k in range(6):
        for lado in (1, -1):
            c = c - Pos(110 + k * 14, lado * 31, 6) * Box(6, 8, 30)
    # interruptor de bloqueo
    c = c + Pos(L - 70, 0, 31) * Box(28, 16, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return c


def p24_empunadura_tras():
    """Empuñadura tipo pistola, colgando bajo la carcasa (Z local negativo)."""
    pl = Plane.XZ
    pts = [(-30, -20), (24, -20), (30, -40), (22, -128), (14, -140), (-22, -140), (-30, -130), (-16, -40)]
    perfil = poly(*pts)
    sol = pl * extrude(perfil, 15, both=True)
    sol = safe_fillet(sol, sol.edges().filter_by(Axis.Y, reverse=True), 7)
    return sol


def p25_gatillo():
    pl = Plane.XZ
    pts = [(28, -44), (40, -46), (44, -60), (40, -86), (33, -88), (30, -60)]
    sol = pl * extrude(poly(*pts), 6, both=True)
    return sol


def loc_varilla(theta):
    a = punto_a(angulo_balancin(theta))
    o = (a[0] + 10 * U[0], a[1], a[2] + 10 * U[2])
    return Location(Plane(origin=o, x_dir=U, z_dir=N_ARRIBA))


def p22_varilla():
    return tubo(S_VARILLA[1] - S_VARILLA[0], 10, 7)


def interior_motor():
    m = Pos(130, 0, 0) * tubo(80, 52, 0)          # motor sin escobillas
    r = Pos(80, 0, 0) * tubo(50, 44, 0)           # reductor planetario
    h = Pos(10, 0, 0) * tubo(80, 16, 0)           # husillo de bolas SFU1605
    t = Pos(40, 0, 0) * tubo(38, 30, 0)           # tuerca del husillo
    return m, r, h, t


def p26_bateria():
    b = Box(170, 60, 105, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b = safe_fillet(b, b.edges(), 8)
    clip = Pos(0, -34, 60) * Box(120, 8, 50, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return b + clip


def tallo(altura=3500.0, d=45.0, tocon=False):
    """Caña de referencia (no es parte de la máquina)."""
    segs = []
    z = 0.0
    paso = 140.0
    while z < altura:
        h = min(paso, altura - z)
        segs.append(Pos(0, 0, z) * Cylinder(d / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        segs.append(Pos(0, 0, z) * Cylinder(d / 2 + 1.2, 6, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        z += paso
    return segs


# ---------------------------------------------------------------------------
# Lista de piezas y conjunto
# ---------------------------------------------------------------------------
@dataclass
class Pieza:
    codigo: str
    nombre: str
    material: str
    cantidad: int
    geometria: object              # sólido en su sistema local
    ubicacion: Location            # local -> H
    color: tuple
    grupo: str
    plano: bool = True             # se fabrica (lleva plano DXF)
    explosion: tuple = (0, 0, 0)   # desplazamiento en la vista explosionada (H)
    densidad: float = 7.85         # g/cm3
    cascara: float = 0.0           # >0: pieza hueca de este espesor (para la masa)
    notas: str = ""

    def masa(self):
        g = self.geometria
        if self.cascara > 0:
            return g.area * self.cascara / 1000 * self.densidad
        return g.volume / 1000 * self.densidad


ACERO_TEMPLADO = (0.42, 0.45, 0.49)
ACERO_FILO = (0.74, 0.77, 0.80)
ALUMINIO = (0.70, 0.72, 0.75)
ALUMINIO_ANOD = (0.20, 0.36, 0.62)
CARBONO = (0.10, 0.10, 0.11)
NARANJA = (0.95, 0.45, 0.10)
CAUCHO = (0.16, 0.16, 0.17)
INOX = (0.80, 0.81, 0.83)
FUNDA_PU = (0.98, 0.70, 0.10)
VERDE_CANA = (0.55, 0.64, 0.27)


def construir(theta=0.0):
    """Devuelve la lista de piezas con la cuchilla abierta theta grados (0 = cerrada)."""
    ident = Location()
    phi = angulo_balancin(theta)
    q = Q_BALANCIN
    rot_bal = Location(q) * Location((0, 0, 0), (0, 1, 0), -phi) * Location((-q[0], -q[1], -q[2]))
    rot_cuch = Location((0, 0, 0), (0, 0, 1), theta)

    def en_eje(s):
        return Location(plano_eje(s))

    up = tuple(14 * c for c in N_ARRIBA)
    piezas = [
        Pieza("P01", "Contracuchilla-gancho", "Acero SK5 / 65Mn templado 52-55 HRC", 1, p01_gancho(), ident,
              ACERO_TEMPLADO, "Cabezal", explosion=(0, 0, -60)),
        Pieza("P02", "Cuchilla móvil", "Acero D2 o SK5 templado 56-58 HRC", 1, p02_cuchilla(), rot_cuch,
              ACERO_FILO, "Cabezal", explosion=(0, 0, 70)),
        Pieza("P03", "Uña de retención", "Acero inoxidable AISI 304, 3 mm", 1, p03_una(), ident,
              INOX, "Cabezal", explosion=(60, -40, 40)),
        Pieza("P04", "Torre del cabezal", "Aluminio 6061-T6 mecanizado, anodizado", 1, p04_torre(), ident,
              ALUMINIO_ANOD, "Cabezal", explosion=(-40, 70, 60), densidad=2.70),
        Pieza("P05", "Placa base (chasis)", "Aluminio 7075-T6, 10 mm, anodizado", 1, p05_chasis(), ident,
              ALUMINIO_ANOD, "Cabezal", explosion=(0, 0, -130), densidad=2.81),
        Pieza("P06", "Collar giratorio indexado", "Aluminio 6061-T6, anodizado", 1, p06_collar(),
              en_eje(S_COLLAR[0]), ALUMINIO, "Pértiga", explosion=tuple(150 * c for c in U), densidad=2.70),
        Pieza("P07", "Patín de altura", "Suela UHMW-PE 6 mm + alas aluminio 5052 de 3 mm", 1, p07_patin(), ident,
              (0.30, 0.31, 0.33), "Cabezal", explosion=(0, 0, -210), densidad=1.25),
        Pieza("P08", "Codo del cabezal", "Tubo aluminio 6061-T6 Ø32 x 3", 1, p08_codo(), en_eje(S_CODO[0]),
              ALUMINIO, "Cabezal", explosion=tuple(90 * c for c in U), densidad=2.70),
        Pieza("P09", "Biela", "Acero SAE 1045, 8 mm", 1, p09_biela(), loc_biela(theta), ACERO_TEMPLADO, "Cabezal",
              explosion=(0, 0, 120)),
        Pieza("P10", "Gancho trasero de arrastre", "Acero SAE 1045, 6 mm", 1, p10_gancho_trasero(), ident,
              ACERO_TEMPLADO, "Cabezal", explosion=(-80, 60, 0)),
        Pieza("P11", "Mástil de la guía", "Tubo de carbono Ø16 x 1.5", 1, p11_mastil(), ident, CARBONO,
              "Guía superior", explosion=(0, -90, 0), densidad=1.55),
        Pieza("P11B", "Terminales del mástil", "Aluminio 6061-T6", 2, p11b_terminales(), ident, ALUMINIO,
              "Guía superior", explosion=(0, -90, 0), densidad=2.70),
        Pieza("P12", "Bisagra del mástil", "Aluminio 6061-T6", 1, p12_bisagra(), ident, ALUMINIO_ANOD,
              "Guía superior", explosion=(0, -50, -40), densidad=2.70),
        Pieza("P13", "Horquilla guía", "Aluminio 6061-T6, 6 mm, con forro UHMW", 1, p13_horquilla(), ident,
              ALUMINIO_ANOD, "Guía superior", explosion=(0, -90, 60), densidad=2.70),
        Pieza("P14", "Compuerta de resorte", "Acero inoxidable AISI 301 templado, 3 mm", 1, p14_compuerta(), ident,
              INOX, "Guía superior", explosion=(0, -90, 110)),
        Pieza("P15", "Palanca angular (balancín)", "Acero SAE 4140 bonificado, 10 mm", 1, p15_balancin(), rot_bal,
              ACERO_TEMPLADO, "Cabezal", explosion=(-40, 140, 60)),
        Pieza("P16", "Tramo inferior de pértiga", "Tubo de carbono Ø32 x 2 (enrollado)", 1, p16_tubo_inf(),
              en_eje(S_TUBO_INF[0]), CARBONO, "Pértiga", explosion=tuple(230 * c for c in U), densidad=1.55),
        Pieza("P17", "Funda protectora", "Poliuretano 2.5 mm", 1, p17_funda(), en_eje(S_FUNDA[0]), FUNDA_PU,
              "Pértiga", explosion=tuple(230 * c + 70 * n for c, n in zip(U, N_ARRIBA)), densidad=1.2),
        Pieza("P18", "Acople rápido con seguro", "Aluminio 6061-T6 + leva de acero", 1, p18_acople(),
              en_eje(S_ACOPLE[0]), ALUMINIO, "Pértiga", explosion=tuple(330 * c for c in U), densidad=2.70),
        Pieza("P19", "Tramo superior de pértiga", "Tubo de carbono Ø32 x 2 (enrollado)", 1, p19_tubo_sup(),
              en_eje(S_TUBO_SUP[0]), CARBONO, "Pértiga", explosion=tuple(430 * c for c in U), densidad=1.55),
        Pieza("P20", "Empuñadura delantera con mandos", "Caucho EPDM + caja PA6-GF30", 1, p20_empunadura_del(),
              en_eje(S_EMP_DEL[0]), CAUCHO, "Pértiga", explosion=tuple(430 * c + 90 * n for c, n in zip(U, N_ARRIBA)),
              densidad=1.25),
        Pieza("P21", "Anilla para arnés", "Acero inoxidable + PA6", 1, p21_anilla(), en_eje(S_ANILLA), INOX, "Pértiga",
              explosion=tuple(430 * c + 120 * n for c, n in zip(U, N_ARRIBA)), densidad=3.0),
        Pieza("P22", "Varilla de tracción", "Tubo aluminio 7075-T6 Ø10 x 1.5, en 2 tramos", 1, p22_varilla(), loc_varilla(theta),
              ACERO_FILO, "Accionamiento", explosion=tuple(-150 * n for n in N_ARRIBA), densidad=2.81),
        Pieza("P23", "Carcasa de accionamiento", "PA6-GF30 inyectado (prototipo: impresión 3D PA-CF)", 1,
              p23_carcasa(), en_eje(S_CARCASA[0]), NARANJA, "Accionamiento",
              explosion=tuple(560 * c for c in U), densidad=1.36, cascara=2.5),
        Pieza("P24", "Empuñadura trasera tipo pistola", "PA6-GF30 con sobremoldeo TPE", 1, p24_empunadura_tras(),
              en_eje(S_EMP_TRAS), NARANJA, "Accionamiento",
              explosion=tuple(560 * c - 120 * n for c, n in zip(U, N_ARRIBA)), densidad=1.36, cascara=3.0),
        Pieza("P25", "Gatillo proporcional", "PA6-GF30", 1, p25_gatillo(), en_eje(S_EMP_TRAS), CAUCHO,
              "Accionamiento", explosion=tuple(560 * c - 120 * n + 0 for c, n in zip(U, N_ARRIBA)), densidad=1.36),
    ]
    m, r, h, t = interior_motor()
    piezas += [
        Pieza("C01", "Motor sin escobillas 400-500 W, 36 V", "Comercial", 1, m, en_eje(S_CARCASA[0]),
              (0.55, 0.55, 0.58), "Accionamiento", plano=False,
              explosion=tuple(560 * c + 130 * n for c, n in zip(U, N_ARRIBA)), densidad=2.6),
        Pieza("C02", "Reductor planetario 15:1", "Comercial", 1, r, en_eje(S_CARCASA[0]), (0.45, 0.46, 0.5),
              "Accionamiento", plano=False, explosion=tuple(560 * c + 130 * n for c, n in zip(U, N_ARRIBA)),
              densidad=4.5),
        Pieza("C03", "Husillo de bolas SFU1605", "Comercial", 1, h, en_eje(S_CARCASA[0]), ACERO_FILO,
              "Accionamiento", plano=False, explosion=tuple(560 * c + 130 * n for c, n in zip(U, N_ARRIBA))),
        Pieza("C04", "Tuerca del husillo + horquilla de tiro", "Comercial", 1, t, en_eje(S_CARCASA[0]),
              (0.35, 0.36, 0.4), "Accionamiento", plano=False,
              explosion=tuple(560 * c + 130 * n for c, n in zip(U, N_ARRIBA)), densidad=5.0),
    ]
    return piezas


def bateria():
    return Pieza("C05", "Batería Li-ion 36 V 4 Ah al cinturón (IP65) + cable espiral", "Comercial", 1,
                 p26_bateria(), Location(), (0.12, 0.12, 0.13), "Accionamiento", plano=False, densidad=1.9)


def a_mundo():
    return Location(H_A_MUNDO)
