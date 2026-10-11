# Tijera de caña con apoyo de antebrazo (Rev. A, conceptual)

Esta tijera eléctrica se usa con una mano y sirve para cortar caña de hasta 6 cm de diámetro al ras del suelo, en matas cerradas y con retoños. Se trabaja igual que con el machete: **la mano libre sostiene la caña** y decide hacia dónde cae, y la otra mano corta. La diferencia es que no hace falta fuerza ni puntería. El gancho centra la caña sola, se aprieta el gatillo y la cuchilla corta en menos de un segundo.

El antebrazo descansa en una **cuna (P14)**, así que la muñeca no carga el peso del cabezal.

> Es un diseño para fabricar y probar un prototipo. Antes de cortar acero hay que medir en campo la fuerza de corte de las cañas más gruesas.

## Cómo funciona

1. Se mete el pico del gancho (P01) entre las cañas hasta rodear la caña elegida. El pico es redondeado y sin filo, para no lastimar los retoños.
2. El cabezal se apoya en el suelo sobre el patín de UHMW (P04). Gancho y placa base forman un fondo plano, y el corte queda a **11 mm del suelo**.
3. Se aprieta la palanca de seguridad con la palma y luego el gatillo (P12). El motor tira de la varilla (P09), la varilla gira el balancín (P06) y la biela (P07) cierra la cuchilla (P02) contra el gancho.
4. La mano libre sostiene la caña cortada y la baja hacia la calle.
5. Para una caña virada, se gira el antebrazo y el cabezal queda de canto.

## Cifras del modelo

| Concepto | Valor |
|---|---|
| Capacidad de corte | tallos de hasta Ø65 mm |
| Altura de corte | 11 mm sobre el suelo |
| Masa sin batería | ≈ 3,6 kg (incluye 0,15 kg estimados de tornillería y cables) |
| Batería | 36 V al cinturón, con cable espiral (no pesa en el brazo) |
| Momento sobre la muñeca **sin** apoyo | ≈ 9,5 N·m: más de lo que una muñeca aguanta todo un día |
| Con la cuna de antebrazo | el antebrazo recibe ≈ 5,6 kg de presión y la muñeca solo guía |
| Carga en la mano con el patín apoyado | ≈ 1,6 kg |
| Postura | mano a 0,43 m del suelo y a 0,64 m del tallo, parecida a la del machete |
| Accionamiento | motor 300–400 W, reductor 15:1, husillo de bolas SFU1605, balancín y biela |

La herramienta pesa bastante más que un machete. Por eso lleva tres cosas:
- La cuna, que se lleva el momento del cabezal.
- El patín, que apoya el cabezal en la tierra mientras corta.
- Una anilla (P16) en el centro de gravedad para colgarla de una correa de hombro entre corte y corte.

## Seguridad

- **Dos mandos:** la cuchilla solo cierra si están apretados a la vez la palanca de palma y el gatillo.
- **Freno eléctrico:** al soltar el gatillo, la cuchilla se detiene y vuelve a abrir.
- **Cuna abierta arriba con hebilla de liberación rápida:** si el operario resbala en la ladera, el brazo sale de un tirón.
- **Regla de trabajo:** la mano que sostiene la caña siempre a unos 40 cm o más por encima del corte, y usar botas o canilleras.

## Contenido

| Carpeta / archivo | Qué es | Con qué se abre |
|---|---|---|
| `imagenes/` | Vistas 3D: armada, cabezal cerrado y abierto, planta, lateral con medidas, despiece, en la mata | Cualquier visor de imágenes |
| `planos_cortadora.pdf` | Los 17 planos en un PDF a escala | Cualquier lector de PDF |
| `planos_dxf/` | Un DXF por pieza (P01…P16) y el conjunto `00` con la lista de materiales | AutoCAD (Guardar como → DWG), DraftSight, LibreCAD, QCAD |
| `modelo_3d/tijera_conjunto.step` y `piezas_step/` | Modelo 3D del conjunto y de cada pieza | FreeCAD, Fusion 360, SolidWorks |
| `modelo_3d/tijera.glb` | Modelo 3D liviano con colores | Visor 3D de Windows, Blender |
| `visor/` | Visor 3D interactivo (HTML) | Navegador, servido por HTTP |
| `fuente/` | Modelo paramétrico y generadores de planos | Python 3 |

En los DXF, la geometría está a escala real 1:1. El contorno de las piezas de chapa (P01, P02, P03, P04, P06, P07) va directo a corte láser, plasma o chorro de agua; solo hay que borrar las capas `COTAS`, `TEXTO`, `EJES` y `MARCO`.

## Siguiente paso

1. Medir la fuerza de corte en las cañas de 6 cm, con una gata hidráulica y una celda de carga. El diseño supone entre 3 y 3,5 kN.
2. Primero armar el cabezal (P01 a P07) y la cuna, y probar el corte y la postura en la mata, aunque el accionamiento sea provisional.
3. Con los datos reales, ajustar `fuente/modelo.py` y regenerar todo.

## Regenerar todo

```bash
pip install build123d ezdxf matplotlib
cd fuente
python3 generar_todo.py
```
