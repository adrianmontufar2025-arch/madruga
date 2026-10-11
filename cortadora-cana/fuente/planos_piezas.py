"""Definición de cada plano (vistas, cotas, notas, tabla de agujeros) y generación de todos los DXF."""
from __future__ import annotations

import math
import os
import sys

from build123d import Pos, Rot

sys.path.insert(0, os.path.dirname(__file__))
import modelo as MD  # noqa: E402
from planos import Cota, Plano, generar  # noqa: E402

PIEZAS = {p.codigo: p for p in MD.construir(0.0)}
C = MD.C_GARGANTA


def masa(cod):
    return PIEZAS[cod].masa()


def bb(f):
    return f.bounding_box()


def L(v, a, b, dist=12, ang=0, txt="<>"):
    return Cota("lin", v, a, b, dist=dist, angulo=ang, texto=txt)


def D(v, c, r, ang=45, txt="<>"):
    return Cota("dia", v, c, r=r, angulo=ang, texto=txt)


def R(v, c, r, ang=45, txt="<>"):
    return Cota("rad", v, c, r=r, angulo=ang, texto=txt)


def N(v, p, dx, dy, txt):
    return Cota("nota", v, p, (dx, dy), texto=txt)


def num(x):
    return f"{x:.1f}".replace(".", ",").replace(",0", "")


# ---------------------------------------------------------------------------
def p01():
    f = MD.p01_gancho()
    b = bb(f)
    ag = [("A", 0, 0, 12.5, "pivote, pasante")]
    for i, (x, y) in enumerate(MD.AGUJEROS_GANCHO):
        ag.append(("BCD"[i], x, y, 8.5, "avellanado 90° M8"))
    for i, (x, y) in enumerate(MD.AGUJEROS_UNA):
        ag.append(("EF"[i], round(x, 1), round(y, 1), 5, "roscar M6 (uña)"))
    cot = [
        L("planta", (b.min.X, b.min.Y, 0), (b.max.X, b.min.Y, 0), -16),
        L("planta", (b.max.X, b.min.Y, 0), (b.max.X, b.max.Y, 0), 14, 90),
        L("planta", (0, 0, 0), (C[0], 0, 0), 46, 0),
        L("planta", (C[0], 0, 0), (C[0], C[1], 0), -54, 90),
        R("planta", (C[0], C[1], 0), MD.R_GANCHO_INT, 335, "R30 filo"),
        R("planta", (C[0], C[1], 0), MD.R_GANCHO_EXT, 268),
        N("planta", (C[0] + 30 * math.cos(math.radians(300)), C[1] + 30 * math.sin(math.radians(300)), 0), 20, -24,
          "filo de la garganta"),
    ]
    return Plano("P01", "Contracuchilla-gancho", "Acero SK5 o 65Mn, chapa e = 8 mm", 1, masa("P01"), f, ["planta"],
                 cot, [
                     "Cortar por láser o chorro de agua desde este DXF (geometría a escala real 1:1). Espesor 8 mm.",
                     "Templar y revenir a 52-55 HRC después de mecanizar los agujeros.",
                     "Filo: borde interior R30 de la garganta, bisel simple de 25° por la cara INFERIOR.",
                     "La cara superior queda plana y rectificada: es la cara de contacto con la cuchilla.",
                     "Avellanar B, C y D a 90° hasta Ø16 por la cara superior. Roscar E y F M6 para la uña P03.",
                     "Romper aristas 0,5 mm excepto el filo. Punta del pico redondeada R11 (no afilar).",
                 ], ag, tratamiento="Temple 52-55 HRC; pavonado")


