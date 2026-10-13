#!/usr/bin/env python3
"""Arma el HTML de impresión (A3 horizontal, escalas exactas) a partir de gen.py."""
import re
import sys

import generar_planos as gen

ESCALAS = {"PLANTA_BAJA": 75, "PLANTA_ALTA": 75, "PLANTA_TECHO": 75, "PLANTA_EST": 75,
           "ELEV_FRONT": 50, "ELEV_LAT": 50, "CORTE": 50, "ESCALERA": 25}
DIBUJOS = {"PLANTA_BAJA": gen.planta_baja, "PLANTA_ALTA": gen.planta_alta, "PLANTA_TECHO": gen.planta_techo,
           "PLANTA_EST": gen.planta_estructural, "ELEV_FRONT": gen.elevacion_frontal,
           "ELEV_LAT": gen.elevacion_lateral, "CORTE": gen.corte_aa, "ESCALERA": gen.detalle_escalera}
TOTAL = 12


PX_MM = 25.4 / 96  # un px de CSS en milímetros


def a_escala(svg, escala):
    """Fija el tamaño real en mm y el grosor de línea en unidades del dibujo."""
    x, y, w, h = map(float, re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    mm = 1000 / escala
    u = PX_MM / mm
    return svg.replace("<svg ", f'<svg style="width:{w * mm:.1f}mm;height:{h * mm:.1f}mm;--u:{u:.5f}px" ', 1)


def trazos_reales(css):
    """En impresión no hay non-scaling-stroke: pasa grosores y guiones a unidades del dibujo."""
    css = css.replace("vector-effect:non-scaling-stroke", "vector-effect:none")
    css = re.sub(r"stroke-width:([\d.]+)", lambda m: f"stroke-width:calc({m.group(1)} * var(--u))", css)
    css = re.sub(r"stroke-dasharray:([\d. ]+)",
                 lambda m: "stroke-dasharray:" + " ".join(f"calc({n} * var(--u))" for n in m.group(1).split()), css)
    return css


def cajetin(m):
    hoja, cod, titulo, esc = m.group(1).split("|")
    return f'''<div class="cajetin">
  <div class="cj cj-proy"><div><span>Proyecto</span><b>Casa Elevada 200 msnm</b><br>Vivienda unifamiliar elevada · Ecuador, ≈ 200 msnm</div></div>
  <div class="cj cj-3"><div class="cj-cod"><span>Lámina</span><b>{cod}</b></div><div><span>Contenido</span><b>{titulo}</b></div><div><span>Escala</span><b>{esc}</b></div></div>
  <div class="cj" style="grid-template-columns:1fr 1fr 1fr"><div><span>Fecha</span>Octubre 2026</div><div><span>Formato</span>A3 horizontal</div><div><span>Hoja</span>{hoja} de {TOTAL}</div></div>
  <div class="cj cj-firma"><div><span>Arquitecto responsable</span></div><div><span>Ingeniero estructural</span></div></div>
  <div class="cj cj-estado"><div>Anteproyecto · no apto para construcción</div></div>
</div>'''


def main(tpl_web, tpl_pdf, out):
    web = open(tpl_web, encoding="utf-8").read()
    css = web[web.index("/* ---------- dibujo técnico ---------- */"):web.index(".defs{")]
    defs = web[web.index('<svg class="defs"'):web.index("</defs></svg>") + len("</defs></svg>")]
    html = open(tpl_pdf, encoding="utf-8").read()
    css = "svg{--u:0.02px}\n.leyenda svg{--u:0.0144px}\n" + trazos_reales(css)
    html = html.replace("{{CSS_DIB}}", css).replace("{{DEFS}}", defs)
    for k, f in DIBUJOS.items():
        html = html.replace("{{" + k + "}}", a_escala(f(), ESCALAS[k]))
    html = re.sub(r"\{\{CAJ:([^}]+)\}\}", cajetin, html)
    assert "{{" not in html, re.findall(r"\{\{[^}]+\}\}", html)
    open(out, "w", encoding="utf-8").write(html)
    print("ok", out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
