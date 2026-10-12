"""Planos DXF pieza por pieza de la tijera de antebrazo."""
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


def p01():
    f = MD.p01_gancho()
    b = bb(f)
    ag = [("A", 0, 0, 12.5, "pivote, avellanado abajo")]
    for i, (x, y) in enumerate(MD.AGUJEROS_LAP):
        ag.append(("BCD"[i], x, y, 6.6, "M6 avellanado abajo"))
    ag.append(("E", round(MD.BISAGRA_DEDO[0], 1), round(MD.BISAGRA_DEDO[1], 1), 6, "pasador punta P17 (H7)"))
    cot = [
        L("planta", (b.min.X, b.min.Y, 0), (b.max.X, b.min.Y, 0), -16),
        L("planta", (b.max.X, b.min.Y, 0), (b.max.X, b.max.Y, 0), 14, 90),
        L("planta", (0, 0, 0), (C[0], 0, 0), 52, 0),
        L("planta", (C[0], 0, 0), (C[0], C[1], 0), -62, 90),
        R("planta", (C[0], C[1], 0), MD.R_GANCHO_INT, 285, "R35 filo"),
        N("planta", (C[0] + 35.6 * math.cos(math.radians(322)), C[1] + 35.6 * math.sin(math.radians(322)), 0), 24, -30,
          "dientes de agarre: paso 3, alto 1,2"),
        R("planta", (C[0], C[1], 0), MD.R_GANCHO_EXT, 268),
        L("alzado", (MD.LAP_X[0], 0, 0), (MD.LAP_X[1], 0, 0), 16),
        L("alzado", (b.min.X, 0, 0), (b.min.X, 0, 4), -10, 90),
        L("alzado", (b.max.X, 0, 0), (b.max.X, 0, 8), 10, 90),
    ]
    return Plano("P01", "Contracuchilla-gancho", "Acero SK5 o 65Mn, chapa e = 8 mm", 1, masa("P01"), f,
                 ["alzado", "planta"], cot, [
                     "Cortar por láser o chorro de agua desde este DXF (1:1). Espesor 8 mm.",
                     "Media madera: fresar 4 mm de la cara superior entre x = -52 y x = -32 (empalme con P03).",
                     "Templar y revenir a 52-55 HRC después de mecanizar.",
                     "Filo: borde interior R35 de la garganta, bisel simple de 25° por la cara INFERIOR.",
                     "Cara superior plana y rectificada (contacto con la cuchilla P02).",
                     "Avellanar A (perno pivote) y B, C, D por la cara inferior: el fondo de la herramienta queda plano.",
                     "Mandíbula corta (termina a 345°) con punta roma R11: entra entre cañas y retoños.",
                     "Dientes de agarre en el tramo delantero (300° a 343°), inclinados hacia el fondo de la garganta:",
                     "   sujetan la caña en el corte parcial, cuando no entra completa.",
                     "Agujero E: pasador Ø6 de la punta envolvente P17 (ajuste a presión por abajo)",
                 ], ag, tratamiento="Temple 52-55 HRC; pavonado")


def p02():
    f = Pos(0, 0, -MD.Z_CORTE) * MD.p02_cuchilla()
    b = bb(f)
    tx, ty = MD.punta_cola(0)
    ag = [("A", 0, 0, 12.5, "pivote"), ("B", round(tx, 1), round(ty, 1), 8, "pasador biela")]
    cot = [
        L("planta", (b.min.X, b.min.Y, 0), (b.max.X, b.min.Y, 0), -16),
        L("planta", (b.max.X, b.min.Y, 0), (b.max.X, b.max.Y, 0), 14, 90),
        R("planta", (C[0], C[1], 0), MD.R_GANCHO_INT + 4, 290, "R39 filo"),
        Cota("lin", "planta", (0, 0, 0), (tx, ty, 0), dist=-18, angulo=90),
        Cota("lin", "planta", (tx, ty, 0), (0, 0, 0), dist=26, angulo=0),
    ]
    return Plano("P02", "Cuchilla móvil", "Acero D2 (o SK5), chapa e = 5 mm", 1, masa("P02"), f, ["planta"], cot, [
        "Cortar por láser o hilo desde este DXF (1:1). Espesor 5 mm. Se muestra en posición CERRADA.",
        "Temple y revenido a 56-58 HRC. Rectificar plana la cara inferior (contacto con el gancho P01).",
        "Filo: borde convexo R39, bisel simple de 22° por la cara SUPERIOR; asentar con piedra fina.",
        "Pivote: perno con hombro ISO 7379 Ø12 + 2 arandelas Belleville + tuerca autoblocante.",
        "Apertura de trabajo: 62° alrededor de A.",
    ], ag, tratamiento="Temple 56-58 HRC; filo asentado")