def p02():
    f = Pos(0, 0, -MD.Z_CORTE) * MD.p02_cuchilla()
    b = bb(f)
    tx, ty = MD.punta_cola(0)
    ag = [("A", 0, 0, 12.5, "pivote, pasante"), ("B", round(tx, 1), round(ty, 1), 8, "pasador biela")]
    cot = [
        L("planta", (b.min.X, b.min.Y, 0), (b.max.X, b.min.Y, 0), -16),
        L("planta", (b.max.X, b.min.Y, 0), (b.max.X, b.max.Y, 0), 14, 90),
        R("planta", (C[0], C[1], 0), MD.R_GANCHO_INT + 4, 290, "R34 filo"),
        Cota("lin", "planta", (0, 0, 0), (tx, ty, 0), dist=-18, angulo=90),
        Cota("lin", "planta", (tx, ty, 0), (0, 0, 0), dist=24, angulo=0),
    ]
    return Plano("P02", "Cuchilla móvil", "Acero D2 (o SK5), chapa e = 5 mm", 1, masa("P02"), f, ["planta"], cot, [
        "Cortar por láser o hilo desde este DXF (1:1). Espesor 5 mm. Se muestra en posición CERRADA.",
        "Temple y revenido a 56-58 HRC. Rectificar plana la cara inferior (contacto con el gancho P01).",
        "Filo: borde convexo R34, bisel simple de 22° por la cara SUPERIOR; asentar con piedra fina.",
        "Agujero A con buje de bronce o perno con hombro ISO 7379 Ø12 + arandela Belleville.",
        "Apertura de trabajo: 62° alrededor de A (cuchilla abierta hacia la cola).",
    ], ag, tratamiento="Temple 56-58 HRC; filo asentado")


def p03():
    f = Pos(-C[0], -C[1], -MD.Z_CORTE) * MD.p03_una()
    b = bb(f)
    a0, a1 = MD.UNA_ANG
    barrido = (a1 - a0) % 360
    desarrollo = MD.R_UNA * math.radians(barrido)
    cot = [
        R("planta", (0, 0, 0), MD.R_UNA + 1.5, (a0 + 12) % 360, "R48,5 ext."),
        L("alzado", (b.max.X, 0, 0), (b.max.X, 0, 40), 12, 90),
        Cota("ang", "planta", (0, 0, 0), (a0, a1), dist=0, r=MD.R_UNA + 26, texto="<>"),
    ]
    return Plano("P03", "Uña de retención", "Pletina inoxidable AISI 304, 40 x 3 mm", 1, masa("P03"), f,
                 ["alzado", "planta"], cot, [
                     f"Pletina 40 x 3, longitud desarrollada {num(desarrollo)} mm, rolada a radio medio R47.",
                     "Soldar (TIG) dos pestañas 14 x 14 x 3 con agujero Ø6,5 en los extremos, a 90° de la pared.",
                     "Se fija sobre la mandíbula del gancho P01 con 2 tornillos M6 en E y F.",
                     "Retiene la base del tallo cortado para arrastrarlo hacia la calle sin que se escape.",
                     "Centro del arco = centro de la garganta (62; 12 desde el pivote de P01).",
                 ], [], origen="centro de la garganta")


def p04():
    x0, y0 = MD.TORRE_X[0], MD.TORRE_Y[0]
    f = Pos(-x0, -y0, 0) * MD.p04_torre()
    b = bb(f)
    q = MD.Q_BALANCIN
    qx, qy, qz = q[0] - x0, q[1] - y0, q[2]
    cot = [
        L("alzado", (0, 0, 0), (MD.TORRE_X[1] - x0, 0, 0), -14),
        L("alzado", (0, 0, 0), (0, 0, MD.TORRE_Z[1]), -14, 90),
        L("alzado", (0, 0, 0), (qx, 0, 0), 30 + MD.TORRE_Z[1] - qz, 0),
        L("alzado", (0, 0, 0), (0, 0, qz), -30, 90),
        D("alzado", (qx, 0, qz), 5, 45, "Ø10 H7 eje balancín"),
        L("planta", (0, 0, 0), (0, MD.TORRE_Y[1] - y0, 0), -14, 90),
        L("perfil", (0, MD.TORRE_Y[1] - y0, 0), (0, 0, 0), -14, 0),
        N("alzado", (b.max.X - 25, 0, b.max.Z - 18), -30, 26, "alojamiento %%c32,2 H8 a 40°, prof. 50"),
    ]
    ag = []
    for i, (x, y) in enumerate(MD.AGUJEROS_TORRE):
        ag.append(("ABCD"[i], x - x0, y - y0, 5, "roscar M6 x 15 (base)"))
    return Plano("P04", "Torre del cabezal", "Aluminio 6061-T6, bloque mecanizado", 1, masa("P04"), f,
                 ["alzado", "planta", "perfil"], cot, [
                     "Mecanizar en CNC desde bloque. Anodizado duro, color azul.",
                     "Cavidad interior de 27 mm de ancho para el balancín P15 y la biela P09 (abierta al frente).",
                     "El eje del alojamiento del codo P08 coincide con el eje de la pértiga: 40° sobre la base.",
                     "Agujeros de la base (A-D, tabla) desde abajo; 2 roscas M6 laterales (cara izq.) para el gancho P10.",
                     "Ver el modelo STEP P04 para la geometría completa de la cavidad.",
                 ], ag, origen="esquina trasera-derecha-inferior", tratamiento="Anodizado duro 25 µm")


