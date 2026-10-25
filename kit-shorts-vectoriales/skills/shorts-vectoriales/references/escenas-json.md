# escenas.json — especificación de un short

Ejemplos completos y probados: `../../ejemplos/sexagesimal/escenas.json` (corto, 7 escenas, 45 s) y
`../../ejemplos/rgb-cmy/escenas.json` (formato largo, 15 escenas, 2:28: modos de fusión, fondos claros, tarjetas).

```jsonc
{
  "titulo": "Por qué el tiempo va de 60 en 60",       // también da nombre al .mp4 final
  "voz": {"id": "d047b6a8f24f4d56ba818b08dbd9d089", "velocidad": 1.1},
  "subtitulos": true,                                  // palabra por palabra (por defecto true)
  "estilo": {"tema": "libreta", "acento": "#FF6A1A"},  // tema (ver abajo) + ajustes sueltos de comun.ESTILO
  "vida": {"onda": 2.5, "deriva": 3},                 // micro-animación por defecto de todas las capas (ver abajo)
  "max_quieto": 3.0,                                   // s máximos sin un cambio nuevo antes de insertar pulsos
  "mezcla": {"musica_db": -13, "whoosh_db": -14, "pops_db": -9, "tictac_db": -16, "objetivo_lufs": -14},
  "escenas": [ /* ver abajo */ ],
  "miniatura": {"texto": "¿POR QUÉ 60\nY NO 100?", "acento": "60",
                "ilustraciones": ["reloj", {"svg": "luz_r", "pos": [430, 1230], "modo": "Screen"}], "centro": [540, 1250], "tam": 200},
  "fuentes": ["notas de verificación de datos (no se usan al renderizar)"]
}
```

## Escena

```jsonc
{
  "narracion": "Texto que lee la voz (una escena = un párrafo, 1–4 frases).",
  "titulares": [                        // arriba (y=340). Varios = se reemplazan en secuencia
    {"texto": "12 + 12 HORAS", "acento": "12 + 12", "tam": 130, "color_acento": "#FFE500"},
    {"texto": "MINUTO = PARTE DIMINUTA", "acento": "PARTE DIMINUTA", "desde": "astrónomos"}
  ],
  "capas": [                            // ilustraciones (SVG de ilustraciones/), de abajo hacia arriba
    {"svg": "reloj",                    // nombre del archivo sin .svg
     "desde": null,                     // cuándo entra (ver "desde")
     "dibujo": 1.2,                     // segundos que tarda en trazarse (0 = aparece completa)
     "empuje": 0.05,                    // zoom lento: 0.05 = crece 5 % durante la escena
     "escala": 100, "pos": [540, 1130], // % y centro en el cuadro
     "rotacion": 140,                   // grados/segundo (manecillas, engranes…)
     "opacidad": 22,                    // máximo % (para fondos atenuados)
     "golpe": true,                     // efecto: pop grave al entrar
     "tictac": true,                    // efecto: tic-tac de reloj hasta el fin de la escena
     "modo": "add",                     // fusión: add (mezcla de luz) | multiply (tinta) | screen…
     "entrada": "pop",                  // crece con rebote al aparecer (suena pop)
     "desde_pos": [180, 900], "mov": 1.0,  // entra deslizándose desde ese punto en 1 s
     "hasta": "palabra",                // sale antes del fin de escena (también en textos y tarjetas)
     "onda": 2.5, "deriva": 3,          // vida: ondulación de líneas (px) y vaivén lento (px); 0 = quieto
     "temblor": 2.5,                    // vibración rápida (px): máquinas, insectos, "alerta"
     "temblor_en": ["cualquier", {"palabra": "cualquier", "t": 1.5}],  // ventana del temblor
     "semilla": 77,                     // misma semilla en varias capas = se mueven juntas
     "pulsos": ["clave", "nunca"],      // golpes de escala extra al decir esas palabras
     "ritmo": {"bpm": 100,              // movimiento al tempo de la música (t=0 = primer tiempo):
               "tap": -12,              //   golpe de rotación por pulso (un pie que marca)
               "rebote": 8,             //   % de escala por pulso (altavoces, focos)
               "vaiven": 26,            //   péndulo (metrónomo): grados, 2 pulsos por ida y vuelta
               "vuelta": 8,             //   pulsos por giro completo (manecilla de un ciclo de clave)
               "destello": 0.3,         //   opacidad mínima entre pulsos (parpadeo)
               "cada": 2, "desfase": 0.5}}  //   cada cuántos pulsos y desplazamiento (en ciclos)
  ],
  "fondo": "#F2EFE6",                   // fondo propio de la escena; si es claro, títulos y subtítulos pasan a oscuro
                                        // (dibuja esas ilustraciones con línea oscura, no blanca)
  "tarjetas": [                         // tarjeta de cita (recuadro claro + barra de color, monoespaciada)
    {"titulo": "JAMES CLERK MAXWELL", "sub": "Escocia · 1861", "desde": "james", "pos": [540, 735], "color": "acento"}
  ],
  "textos": [                           // etiquetas secundarias (fecha, lugar, unidad); suenan con pop
    {"texto": "1793 · DÍAS DE 10 HORAS", "desde": "días", "y": 1680, "tam": 56,
     "color": "gris", "acento": "1793", "x": 540}   // color: gris | blanco | acento | #hex
  ],
  "anillo": {                           // números/etiquetas en círculo que se encienden al decirse
    "centro_texto": "60", "valores": [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60],
    "palabras": ["uno", "dos", "tres", "cuatro", "cinco", "seis", "diez", "doce", "quince", "veinte", "treinta", "sesenta"],
    "saltar": {"sesenta": 1},           // ignora la 1.ª vez que se dice "sesenta" en la escena
    "radio": 340, "tam": 62, "centro": [540, 1130]
  },
  "sfx": [{"tipo": "pop", "desde": "cien"}]   // efectos extra: whoosh | pop | pop_grave | tictac (+ "duracion")
}
```