def p03():
    f = MD.p03_placa_base()
    b = bb(f)
    ag = []
    for i, (x, y) in enumerate(MD.AGUJEROS_LAP):
        ag.append(("ABC"[i], x, y, 6.6, "M6 a P01 (desde abajo)"))
    for i, (x, y) in enumerate(MD.AGUJEROS_TORRE):
        ag.append(("DEFG"[i], x, y, 6.6, "M6 a torre P05 (abajo)"))
    cot = [
        L("planta", (b.min.X, b.min.Y, 0), (b.max.X, b.min.Y, 0), -16),
        L("planta", (b.min.X, b.min.Y, 0), (b.min.X, b.max.Y, 0), -14, 90),
        L("alzado", (MD.LAP_X[0], 0, 0), (b.max.X, 0, 0), 14),
        L("alzado", (b.max.X, 0, 4), (b.max.X, 0, 8), 10, 90),
    ]
    return Plano("P03", "Placa base", "Aluminio 7075-T6, chapa e = 8 mm", 1, masa("P03"), f, ["alzado", "planta"], cot, [
        "Cortar por chorro de agua o fresar desde este DXF (1:1). Espesor 8 mm.",
        "Media madera: fresar 4 mm de la cara INFERIOR en los 20 mm delanteros (empalme con P01).",
        "Agujeros avellanados por abajo: el fondo queda plano para cortar al ras.",
        "La cola de la cuchilla P02 desliza sobre la cara superior: dejarla lisa (Ra 1,6).",
        "Anodizado duro.",
    ], ag, origen="eje del pivote (x hacia el tallo)", tratamiento="Anodizado duro 25 µm")


def p04():
    f = Pos(0, 0, MD.ESP_PATIN) * MD.p04_patin()
    b = bb(f)
    cot = [L("planta", (b.min.X, b.min.Y, 0), (b.max.X, b.min.Y, 0), -16),
           L("planta", (b.min.X, b.min.Y, 0), (b.min.X, b.max.Y, 0), -14, 90)]
    return Plano("P04", "Patín rasante", "Plancha UHMW-PE e = 3 mm", 1, masa("P04"), f, ["planta"], cot, [
        "Cortar desde este DXF. Espesor 3 mm. Se pega con adhesivo para poliolefinas y se fija con los tornillos avellanados.",
        "Agujeros Ø13 para las cabezas avellanadas de los M6 y Ø22 para la cabeza del perno pivote.",
        "Desliza sobre la tierra sin enterrar el cabezal; reemplazable cuando se gaste.",
        "Con el patín, el plano de corte queda a 11 mm del suelo.",
    ], [], origen="eje del pivote")


def p05():
    x0, y0 = MD.TORRE_X[0], MD.TORRE_Y[0]
    f = Pos(-x0, -y0, -MD.ESP_GANCHO) * MD.p05_torre()
    b = bb(f)
    q = MD.Q_BALANCIN
    qx, qz = q[0] - x0, q[2] - MD.ESP_GANCHO
    cot = [
        L("alzado", (0, 0, 0), (MD.TORRE_X[1] - x0, 0, 0), -14),
        L("alzado", (0, 0, 0), (0, 0, MD.TORRE_Z[1] - MD.ESP_GANCHO), -14, 90),
        L("alzado", (0, 0, 0), (qx, 0, 0), 30 + MD.TORRE_Z[1] - q[2], 0),
        L("alzado", (0, 0, 0), (0, 0, qz), -30, 90),
        D("alzado", (qx, 0, qz), 5, 45, "%%c10 H7 eje balancín"),
        L("planta", (0, 0, 0), (0, MD.TORRE_Y[1] - y0, 0), -14, 90),
        N("alzado", (b.max.X - 25, 0, b.max.Z - 18), -30, 26, "alojamiento %%c30,2 H8 a 45°, prof. 50"),
    ]
    ag = [("ABCD"[i], x - x0, y - y0, 5, "roscar M6 x 12 (base)") for i, (x, y) in enumerate(MD.AGUJEROS_TORRE)]
    return Plano("P05", "Torre del cabezal", "Aluminio 6061-T6, bloque mecanizado", 1, masa("P05"), f,
                 ["alzado", "planta", "perfil"], cot, [
                     "Mecanizar en CNC. Paredes laterales de 4 mm con aligeramientos. Anodizado duro.",
                     "Cavidad interior de 27 mm de ancho para el balancín P06 y la biela P07, abierta al frente.",
                     "El alojamiento del tubo P08 va a 45° sobre la base (eje de la herramienta).",
                     "Se atornilla desde abajo a la placa base P03 (agujeros A-D).",
                     "Ver el STEP P05 para la geometría completa de la cavidad.",
                 ], ag, origen="esquina trasera-derecha-inferior", tratamiento="Anodizado duro 25 µm")