def p05():
    f = Pos(0, 0, MD.ESP_CHASIS) * MD.p05_chasis()
    b = bb(f)
    ag = [("A", 0, 0, 12.5, "pivote, pasante")]
    for i, (x, y) in enumerate(MD.AGUJEROS_GANCHO):
        ag.append(("BCD"[i], x, y, 6.8, "roscar M8 (gancho P01)"))
    for i, (x, y) in enumerate(MD.AGUJEROS_TORRE):
        ag.append(("EFGH"[i], x, y, 6.8, "pasante M6 avellanado"))
    cot = [
        L("planta", (b.min.X, b.min.Y, 0), (b.max.X, b.min.Y, 0), -16),
        L("planta", (b.min.X, b.min.Y, 0), (b.min.X, b.max.Y, 0), -14, 90),
        R("planta", (0, 0, 0), 24, 30),
    ]
    return Plano("P05", "Placa base (chasis)", "Aluminio 7075-T6, chapa e = 8 mm", 1, masa("P05"), f, ["planta"], cot, [
        "Cortar por chorro de agua o fresar desde este DXF (1:1). Espesor 8 mm.",
        "Aligeramientos pasantes con radio interior mínimo R6.",
        "Roscas laterales M5 x 10: cara derecha (y = -37) en x = -18 y x = 8 para la bisagra P12;",
        "   ambas caras (y = -37 y y = 74) en x = -150 y x = -50 para las alas del patín P07 (z = mitad del espesor).",
        "Anodizado duro negro o azul. El pivote A recibe el perno M12 por debajo (cabeza baja).",
    ], ag, tratamiento="Anodizado duro 25 µm")


def tubo_plano(cod, titulo, material, forma, d_ext, d_int, largo, notas, extra_cotas=()):
    b = bb(forma)
    cot = [L("alzado", (0, 0, -d_ext / 2), (largo, 0, -d_ext / 2), -14),
           Cota("lin", "perfil", (0, d_ext / 2, 0), (0, -d_ext / 2, 0), dist=d_ext / 2 + 10, angulo=0,
                texto=f"%%c{num(d_ext)}")]
    if d_int:
        cot.append(D("perfil", (0, 0, 0), d_int / 2, 45, f"%%c{num(d_int)}"))
    cot += list(extra_cotas)
    return Plano(cod, titulo, material, 1, masa(cod), forma, ["alzado", "perfil"], cot, notas, [])


def p06():
    f = MD.p06_collar()
    Lc = MD.S_COLLAR[1] - MD.S_COLLAR[0]
    return tubo_plano("P06", "Collar giratorio indexado", "Aluminio 6061-T6, barra Ø50", f, 46, 32.2, Lc, [
        "Tornear desde barra. Interior Ø32,2 H8 en toda la longitud.",
        "8 muescas de indexado 8 x 6 x 6 cada 45°, a mitad de la longitud, para el pasador con resorte.",
        "El pasador (Ø8, comercial con pomo) se aloja en el saliente superior. Anodizar.",
        "Lado cabezal: pegar y pasar pasador Ø4 al codo P08. Lado pértiga: gira sobre el tubo P16.",
    ])


