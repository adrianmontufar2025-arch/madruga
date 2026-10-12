"""Exporta el conjunto 3D: STEP del conjunto y por pieza, GLB y datos para el visor."""
import base64
import json
import math
import os
import re
import sys
import unicodedata

from build123d import Circle, Color, Compound, Location, Pos, Vector, export_gltf, export_step, extrude

sys.path.insert(0, os.path.dirname(__file__))
import modelo as MD  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D3 = os.path.join(RAIZ, "modelo_3d")
DPZ = os.path.join(D3, "piezas_step")
DVIS = os.path.join(RAIZ, "visor")
for d in (D3, DPZ, DVIS):
    os.makedirs(d, exist_ok=True)

MOVILES = ("P02", "P06", "P07", "P09")
FRAMES = [0.0, 10.0, 20.0, 31.0, 41.0, 52.0, MD.ANG_APERTURA]
TORNILLERIA_G = 150


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()


def colocar(p, mundo, etiqueta=None):
    g = mundo * p.ubicacion * p.geometria
    g.label = etiqueta or p.codigo
    g.color = Color(*p.color)
    return g


def balance(piezas):
    """Cargas en la mano, la cuna y la muñeca en la postura de corte (eje a 45°).

    La cuna solo empuja perpendicular al antebrazo; lo que tira de la herramienta hacia la punta (a lo largo
    del eje) lo aguantan los dedos, salvo que la correa de hombro lo tome."""
    mundo = MD.a_mundo()
    tot = mx = mz = 0.0
    for p in piezas:
        c = (mundo * p.ubicacion * p.geometria).center()
        m = p.masa()
        tot += m
        mx += m * c.X
        mz += m * c.Z
    cc = [v + o for v, o in zip(MD.eje(sum(MD.S_CARCASA) / 2), MD.H_A_MUNDO)]
    tot += TORNILLERIA_G
    mx += TORNILLERIA_G * cc[0]
    mz += TORNILLERIA_G * cc[2]
    cg = (mx / tot, mz / tot)
    W = tot / 1000 * 9.81
    kgf = lambda f: round(abs(f) / 9.81, 1)  # noqa: E731

    o = [v + h for v, h in zip(MD.eje(0), MD.H_A_MUNDO)]
    def local(x, z):
        return ((x - o[0]) * MD.U[0] + (z - o[2]) * MD.U[2], (x - o[0]) * MD.N_ARRIBA[0] + (z - o[2]) * MD.N_ARRIBA[2])
    sg, ng = local(*cg)
    sh, nh = MD.S_EMP, -85.0                                   # mano en la empuñadura
    sw, nw = MD.S_EMP + 45.0, MD.Z_ANTEBRAZO + 5.0             # muñeca
    sc = sum(MD.S_CUNA) / 2                                    # cuna (empuja solo según N)
    wu, wn = -W * MD.U[2], -W * MD.N_ARRIBA[2]                 # peso en ejes locales
    m_peso = (sg - sh) * wn - (ng - nh) * wu                   # momento del peso respecto de la mano

    def muneca(fu, fn):
        return abs((sh - sw) * fn - (nh - nw) * fu) / 1000

    ref = MD.antebrazo_mundo()
    mano, mun = ref["mano"], ref["muneca"]
    # 1) en el aire, sin cuna: la muñeca aguanta todo el momento del peso
    m_sin = W * abs(mun[0] - cg[0]) / 1000
    # 2) en el aire, con cuna
    fc = -m_peso / (sc - sh)
    fu = -wu
    fn = -wn - fc
    aire_cuna = dict(mano_kgf=kgf(math.hypot(fu, fn)), dedos_kgf=kgf(fu), cuna_kgf=kgf(fc), muneca_Nm=round(muneca(fu, fn), 1))
    # 3) en el aire, con cuna y correa de hombro (la correa toma lo que tira hacia la punta)
    tu, ty, tn = MD.direccion_correa()
    a = MD.anilla_mundo()
    sr, nr = local(a[0], a[2])
    T = -wu / tu
    fc2 = -(m_peso + (sr - sh) * T * tn - (nr - nh) * T * tu) / (sc - sh)
    fn2 = -wn - fc2 - T * tn
    aire_correa = dict(mano_kgf=kgf(fn2), dedos_kgf=0.0, cuna_kgf=kgf(fc2), correa_kgf=kgf(T),
                       lateral_kgf=kgf(T * ty), muneca_Nm=round(muneca(0.0, fn2), 1))
    # 4) cortando: el patín apoya en el suelo y la mano lleva el resto (fuerzas verticales)
    x_apoyo = -80 + MD.H_A_MUNDO[0]
    carga_apoyado = tot * (cg[0] - x_apoyo) / (mano[0] - x_apoyo)
    apoyado = dict(mano_kgf=round(carga_apoyado / 1000, 1),
                   muneca_Nm=round(carga_apoyado / 1000 * 9.81 * abs(mano[0] - mun[0]) / 1000, 1))
    return dict(masa_total_g=round(tot), cg_mundo=[round(cg[0]), round(cg[1])], momento_muneca_Nm=round(m_sin, 1),
                aire_cuna=aire_cuna, aire_correa=aire_correa, apoyado=apoyado,
                fuerza_cuna_kgf=aire_cuna["cuna_kgf"], carga_mano_apoyado_g=round(carga_apoyado),
                anilla_sobre_cg_mm=round(sr - sg), altura_mano_mm=round(mano[2]), distancia_mano_tallo_mm=round(-mano[0]))


