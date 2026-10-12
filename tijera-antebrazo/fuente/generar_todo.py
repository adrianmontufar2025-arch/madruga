"""Regenera todo: modelo 3D (STEP/GLB), planos DXF pieza por pieza, plano de conjunto, PDF, lista de materiales y dossier de fabricación.

Uso:  python3 generar_todo.py
Requiere: pip install build123d ezdxf matplotlib openpyxl reportlab pypdf
"""
import dossier
import exportar_3d
import lista_materiales
import pdf_planos
import plano_conjunto
import planos_piezas

if __name__ == "__main__":
    exportar_3d.main()
    planos_piezas.main()
    plano_conjunto.main()
    pdf_planos.main()
    lista_materiales.main()
    dossier.main()             # usa las imágenes de imagenes/sin_rotulo (se generan desde el visor)