def p06():
    q = MD.Q_BALANCIN
    f = Pos(-q[0], -q[1], -q[2]) * MD.p06_balancin()
    bx, _, bz = MD.punto_b(0)
    ax, _, az = MD.punto_a(0)
    cot = [L("alzado", (0, 0, 0), (0, 0, bz - q[2]), -16, 90),
           L("alzado", (0, 0, 0), (ax - q[0], 0, 0), 16 + max(az - q[2], 0), 0),
           L("alzado", (0, 0, 0), (0, 0, az - q[2]), 26, 90),
           D("alzado", (0, 0, 0), 5, 135, "%%c10 H7"),
           L("planta", (0, -4, 0), (0, 4, 0), -16, 90)]
    return Plano("P06", "Palanca angular (balancín)", "Acero SAE 4140 bonificado, e = 8 mm", 1, masa("P06"), f,
                 ["alzado", "planta"], cot, [
                     "Cortar por láser o hilo desde este DXF (1:1). Espesor 8 mm.",
                     "Brazo B (50 mm) a la biela P07; brazo A (38 mm) a la varilla P09.",
                     "Agujeros de brazo Ø8 H7; eje central Ø10 H7 con buje de bronce.",
                     f"Giro de trabajo: de {num(MD.angulo_balancin(MD.ANG_APERTURA))}° (abierta) a "
                     f"{num(MD.angulo_balancin(0))}° (cerrada) respecto a la vertical.",
                 ], [], origen="eje del balancín")


def p07():
    f = MD.p07_biela()
    cot = [L("alzado", (0, 0, 0), (MD.L_BIELA, 0, 0), 16), D("alzado", (0, 0, 0), 4, 135, "2x %%c8 H7"),
           L("alzado", (MD.L_BIELA, 0, -8), (MD.L_BIELA, 0, 8), 14, 90), L("planta", (0, -3, 0), (0, 3, 0), -14, 90)]
    return Plano("P07", "Biela", "Acero SAE 1045, pletina 16 x 6", 1, masa("P07"), f, ["alzado", "planta"], cot, [
        "Distancia entre centros 100 mm ±0,05. Agujeros Ø8 H7 para pasadores o rótulas.",
        "Trabaja a compresión: empuja la cola de la cuchilla P02 para cerrarla. Zincado.",
    ], [])


def tubo_plano(cod, titulo, material, forma, d_ext, d_int, largo, notas):
    cot = [L("alzado", (0, 0, -d_ext / 2), (largo, 0, -d_ext / 2), -14),
           Cota("lin", "perfil", (0, d_ext / 2, 0), (0, -d_ext / 2, 0), dist=d_ext / 2 + 10, angulo=0,
                texto=f"%%c{num(d_ext)}")]
    if d_int:
        cot.append(D("perfil", (0, 0, 0), d_int / 2, 45, f"%%c{num(d_int)}"))
    return Plano(cod, titulo, material, 1, masa(cod), forma, ["alzado", "perfil"], cot, notas, [])


