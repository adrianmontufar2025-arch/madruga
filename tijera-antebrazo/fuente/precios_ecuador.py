"""Precios de referencia y proveedores en Ecuador para el prototipo (consulta web del 12-oct-2026).

Casi ningún proveedor ecuatoriano publica precios: la mayoría de las filas son rangos estimados o precios de
importación. Cada fila dice su confianza y de dónde sale el dato. Los precios se tomaron de los resúmenes del
buscador (no se pudieron abrir las páginas), así que hay que confirmarlos al cotizar.

Confianza: "alta" = precio publicado en una tienda de Ecuador; "media" = precio de importación, de otro país o de
otra presentación; "baja" = estimado (la nota explica cómo).
"""

FECHA_CONSULTA = "12-oct-2026"

GRUPOS = [
    "A. Materia prima",
    "B. Talleres y servicios",
    "C. Motor, batería y electrónica",
    "D. Piezas comerciales y accesorios",
    "E. Opcionales y alternativas (no suman al total)",
]

# (grupo, códigos, qué comprar, medida/cantidad, proveedor, ciudad, cant., mín. USD, máx. USD, confianza, fuente, nota)
LINEAS = [
    # --- A. Materia prima
    ("A", "P02", "Acero D2 (Böhler K110)", "1 trozo 140 x 110 x 6 mm (≈0,7 kg)",
     "voestalpine High Performance Metals del Ecuador (ex Aceros Böhler)", "Quito", 1, 10, 45, "baja",
     "https://voestalpine.com/highperformancemetals/ecuador/es/",
     "Precio a cotizar. Rango: 0,7 kg x 15-64 USD/kg (64 USD/kg es D2 importado de EE. UU., Maker Material "
     "Supply). Se compra de 6 mm y se rectifica a 5 mm."),
    ("A", "P01", "Acero O1 (Böhler K460) o acero de resorte", "1 trozo 180 x 70 x 8 mm (≈0,8 kg)",
     "voestalpine HPM Ecuador (Böhler)", "Quito", 1, 6, 25, "baja",
     "https://voestalpine.com/highperformancemetals/ecuador/es/bohler/tabla-de-colores-bohler-digital_compressed",
     "K460 figura en el catálogo Böhler de Ecuador. No se encontró 65Mn ni SK5 de 8 mm en Ecuador. Alternativa "
     "barata: hoja de ballesta usada (SAE 5160)."),
    ("A", "P06, P07", "Acero SAE 4140 bonificado (Böhler V320) + platina 16 x 6", "trozo 90 x 55 x 8 mm + 150 mm de platina",
     "voestalpine HPM Ecuador / Dipac (eje bonificado 705) / Importaceros (platina)", "Quito / Manta", 1, 3, 15,
     "baja", "https://dipacmanta.com/ejes-dipac-2/",
     "Platina publicada solo en A36 (no se templa): para la biela sirve A36 o 1045. Se factura por peso con "
     "mínimo de corte."),
    ("A", "P03", "Aluminio 7075-T6, placa de 8 mm", "1 trozo 170 x 130 mm (≈0,5 kg)",
     "Dismetal / Importaceros (pedir 7075 o 6061)", "Quito", 1, 5, 25, "baja",
     "https://dismetal.ec/productos/planchas/aluminio-liso",
     "En la web solo publican AA1100: pedir 7075-T6. Si no hay, 6061-T6 (menos resistente; vigilarlo en el "
     "ensayo). Referencia de importación: OnlineMetals."),
    ("A", "P05", "Aluminio 6061-T6, bloque para mecanizar", "1 bloque 160 x 90 x 55 mm (≈2,1 kg)",
     "Dismetal / Importaceros / el mismo taller CNC", "Quito", 1, 21, 54, "baja", "https://www.importaceros.com/",
     "Estimado: 2,1 kg x 10-25 USD/kg para cortes pequeños."),
    ("A", "P13", "Aluminio 5052-H32, chapa de 6 mm", "1 trozo 150 x 80 mm", "Dismetal / Importaceros", "Quito", 1, 2, 8,
     "baja", "https://dismetal.ec/productos/planchas/aluminio-liso",
     "No usar 6061-T6: se agrieta al plegar 6 mm. Radio interior del pliegue ≥ 9 mm."),
    ("A", "P08, P09, P19", "Tubos de aluminio Ø30 x 2 (0,5 m), Ø10 x 1,5 (0,6 m), Ø12 x 1 (0,7 m)", "3 tramos",
     "Mercado Libre Ecuador / Cedal (Latacunga, sin verificar)", "Nacional / Latacunga", 1, 10, 50, "media",
     "https://listado.mercadolibre.com.ec/tubo-redondo-de-aluminio",
     "Tubo 6061 Ø4-10 a 4,19 USD; pértiga agrícola de aluminio a 40 USD (medidas sin confirmar). Cedal es "
     "extrusora en Latacunga: vale la pena llamar."),
    ("A", "P04", "Lámina UHMW-PE de 3 mm", "1 trozo 210 x 130 mm (o lámina de 305 x 305)",
     "Sutin - Suministros Técnicos Industriales, tel. (04) 2881484", "Guayaquil", 1, 5, 16, "media",
     "https://www.sutin.ec/productos/plasticos-de-ingenieria",
     "Sutin cotiza UHMW. Referencia de importación: lámina de 1/8 x 12 x 12 pulgadas a 15,95 USD (Zoro)."),
    ("A", "P17", "Acero inoxidable 17-4PH (Böhler N700) o 420 templable", "1 trozo 70 x 40 x 6 mm",
     "voestalpine HPM Ecuador (Böhler)", "Quito", 1, 3, 15, "baja",
     "https://voestalpine.com/highperformancemetals/ecuador/es/",
     "Stock no confirmado. El inoxidable 304 de ferretería no se endurece: alternativa SAE 4140 pavonado."),
    ("A", "P15", "Goma EVA de 5 mm + correa de velcro con hebilla", "1 pliego + 1 m de correa",
     "Mercado Libre Ecuador (mayorista de goma EVA en Quito) / Kywi (velcro)", "Quito / nacional", 1, 3, 10, "baja",
     "https://listado.mercadolibre.com.ec/goma-eva", "Sin precio publicado para 5 mm; estimado."),

    # --- B. Talleres y servicios
    ("B", "P01, P02, P03, P06, P13, P17", "Corte láser de fibra desde los DXF",
     "≈1,7 m en acero de 5-8 mm y ≈1,8 m en aluminio de 6-8 mm",
     "Prosoldes (1-16 mm) / Stands Creativa / Prosergraf / R3lab", "Guayaquil / Quito / Cuenca", 1, 30, 70, "baja",
     "https://prosoldes.com/servicios/corte-por-laser-de-fibra-optica-oxi-y-plasma/",
     "Ningún taller publica tarifa. Estimado con 4-12 USD/m (referencia internacional) más un mínimo. Para "
     "aluminio de 8 mm se necesita láser de 3 kW o más; preguntar. Láser Metal Quito corta acero solo hasta 6 mm."),
    ("B", "P04", "Corte del patín de UHMW", "1 pieza", "Router CNC o a mano con plantilla impresa", "—", 1, 0, 15,
     "baja", "", "El láser de fibra no corta bien el UHMW (se funde). Se puede cortar con caladora y la plantilla 1:1."),
    ("B", "P05", "Fresado CNC de la torre del cabezal", "3-6 h de máquina",
     "Lathe Center (atiende en Latacunga y Machachi)", "Quito / Latacunga", 1, 80, 250, "baja",
     "https://lathecenter.com/",
     "Estimado: CNC 25-45 USD/h; fresa convencional 10-20 USD/h. El bloque de aluminio va en la fila de materia prima."),
    ("B", "C04, P07, P08, P09, C06", "Torno y taller: horquilla de tiro, extremos de tubo y varilla, escariado, pasadores",
     "≈2-3 h", "Taller de torno local", "Latacunga / Quevedo", 1, 20, 60, "baja", "",
     "Estimado con 10-20 USD/h de torno convencional."),
    ("B", "P01, P02, P17", "Temple y revenido", "1 lote ≈0,7 kg (D2, O1, 17-4PH)",
     "voestalpine HPM Ecuador (tratamiento térmico propio)", "Quito / Guayaquil", 1, 20, 50, "baja",
     "https://www.voestalpine.com/highperformancemetals/ecuador/es/tratamiento-termico/",
     "Precio a cotizar; en lotes pequeños manda el mínimo. El D2 se templa a 1.010-1.040 °C: pedir 56-58 HRC. "
     "P06 se compra ya bonificado (V320)."),
    ("B", "P02, P01", "Afilado de la cuchilla y rectificado del borde del gancho", "2 piezas",
     "ACEIN / Aceros (Cuchillas Industriales) / Import Sierra", "Quito / Guayaquil", 2, 5, 20, "baja",
     "https://acein.com.ec/servicios/afilado-rectificado/", "Precio a cotizar."),
    ("B", "P13", "Plegado de la chapa de 6 mm", "1 pliegue", "Taller de plegado (no se encontró con nombre)", "—", 1,
     10, 25, "baja", "", "Estimado. Usar 5052-H32 y radio interior ≥ 9 mm."),
    ("B", "P10, P11, P12, P14, P16, P18, P19", "Impresión 3D de las piezas plásticas", "≈450 g en PETG o nylon",
     "Prodemaq / Maker Group (Quito); R3lab, Plastigram (Cuenca)", "Quito / Cuenca", 1, 45, 113, "alta",
     "https://prodemaq.com/servicios/",
     "Prodemaq publica 0,10-0,25 USD/g (página de ~2023). Pedir PETG o nylon: el PLA se ablanda al sol."),

    # --- C. Motor, batería y electrónica
    ("C", "C01, C02", "Motor sin escobillas 36 V ~400 W con reductor planetario ~15:1 (57 mm)", "1 conjunto",
     "Importación (AliExpress / Frankhumotor / made-in-china)", "Importación", 1, 90, 170, "media",
     "https://www.aliexpress.com/w/wholesale-brushless-dc-planetary-gear-motor.html",
     "No se encontró en Ecuador. Verificar ≥ 300 W y ≥ 13 N·m a la salida del reductor: muchos motores de 57 mm "
     "son de 46-140 W."),
    ("C", "C01", "Controlador BLDC 36 V con sensores Hall y freno", "1",
     "Mercado Libre Ecuador (controladores de bicicleta eléctrica)", "Nacional", 1, 15, 50, "media",
     "https://listado.mercadolibre.com.ec/bicicletas-ciclismo/motor-ebike",
     "Controlador de bicicleta 36/48 V 350 W ≈ 40 USD en Mercado Libre; importado ≈ 15-20 USD."),
    ("C", "C03, C04", "Kit de husillo de bolas SFU1605 de 300 mm con tuerca, soportes BK12/BF12 y acople", "1 kit",
     "AliExpress (importación) o Mercado Libre Ecuador", "Importación / nacional", 1, 31, 108, "media",
     "https://www.aliexpress.us/item/3256804643265503.html",
     "31-35 USD importado; 108 USD en Mercado Libre Ecuador (sin datos de largo ni soportes)."),
    ("C", "C05", "Batería de litio 36 V 10S (tipo hoverboard, ≈4 Ah) + cargador de 36 V", "1 + 1",
     "Mercado Libre Ecuador", "Nacional", 1, 125, 160, "media",
     "https://listado.mercadolibre.com.ec/bateria-de-litio-36v",
     "Batería ≈ 70 USD y cargador ≈ 55 USD. Revisar que su BMS dé 15 A o más. Opción más barata para el "
     "prototipo; ver alternativas Makita abajo."),
    ("C", "—", "Electrónica: Arduino Nano, sensor Hall, sensor táctil TTP223, conectores XT60, cable espiral, cables",
     "1 juego", "Mercado Libre Ecuador / Steren", "Nacional", 1, 15, 40, "media",
     "https://listado.mercadolibre.com.ec/arduino-nano-v3",
     "Nano 5,70-14 USD; Hall ≈ 1,25; TTP223 1,20-2,50; XT60 1,60-2,50 el par. Cable espiral no encontrado en "
     "Ecuador: estimado."),
    ("C", "—", "Importación por courier (categoría B o 4x4)", "1 envío consolidado", "Courier autorizado por el SENAE",
     "—", 1, 35, 70, "baja",
     "https://www.aduana.gob.ec/gaceta-boletin/nueva-tarifa-para-envios-por-categoria-b-bajo-el-regimen-de-mensajeria-acelerada-o-courier/",
     "Arancel fijo de 20 USD por envío (desde el 16-06-2025), hasta 4 kg y 400 USD FOB. Más el flete del courier "
     "(no investigado). No traer baterías de litio por courier."),

    # --- D. Piezas comerciales y accesorios
    ("D", "C06", "Perno con hombro ISO 7379 Ø12 x 25, rosca M10, clase 12.9", "1",
     "Tornearlo en 4140 en el taller, o importar (ASMC)", "Taller local / importación", 1, 5, 60, "media",
     "https://www.asmc.net/m12-x-m10-x-25-mm-coarse-thread-iso-7379-class-12-9-socket-shoulder-screw-alloy-steel-black-oxide/",
     "No se encontró en Ecuador. ASMC: 2,41 USD c/u con compra mínima de 25 (≈60 USD). Ojo: el hombro de Ø12 "
     "lleva rosca M10."),
    ("D", "C06", "Arandelas Belleville DIN 2093 12,2 x 25", "2", "123Bearing (importación)", "Importación", 2, 1.1, 2.7,
     "media", "https://www.123bearing.com/accessories/washer/spring-disc-din2093/s4287",
     "No se encontraron en Ecuador; confirmar si el precio es por unidad."),
    ("D", "C07", "Resorte de torsión (0,3 N·m) y pasador Ø6", "1 + 1",
     "Taller de resortes (cotizar) o kit importado (eBay)", "Ambato / Quito / importación", 1, 5, 20, "media",
     "https://www.ebay.de/itm/157333044301",
     "Kit de 80 resortes a 20,46 USD, pero pueden ser finos: hace falta alambre de 1,5-2 mm."),
    ("D", "—", "Tornillería: M6 avellanados inoxidables, M6 x 20, tuercas y arandelas", "1 juego",
     "Kywi (pernos DISMAC) / Mercado Libre Ecuador", "Quito y sucursales", 1, 8, 20, "alta",
     "https://www.kywi.com.ec/perno-c-cilindrica-metrico-m6x20-2u-/p",
     "M6 x 20 (2 u) a 0,62 USD; avellanados inoxidables ≈ 0,30-0,60 USD c/u (estimado)."),
    ("D", "C08", "Arnés de hombro para motoguadaña", "1", "Mercado Libre Ecuador", "Nacional", 1, 42.29, 48, "alta",
     "https://listado.mercadolibre.com.ec/agro/arnes-para-motoguadana",
     "Pueden ser arneses acolchados o dobles; basta uno simple de una correa."),
    ("D", "P16, C08", "Mosquetón de acero 5/16\" (230 kg) + argolla de 20 mm", "1 + 1", "Kywi (FIERO)",
     "Quito y sucursales", 1, 2.7, 5, "alta",
     "https://www.kywi.com.ec/mosqueton-de-enlace-rapido-de-5-16-x-3-8-x-3-pulgadas-con-capacidad-de-carga-maxima-de-230-kg/p",
     "Mosquetón 1,22 USD. Argolla inoxidable estimada en 1,5-3 USD."),
    ("D", "C09", "Cable de freno de bicicleta con funda + palanca pequeña", "1 + 1",
     "Tienda de bicicletas local / Mercado Libre Ecuador", "Latacunga / Ambato", 1, 7, 28, "baja",
     "https://listado.mercadolibre.com.ec/bicicletas-ciclismo/cable-de-freno-bicicleta",
     "Estimado: cable 2-5 USD y palanca 5-12 USD (una palanca de ruta cuesta 23 USD en Mercado Libre)."),
    ("D", "P19", "Puntas de acero para tubo de 12 mm (repuesto de bastón de trekking) + tacos de caucho", "1 par",
     "Importación (Mountainsmith / Amazon) o tornearlas en el taller", "Importación / taller local", 1, 6, 15, "media",
     "https://mountainsmith.com/products/carbine-tips",
     "Puntas de carburo a 5,95 USD el par. Los regatones de bastón de Mercado Libre (5,75 USD el par) suelen ser "
     "de 19-22 mm: revisar el diámetro."),

    # --- E. Opcionales y alternativas (no suman al total)
    ("E", "P08", "Tubo de fibra de carbono 30 x 26 x 500 mm (versión final)", "1", "Rees52 / carbonfibertubes.net",
     "Importación", 1, 18, 47, "media",
     "https://carbonfibertubes.net/products/od-30mm-x-id-20mm-25mm-26mm-27mm-28mm-x-500mm-100-roll-wrapped-carbon-fiber-tube-3k-tubing-twill-plain-glossy-matte-30-20-30-25-30-26-30-27-30-28",
     "El prototipo usa tubo de aluminio. No se encontró en Ecuador."),
    ("E", "P03, P05, P13", "Anodizado del aluminio", "1 lote", "Cotizar (FISA, Quito, sin confirmar)", "Quito", 1, 20,
     60, "baja", "", "No hace falta para el prototipo."),
    ("E", "C05", "Alternativa de batería: Makita XGT 40 V máx. (36 V) de 4 Ah", "1 (+ cargador XGT a cotizar)",
     "Pintulac", "Nacional", 1, 227.86, 227.86, "alta",
     "https://www.pintulac.com.ec/categorias/herramientas/herramientas-electricas/makita/baterias-y-cargadores-makita.html",
     "Batería de herramienta, más robusta. El cargador XGT no apareció con precio."),
    ("E", "C05", "Alternativa de batería: 2 Makita LXT 18 V 5 Ah en serie (36 V) + cargador DC18SD", "2 + 1",
     "Pintulac", "Nacional", 1, 361, 370, "alta", "https://www.pintulac.com.ec/bateria-lxt-litio-5ah-18v-makita.html",
     "147,48-151,90 USD cada batería y 65,79 USD el cargador. Falta el adaptador doble a cable (importado, sin precio)."),
    ("E", "P10, P11, P12, P14, P16, P18", "Filamento, si se imprime en casa: PETG (SKP3D) o nylon (Creality)", "1 kg",
     "SKP3D / Cmprodemaq (Mercado Libre)", "Quito / nacional", 1, 26.7, 44.8, "alta",
     "https://skp3d.com/product-category/consumibles/filamentos/",
     "Reemplaza la impresión por servicio. El PLA-CF de Novatronic (Riobamba, 30 USD) es PLA: se ablanda al sol."),
]