def p07():
    f = Pos(180, -(MD.CHASIS_Y[0] - 3), MD.ALTURA_CORTE - MD.Z_CORTE) * MD.p07_patin()
    b = bb(f)
    cot = [
        L("alzado", (b.min.X, 0, 0), (b.max.X, 0, 0), -14),
        L("alzado", (b.max.X, 0, 0), (b.max.X, 0, b.max.Z), 14, 90),
        L("planta", (b.min.X, b.min.Y, 0), (b.min.X, b.max.Y, 0), -14, 90),
        L("alzado", (30, 0, 0), (130, 0, 0), 40),
    ]
    return Plano("P07", "Patín de altura", "Suela UHMW-PE 6 mm + alas aluminio 5052 3 mm", 1, masa("P07"), f,
                 ["alzado", "planta", "perfil"], cot, [
                     "Suela de polietileno UHMW de 6 mm con puntas curvadas R20 (termoformar a 130 °C o mecanizar).",
                     "Alas laterales de aluminio 5052 de 3 mm, plegadas y atornilladas a la suela (4 x M5 avellanado).",
                     "Colisos verticales 6,5 x 24,5 para regular la altura de corte entre 15 y 45 mm.",
                     "El patín apoya el cabezal en el suelo: el peso de la caña y del cabezal se va a la tierra.",
                 ], [], origen="punta trasera")


def p08():
    f = MD.p08_codo()
    Lc = MD.S_CODO[1] - MD.S_CODO[0]
    return tubo_plano("P08", "Codo del cabezal", "Tubo aluminio 6061-T6 Ø32 x 3", f, 32, 26, Lc, [
        "Cortar a escuadra y desbarbar. Pegar con epoxi estructural en la torre P04 y pasar pasador Ø4.",
        "Por dentro pasa la varilla de tracción P22 (Ø10).",
    ])


def p09():
    f = MD.p09_biela()
    cot = [L("alzado", (0, 0, 0), (MD.L_BIELA, 0, 0), 16), D("alzado", (0, 0, 0), 4, 135, "2x %%c8 H7"),
           L("alzado", (MD.L_BIELA, 0, -8), (MD.L_BIELA, 0, 8), 14, 90), L("planta", (0, -3, 0), (0, 3, 0), -14, 90)]
    return Plano("P09", "Biela", "Acero SAE 1045, pletina 16 x 6", 1, masa("P09"), f, ["alzado", "planta"], cot, [
        "Distancia entre centros 90 mm ±0,05. Agujeros Ø8 H7 para pasadores o rótulas.",
        "Trabaja a compresión: empuja la cola de la cuchilla P02 para cerrarla.",
        "Zincado o pavonado.",
    ], [])


def p10():
    x1 = MD.AGUJEROS_GANCHO_TRAS[0]
    f = Pos(-x1[0], -MD.TORRE_Y[1], -x1[1]) * MD.p10_gancho_trasero()
    b = bb(f)
    c = (-218 - x1[0], 0, 52 - x1[1])
    ag = [("A", 0, 0, 6.5, "pasante M6"), ("B", MD.AGUJEROS_GANCHO_TRAS[1][0] - x1[0], 0, 6.5, "pasante M6")]
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -14),
           L("alzado", (b.max.X, 0, b.min.Z), (b.max.X, 0, b.max.Z), 14, 90),
           R("alzado", c, 26, 0, "R26 int."), R("alzado", c, 36, 225, "R36"),
           L("alzado", c, (0, 0, 0), 30, 0)]
    pl = Plano("P10", "Gancho trasero de arrastre", "Acero SAE 1045, chapa e = 5 mm", 1, masa("P10"), f,
               ["alzado", "planta"], cot, [
                   "Cortar por láser o plasma desde este DXF (1:1). Espesor 5 mm.",
                   "Se atornilla a la cara izquierda de la torre P04 con 2 tornillos M6.",
                   "Boca de la C hacia el operario: engancha cañas tendidas para jalarlas a la calle.",
                   "Romper aristas, pintura epoxi negra.",
               ], ag, vista_agujeros="alzado", origen="agujero A")
    return pl


def p11():
    x, y = MD.MASTIL_BASE
    f = Rot(0, 90, 0) * Pos(-x, -y, -(MD.Z_BISAGRA + 16)) * MD.p11_mastil()
    Lc = (MD.Z_HORQUILLA - 20) - (MD.Z_BISAGRA + 16)
    return tubo_plano("P11", "Mástil de la guía", "Tubo de carbono Ø16 x 1,5 (enrollado)", f, 16, 13, Lc, [
        "Tubo comercial de fibra de carbono. Cortar con disco diamantado, sellar el corte con epoxi.",
        "Se pega en los terminales P11B (epoxi estructural, 25 mm de inserción en cada extremo).",
    ])


