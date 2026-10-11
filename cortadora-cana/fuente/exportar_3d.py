"""Exporta el conjunto 3D: STEP del conjunto, STEP por pieza, GLB para el visor y datos de piezas."""
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

MOVILES = ("P02", "P09", "P15", "P22")
FRAMES = [0.0, 10.0, 20.0, 31.0, 41.0, 52.0, MD.ANG_APERTURA]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()


def colocar(p, mundo):
    g = mundo * p.ubicacion * p.geometria
    g.label = p.codigo
    g.color = Color(*p.color)
    return g


def main():
    mundo = MD.a_mundo()
    piezas = MD.construir(0.0)
    bat = MD.bateria()

    # --- STEP del conjunto (cuchilla cerrada) y por pieza
    hijos = [colocar(p, mundo) for p in piezas]
    conj = Compound(children=hijos)
    conj.label = "Cortadora_selectiva_de_cana"
    export_step(conj, os.path.join(D3, "cortadora_conjunto.step"))
    for p in piezas:
        if p.codigo.startswith("C"):
            continue
        g = p.geometria
        g.label = p.codigo
        g.color = Color(*p.color)
        export_step(g, os.path.join(DPZ, f"{p.codigo}_{slug(p.nombre)}.step"))

    # --- GLB del visor: piezas fijas + piezas móviles en varios cuadros
    nodos = []
    for p in piezas:
        if p.codigo in MOVILES:
            continue
        nodos.append(colocar(p, mundo))
    for th in FRAMES:
        for p in MD.construir(th):
            if p.codigo in MOVILES:
                g = mundo * p.ubicacion * p.geometria
                g.label = f"{p.codigo}@{int(round(th))}"
                g.color = Color(*p.color)
                nodos.append(g)
    # batería: colgada del cinturón, al costado del operario (solo referencia)
    loc_bat = Location((-1150.0, -330.0, 420.0))   # solo se muestra en el despiece
    gb = loc_bat * Location((0, 0, 0), (0, 0, 1), 90) * bat.geometria
    gb.label = "C05"
    gb.color = Color(*bat.color)
    nodos.append(gb)
    ruta_glb = os.path.join(D3, "cortadora.glb")
    export_gltf(Compound(children=nodos), ruta_glb, binary=True, linear_deflection=0.08, angular_deflection=0.25)
    # el visor web recibe el GLB empaquetado en JSON (base64)
    with open(ruta_glb, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    with open(os.path.join(DVIS, "cortadora_glb.json"), "w") as f:
        json.dump({"formato": "glb-base64", "glb": b64}, f)

    # --- datos de piezas para el visor y la lista de materiales
    datos = []
    total = 0.0
    for p in piezas + [bat]:
        m = p.masa()
        if p.codigo != "C05":
            total += m
        ex = p.explosion
        datos.append(dict(codigo=p.codigo, nombre=p.nombre, material=p.material, cantidad=p.cantidad,
                          grupo=p.grupo, masa_g=round(m), plano=p.plano,
                          explosion=[round(ex[0], 1), round(ex[1], 1), round(ex[2], 1)],
                          color=[round(c, 3) for c in p.color]))
    info = dict(
        piezas=datos,
        moviles=list(MOVILES),
        cuadros=[int(round(t)) for t in FRAMES],
        masa_modelo_g=round(total),
        tornilleria_cables_g=250,
        pivote_mundo=[MD.H_A_MUNDO[0], MD.H_A_MUNDO[1], MD.H_A_MUNDO[2]],
        altura_horquilla_mm=MD.Z_HORQUILLA + MD.H_A_MUNDO[2],
        empunadura_trasera_mundo=[round(v + o, 1) for v, o in zip(MD.eje(MD.S_EMP_TRAS), MD.H_A_MUNDO)],
        angulo_pertiga=MD.ANG_PERTIGA,
    )
    with open(os.path.join(DVIS, "piezas.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    print("masa del modelo (sin batería):", round(total), "g")


if __name__ == "__main__":
    main()
