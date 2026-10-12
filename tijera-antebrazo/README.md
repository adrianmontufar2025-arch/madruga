# Tijera de caña con apoyo de antebrazo (Rev. B, conceptual)

Esta tijera eléctrica se usa con una mano y sirve para cortar caña de hasta 6 cm de diámetro al ras del suelo, en matas cerradas y con retoños. Se trabaja igual que con el machete: **la mano libre sostiene la caña** y decide hacia dónde cae, y la otra mano corta. La diferencia es que no hace falta fuerza ni puntería. El gancho centra la caña sola, se aprieta el gatillo y la cuchilla corta en menos de un segundo.

El antebrazo descansa en una **cuna (P14)**, que se lleva casi todo el momento del cabezal. Como en la rozadora, una **correa de hombro (C08)** enganchada en el centro de gravedad aguanta el resto del peso. Así los dedos quedan libres para el gatillo.

> Es un diseño para fabricar y probar un prototipo. Antes de cortar acero hay que medir en campo la fuerza de corte de las cañas más gruesas.

## Cómo funciona

1. Se mete la punta del gancho (P01) entre las cañas, junto a la caña elegida. La punta es roma, para no lastimar los retoños.
   - **Si hay espacio:** la punta envolvente con resorte (P17) rodea la caña sola y la deja centrada en la garganta.
   - **Si la caña está apretada entre otras:** la punta cede hacia afuera y la tijera muerde solo la parte de la caña que alcanza (ver "Corte parcial").
2. El cabezal se apoya en el suelo sobre el patín de UHMW (P04). Gancho y placa base forman un fondo plano, y el corte queda a **11 mm del suelo**.
3. Con la mano en el mango (el sensor de presencia lo detecta), se aprieta el gatillo de cuatro dedos (P12) o la palanca de pulgar (P18). El motor tira de la varilla (P09), la varilla gira el balancín (P06) y la biela (P07) cierra la cuchilla (P02) contra el gancho.
4. La mano libre sostiene la caña cortada y la baja hacia la calle.
5. Para una caña virada, se gira el antebrazo y el cabezal queda de canto.

## Corte parcial (caña apretada)

Cuando las cañas vecinas no dejan rodear la caña, la tijera igual corta lo que entra en la boca:
- La mandíbula fija es corta (sin pico curvo) y tiene **dientes de agarre** en el tramo delantero. Los dientes sujetan la caña para que no se salga mientras la cuchilla cierra.
- La cuchilla llega hasta la punta de la mandíbula, así que corta también lo que queda en la entrada de la boca.

Comprobado en el modelo con una caña de Ø60:

| Cuánto entra la caña | Lo que corta la cuchilla |
|---|---|
| Completa | 100 % |
| La mitad afuera de la garganta (centro 30 mm afuera) | 68–78 % del diámetro |
| Dos tercios afuera (centro 40 mm afuera) | 52–61 % del diámetro |

El rango depende del ángulo con que entra la caña (45° a 60°). Después del corte, la mano libre empuja la caña **hacia el lado contrario al corte**, para que el corte se abra. La caña madura es cristalina, se parte por lo que falta y sale.

## Cifras del modelo

| Concepto | Valor |
|---|---|
| Capacidad de corte | tallos de hasta Ø65 mm |
| Altura de corte | 11 mm sobre el suelo |
| Masa sin batería | ≈ 3,7 kg (incluye 0,15 kg estimados de tornillería y cables) |
| Batería | 36 V al cinturón, con cable espiral (no pesa en el brazo) |
| Postura | mano a 0,43 m del suelo y a 0,64 m del tallo, parecida a la del machete |
| Accionamiento | motor 300–400 W, reductor 15:1, husillo de bolas SFU1605, balancín y biela |

### Cuánto carga el brazo

| Situación | Mano | Dedos | Cuna (antebrazo) | Muñeca |
|---|---|---|---|---|
| En el aire, **sin** apoyo | 3,7 kg | — | — | ≈ 10,7 N·m: más de lo que una muñeca aguanta todo un día |
| En el aire, con la cuna | 7,1 kg | 2,6 kg | 4,0 kg | ≈ 2,7 N·m |
| En el aire, con la cuna y la correa de hombro | 4,7 kg en el tope del mango | 0 kg | 2,4 kg | ≈ 2,1 N·m |
| Cortando, con el patín apoyado | 1,7 kg | — | — | ≈ 0,4 N·m |
| Caminando, colgada de la correa | solo guía | 0 kg | — | ≈ 0 |

"En el aire" es cuando se lleva la herramienta de una caña a la otra, con el tubo a 45°. La cuna solo puede empujar de costado al antebrazo. Lo que la herramienta tira hacia la punta (2,6 kg) lo aguantan los dedos, salvo que lo tome la correa. En la postura de corte, la correa queda casi en línea con el tubo y toma justo esa parte (unos 2,9 kg de tensión). Las cifras salen del modelo (`fuente/exportar_3d.py`, función `balance`) y cambian con la postura de cada operario.

La herramienta pesa bastante más que un machete. Por eso lleva cuatro cosas:
- La cuna, que se lleva el momento del cabezal.
- El patín, que apoya el cabezal en la tierra mientras corta.
- La anilla (P16) justo sobre el centro de gravedad, donde se engancha la correa de hombro C08. Es un arnés simple de rozadora, cruzado al hombro izquierdo. Colgada de la anilla, la herramienta queda horizontal.
- El tope del mango, donde la mano levanta la herramienta sin usar los dedos.

## Mango ergonómico