## "desde": cuándo aparece algo

| Valor | Significado |
|---|---|
| ausente / `null` | al empezar la escena |
| `"palabra"` | cuando la voz dice esa palabra (1.ª aparición en la escena; ignora mayúsculas y puntuación) |
| `{"palabra": "doce", "n": 2}` | 2.ª aparición |
| `{"palabra": "doce", "t": 0.2}` | 0.2 s después de decirla |
| `{"t": 0.6}` | 0.6 s después del inicio de la escena |

Si la palabra no existe en la narración, el script se detiene y dice cuál falta: así se detectan
errores al editar el texto.

## Efectos automáticos (mezcla.py)

- whoosh en cada cambio de escena (pico en el corte)
- pop al aparecer cada `textos`, cada titular después del primero y cada valor del `anillo`
- pop grave en capas con `golpe`, tic-tac en capas con `tictac`

## Maquetación del cuadro 1080×1920

| Zona | y | Uso |
|---|---|---|
| Titular | 340 (1–3 líneas, 120 pt) | la idea de la escena |
| Subtítulos | 618 | palabra por palabra |
| Ilustración | 1130 ± 450 | el dibujo principal (lienzo 900×900) |
| Etiquetas | 1650–1730 | datos secundarios (cuidado: la UI de Shorts tapa y > 1530 a la izquierda) |

## Nada estático

Ninguna imagen debe quedarse quieta mientras la voz habla:
- Toda capa tiene vida por defecto: las líneas ondulan (Wiggle Paths), deriva lenta, respiración
  de escala y balanceo leve. Desactívalo por capa con `"onda": 0, "deriva": 0`.
- Si en una escena pasan más de `max_quieto` s sin que aparezca nada nuevo, animacion.py inserta
  pulsos de escala en las palabras largas (las acentuadas) cada ~2.2 s.
- Tras construir imprime "máximo sin cambio nuevo" por escena: si pasa de ~3 s, añade un
  elemento (texto, tarjeta, capa con `desde`) o `pulsos` en palabras clave.
- Usa `temblor` con `temblor_en` para momentos de acción (una impresora imprimiendo, un hilo que vibra).

## Música propia del proyecto

Si la carpeta del proyecto tiene `musica.py`, `producir.py` la ejecuta en el paso sfx (y el kit solo
sintetiza los efectos). Úsalo cuando la música es parte del tema: el ejemplo `ejemplos/ritmos-latinos`
sintetiza un groove latino a 100 BPM cuyo arreglo sigue a la narración (metrónomo solo, clave sola,
instrumentos que entran al nombrarse). Mantén el mismo `bpm` en los `ritmo` de las capas para que
la animación caiga con la música.