def p08():
    Lc = MD.S_TUBO[1] - MD.S_TUBO[0]
    return tubo_plano("P08", "Tubo", "Tubo de carbono Ø30 x 2 (prototipo: aluminio 6061-T6 Ø30 x 2)", MD.p08_tubo(),
                      30, 26, Lc, [
                          "Cortar a escuadra. Si es de carbono: disco diamantado y sellar el corte con epoxi.",
                          "Entra 40 mm en la torre P05 y 20 mm en la carcasa P10; pegar con epoxi estructural y pasador Ø4.",
                          "Con carbono, aislar el contacto con el aluminio (capa de fibra de vidrio o anodizado).",
                      ])


def p09():
    Lc = MD.S_VARILLA[1] - MD.S_VARILLA[0] - 10
    return tubo_plano("P09", "Varilla de tracción", "Tubo aluminio 7075-T6 Ø10 x 1,5", MD.p09_varilla(), 10, 7, Lc, [
        "Extremo del cabezal: horquilla con pasador Ø8 al brazo A del balancín P06.",
        "Extremo del motor: roscada a la horquilla de la tuerca del husillo SFU1605.",
        "Trabaja a tracción (carga máx. estimada 5 kN): confirmar con el ensayo de fuerza de corte.",
    ])


def p10():
    Lc = MD.S_CARCASA[1] - MD.S_CARCASA[0]
    pl = tubo_plano("P10", "Carcasa de accionamiento", "PA6-GF30 inyectado (prototipo: impresión 3D PA-CF)",
                    MD.p10_carcasa(), 58, 0, Lc, [
                        "Dos medias carcasas atornilladas. Pared 2,5 mm con nervios. Electrónica IP65.",
                        "Aloja: motor sin escobillas 300-400 W, reductor 15:1, husillo SFU1605 y controlador.",
                        "La empuñadura P11 cuelga a 40 mm del frente; la escuadra P13 se atornilla debajo de la cola.",
                        "Conector del cable espiral de la batería en la tapa trasera.",
                    ])
    pl.vistas = ["alzado", "planta", "perfil"]
    return pl


def p11():
    f = MD.p11_empunadura()
    b = bb(f)
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -14),
           L("alzado", (b.max.X, 0, b.min.Z), (b.max.X, 0, b.max.Z), 14, 90),
           L("perfil", (0, -16, -80), (0, 16, -80), -14, 0)]
    return Plano("P11", "Empuñadura ergonómica con guardamonte", "PA6-GF30 con sobremoldeo TPE 3 mm", 1, masa("P11"), f,
                 ["alzado", "perfil"], cot, [
                     "Sección ovalada 44 x 32 mm (equivale a Ø38): agarre de fuerza cómodo, también con guante.",
                     "Inclinada hacia atrás: con el antebrazo en la cuna, la muñeca queda recta (posición de dar la mano).",
                     "Tope superior trasero (cola de castor): ahí apoya el arco entre pulgar e índice. Por ahí se levanta",
                     "   la herramienta, así los cuatro dedos quedan libres para el gatillo P12.",
                     "Tope inferior para que la mano no resbale; sin estrías de dedos (sirve a cualquier mano).",
                     "Seguridad sin esfuerzo: sensor capacitivo de presencia en la cara trasera (reemplaza la palanca",
                     "   de palma). La cuchilla solo cierra con la mano puesta en el mango.",
                     "Guardamonte amplio (luz de 26 a 48 mm para dedos con guante): protege el gatillo de hojas y ramas.",
                 ], [], origen="eje de la herramienta")


def p12():
    f = MD.p12_gatillo()
    b = bb(f)
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -14),
           L("alzado", (b.min.X, 0, b.min.Z), (b.min.X, 0, b.max.Z), -14, 90),
           L("planta", (b.min.X, -10, 0), (b.min.X, 10, 0), -12, 90)]
    return Plano("P12", "Gatillo de cuatro dedos (tipo rozadora)", "PA6-GF30", 1, masa("P12"), f, ["alzado", "planta"], cot, [
        "Gatillo largo como el acelerador de la rozadora: índice, medio, anular y meñique reparten el esfuerzo.",
        "Cuatro hendiduras ubican los dedos. Pivote arriba, bajo la repisa del guardamonte.",
        "Fuerza 10-12 N (unos 3 N por dedo), recorrido 10 mm en el centro. Imán para sensor Hall.",
        "Al soltarlo, freno eléctrico y la cuchilla vuelve a abrir.",
        "Usar con la correa de hombro C08: en el aire, la correa aguanta lo que la herramienta tira hacia la",
        "   punta y los dedos no aprietan el gatillo sin querer.",
    ], [], origen="eje de la herramienta")


