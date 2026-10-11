# Cortadora selectiva de caña en pértiga (Rev. A, conceptual)

Esta carpeta trae el diseño conceptual de una herramienta para cortar caña tallo por tallo en ladera, pensada para la zona de Ramón Campaña y El Corazón (Pangua, Cotopaxi). Funciona como una tijera eléctrica montada en una pértiga de carbono. El cabezal **corta y sostiene**: después del corte, la caña de 3,5 m queda de pie en el gancho y en la guía superior, y su peso pasa al suelo a través del patín. El operario decide hacia dónde bajarla.

> Es un diseño para fabricar y probar un prototipo, no para producción en serie. Antes de cortar acero hay que medir en campo la fuerza de corte, el diámetro y el peso de los tallos (ver "Siguiente paso").

## Contenido

| Carpeta / archivo | Qué es | Con qué se abre |
|---|---|---|
| `imagenes/` | Vistas 3D renderizadas: armada, cabezal cerrado y abierto, planta del cabezal, lateral con medidas, despiece, en la mata | Cualquier visor de imágenes |
| `planos_cortadora.pdf` | Los 27 planos en un solo PDF (A3 y A2, a escala) | Cualquier lector de PDF |
| `planos_dxf/` | Un DXF por pieza (P01…P25) más el plano de conjunto `00` con la lista de materiales | AutoCAD, DraftSight, LibreCAD, QCAD, BricsCAD, Fusion 360 |
| `modelo_3d/cortadora_conjunto.step` | Modelo 3D completo con los nombres de las piezas | FreeCAD, Fusion 360, SolidWorks, Inventor, Onshape |
| `modelo_3d/piezas_step/` | Un STEP por pieza (para CNC, impresión 3D o para modificarla) | Igual que el anterior |
| `modelo_3d/cortadora.glb` | Modelo 3D liviano con colores | Visor 3D de Windows, Blender, visores web de glTF |
| `visor/` | Visor 3D interactivo (HTML + modelo empaquetado en `cortadora_glb.json`) | Navegador, servido por HTTP |
| `fuente/` | Modelo paramétrico en Python y generadores de planos | Python 3 |

### DXF y DWG

Los planos están en **DXF R2013**. AutoCAD los abre directamente y con *Guardar como → DWG* quedan en DWG. Otra opción es el programa gratuito *ODA File Converter*. En cada DXF la geometría está a **escala real 1:1** en el espacio modelo; solo el marco y el cajetín están escalados. Por eso el contorno de las piezas de chapa (P01, P02, P05, P09, P10, P13, P14, P15) puede ir directo a corte láser, plasma o chorro de agua: basta con borrar las capas `COTAS`, `TEXTO`, `EJES` y `MARCO`.

Capas: `VISIBLE` (contorno), `OCULTAS` (aristas ocultas), `EJES`, `COTAS`, `TEXTO`, `MARCO`. Proyección europea (ISO-E). Tolerancias generales ISO 2768-mK.

## Cifras del modelo

| Concepto | Valor |
|---|---|
| Capacidad de corte | tallos de hasta Ø55 mm |
| Altura de corte | 15–45 mm, se regula con el patín P07 |
| Pértiga | Ø32 de carbono a 40°, en 2 tramos con acople rápido |
| Distancia del operario al tallo | 1,08 m (empuñadura trasera a 0,88 m de altura) |
| Guía superior | horquilla con compuerta a 0,62 m; el mástil se abate para transporte |
| Masa sin batería | ≈ 4,8 kg (4,5 kg del modelo + 0,25 kg estimados de tornillería y cables) |
| Carga en las manos con el patín apoyado | ≈ 1,8 kg |
| Accionamiento | motor 36 V 400–500 W, reductor 15:1, husillo de bolas SFU1605, balancín y biela |
| Apertura de la cuchilla / carrera de la varilla | 62° / 31 mm |

La masa salió mayor que los 2,5–3 kg que se estimaron al inicio. La mayor parte está en el cabezal (≈ 2,4 kg con la guía) y en el accionamiento (≈ 1,3 kg). Como el cabezal trabaja apoyado en el suelo y la herramienta cuelga del arnés al caminar, el operario no carga ese peso con los brazos. Para la Rev. B hay margen de bajar 0,6 a 0,8 kg:

- Hacer la torre P04 en PA6-GF30.
- Usar un motor más chico si el ensayo de fuerza lo permite.
- Hacer la guía desmontable para cuando no haga falta.

## Siguiente paso

1. Medir unas 20 cañas en campo: peso, diámetro en la base y fuerza de corte. La fuerza se puede medir con una gata hidráulica y una celda de carga. El diseño supone 2,5 a 3 kN.
2. Armar una maqueta manual con el cabezal (P01, P02, P03, P05, P07 y la guía) accionado por palanca. Con ella se prueban en ladera el corte, el tumbado dirigido, la bajada por arrastre y el corte de cañas volcadas.
3. Con las medidas reales, ajustar los parámetros de `fuente/modelo.py` y regenerar todo.

## Regenerar todo

```bash
pip install build123d ezdxf matplotlib
cd fuente
python3 generar_todo.py        # STEP, GLB, 27 DXF y el PDF
```

Las medidas principales se cambian al inicio de `fuente/modelo.py`: capacidad, radios del gancho, ángulo de la pértiga, largo de los tramos, altura de la guía, etc. Los planos se vuelven a acotar solos.

Para ver el visor en local, sirve la carpeta `visor/` por HTTP:

```bash
cd visor && python3 -m http.server 8000
```

Luego abre `http://localhost:8000` en el navegador.
