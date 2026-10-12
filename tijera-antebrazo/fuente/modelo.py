"""
Tijera de caña con apoyo de antebrazo — modelo paramétrico conceptual (Rev. A).

Herramienta de una mano: el operario sostiene la caña con la mano libre y con la
otra corta al ras del suelo. El antebrazo descansa en una cuna (P14) que recibe casi
todo el momento del cabezal; la correa de hombro (C08), enganchada en la anilla P16
sobre el centro de gravedad, toma lo que la herramienta tira hacia la punta, así los
dedos quedan libres para el gatillo de cuatro dedos (P12).

Todas las medidas en mm.

Sistema del cabezal (H): origen en el eje del perno pivote, z = 0 en la cara
inferior del gancho y de la placa base (fondo plano), X hacia la caña, Y a la
izquierda, Z arriba. Plano de corte en z = 8.
Sistema del mundo (W): suelo en z = 0, caña cortada centrada en x = y = 0.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from build123d import (
    Align, Axis, Box, CenterArc, Circle, Color, Cone, Cylinder, Face, Line, Location,
    Plane, Polygon, Pos, Rectangle, RectangleRounded, Rot, SlotCenterToCenter, Spline,
    Vector, Wire, extrude, fillet,
)

# ---------------------------------------------------------------------------
# Parámetros principales
# ---------------------------------------------------------------------------
D_TALLO_MAX = 65.0             # capacidad de corte (cañas de hasta ~6 cm)
C_GARGANTA = (72.0, 14.0)      # centro de la garganta en H
R_GANCHO_INT = 35.0
R_GANCHO_EXT = 57.0
ESP_GANCHO = 8.0
ESP_CUCHILLA = 5.0
Z_CORTE = ESP_GANCHO
ESP_PATIN = 3.0                # suela UHMW bajo el fondo plano
H_A_MUNDO = (-C_GARGANTA[0], -C_GARGANTA[1], ESP_PATIN)
ALTURA_CORTE = ESP_PATIN + Z_CORTE   # 11 mm sobre el suelo

ANG_APERTURA = 62.0
COLA_R = 70.0
COLA_ANG = 100.0

ANG_EJE = 45.0                 # inclinación del tubo cuando el cabezal apoya plano
U = (-math.cos(math.radians(ANG_EJE)), 0.0, math.sin(math.radians(ANG_EJE)))
N_ARRIBA = (math.sin(math.radians(ANG_EJE)), 0.0, math.cos(math.radians(ANG_EJE)))

BRAZO_B = 50.0
BRAZO_A = 38.0
Z_BIELA = 24.0
Y_EJE = 50.0
Y_BIELA = Y_EJE + 11.5
L_BIELA = 100.0
D_TUBO = 30.0

LAP_X = (-52.0, -32.0)         # junta a media madera gancho / placa base

# Rev. B: gancho corto con dientes + punta envolvente con resorte
FIN_MANDIBULA = 345.0          # la mandíbula fija termina aquí (sin pico curvo)
R_BISAGRA_DEDO = 46.0
BISAGRA_DEDO = (C_GARGANTA[0] + R_BISAGRA_DEDO * math.cos(math.radians(FIN_MANDIBULA)),
                C_GARGANTA[1] + R_BISAGRA_DEDO * math.sin(math.radians(FIN_MANDIBULA)))
DEDO_ARCO = (352.0, 60.0)      # arco que cubre la punta envolvente cuando está cerrada
ANG_DEDO_ABIERTO = -80.0       # giro de la punta cuando cede (caña apretada)
Z_DEDO = ESP_GANCHO + ESP_CUCHILLA + 0.8
ESP_DEDO = 6.0
DIENTES = (300.0, 343.0, 3.0, 1.2)   # tramo con dientes de agarre: desde, hasta, paso (mm), alto (mm)
FIN_FILO = 345.0               # la cuchilla barre hasta la punta de la mandíbula


def _rot2(v, ang_deg):
    a = math.radians(ang_deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def punta_cola(theta):
    return _rot2((COLA_R * math.cos(math.radians(COLA_ANG)), COLA_R * math.sin(math.radians(COLA_ANG))), theta)


_t_mid = punta_cola(ANG_APERTURA / 2)
Q_BALANCIN = (_t_mid[0] - math.sqrt(L_BIELA ** 2 - (_t_mid[1] - Y_BIELA) ** 2), Y_EJE, Z_BIELA + BRAZO_B)


def angulo_balancin(theta):
    tx, ty = punta_cola(theta)
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


# El brazo A queda perpendicular al eje a mitad de su giro, así la varilla casi no se desvía.
PHI_MEDIO = (angulo_balancin(0.0) + angulo_balancin(ANG_APERTURA)) / 2
_A0 = _rot2((BRAZO_A * N_ARRIBA[0], BRAZO_A * N_ARRIBA[2]), -PHI_MEDIO)


def punto_a(phi):
    ax, az = _rot2(_A0, phi)
    return (Q_BALANCIN[0] + ax, Y_EJE, Q_BALANCIN[2] + az)


A_MEDIO = punto_a(PHI_MEDIO)


def eje(s):
    return (A_MEDIO[0] + s * U[0], A_MEDIO[1], A_MEDIO[2] + s * U[2])


def plano_eje(s):
    return Plane(origin=eje(s), x_dir=U, z_dir=N_ARRIBA)


# Estaciones a lo largo del eje (s, mm, desde el brazo A hacia el operario)
S_TUBO = (40.0, 530.0)
S_CARCASA = (510.0, 740.0)
S_EMP = 550.0                  # centro de la empuñadura (mano)
S_CUNA = (765.0, 835.0)        # cuna de antebrazo (cerca del codo)
S_VARILLA = (0.0, 560.0)
Z_ANTEBRAZO = -80.0            # eje del antebrazo bajo el eje de la herramienta (local)
R_ANTEBRAZO = 40.0


# ---------------------------------------------------------------------------
# Utilidades
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
    return Rot(0, 90, 0) * t


def safe_fillet(shape, edges, r):
    try:
        return fillet(edges, r)
    except Exception:
        return shape


# ---------------------------------------------------------------------------
# Cabezal
# ---------------------------------------------------------------------------
AGUJEROS_LAP = [(-42.0, -32.0), (-42.0, -8.0), (-42.0, 14.0)]   # M6 avellanado desde abajo
GANCHO_X0 = LAP_X[0]


def _perfil_gancho():
    cx, cy = C_GARGANTA
    mandibula = sector(C_GARGANTA, R_GANCHO_INT, R_GANCHO_EXT, 250, FIN_MANDIBULA - 250)
    rp = (R_GANCHO_INT + R_GANCHO_EXT) / 2
    pico = circ(cx + rp * math.cos(math.radians(FIN_MANDIBULA)), cy + rp * math.sin(math.radians(FIN_MANDIBULA)),
                (R_GANCHO_EXT - R_GANCHO_INT) / 2)
    a_in = (cx + R_GANCHO_INT * math.cos(math.radians(250)), cy + R_GANCHO_INT * math.sin(math.radians(250)))
    a_out = (cx + R_GANCHO_EXT * math.cos(math.radians(250)), cy + R_GANCHO_EXT * math.sin(math.radians(250)))
    cuello = poly((GANCHO_X0, -43), (a_out[0], -43), a_out, a_in, (21, -11), (21, 23), (GANCHO_X0, 23))
    return mandibula + pico + cuello


def _dientes():
    """Dientes de sierra en el borde interior: apuntan hacia el fondo de la garganta para que la caña no se salga."""
    cx, cy = C_GARGANTA
    a0, a1, paso, alto = DIENTES
    dang = math.degrees(paso / R_GANCHO_INT)
    cortes = None
    a = a0
    while a + dang <= a1 + 1e-6:
        p1 = (cx + (R_GANCHO_INT - 0.5) * math.cos(math.radians(a)), cy + (R_GANCHO_INT - 0.5) * math.sin(math.radians(a)))
        p2 = (cx + (R_GANCHO_INT - 0.5) * math.cos(math.radians(a + dang)), cy + (R_GANCHO_INT - 0.5) * math.sin(math.radians(a + dang)))
        p3 = (cx + (R_GANCHO_INT + alto) * math.cos(math.radians(a + dang)), cy + (R_GANCHO_INT + alto) * math.sin(math.radians(a + dang)))
        t = poly(p1, p2, p3)
        cortes = t if cortes is None else cortes + t
        a += dang
    return cortes


def p01_gancho():
    perfil = _perfil_gancho() - _dientes() - circ(0, 0, 6.25) - circ(*BISAGRA_DEDO, 3.0)
    for x, y in AGUJEROS_LAP:
        perfil = perfil - circ(x, y, 3.3)
    pieza = extrude(perfil, ESP_GANCHO)
    pieza = pieza - Pos(0, 0, -ESP_PATIN) * Cone(11.2, 6.2, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # media madera: la cola del gancho queda con 4 mm (abajo) en la zona de empalme
    rebaje = Pos(LAP_X[0] - 1, -50, 4) * Box(LAP_X[1] - LAP_X[0] + 1, 80, 10, align=(Align.MIN, Align.MIN, Align.MIN))
    return pieza - rebaje


def _perfil_cuchilla():
    r_filo = R_GANCHO_INT + 4.0
    filo = CenterArc(C_GARGANTA, r_filo, 251.0, FIN_FILO - 251.0)
    p_ini, p_fin = filo @ 0, filo @ 1
    lomo = Spline((p_fin.X, p_fin.Y), (106, 16), (95, 24), (80, 26.5), (60, 25.5), (40, 24), (20, 22), (0, 20.0))
    cuerpo = Face(Wire([Line((0, 20.0), (0, -20.0)), Line((0, -20.0), p_ini), filo, lomo]))
    cubo = circ(0, 0, 23)
    tx, ty = punta_cola(0)
    ang = math.degrees(math.atan2(ty, tx))
    brazo = Rot(0, 0, ang) * Pos(COLA_R / 2, 0) * Rectangle(COLA_R, 25)
    ojo = circ(tx, ty, 12.5)
    perfil = cuerpo + cubo + brazo + ojo
    return perfil - circ(0, 0, 6.25) - circ(tx, ty, 4.0)


def p02_cuchilla():
    return Pos(0, 0, Z_CORTE) * extrude(_perfil_cuchilla(), ESP_CUCHILLA)


BASE_X0 = -192.0
BASE_Y = (-43.0, Y_EJE + 30.0)


def _perfil_base():
    y0, y1 = BASE_Y
    trasera = Pos((BASE_X0 + LAP_X[1]) / 2, (y0 + y1) / 2) * RectangleRounded(LAP_X[1] - BASE_X0, y1 - y0, 10)
    return trasera


def p03_placa_base():
    perfil = _perfil_base()
    for x, y in AGUJEROS_LAP:
        perfil = perfil - circ(x, y, 3.3)
    for x, y in AGUJEROS_TORRE:
        perfil = perfil - circ(x, y, 3.3)
    perfil = perfil - Pos(-75, -14) * RectangleRounded(30, 36, 8)
    perfil = perfil - Pos(-75, 42) * RectangleRounded(30, 40, 8)
    perfil = perfil - Pos(-150, -8) * RectangleRounded(40, 40, 8)
    perfil = perfil - Pos(-118, -20) * RectangleRounded(22, 30, 6)
    perfil = perfil - Pos(-140, 20) * RectangleRounded(50, 14, 5)
    pieza = extrude(perfil, ESP_GANCHO)
    rebaje = Pos(LAP_X[0], -50, -1) * Box(LAP_X[1] - LAP_X[0] + 1, 140, 5, align=(Align.MIN, Align.MIN, Align.MIN))
    return pieza - rebaje


def p04_patin():
    perfil = _perfil_base() + Pos((LAP_X[0] + 15) / 2, -10) * RectangleRounded(15 - LAP_X[0], 66, 10)
    perfil = perfil - circ(0, 0, 11)                       # paso de la cabeza del perno pivote
    for x, y in AGUJEROS_LAP + AGUJEROS_TORRE:
        perfil = perfil - circ(x, y, 6.5)                  # avellanados
    return Pos(0, 0, -ESP_PATIN) * extrude(perfil, ESP_PATIN)


TORRE_X = (-180.0, -98.0)
TORRE_Y = (Y_EJE - 18.0, Y_EJE + 28.0)
TORRE_Z = (ESP_GANCHO, 136.0)
TORRE_CAV_Y = (Y_EJE - 8.0, Y_EJE + 19.0)
AGUJEROS_TORRE = [(-172.0, Y_EJE - 13.0), (-172.0, Y_EJE + 23.5), (-106.0, Y_EJE - 13.0), (-106.0, Y_EJE + 23.5)]


def p05_torre():
    x0, x1 = TORRE_X
    y0, y1 = TORRE_Y
    z0, z1 = TORRE_Z
    caja = Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN))
    caja = safe_fillet(caja, caja.edges().filter_by(Axis.Y), 8)
    jefe = plano_eje(-10) * tubo(80, 46, 0)
    torre = caja + jefe
    cy0, cy1 = TORRE_CAV_Y
    cav = Pos(x0 + 10, cy0, z0 + 6) * Box(x1 - x0 - 10, cy1 - cy0, z1 - z0 - 12, align=(Align.MIN, Align.MIN, Align.MIN))
    paso = Pos(x1 - 40, 30, z0 + 6) * Box(60, cy1 - 30, 46, align=(Align.MIN, Align.MIN, Align.MIN))
    torre = torre - cav - paso
    torre = torre - plano_eje(-30) * tubo(70, 30, 0)
    torre = torre - plano_eje(30) * tubo(50, D_TUBO + 0.2, 0)
    torre = torre - Pos(Q_BALANCIN[0], Y_EJE, Q_BALANCIN[2]) * Rot(90, 0, 0) * Cylinder(5, 80)
    for x, y in AGUJEROS_TORRE:
        torre = torre - Pos(x, y, z0) * Cylinder(2.5, 16, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # aligeramientos en las dos caras laterales (paredes de 4 mm)
    for yy, ancho in ((y0, cy0 - y0 - 4), (cy1 + 4, y1 - cy1 - 4)):
        bolsillo = Pos(x0 + 16, yy, z0 + 24) * Box(x1 - x0 - 30, ancho, 70, align=(Align.MIN, Align.MIN, Align.MIN))
        torre = torre - bolsillo
    return torre


def p06_balancin():
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

    perfil = c2(qx, qz, 12) + c2(bx, bz, 9) + c2(ax, az, 9) + barra((qx, qz), (bx, bz), 15) + barra((qx, qz), (ax, az), 15)
    perfil = perfil - c2(qx, qz, 5.0) - c2(bx, bz, 4.0) - c2(ax, az, 4.0)
    return Pos(0, Y_EJE, 0) * extrude(perfil, 4, both=True)


def p07_biela():
    perfil = Pos(L_BIELA / 2, 0) * SlotCenterToCenter(L_BIELA, 16) - circ(0, 0, 4) - circ(L_BIELA, 0, 4)
    return Plane.XZ * extrude(perfil, 3, both=True)


def loc_biela(theta):
    phi = angulo_balancin(theta)
    b = punto_b(phi, Y_BIELA)
    tx, ty = punta_cola(theta)
    d = (tx - b[0], ty - b[1], Z_BIELA - b[2])
    dl = math.sqrt(sum(c * c for c in d))
    xd = tuple(c / dl for c in d)
    dot = xd[2]
    zd = (-dot * xd[0], -dot * xd[1], 1 - dot * xd[2])
    return Location(Plane(origin=b, x_dir=xd, z_dir=zd))


def p17_dedo(abierto=False):
    """Punta envolvente con resorte: rodea la caña si hay espacio; cede si la caña está apretada."""
    cx, cy = C_GARGANTA
    a0, a1 = DEDO_ARCO
    arco = sector(C_GARGANTA, R_GANCHO_INT + 3, R_GANCHO_EXT - 4, a0, (a1 - a0) % 360)
    rp = (R_GANCHO_INT + 3 + R_GANCHO_EXT - 4) / 2
    punta = circ(cx + rp * math.cos(math.radians(a1)), cy + rp * math.sin(math.radians(a1)), (R_GANCHO_EXT - R_GANCHO_INT - 7) / 2)
    cubo = circ(*BISAGRA_DEDO, 8.5)
    tope = Pos(*BISAGRA_DEDO) * Rot(0, 0, FIN_MANDIBULA - 90) * Pos(0, -9, 0) * Rectangle(8, 6)
    perfil = arco + punta + cubo + tope - circ(*BISAGRA_DEDO, 3.1)
    pieza = Pos(0, 0, Z_DEDO) * extrude(perfil, ESP_DEDO)
    if abierto:
        bx, by = BISAGRA_DEDO
        pieza = Location((bx, by, 0)) * Location((0, 0, 0), (0, 0, 1), ANG_DEDO_ABIERTO) * Location((-bx, -by, 0)) * pieza
    return pieza


def c07_pasador_resorte():
    bx, by = BISAGRA_DEDO
    pasador = Pos(bx, by, 0) * Cylinder(3, Z_DEDO + ESP_DEDO + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    separador = Pos(bx, by, ESP_GANCHO) * Cylinder(4.5, Z_DEDO - ESP_GANCHO, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cabeza = Pos(bx, by, Z_DEDO + ESP_DEDO) * Cylinder(5, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    resorte = Pos(bx, by, Z_DEDO + ESP_DEDO + 2.5) * (Cylinder(4.5, 3, align=(Align.CENTER, Align.CENTER, Align.MIN)) -
                                                      Cylinder(3.2, 3, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return pasador + separador + cabeza + resorte


def c06_perno():
    cabeza = Pos(0, 0, -ESP_PATIN) * Cone(11, 6.5, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    vastago = Cylinder(6, Z_CORTE + ESP_CUCHILLA + 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tuerca = Pos(0, 0, Z_CORTE + ESP_CUCHILLA) * Cylinder(11, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return cabeza + vastago + tuerca


# ---------------------------------------------------------------------------
# Brazo de la herramienta (sistema local: X a lo largo del eje, Z "arriba")
# ---------------------------------------------------------------------------
def p08_tubo():
    return tubo(S_TUBO[1] - S_TUBO[0], D_TUBO, D_TUBO - 4)


def p09_varilla():
    return tubo(S_VARILLA[1] - S_VARILLA[0] - 10, 10, 7)


def loc_varilla(theta):
    a = punto_a(angulo_balancin(theta))
    fin = eje(S_VARILLA[1])
    d = [f - c for f, c in zip(fin, a)]
    n = math.sqrt(sum(c * c for c in d))
    d = [c / n for c in d]
    o = (a[0] + 10 * d[0], a[1], a[2] + 10 * d[2])
    zd = (-d[2], 0.0, d[0])
    return Location(Plane(origin=o, x_dir=tuple(d), z_dir=zd))


def p10_carcasa():
    L = S_CARCASA[1] - S_CARCASA[0]
    cono = Rot(0, 90, 0) * Cone(17, 29, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cuerpo = Pos(40, 0, 0) * tubo(L - 60, 58, 0)
    tapa = Pos(L - 20, 0, 0) * Rot(0, 90, 0) * Cone(29, 22, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c = cono + cuerpo + tapa
    for k in range(5):
        for lado in (1, -1):
            c = c - Pos(120 + k * 14, lado * 28, 8) * Box(6, 8, 26)
    c = c + Pos(L - 60, 0, 28) * Box(26, 14, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return c


def _trazo(puntos, ancho):
    """Barra de ancho constante que sigue una poligonal (plano XZ local)."""
    pieza = None
    for (x0, z0), (x1, z1) in zip(puntos[:-1], puntos[1:]):
        L = math.hypot(x1 - x0, z1 - z0)
        ang = math.degrees(math.atan2(z1 - z0, x1 - x0))
        seg = Pos((x0 + x1) / 2, (z0 + z1) / 2) * Rot(0, 0, ang) * Rectangle(L, ancho)
        pieza = seg if pieza is None else pieza + seg
    for x, z in puntos:
        pieza = pieza + circ(x, z, ancho / 2)
    return pieza


GUARDAMONTE = [(-6.0, -150.0), (-78.0, -148.0), (-90.0, -74.0), (-48.0, -25.0)]


def p11_empunadura():
    """Empuñadura tipo pistola con gatillo de cuatro dedos y guardamonte (plano XZ local; el frente mira al cabezal, -X).

    Sección ovalada de 44 x 32 mm (equivale a Ø38: agarre de fuerza con guante), inclinada hacia atrás para que la
    muñeca quede neutra con el antebrazo en la cuna. Arriba atrás lleva un tope (cola de castor) donde apoya el arco
    entre pulgar e índice: por ahí se levanta la herramienta, así los dedos quedan libres para el gatillo. Arriba
    adelante, una repisa cierra el guardamonte sobre el índice. Tope inferior para que la mano no resbale.
    La seguridad es un sensor capacitivo de presencia en la cara trasera: no hay que apretar nada."""
    pl = Plane.XZ
    pts = [(-50, -20), (30, -20), (50, -23), (49, -31), (37, -44), (41, -128), (48, -140), (43, -156), (-7, -156),
           (-12, -144), (-7, -132), (-20, -45), (-24, -31), (-50, -29)]
    sol = pl * extrude(poly(*pts), 16, both=True)
    sol = safe_fillet(sol, sol.edges().filter_by(Axis.Y, reverse=True), 8)
    guarda = pl * extrude(_trazo(GUARDAMONTE, 8), 6, both=True)
    return sol + guarda


def _frente_empunadura(z):
    """x local de la cara delantera de la empuñadura a la altura z (z negativo hacia abajo)."""
    if z >= -45:
        return -24 + (-31 - z) * (4 / 14)
    return -20 + (-45 - z) * (13 / 87)


GATILLO_Z = (-35.0, -128.0)      # el gatillo cubre los cuatro dedos
GATILLO_DEDOS = (-48.0, -71.0, -94.0, -116.0)


def p12_gatillo():
    """Gatillo largo de cuatro dedos, como el acelerador de una rozadora: índice, medio, anular y meñique
    reparten el esfuerzo. Cuatro hendiduras ubican los dedos; pivote arriba, bajo la repisa."""
    z0, z1 = GATILLO_Z
    n = 40
    atras, frente = [], []
    for k in range(n + 1):
        z = z0 + (z1 - z0) * k / n
        xb = _frente_empunadura(z) - 3.5
        hondo = min(abs(z - zd) for zd in GATILLO_DEDOS)
        esp = 13.0 + 4.0 * min(hondo / 11.5, 1.0)          # 13 mm en la hendidura, 17 mm en las crestas
        atras.append((xb, z))
        frente.append((xb - esp, z))
    pts = frente + [(frente[-1][0] + 6, z1 - 3), (atras[-1][0], z1)] + atras[::-1]
    return Plane.XZ * extrude(poly(*pts), 10, both=True)


def p18_pulgar():
    """Palanca de pulgar arriba, en el costado izquierdo de la empuñadura (opcional, trabaja en paralelo con el
    gatillo): el operario puede alternar dedos y pulgar durante la jornada."""
    paleta = Pos(4, -25, -26) * Box(30, 7, 12, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    paleta = safe_fillet(paleta, paleta.edges(), 2.5)
    eje = Pos(-10, -20, -26) * Rot(90, 0, 0) * Cylinder(4, 10)
    return paleta + eje


def p13_brazo_apoyo():
    """Escuadra lateral (lado exterior del antebrazo derecho) que une la carcasa con la cuna."""
    s0 = S_CARCASA[1] - S_CARCASA[0]           # coordenadas relativas al inicio de la carcasa
    ala = Pos(s0 - 50, 10, -36) * Box(50, 45, 7, align=(Align.MIN, Align.MIN, Align.MIN))
    perfil = poly((s0 - 50, -29), (s0, -29), (s0 + 95, -62), (s0 + 95, -100), (s0 + 25, -100), (s0 + 25, -66),
                  (s0 - 50, -36))
    placa = Pos(0, 49, 0) * (Plane.XZ * extrude(perfil, 6))       # y local de 49 a 55 (lado exterior)
    pieza = ala + placa
    for ds in (-38.0, -14.0):
        pieza = pieza - Pos(s0 + ds, 20, -40) * Cylinder(3.3, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    sc = (S_CUNA[0] + S_CUNA[1]) / 2 - S_CARCASA[0]
    ranura = Pos(sc, 52, Z_ANTEBRAZO) * Rot(90, 0, 0) * extrude(SlotCenterToCenter(40, 8.2), 10, both=True)
    return pieza - ranura


CUNA_ANG = (150.0, 240.0)       # arco de la cuna (abierta arriba 120°)


def p14_cuna():
    L = S_CUNA[1] - S_CUNA[0]
    a0, barrido = CUNA_ANG
    sec = sector((0, 0), R_ANTEBRAZO + 5, R_ANTEBRAZO + 9, a0, barrido)
    sol = Plane.YZ * extrude(sec, L)
    pieza = sol
    pieza = pieza - Pos(L / 2, R_ANTEBRAZO + 2, 0) * Rot(90, 0, 0) * Cylinder(3.3, 30)
    return Pos(0, 0, Z_ANTEBRAZO) * pieza


def p15_almohadilla():
    L = S_CUNA[1] - S_CUNA[0]
    a0, barrido = CUNA_ANG
    pad = Plane.YZ * extrude(sector((0, 0), R_ANTEBRAZO, R_ANTEBRAZO + 5, a0, barrido), L)
    correa = Pos(10, 0, 0) * (Plane.YZ * extrude(sector((0, 0), R_ANTEBRAZO, R_ANTEBRAZO + 2, 30, 120), L - 20))
    hebilla = Pos(L / 2, (R_ANTEBRAZO + 3) * math.cos(math.radians(140)), (R_ANTEBRAZO + 3) * math.sin(math.radians(140))) * \
        Box(24, 6, 10)
    return Pos(0, 0, Z_ANTEBRAZO) * (pad + correa + hebilla)


S_ANILLA = 230.0               # el agujero de la anilla queda sobre el centro de gravedad (ver balance)


def p16_anilla():
    a = tubo(22, 38, D_TUBO)
    a = a + Pos(11, 0, 19) * Box(16, 10, 9, align=(Align.CENTER, Align.CENTER, Align.MIN))
    anillo = Pos(11, 0, 36) * Rot(90, 0, 0) * (Cylinder(11, 5) - Cylinder(7, 5))
    return a + anillo


ANILLA_AGUJERO = (11.0, 36.0)   # centro del agujero de la anilla (local: a lo largo del eje, hacia N_ARRIBA)
HOMBRO_SOBRE_CODO = 300.0       # brazo (húmero) aproximadamente vertical en la postura de corte
ANCHO_HOMBROS = 400.0


def hombro_izquierdo():
    """Hombro izquierdo del operario (mundo, mm): ahí pasa la correa, cruzada sobre el pecho como en la rozadora."""
    e = eje(S_CUNA[1] + 30)
    codo = [e[0] + Z_ANTEBRAZO * N_ARRIBA[0] + H_A_MUNDO[0], e[1] + H_A_MUNDO[1],
            e[2] + Z_ANTEBRAZO * N_ARRIBA[2] + H_A_MUNDO[2]]
    return (codo[0], codo[1] + ANCHO_HOMBROS, codo[2] + HOMBRO_SOBRE_CODO)


def anilla_mundo():
    e = eje(S_ANILLA + ANILLA_AGUJERO[0])
    z = ANILLA_AGUJERO[1]
    return (e[0] + z * N_ARRIBA[0] + H_A_MUNDO[0], e[1] + H_A_MUNDO[1], e[2] + z * N_ARRIBA[2] + H_A_MUNDO[2])


def direccion_correa():
    """Dirección unitaria de la correa (anilla -> hombro) en el sistema local del eje (x = U, y, z = N_ARRIBA)."""
    a, h = anilla_mundo(), hombro_izquierdo()
    d = [hh - aa for hh, aa in zip(h, a)]
    n = math.sqrt(sum(c * c for c in d))
    d = [c / n for c in d]
    # el eje local y es -Y del mundo (plano_eje: x = U, z = N_ARRIBA)
    return (d[0] * U[0] + d[2] * U[2], -d[1], d[0] * N_ARRIBA[0] + d[2] * N_ARRIBA[2])


LARGO_TRAMO_CORREA = 260.0      # tramo de correa dibujado (el resto sube al hombro)


def c08_correa():
    """Mosquetón enganchado en la anilla P16 y el arranque de la correa de hombro (sistema local de P16)."""
    dx, dy, dz = direccion_correa()
    n = math.hypot(dx, dz)
    a, c = dx / n, dz / n                          # el mosquetón gira sobre la anilla, en el plano local XZ
    hx, hz = ANILLA_AGUJERO
    centro = (hx + 29.0 * a, 0.0, hz + 29.0 * c)
    pl = Plane(origin=centro, x_dir=(a, 0, c), z_dir=(-c, 0, a))
    mosqueton = pl * extrude(SlotCenterToCenter(30, 25) - SlotCenterToCenter(30, 15), 2, both=True)
    arriba = (hx + 54.0 * a, 0.0, hz + 54.0 * c)
    zc = (-dz, 0.0, dx)
    nz = math.hypot(zc[0], zc[2])
    plc = Plane(origin=arriba, x_dir=(dx, dy, dz), z_dir=(zc[0] / nz, 0.0, zc[2] / nz))
    correa = plc * Box(LARGO_TRAMO_CORREA, 25, 2, align=(Align.MIN, Align.CENTER, Align.CENTER))
    return mosqueton + correa


# Pata de apoyo plegable (bípode): la tijera se queda parada sola sobre el patín y dos patas
S_PATA = 100.0                  # abrazadera sobre el tubo, justo detrás de la torre
PATA_BISAGRA = (12.0, 28.0, -8.0)   # bisagra de cada pata (local: a lo largo del eje, ±costado, hacia N_ARRIBA)
PATA_PIE_X = -470.0             # pies en el suelo, detrás del centro de gravedad (mundo)
PATA_ABERTURA = 200.0           # separación de cada pie respecto del eje de la herramienta (mundo, ±y)
PIE_D, PIE_H = 28.0, 6.0        # disco de tope (caucho) sobre la punta de anclaje
PUNTA_L, PUNTA_D = 25.0, 8.0    # punta de acero que se clava en la tierra
PATA_D = 12.0                   # tubo de aluminio Ø12 x 1


def _a_mundo_pata():
    return a_mundo() * Location(plano_eje(S_PATA))


def pata_bisagras_mundo():
    t = _a_mundo_pata()
    bx, by, bz = PATA_BISAGRA
    return [(t * Pos(bx, s * by, bz)).position for s in (1, -1)]


def pata_pies_mundo():
    y0 = Y_EJE + H_A_MUNDO[1]
    return [Vector(PATA_PIE_X, y0 + s * PATA_ABERTURA, PIE_H) for s in (-1, 1)]


def p19_pata(desplegada=True):
    """Bípode bajo el tubo. Plegado: las patas quedan a los costados del tubo, con las puntas delante del guardamonte.
    Desplegado: las puntas de acero se clavan en la tierra detrás del centro de gravedad y la tijera se queda
    parada sola, sin resbalar en la ladera."""
    T = _a_mundo_pata()
    abraz = tubo(24, 40, D_TUBO)
    bx, by, bz = PATA_BISAGRA
    for s in (1, -1):
        abraz = abraz + Pos(bx, s * (by - 2), bz) * Box(20, 14, 16)
    pieza = abraz
    u_mundo = Vector(*U)
    for h, f in zip(pata_bisagras_mundo(), pata_pies_mundo()):
        d = f - h
        largo = d.length
        d = d.normalized()
        pl = Plane(origin=h, z_dir=d)
        pata = pl * (Cylinder(PATA_D / 2, largo, align=(Align.CENTER, Align.CENTER, Align.MIN))
                     - Cylinder(PATA_D / 2 - 1, largo, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        pie = Pos(f.X, f.Y, 0) * Cylinder(PIE_D / 2, PIE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        pie = pie + Pos(f.X, f.Y, 0) * Cone(0.5, PUNTA_D / 2, PUNTA_L, align=(Align.CENTER, Align.CENTER, Align.MAX))
        pata_mundo = pata + pie
        if not desplegada:
            eje_giro = d.cross(u_mundo).normalized()
            ang = math.degrees(math.acos(max(-1.0, min(1.0, d.dot(u_mundo)))))
            pata_mundo = Pos(h) * Location((0, 0, 0), tuple(eje_giro), ang) * Pos(-h) * pata_mundo
        pieza = pieza + T.inverse() * pata_mundo
    return pieza


def largo_pata():
    h, f = pata_bisagras_mundo()[0], pata_pies_mundo()[0]
    return (f - h).length


def interior_motor():
    h = Pos(10, 0, 0) * tubo(80, 16, 0)
    t = Pos(28, 0, 0) * tubo(38, 30, 0)
    r = Pos(92, 0, 0) * tubo(45, 40, 0)
    m = Pos(137, 0, 0) * tubo(75, 48, 0)
    return m, r, h, t


def c05_bateria():
    b = Box(150, 55, 95, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return safe_fillet(b, b.edges(), 8)


# ---------------------------------------------------------------------------
# Lista de piezas
# ---------------------------------------------------------------------------
@dataclass
class Pieza:
    codigo: str
    nombre: str
    material: str
    cantidad: int
    geometria: object
    ubicacion: Location
    color: tuple
    grupo: str
    plano: bool = True
    explosion: tuple = (0, 0, 0)
    densidad: float = 7.85
    cascara: float = 0.0
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
UHMW = (0.92, 0.92, 0.88)
ESPUMA = (0.22, 0.24, 0.26)


def _ex(a, b=0.0):
    return tuple(a * u + b * n for u, n in zip(U, N_ARRIBA))


def construir(theta=0.0):
    ident = Location()
    phi = angulo_balancin(theta)
    q = Q_BALANCIN
    rot_bal = Location(q) * Location((0, 0, 0), (0, 1, 0), -phi) * Location((-q[0], -q[1], -q[2]))
    rot_cuch = Location((0, 0, 0), (0, 0, 1), theta)

    def en_eje(s):
        return Location(plano_eje(s))

    p = [
        Pieza("P01", "Contracuchilla-gancho", "Acero O1 (Böhler K460), SK5 o 65Mn templado 52-55 HRC, e = 8", 1, p01_gancho(), ident,
              ACERO_TEMPLADO, "Cabezal", explosion=(0, 0, -50)),
        Pieza("P02", "Cuchilla móvil", "Acero D2 (Böhler K110) o SK5 templado 56-58 HRC, e = 5", 1, p02_cuchilla(), rot_cuch,
              ACERO_FILO, "Cabezal", explosion=(0, 0, 60)),
        Pieza("P03", "Placa base", "Aluminio 7075-T6, e = 8, anodizado", 1, p03_placa_base(), ident,
              ALUMINIO_ANOD, "Cabezal", explosion=(-60, 0, -50), densidad=2.81),
        Pieza("P04", "Patín rasante", "UHMW-PE, e = 3", 1, p04_patin(), ident, UHMW, "Cabezal",
              explosion=(0, 0, -120), densidad=0.94),
        Pieza("P05", "Torre del cabezal", "Aluminio 6061-T6 mecanizado, anodizado", 1, p05_torre(), ident,
              ALUMINIO_ANOD, "Cabezal", explosion=(-40, 70, 70), densidad=2.70),
        Pieza("P06", "Palanca angular (balancín)", "Acero SAE 4140 bonificado (Böhler V320), e = 8", 1, p06_balancin(), rot_bal,
              ACERO_TEMPLADO, "Cabezal", explosion=(-40, 150, 70)),
        Pieza("P07", "Biela", "Acero SAE 1045, pletina 16 x 6", 1, p07_biela(), loc_biela(theta), ACERO_TEMPLADO,
              "Cabezal", explosion=(0, 40, 110)),
        Pieza("P08", "Tubo", "Tubo de carbono Ø30 x 2 (prototipo: aluminio 6061-T6)", 1, p08_tubo(),
              en_eje(S_TUBO[0]), CARBONO, "Brazo", explosion=_ex(110), densidad=1.55),
        Pieza("P09", "Varilla de tracción", "Tubo aluminio 7075-T6 Ø10 x 1,5", 1, p09_varilla(), loc_varilla(theta),
              ACERO_FILO, "Brazo", explosion=_ex(0, -120), densidad=2.81),
        Pieza("P10", "Carcasa de accionamiento", "PA6-GF30 (prototipo: impresión 3D PA-CF)", 1, p10_carcasa(),
              en_eje(S_CARCASA[0]), NARANJA, "Brazo", explosion=_ex(260), densidad=1.36, cascara=2.5),
        Pieza("P11", "Empuñadura ergonómica con guardamonte", "PA6-GF30 con sobremoldeo TPE", 1, p11_empunadura(),
              en_eje(S_EMP), NARANJA, "Brazo", explosion=_ex(260, -110), densidad=1.36, cascara=3.0),
        Pieza("P12", "Gatillo de cuatro dedos (tipo rozadora)", "PA6-GF30", 1, p12_gatillo(), en_eje(S_EMP), CAUCHO, "Brazo",
              explosion=_ex(260, -110), densidad=1.36),
        Pieza("P18", "Palanca de pulgar (opcional)", "PA6-GF30 con TPE", 1, p18_pulgar(), en_eje(S_EMP), CAUCHO,
              "Brazo", explosion=_ex(260, -110), densidad=1.36),
        Pieza("P13", "Brazo del apoyo de antebrazo", "Aluminio 5052-H32, chapa 6 mm plegada", 1, p13_brazo_apoyo(),
              en_eje(S_CARCASA[0]), ALUMINIO, "Apoyo de antebrazo", explosion=_ex(330, -60), densidad=2.70),
        Pieza("P14", "Cuna de antebrazo", "PA6-GF30 (o aluminio 5052 plegado)", 1, p14_cuna(), en_eje(S_CUNA[0]),
              NARANJA, "Apoyo de antebrazo", explosion=_ex(400, -120), densidad=1.36),
        Pieza("P15", "Almohadilla y correa", "EVA 5 mm + correa de velcro con hebilla de liberación", 1,
              p15_almohadilla(), en_eje(S_CUNA[0]), ESPUMA, "Apoyo de antebrazo", explosion=_ex(400, -40),
              densidad=0.15),
        Pieza("P17", "Punta envolvente con resorte", "Acero inoxidable 17-4PH o SAE 4140 pavonado, e = 6", 1,
              p17_dedo(False), ident, ACERO_FILO, "Cabezal", explosion=(30, 0, 90)),
        Pieza("P19", "Pata de apoyo plegable (bípode)", "Tubo aluminio 6061 Ø12 x 1, abrazadera PA6-GF30, tacos de caucho",
              1, p19_pata(False), en_eje(S_PATA), (0.30, 0.32, 0.36), "Brazo", explosion=_ex(60, -150), densidad=2.7),
        Pieza("P16", "Anilla para correa de hombro", "Abrazadera PA6 + anilla inoxidable", 1, p16_anilla(),
              en_eje(S_ANILLA), (0.80, 0.81, 0.83), "Brazo", explosion=_ex(110, 90), densidad=2.0),
    ]
    m, r, h, t = interior_motor()
    ex_mot = _ex(260, 110)
    p += [
        Pieza("C01", "Motor sin escobillas 300-400 W, 36 V", "Comercial", 1, m, en_eje(S_CARCASA[0]),
              (0.55, 0.55, 0.58), "Accionamiento", plano=False, explosion=ex_mot, densidad=2.6),
        Pieza("C02", "Reductor planetario 15:1", "Comercial", 1, r, en_eje(S_CARCASA[0]), (0.45, 0.46, 0.5),
              "Accionamiento", plano=False, explosion=ex_mot, densidad=4.5),
        Pieza("C03", "Husillo de bolas SFU1605", "Comercial", 1, h, en_eje(S_CARCASA[0]), ACERO_FILO,
              "Accionamiento", plano=False, explosion=ex_mot),
        Pieza("C04", "Tuerca del husillo + horquilla de tiro", "Comercial", 1, t, en_eje(S_CARCASA[0]),
              (0.35, 0.36, 0.4), "Accionamiento", plano=False, explosion=ex_mot, densidad=5.0),
        Pieza("C07", "Pasador Ø6 + separador + resorte de torsión de la punta", "Comercial", 1, c07_pasador_resorte(),
              ident, (0.6, 0.6, 0.62), "Cabezal", plano=False, explosion=(30, 0, 140)),
        Pieza("C06", "Perno pivote con hombro Ø12, rosca M10 + arandelas Belleville", "Comercial (ISO 7379 / DIN 2093)", 1, c06_perno(),
              ident, (0.6, 0.6, 0.62), "Cabezal", plano=False, explosion=(0, 0, 150)),
        Pieza("C08", "Correa de hombro de rozadora con mosquetón", "Comercial (arnés simple de desbrozadora)", 1,
              c08_correa(), en_eje(S_ANILLA), (0.16, 0.20, 0.26), "Brazo", plano=False, explosion=_ex(110, 150),
              densidad=0.9),
    ]
    return p


def bateria():
    return Pieza("C05", "Batería Li-ion 36 V 2,5-4 Ah al cinturón + cable espiral", "Comercial", 1, c05_bateria(),
                 Location(), (0.12, 0.12, 0.13), "Accionamiento", plano=False, densidad=1.9)


def a_mundo():
    return Location(H_A_MUNDO)


def correa_fin_mundo():
    """Extremo del tramo de correa dibujado en C08 (mundo, mm); desde ahí el visor la sigue hasta el hombro."""
    dx, dy, dz = direccion_correa()
    n = math.hypot(dx, dz)
    hx, hz = ANILLA_AGUJERO
    p = (hx + 54.0 * dx / n + LARGO_TRAMO_CORREA * dx, LARGO_TRAMO_CORREA * dy, hz + 54.0 * dz / n + LARGO_TRAMO_CORREA * dz)
    v = (a_mundo() * Location(plano_eje(S_ANILLA))) * Pos(*p)
    t = v.position
    return [t.X, t.Y, t.Z]


def antebrazo_mundo():
    """Puntos de referencia del brazo del operario (mundo, mm) para el visor."""
    def local(s, z):
        e = eje(s)
        return [e[0] + z * N_ARRIBA[0] + H_A_MUNDO[0], e[1] + H_A_MUNDO[1], e[2] + z * N_ARRIBA[2] + H_A_MUNDO[2]]
    return {
        "muneca": local(S_EMP + 45, Z_ANTEBRAZO + 5),
        "codo": local(S_CUNA[1] + 30, Z_ANTEBRAZO),
        "mano": local(S_EMP, -85),
        "hombro": list(hombro_izquierdo()),
        "anilla": list(anilla_mundo()),
        "correa_fin": correa_fin_mundo(),
        "radio": R_ANTEBRAZO,
    }