PROVEEDORES = [
    ("voestalpine High Performance Metals del Ecuador (ex Aceros Böhler)", "Quito y Guayaquil",
     "Aceros de herramienta Böhler (D2 = K110, O1 = K460, 4140 = V320, 17-4PH = N700) y tratamiento térmico propio",
     "https://voestalpine.com/highperformancemetals/ecuador/es/"),
    ("Dipac", "Manta (envío nacional)", "Platinas A36, eje 1018, eje bonificado 4340/705, inoxidable; corte a medida",
     "https://dipacmanta.com"),
    ("Importaceros", "Quito", "Platinas, planchas de aluminio, inoxidable y tubería", "https://www.importaceros.com"),
    ("Dismetal", "Quito", "Planchas de aluminio y platinas", "https://dismetal.ec"),
    ("Cedal", "Latacunga", "Extrusora de aluminio: posible tubo Ø30 y Ø12 (no verificado)", "—"),
    ("Sutin - Suministros Técnicos Industriales", "Guayaquil, tel. (04) 2881484",
     "Plásticos de ingeniería: UHMW, nylon, PTFE, acetal", "https://www.sutin.ec"),
    ("Prosoldes", "Guayaquil (por verificar)", "Corte láser de fibra de 1 a 16 mm, oxicorte y plasma", "https://prosoldes.com"),
    ("Stands Creativa", "Quito (envía a todo el país)", "Corte láser y plasma de acero, inoxidable y aluminio",
     "https://standscreativa.com"),
    ("Prosergraf", "Guayaquil", "Corte láser", "http://prosergraf.com"),
    ("Láser Metal Quito (Metalmachine)", "Quito", "Corte láser de acero hasta 6 mm", "https://lasermetalquito.com.ec"),
    ("R3lab", "Cuenca (envía a Ambato)", "Corte láser de fibra e impresión 3D", "https://r3labecuador.com"),
    ("Lathe Center", "Quito; atiende en Latacunga y Machachi", "Torno y fresado CNC", "https://lathecenter.com"),
    ("ACEIN", "Quito y Guayaquil", "Afilado y rectificado industrial", "https://acein.com.ec"),
    ("Aceros (Cuchillas Industriales Ecuador)", "Quito", "Fabricación y afilado de cuchillas", "https://aceros.ec"),
    ("Import Sierra", "Quito", "Afilado de cuchillas y sierras", "https://importsierra.com"),
    ("Prodemaq", "Quito", "Impresión 3D (0,10-0,25 USD/g)", "https://prodemaq.com"),
    ("Maker Group", "Quito", "Diseño e impresión 3D", "https://www.makergroupecuador.com"),
    ("SKP3D", "Quito", "Filamentos e impresoras 3D", "https://skp3d.com"),
    ("Novatronic", "Riobamba", "Electrónica y filamentos 3D", "https://novatronicec.com"),
    ("Pintulac", "Nacional (en línea)", "Baterías y cargadores Makita", "https://www.pintulac.com.ec"),
    ("DeWalt Ecuador / Promart", "Nacional (en línea)", "Baterías DeWalt (las FlexVolt son de 54 V: no sirven con un "
     "controlador de 36 V)", "https://dewalt.ec"),
    ("Kywi", "Quito y sucursales", "Tornillería DISMAC, mosquetones, velcro, regatones", "https://www.kywi.com.ec"),
    ("Steren Ecuador", "Nacional", "Electrónica (placa Nano)", "https://www.steren.com.ec"),
    ("Mercado Libre Ecuador", "Envío nacional", "Arneses, husillos, controladores, baterías 36 V, electrónica, tubos",
     "https://www.mercadolibre.com.ec"),
]

IMPORTACION = [
    "Régimen courier categoría B (4x4): hasta 4 kg y hasta 400 USD FOB por paquete, para uso personal.",
    "Cupo anual de 1.600 USD FOB por persona (Resolución COMEX 008-2022). Consulta: https://www.aduana.gob.ec/consultacupos/",
    "Arancel fijo de 20 USD desde el 16-06-2025 (Resolución COMEX 006-2025), más FODINFA de 0,5 %. Consolidar las "
    "compras en un solo envío para pagarlo una vez.",
    "Si se pasa de 4 kg o de 400 USD, el envío pasa a categoría C: arancel según la partida, FODINFA e IVA del 15 %.",
    "Las baterías de litio suelen estar restringidas por los couriers: comprarlas en Ecuador.",
    "Hay una resolución del SENAE de mayo de 2026 (SENAE-SENAE-2026-0041-RE) que no se pudo leer: revisar si cambia algo.",
    "Fuente: https://www.aduana.gob.ec/regimen-courier-4x4-tendra-arancel-fijo-para-garantizar-su-correcto-uso-y-proteger-la-produccion-nacional/",
]
