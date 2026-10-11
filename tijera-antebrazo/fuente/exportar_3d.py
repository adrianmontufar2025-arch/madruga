"""Exporta el conjunto 3D: STEP del conjunto y por pieza, GLB y datos para el visor."""
import base64
import json
import math
import os
import re
import sys
import unicodedata

from build123d import Color, Compound, Location, export_gltf, export_step

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
    ref = MD.antebrazo_mundo()
    mano = ref["mano"]
    e = MD.eje(sum(MD.S_CUNA) / 2)
    cuna_x = e[0] + MD.Z_ANTEBRAZO * MD.N_ARRIBA[0] + MD.H_A_MUNDO[0]
    peso = tot / 1000 * 9.81
    momento = abs(peso * (mano[0] - cg[0]) / 1000)
    brazo = abs(cuna_x - mano[0]) / 1000
    x_apoyo = -80 + MD.H_A_MUNDO[0]
    carga_apoyado = tot * (cg[0] - x_apoyo) / (mano[0] - x_apoyo)
    return dict(masa_total_g=round(tot), cg_mundo=[round(cg[0]), round(cg[1])], momento_muneca_Nm=round(momento, 1),
                fuerza_cuna_kgf=round(momento / brazo / 9.81, 1), carga_mano_apoyado_g=round(carga_apoyado),
                altura_mano_mm=round(mano[2]), distancia_mano_tallo_mm=round(-mano[0]))


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
                capacidad_mm=MD.D_TALLO_MAX, angulo_eje=MD.ANG_EJE, **bal)
    with open(os.path.join(DVIS, "piezas.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    print(json.dumps(bal))


if __name__ == "__main__":
    main()