def corte_parcial(a_dir=50.0, d=35.0, D=60.0):
    """Caña Ø60 que entra solo una parte (centro a d mm afuera del centro de la garganta).

    Devuelve la zona que barre la cuchilla (se corta) y la que queda (se parte con el tirón)."""
    cuchillas = [Location((0, 0, 0), (0, 0, 1), t) * MD.p02_cuchilla() for t in range(0, int(MD.ANG_APERTURA) + 1, 2)]
    barrido = cuchillas[0]
    for c in cuchillas[1:]:
        barrido = barrido + c
    ux, uy = math.cos(math.radians(a_dir)), math.sin(math.radians(a_dir))
    cx, cy = MD.C_GARGANTA[0] + d * ux, MD.C_GARGANTA[1] + d * uy
    zc = MD.Z_CORTE + 1.0
    losa = Pos(cx, cy, zc) * extrude(Circle(D / 2), 1.2)
    corte = losa & barrido
    resto = losa - barrido
    n, k = 120, 0
    while k <= n:
        t = D * k / n
        p = Vector(cx - (D / 2 - t) * ux, cy - (D / 2 - t) * uy, zc + 0.6)
        if not any(c.is_inside(p) for c in cuchillas):
            break
        k += 1
    profundidad = max(k - 1, 0) / n
    area = corte.volume / losa.volume
    v1 = (cx + (D / 2 + 25 + 3) * ux, cy + (D / 2 + 25 + 3) * uy)
    v2 = (cx + 55 * math.cos(math.radians(a_dir - 30)), cy + 55 * math.sin(math.radians(a_dir - 30)))
    return dict(corte=corte, resto=resto, centro=(cx, cy), vecinas=[(v1, 25.0), (v2, 22.0)], zc=zc,
                profundidad_pct=round(profundidad * 100), area_pct=round(area * 100), D=D, d=d, a_dir=a_dir)


def main():
    mundo = MD.a_mundo()
    piezas = MD.construir(0.0)
    bat = MD.bateria()

    conj = Compound(children=[colocar(p, mundo) for p in piezas])
    conj.label = "Tijera_de_cana_con_apoyo_de_antebrazo"
    export_step(conj, os.path.join(D3, "tijera_conjunto.step"))
    for p in piezas:
        if p.codigo.startswith("C"):
            continue
        g = p.geometria
        g.label = p.codigo
        g.color = Color(*p.color)
        export_step(g, os.path.join(DPZ, f"{p.codigo}_{slug(p.nombre)}.step"))

    nodos = [colocar(p, mundo) for p in piezas if p.codigo not in MOVILES]
    for th in FRAMES:
        for p in MD.construir(th):
            if p.codigo in MOVILES:
                nodos.append(colocar(p, mundo, f"{p.codigo}@{int(round(th))}"))
    # punta envolvente: cerrada (@0) y abierta (@1)
    for k, abierto in enumerate((False, True)):
        g = mundo * MD.p17_dedo(abierto)
        g.label = f"P17@{k}"
        g.color = Color(*MD.ACERO_FILO)
        nodos.append(g)
    nodos = [n for n in nodos if n.label != "P17"]
    # escena de corte parcial (solo para la vista "Corte parcial")
    cp = corte_parcial()
    zc = cp["zc"]
    extra = [("XCORTE", cp["corte"], (0.95, 0.45, 0.10)),
             ("XRESTO", cp["resto"], (0.55, 0.64, 0.27)),
             ("XTOCON", Pos(cp["centro"][0], cp["centro"][1], -MD.ESP_PATIN) * extrude(Circle(cp["D"] / 2), zc + MD.ESP_PATIN), (0.62, 0.66, 0.30))]
    for i, ((x, y), r) in enumerate(cp["vecinas"]):
        extra.append((f"XVECINA{i + 1}", Pos(x, y, -MD.ESP_PATIN) * extrude(Circle(r), 120), (0.62, 0.66, 0.30)))
    for nombre, forma, color in extra:
        g = mundo * forma
        g.label = nombre
        g.color = Color(*color)
        nodos.append(g)
    ruta_glb = os.path.join(D3, "tijera.glb")
    export_gltf(Compound(children=nodos), ruta_glb, binary=True, linear_deflection=0.06, angular_deflection=0.25)
    with open(ruta_glb, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    with open(os.path.join(DVIS, "tijera_glb.json"), "w") as f:
        json.dump({"formato": "glb-base64", "glb": b64}, f)

    bal = balance(piezas)
    datos = []
    for p in piezas + [bat]:
        ex = p.explosion
        datos.append(dict(codigo=p.codigo, nombre=p.nombre, material=p.material, cantidad=p.cantidad, grupo=p.grupo,
                          masa_g=round(p.masa()), plano=p.plano,
                          explosion=[round(ex[0], 1), round(ex[1], 1), round(ex[2], 1)],
                          color=[round(c, 3) for c in p.color]))
    info = dict(piezas=datos, moviles=list(MOVILES), cuadros=[int(round(t)) for t in FRAMES],
                tornilleria_cables_g=TORNILLERIA_G, brazo=MD.antebrazo_mundo(), altura_corte_mm=MD.ALTURA_CORTE,
                capacidad_mm=MD.D_TALLO_MAX, angulo_eje=MD.ANG_EJE,
                corte_parcial={k: v for k, v in cp.items() if k in ("profundidad_pct", "area_pct", "D", "d", "a_dir")},
                **bal)
    with open(os.path.join(DVIS, "piezas.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    print(json.dumps(bal), info["corte_parcial"])


if __name__ == "__main__":
    main()