def p18():
    f = MD.p18_pulgar()
    b = bb(f)
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -12),
           L("alzado", (b.max.X, 0, b.min.Z), (b.max.X, 0, b.max.Z), 12, 90)]
    return Plano("P18", "Palanca de pulgar (opcional)", "PA6-GF30 con TPE", 1, masa("P18"), f, ["alzado", "planta"],
                 cot, [
                     "Palanca arriba, en el costado izquierdo del mango, donde descansa el pulgar.",
                     "Trabaja en paralelo con el gatillo P12: cualquiera de los dos cierra la cuchilla.",
                     "Sirve para alternar pulgar y dedos durante la jornada y descansar la mano.",
                     "Fuerza 5 N, recorrido 5 mm. Se puede desactivar en el controlador si el operario no la usa.",
                 ], [], origen="eje de la herramienta")


def p13():
    f = MD.p13_brazo_apoyo()
    b = bb(f)
    s0 = MD.S_CARCASA[1] - MD.S_CARCASA[0]
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -14),
           L("alzado", (b.max.X, 0, b.min.Z), (b.max.X, 0, b.max.Z), 14, 90),
           N("alzado", ((MD.S_CUNA[0] + MD.S_CUNA[1]) / 2 - MD.S_CARCASA[0], 0, MD.Z_ANTEBRAZO), 24, -26,
             "colisa 8,2 x 48: ajuste ±20 mm")]
    return Plano("P13", "Brazo del apoyo de antebrazo", "Aluminio 6061-T6, chapa 6 mm plegada + ala de 7 mm", 1,
                 masa("P13"), f, ["alzado", "planta", "perfil"], cot, [
                     "Escuadra en el lado EXTERIOR del antebrazo (lado derecho para un operario diestro).",
                     "Ala superior atornillada bajo la cola de la carcasa P10 con 2 tornillos M6.",
                     "La colisa permite correr la cuna ±20 mm según el largo del antebrazo y deja girarla ±15°.",
                     "Medidas en el sistema de la carcasa (x desde su frente).",
                 ], [], origen="frente de la carcasa P10")


def p14():
    f = MD.p14_cuna()
    b = bb(f)
    Lc = MD.S_CUNA[1] - MD.S_CUNA[0]
    cot = [L("alzado", (0, 0, b.min.Z), (Lc, 0, b.min.Z), -14),
           R("perfil", (0, 0, MD.Z_ANTEBRAZO), MD.R_ANTEBRAZO + 5, 270, "R45 int.")]
    return Plano("P14", "Cuna de antebrazo", "PA6-GF30 (o aluminio 5052 de 4 mm rolado)", 1, masa("P14"), f,
                 ["alzado", "perfil"], cot, [
                     "Canal en U con abertura superior de 120°: el antebrazo entra y sale sin soltar hebillas.",
                     "Recibe el momento del cabezal: con la herramienta en el aire, unos 5-6 kg de presión hacia abajo.",
                     "Inserto roscado M8 en el costado exterior para el perno de la escuadra P13.",
                     "Interior con almohadilla P15. Tallas: R40 (estándar) y R45 (antebrazo grueso).",
                 ], [], origen="extremo delantero de la cuna")


def p15():
    f = MD.p15_almohadilla()
    Lc = MD.S_CUNA[1] - MD.S_CUNA[0]
    cot = [L("alzado", (0, 0, MD.Z_ANTEBRAZO - 50), (Lc, 0, MD.Z_ANTEBRAZO - 50), -14),
           R("perfil", (0, 0, MD.Z_ANTEBRAZO), MD.R_ANTEBRAZO, 250, "R40")]
    return Plano("P15", "Almohadilla y correa", "EVA 5 mm + correa velcro 50 mm + hebilla de liberación", 1,
                 masa("P15"), f, ["alzado", "perfil"], cot, [
                     "Almohadilla de EVA pegada dentro de la cuna P14. Lavable.",
                     "Correa de velcro sobre el antebrazo con hebilla de liberación rápida del lado interior:",
                     "   si el operario resbala en la ladera, el brazo sale de la cuna con un tirón.",
                 ], [], origen="extremo delantero de la cuna")


