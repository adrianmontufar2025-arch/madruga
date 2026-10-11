"""Une todos los planos DXF en un PDF a escala (A3/A2) para verlos sin programa CAD."""
import glob
import os
import sys

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from ezdxf.addons.drawing import Frontend, RenderContext  # noqa: E402
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration  # noqa: E402
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def pagina(pdf, ruta):
    doc = ezdxf.readfile(ruta)
    msp = doc.modelspace()
    k = float(doc.header.get("$LTSCALE", 1.0))
    xs = []
    ys = []
    for e in msp.query("LINE"):
        xs += [e.dxf.start.x, e.dxf.end.x]
        ys += [e.dxf.start.y, e.dxf.end.y]
    W, H = (594.0, 420.0) if (max(xs) - min(xs)) / k > 450 else (420.0, 297.0)
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK,
                        lineweight_scaling=1.0, min_lineweight=0.12)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(msp, finalize=False)
    ax.set_xlim(0, W * k)
    ax.set_ylim(0, H * k)
    ax.set_aspect("equal")
    ax.axis("off")
    pdf.savefig(fig)
    plt.close(fig)


def main():
    rutas = sorted(glob.glob(os.path.join(RAIZ, "planos_dxf", "*.dxf")))
    salida = os.path.join(RAIZ, "planos_cortadora.pdf")
    with PdfPages(salida) as pdf:
        for r in rutas:
            pagina(pdf, r)
            print("pág.", os.path.basename(r))
    print(salida)


if __name__ == "__main__":
    main()