def p11b():
    x, y = MD.MASTIL_BASE
    f = Rot(0, 90, 0) * Pos(-x, -y, -MD.Z_BISAGRA) * MD.p11b_terminales()
    b = bb(f)
    cot = [L("alzado", (0, 0, 0), (45, 0, 0), -18), D("alzado", (0, 0, 0), 3.1, 45, "%%c6,2 pasador"),
           L("alzado", (b.max.X - 40, 0, 0), (b.max.X, 0, 0), -18)]
    return Plano("P11B", "Terminales del mástil", "Aluminio 6061-T6, barra Ø20", 2, masa("P11B"), f,
                 ["alzado", "planta"], cot, [
                     "Terminal inferior: ojo de bisagra 18 mm de ancho con agujero Ø6,2 + casquillo Ø18 x 45.",
                     "Terminal superior: casquillo Ø18 x 40 con espiga roscada M8 para la horquilla P13.",
                     "Alojamiento interior Ø16,1 x 25 para el tubo P11. Anodizar.",
                     "El dibujo muestra ambos terminales a su distancia real de montaje (sin el tubo).",
                 ], [], escala=None)


def p12():
    x, y = MD.MASTIL_BASE
    f = Pos(-x, -MD.CHASIS_Y[0], MD.ESP_CHASIS) * MD.p12_bisagra()
    b = bb(f)
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -14),
           L("perfil", (0, b.min.Y, 0), (0, b.max.Y, 0), -14, 0),
           L("alzado", (b.max.X, 0, b.min.Z), (b.max.X, 0, b.max.Z), 14, 90)]
    return Plano("P12", "Bisagra del mástil", "Aluminio 6061-T6", 1, masa("P12"), f, ["alzado", "planta", "perfil"],
                 cot, [
                     "Mecanizar o soldar (TIG) desde placa de 6 mm. Anodizar.",
                     "Pasador Ø6 de acero inoxidable con retén. Bola-resorte para fijar dos posiciones:",
                     "   vertical (trabajo) y abatida 50° hacia atrás, paralela a la pértiga (transporte).",
                     "Se fija al costado derecho de la placa base P05 con 2 tornillos M5.",
                 ], [], origen="cara de apoyo")


def p13():
    f = Pos(-C[0], -C[1], -MD.Z_HORQUILLA) * MD.p13_horquilla()
    b = bb(f)
    mx, my = MD.MASTIL_BASE[0] - C[0], MD.MASTIL_BASE[1] - C[1]
    a_fin, a_ini = MD.HORQ_BOCA
    gx = (MD.HORQ_RI + MD.HORQ_RO) / 2 * math.cos(math.radians(a_ini))
    gy = (MD.HORQ_RI + MD.HORQ_RO) / 2 * math.sin(math.radians(a_ini))
    ag = [("A", round(mx, 1), round(my, 1), 16.2, "espiga del mástil"), ("B", round(gx, 1), round(gy, 1), 5.2, "eje compuerta")]
    cot = [R("planta", (0, 0, 0), MD.HORQ_RI, 200, "R34"), R("planta", (0, 0, 0), MD.HORQ_RO, 250, "R46"),
           Cota("ang", "planta", (0, 0, 0), (a_fin, a_ini), dist=0, r=MD.HORQ_RO + 12, texto="boca <>"),
           L("planta", (mx, my, 0), (0, 0, 0), -20, 0), L("planta", (mx, my, 0), (0, 0, 0), 20, 90)]
    return Plano("P13", "Horquilla guía", "Aluminio 6061-T6, chapa e = 6 mm", 1, masa("P13"), f, ["planta"], cot, [
        "Cortar por chorro de agua o láser desde este DXF (1:1). Espesor 6 mm.",
        "Forrar el interior R34 con cinta de UHMW de 1 mm para no lastimar la caña.",
        "La compuerta P14 cierra la boca con un resorte de torsión (comercial, 0,8 N·m).",
        "Centro del aro = eje del tallo (sobre el centro de la garganta del gancho).",
    ], ag, origen="centro del aro")