def p16():
    return tubo_plano("P16", "Anilla para correa de hombro", "Abrazadera PA6 + anilla inoxidable", MD.p16_anilla(),
                      38, 30, 22, [
                          f"Se ubica en el centro de gravedad de la herramienta (a {int(MD.S_ANILLA)} mm del brazo A, sobre P08):",
                          "   colgada de la anilla, la herramienta queda horizontal.",
                          "Engancha la correa de hombro C08 (arnés simple de rozadora, cruzado al hombro izquierdo).",
                          "Al caminar y entre corte y corte la herramienta cuelga y el brazo descansa.",
                      ])


def p17():
    f = Pos(-C[0], -C[1], -MD.Z_DEDO) * MD.p17_dedo(False)
    b = bb(f)
    bx, by = MD.BISAGRA_DEDO[0] - C[0], MD.BISAGRA_DEDO[1] - C[1]
    a0, a1 = MD.DEDO_ARCO
    cot = [R("planta", (0, 0, 0), MD.R_GANCHO_INT + 3, 20, "R38"), R("planta", (0, 0, 0), MD.R_GANCHO_EXT - 4, 30, "R53"),
           Cota("ang", "planta", (0, 0, 0), (a0, a1), dist=0, r=MD.R_GANCHO_EXT + 6, texto="<>"),
           D("planta", (bx, by, 0), 3.1, 225, "%%c6,2")]
    return Plano("P17", "Punta envolvente con resorte", "Acero inoxidable 17-4PH (o SAE 4140 pavonado), e = 6 mm", 1,
                 masa("P17"), f, ["planta"], cot, [
                     "Cortar por láser o hilo desde este DXF (1:1). Espesor 6 mm. Dibujada en posición CERRADA.",
                     "Gira sobre el pasador Ø6 del gancho P01 (agujero E), 0,8 mm por encima de la cuchilla.",
                     "Resorte de torsión de 0,3 N·m: la punta rodea la caña sola cuando hay espacio.",
                     f"Si las cañas vecinas no la dejan pasar, cede hacia afuera (hasta {int(-MD.ANG_DEDO_ABIERTO)}°) y la tijera",
                     "   corta igual con la mordida parcial. El tope evita que se cierre hacia la garganta.",
                     "Pasador de bloqueo opcional para dejarla fija abierta en zonas muy cerradas.",
                 ], [], origen="centro de la garganta", tratamiento="H1025 o pavonado")


def p19():
    import exportar_3d as EX
    rp = EX.reposo(list(PIEZAS.values()))
    f = MD.p19_pata(True)
    b = bb(f)
    cot = [L("alzado", (b.min.X, 0, b.min.Z), (b.max.X, 0, b.min.Z), -14),
           L("alzado", (b.max.X, 0, b.min.Z), (b.max.X, 0, b.max.Z), 14, 90),
           Cota("lin", "perfil", (0, b.max.Y, b.min.Z), (0, b.min.Y, b.min.Z), dist=-14, angulo=0)]
    return Plano("P19", "Pata de apoyo plegable (bípode)", "Patas: tubo aluminio 6061 Ø12 x 1. Abrazadera: PA6-GF30", 1,
                 masa("P19"), f, ["alzado", "perfil"], cot, [
                     "Dibujada desplegada, en el sistema del tubo (x a lo largo del eje). Plegada, cada pata queda a un",
                     "   costado del tubo y la punta queda 65 mm delante del guardamonte, lejos de los dedos.",
                     f"Patas de {rp['largo_pata_mm']} mm. Pie: punta de acero templado Ø8 x {int(MD.PUNTA_L)} mm que se clava en la tierra,",
                     "   con disco de caucho Ø28 de tope (en piedra o suelo duro apoya el disco).",
                     "Bisagras con pasador Ø5 y tope que fija el ángulo de la pata abierta.",
                     "Se baja con el botón de pulgar de la carcasa (cable de freno de bicicleta, C09). Un resorte la",
                     "   recoge sola cuando deja de cargar peso, al levantar la tijera.",
                     f"Parada sola, con las puntas clavadas, se vuelca recién en una pendiente de {rp['pendiente_max_grados']}°"
                     f" ({rp['pendiente_max_pct']} %).",
                 ], [], origen="eje de la herramienta")


TODOS = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19]


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