Para que la mano no se canse en una jornada de cientos de cortes:
- **Gatillo de cuatro dedos (P12):** es largo, como el acelerador de una rozadora. Índice, medio, anular y meñique reparten el esfuerzo, con unos 3 N por dedo (10–12 N en total) y 10 mm de recorrido. Tiene cuatro hendiduras para ubicar los dedos.
- **Tope arriba atrás (P11):** ahí apoya el arco entre pulgar e índice. Por ahí se levanta la herramienta, así los dedos no tienen que levantarla y no aprietan el gatillo sin querer.
- **Palanca de pulgar arriba (P18, opcional):** trabaja en paralelo con el gatillo. Sirve para alternar dedos y pulgar y descansar la mano.
- **Sensor de presencia en lugar de la palanca de palma:** basta con tener la mano puesta en el mango.
- **Empuñadura (P11):** sección de 44 x 32 mm (equivale a Ø38), inclinada para que la muñeca quede recta con el antebrazo en la cuna. Tiene tope inferior.
- **Guardamonte amplio:** entre 26 y 48 mm de luz, para que entren los dedos con guante. Evita que las hojas o ramas accionen el gatillo.

### ¿Por qué no el mango arriba, como en la rozadora?

En la rozadora la mano va arriba y los dedos aprietan el gatillo por debajo. Eso funciona porque **el arnés carga todo el peso**: la mano solo guía y los dedos solo aceleran. En esta tijera, para llevarla de una caña a otra, la mano tiene que levantar el cabezal:

| | Mango arriba (como la rozadora) | Pistola con gatillo de 4 dedos (este diseño) |
|---|---|---|
| Quién levanta la herramienta en el aire | los dedos que están sobre el gatillo: unos 7 kg, o 4,7 kg con la correa | el arco entre pulgar e índice, en el tope del mango |
| Peso sobre el gatillo en el aire, con la correa | 4,7 kg: la cuchilla se cerraría sola al mover la herramienta | 0 kg |
| Postura de la mano con el antebrazo en la cuna | palma hacia abajo (antebrazo girado) o muñeca doblada | como al dar la mano: la postura más fuerte y que menos cansa |
| Movimiento de los dedos para cortar | cerrar los 4 dedos | cerrar los 4 dedos (igual) |

De la rozadora se toman el gatillo largo de cuatro dedos y la correa de hombro. La pistola se queda porque separa las dos tareas: el tope del mango levanta y los dedos solo cortan.

**Lo que hay que probar:** sin la correa, en el aire los dedos aguantan 2,6 kg sobre el gatillo y podrían cerrarlo sin querer. Hay dos maneras de evitarlo: usar siempre la correa, o subir el resorte del gatillo a unos 30 N. Esto también le pasaba al gatillo de tres dedos de la versión anterior.

## Seguridad

- **Mano en el mango:** la cuchilla solo cierra si el sensor detecta la mano en la empuñadura y se aprieta el gatillo o la palanca de pulgar.
- **Correa puesta:** con la correa, el peso no carga sobre el gatillo cuando se lleva la herramienta en el aire (ver "Cuánto carga el brazo").
- **Correa con liberación rápida:** el mosquetón de la anilla se suelta con una mano.
- **Freno eléctrico:** al soltar el gatillo, la cuchilla se detiene y vuelve a abrir.
- **Cuna abierta arriba con hebilla de liberación rápida:** si el operario resbala en la ladera, el brazo sale de un tirón.
- **Regla de trabajo:** la mano que sostiene la caña siempre a unos 40 cm o más por encima del corte, y usar botas o canilleras.

## Contenido

| Carpeta / archivo | Qué es | Con qué se abre |
|---|---|---|
| `imagenes/` | Vistas 3D: armada, cabezal cerrado y abierto, planta, corte parcial, mango, lateral con medidas, despiece, en la mata | Cualquier visor de imágenes |
| `planos_cortadora.pdf` | Los 19 planos en un PDF a escala | Cualquier lector de PDF |
| `planos_dxf/` | Un DXF por pieza (P01…P18) y el conjunto `00` con la lista de materiales (incluye los comerciales C01…C08) | AutoCAD (Guardar como → DWG), DraftSight, LibreCAD, QCAD |
| `modelo_3d/tijera_conjunto.step` y `piezas_step/` | Modelo 3D del conjunto y de cada pieza | FreeCAD, Fusion 360, SolidWorks |
| `modelo_3d/tijera.glb` | Modelo 3D liviano con colores | Visor 3D de Windows, Blender |
| `visor/` | Visor 3D interactivo (HTML) | Navegador, servido por HTTP |
| `fuente/` | Modelo paramétrico y generadores de planos | Python 3 |

En los DXF, la geometría está a escala real 1:1. El contorno de las piezas de chapa (P01, P02, P03, P04, P06, P07, P17) va directo a corte láser, plasma o chorro de agua; solo hay que borrar las capas `COTAS`, `TEXTO`, `EJES` y `MARCO`.

## Siguiente paso

1. Medir la fuerza de corte en las cañas de 6 cm, con una gata hidráulica y una celda de carga. El diseño supone entre 3 y 3,5 kN.
2. Primero armar el cabezal (P01 a P07) y la cuna, y probar el corte y la postura en la mata, aunque el accionamiento sea provisional.
3. Imprimir en 3D el mango P11 con el gatillo P12 y probarlo con guantes, con y sin la correa de hombro. Comprobar que al levantar la herramienta los dedos no aprietan el gatillo.
4. Con los datos reales, ajustar `fuente/modelo.py` y regenerar todo.

## Regenerar todo

```bash
pip install build123d ezdxf matplotlib
cd fuente
python3 generar_todo.py
```
