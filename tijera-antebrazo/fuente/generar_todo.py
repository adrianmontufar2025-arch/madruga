"""Regenera todo: modelo 3D (STEP/GLB), planos DXF pieza por pieza, plano de conjunto y PDF.

Uso:  python3 generar_todo.py
Requiere: pip install build123d ezdxf matplotlib
"""
import exportar_3d
import pdf_planos
import plano_conjunto
import planos_piezas

if __name__ == "__main__":
    exportar_3d.main()
    planos_piezas.main()
    plano_conjunto.main()
    pdf_planos.main()