def p14():
    f = Pos(-C[0], -C[1], -(MD.Z_HORQUILLA + 6)) * MD.p14_compuerta()
    a_fin, a_ini = MD.HORQ_BOCA
    cot = [R("planta", (0, 0, 0), MD.HORQ_RI + 1, 60, "R35"), R("planta", (0, 0, 0), MD.HORQ_RI + 9, 20, "R43")]
    return Plano("P14", "Compuerta de resorte", "Acero inoxidable AISI 301 templado, e = 3 mm", 1, masa("P14"), f,
                 ["planta"], cot, [
                     "Cortar por láser desde este DXF. Espesor 3 mm.",
                     "Gira sobre el eje B de la horquilla P13; se abre hacia adentro al entrar la caña y se cierra sola.",
                     "Se libera con el cable de la palanca de la empuñadura delantera P20.",
                 ], [], origen="centro del aro")


def p15():
    q = MD.Q_BALANCIN
    f = Pos(-q[0], -q[1], -q[2]) * MD.p15_balancin()
    bx, _, bz = MD.punto_b(0)
    ax, _, az = MD.punto_a(0)
    cot = [L("alzado", (0, 0, 0), (0, 0, bz - q[2]), -16, 90),
           L("alzado", (0, 0, 0), (ax - q[0], 0, 0), 16 + (az - q[2]), 0),
           L("alzado", (0, 0, 0), (0, 0, az - q[2]), 26, 90),
           D("alzado", (0, 0, 0), 5, 135, "%%c10 H7"),
           L("planta", (0, -4, 0), (0, 4, 0), -16, 90)]
    return Plano("P15", "Palanca angular (balancín)", "Acero SAE 4140 bonificado, e = 8 mm", 1, masa("P15"), f,
                 ["alzado", "planta"], cot, [
                     "Cortar por láser o hilo desde este DXF (1:1). Espesor 8 mm.",
                     "Brazo B (45 mm) a la biela P09; brazo A (35 mm) a la varilla P22, a 90° del eje de la pértiga.",
                     "Agujeros de brazo Ø8 H7; eje central Ø10 H7 con buje de bronce.",
                     "Giro de trabajo: de -13° (abierta) a +40° (cerrada) respecto a la vertical.",
                 ], [], origen="eje del balancín")


def p16():
    f = MD.p16_tubo_inf()
    Lc = MD.S_TUBO_INF[1] - MD.S_TUBO_INF[0]
    return tubo_plano("P16", "Tramo inferior de pértiga", "Tubo de carbono Ø32 x 2 enrollado (≥ 60 % fibras a 0°)", f,
                      32, 28, Lc, [
                          "Tubo comercial de fibra de carbono. Cortar con disco diamantado y sellar el corte.",
                          "Extremos con casquillos de aluminio anodizado pegados con epoxi estructural y una capa",
                          "   de fibra de vidrio en la interfaz (evita la corrosión galvánica carbono-aluminio).",
                          "Funda protectora P17 en el tercio inferior. No apretar el carbono con abrazaderas.",
                      ])


def p17():
    f = MD.p17_funda()
    Lc = MD.S_FUNDA[1] - MD.S_FUNDA[0]
    return tubo_plano("P17", "Funda protectora", "Tubo de poliuretano 85A, Ø37 x 2,5", f, 37, 32, Lc, [
        "Protege el carbono de golpes contra piedras. Colocar con aire comprimido o termocontraíble.",
    ])


def p18():
    f = MD.p18_acople()
    Lc = MD.S_ACOPLE[1] - MD.S_ACOPLE[0]
    return tubo_plano("P18", "Acople rápido con seguro", "Aluminio 6061-T6 + leva de acero inoxidable", f, 42, 32.2,
                      Lc, [
                          "Acople macho-hembra con leva de cierre y pasador de seguridad (2 tramos de pértiga).",
                          "La varilla P22 se une dentro con un acople roscado M6 al armar la herramienta.",
                          "Conector eléctrico de 2 polos en el acople si la electrónica va en el cabezal (opcional).",
                      ])


def p19():
    f = MD.p19_tubo_sup()
    Lc = MD.S_TUBO_SUP[1] - MD.S_TUBO_SUP[0]
    return tubo_plano("P19", "Tramo superior de pértiga", "Tubo de carbono Ø32 x 2 enrollado", f, 32, 28, Lc, [
        "Igual que P16. Lleva la empuñadura delantera P20 y entra 10 mm en la carcasa P23.",
    ])