## Elementos que se ven muy poco

animacion.py avisa (⚠) de todo lo que estaría visible menos de 1.2 s: suele pasar al anclar algo a
las últimas palabras de una escena. Ánclalo a una palabra anterior.

## Temas

`"estilo": {"tema": "libreta"}` → hoja amarilla clara con renglones azules, margen rojo y perforaciones.
Cambia a la vez el fondo, la tinta (`W` en vc.py pasa a grafito), el relleno que tapa (`NEGRO` = color
del papel), los titulares y subtítulos (oscuros, contorno del color del papel) y la miniatura. Sin tema:
fondo negro con retícula. Los temas se definen en `comun.TEMAS`.
Sobre papel claro conviene dar color a los dibujos (base/sombra/luz por material; ver la skill
`arte-tecnico-vectorial`). Ejemplo: `ejemplos/falsos-amigos-burro`.

## Acabado de cámara

`"estilo": {"acabado": {...}}` (se mezcla clave a clave con el del tema):

| Clave | Qué hace | Por defecto / libreta |
|---|---|---|
| `sombra` | sombra suave bajo cada ilustración sin `modo` (Drop Shadow, opacidad %, luz arriba a la derecha) | `0` / `25` |
| `sombra_color` | color de esa sombra (cálido sobre papel) | `#000000` / `#7A5A2E` |
| `desenfoque` | desenfoque de movimiento (caro: multiplica el tiempo de render) | `false` |
| `grano`, `vineta` | grano de papel animado (Overlay, %) y viñeta (0–100). Muy caros de render y pesan el doble; el usuario prefirió no usarlos | `0` |

## Movimiento profesional (por defecto)

- **Entrada "asentar"** de toda ilustración: crece 86→~102→100 % con rebote (back-out) y se endereza desde −4°.
  `"entrada": "pop"` = desde 0 con más rebote; `"ninguna"` = solo trazo y fundido.
- **Salida** con ease-in a 90 % en los últimos 0.25 s (nada desaparece de golpe).
- **Respiración** estirar/aplastar (±1.2 % en x/y opuestos) y vaivén vertical de 4 px, además de onda y deriva.
- **Titulares palabra por palabra** con rebote (preset `bounceInWords` re-anclado a la entrada de la capa).
  Desactivar: `"titulares_por_palabra": false` en la raíz.

## Rigs: personajes con partes que se mueven

Separa en `dibujar.py` las partes móviles en SVG propios **sobre el mismo lienzo 900×900 y en sus
coordenadas originales** (no las recortes), y declara el rig una vez en la raíz de `escenas.json`;
se aplica a todas las capas que usen ese dibujo (o pon `"partes": [...]` en una capa concreta):

```json
"rigs": {
  "burro": [
    {"svg": "burro_cola",    "pivote": [205, 430], "detras": true, "balanceo": 9, "periodo": 1.6},
    {"svg": "burro_orejas",  "pivote": [640, 290], "detras": true, "balanceo": 2.5, "sacudida": 12, "cada": 2.9},
    {"svg": "burro_parpado", "pivote": [652, 322], "parpadeo": 3.4, "retraso": 0}
  ]
}
```

| Clave | Qué hace |
|---|---|
| `pivote` | punto de giro en coordenadas del lienzo del dibujo (la base de la oreja, el nacimiento de la cola) |
| `detras` | la parte va detrás del cuerpo (si no, delante) |
| `balanceo` + `periodo` | péndulo continuo (grados, segundos) |
| `sacudida` + `cada` | sacudida amortiguada cada N s (orejas, antenas); signo = sentido |
| `parpadeo` | segundos entre parpadeos: la parte (un párpado con el color de la piel) se ve 0.14 s |
| `retraso` | la parte entra (crece desde su pivote) después del cuerpo; por defecto 0.15 s + 0.08 por parte |
| `fase` | desfase para que dos partes iguales no se muevan al unísono |

Las partes son capas hijas (`layer.setParent`): heredan posición, escala y giro del cuerpo.
Ejemplo completo: `proyectos/05-falsos-amigos-burro` (burro: cola, orejas, párpado; vaca: dos orejas, párpados).