def p20():
    f = MD.p20_empunadura_del()
    Lc = MD.S_EMP_DEL[1] - MD.S_EMP_DEL[0]
    return tubo_plano("P20", "Empuñadura delantera con mandos", "Manguito EPDM 60 Shore A + caja PA6-GF30", f, 40, 32,
                      Lc, [
                          "Caja superior con dos mandos: pulsador de presencia (la herramienta solo corta si está",
                          "   apretado, junto con el gatillo trasero) y palanca de liberación de la guía (cable Ø1,5).",
                          "Prototipo: caja impresa en PA-CF o PETG; manguito de espuma EVA de pértiga comercial.",
                      ])


def p21():
    f = MD.p21_anilla()
    return tubo_plano("P21", "Anilla para arnés", "Abrazadera PA6 + anilla inoxidable Ø24", f, 42, 32, 24, [
        f"Se ubica en el centro de gravedad de la herramienta (a {int(MD.S_ANILLA)} mm del brazo A, sobre P16).",
        "Engancha al mosquetón del arnés de hombro tipo desbrozadora.",
    ])


def p22():
    f = MD.p22_varilla()
    Lc = MD.S_VARILLA[1] - MD.S_VARILLA[0]
    return tubo_plano("P22", "Varilla de tracción", "Tubo aluminio 7075-T6 Ø10 x 1,5", f, 10, 7, Lc, [
        "En dos tramos unidos por un acople roscado M6 a la altura del acople rápido P18.",
        "Extremo del cabezal: horquilla con pasador Ø8 al brazo A del balancín P15.",
        "Extremo del motor: unida a la tuerca del husillo SFU1605. Carrera útil 31 mm.",
        "Trabaja a tracción (carga máx. estimada 4 kN): verificar con el ensayo de fuerza de corte.",
    ])


def p23():
    f = MD.p23_carcasa()
    Lc = MD.S_CARCASA[1] - MD.S_CARCASA[0]
    pl = tubo_plano("P23", "Carcasa de accionamiento", "PA6-GF30 inyectado (prototipo: impresión 3D PA-CF)", f, 64, 0,
                    Lc, [
                        "Dos medias carcasas atornilladas (plano de partición vertical). Pared 2,5 mm con nervios.",
                        "Aloja: motor sin escobillas 400-500 W, reductor 15:1, husillo SFU1605, controlador y fin de carrera.",
                        "Ranuras de ventilación con laberinto contra lluvia; electrónica IP65.",
                        "Interruptor de bloqueo en la parte superior; conector de batería en la tapa trasera.",
                    ])
    pl.vistas = ["alzado", "planta", "perfil"]
    return pl


def p24():
    f = MD.p24_empunadura_tras()
    b = bb(f)
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -14),
           L("alzado", (b.max.X, 0, b.min.Z), (b.max.X, 0, b.max.Z), 14, 90)]
    return Plano("P24", "Empuñadura trasera tipo pistola", "PA6-GF30 con sobremoldeo TPE", 1, masa("P24"), f,
                 ["alzado", "perfil"], cot, [
                     "Inclinación hacia atrás de ~15° para muñeca neutra con la pértiga a 40°.",
                     "Hueca, pared 3 mm; parte de la media carcasa P23 o pieza atornillada.",
                     "Alojamiento del gatillo proporcional P25 (sensor Hall) en la cara delantera.",
                 ], [], origen="eje de la pértiga")


def p25():
    f = MD.p25_gatillo()
    b = bb(f)
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -14),
           L("alzado", (b.max.X, 0, b.min.Z), (b.max.X, 0, b.max.Z), 14, 90)]
    return Plano("P25", "Gatillo proporcional", "PA6-GF30", 1, masa("P25"), f, ["alzado", "planta"], cot, [
        "Gatillo con imán para sensor Hall: la cuchilla sigue la posición del gatillo (corte proporcional).",
        "Resorte de retorno; al soltarlo la cuchilla se detiene y vuelve a abrir.",
    ], [], escala=0.5, origen="eje de la pértiga")


TODOS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p11b, p12, p13, p14, p15, p16, p17, p18, p19, p20,
         p21, p22, p23, p24, p25]


def main(solo=None):
    rutas = []
    for fn in TODOS:
        pl = fn()
        if solo and pl.codigo not in solo:
            continue
        ruta, k = generar(pl)
        print(f"{pl.codigo:5s} escala {k:>4}  {os.path.basename(ruta)}")
        rutas.append(ruta)
    return rutas


if __name__ == "__main__":
    main(sys.argv[1:] or None)
