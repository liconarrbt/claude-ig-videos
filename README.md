# Curiosart · videos de divulgación con Claude

Herramientas para producir los videos verticales del canal **Curiosart**: explicaciones de 2 a 3 minutos
sobre datos curiosos, con animación dibujada a mano, voz de IA, efectos y música. Claude escribe el
guion, genera la voz, dibuja y anima, mezcla el audio y arma el video final usando las apps de
**ArtCraft** por línea de comandos y **Fish Audio** para la narración.

```
idea → guion verificado → voz (Fish Audio) → alineado por palabra → animación → efectos y música → mezcla → MP4 + miniatura
```

## Estructura

```
.
├── README.md                    este archivo
├── .env                         clave de Fish Audio (no se sube; ver «Configuración»)
├── kit-shorts-vectoriales/      el kit: scripts, skills de Claude e instalador → ver su README
├── canal/                       identidad visual: avatar, banner e ilustraciones de marca
└── proyectos/                   un proyecto por video (su contenido no se sube al repositorio)
```

## Requisitos

- macOS, Python 3.10+, Node.js, Google Chrome y `ffmpeg` (`brew install ffmpeg`).
- Las CLIs de ArtCraft (VectorCraft, EffectCraft, FilmCraft, PhotoCraft y SoundCraft). El instalador
  del kit las descarga y verifica: `kit-shorts-vectoriales/instalar.sh --descargar`.
- Una cuenta de [Fish Audio](https://fish.audio) con su API key (basta el modelo gratuito).
- [Claude Code](https://claude.com/claude-code) para usar las skills.

Los detalles de versiones e instalación están en [`kit-shorts-vectoriales/README.md`](kit-shorts-vectoriales/README.md).

## Configuración

Crea un archivo `.env` en la raíz con tu clave de Fish Audio:

```bash
FISHAUDIO_API_KEY=tu_clave
```

El `.env` está en `.gitignore` y nunca se sube. El script de voz lo busca desde la carpeta del proyecto
hacia arriba. Si no lo encuentra, usa la variable de entorno o `~/.zshrc`.

La animación dibujada a mano necesita además `puppeteer-core`:

```bash
cd kit-shorts-vectoriales/skills/hand-drawn-canvas-animation/scripts && npm install
```

## Cómo hacer un video

**Con Claude (recomendado):** abre Claude Code en esta carpeta y pídelo en lenguaje natural, por ejemplo
«haz un video de por qué el cielo es azul». Claude escribe el guion, lo produce y revisa cuadros
clave antes de entregar.

**A mano:**

```bash
S=kit-shorts-vectoriales/skills/shorts-vectoriales/scripts
python3 $S/nuevo_proyecto.py proyectos/17-abejas "Por qué las abejas hacen hexágonos"
# edita proyectos/17-abejas/escenas.json (narración, titulares y focos por escena)
python3 $S/producir.py proyectos/17-abejas                     # pipeline completo
python3 $S/producir.py proyectos/17-abejas --desde animacion   # rehacer desde un paso
```

Pasos de `producir.py`: `voz → alinear → dibujar → animacion → sfx → mezcla → miniatura`.

### Dos modos de animación

| Modo | Cuándo | Cómo se activa |
|---|---|---|
| **Película dibujada a mano** (preferido) | personajes, objetos y todo lo que se mueve | el proyecto tiene `pelicula/pelicula.html` con sus escenas en Canvas 2D (skill `hand-drawn-canvas-animation`); `producir.py` usa `pelicula.py` |
| **Vectores de EffectCraft** | gráficas, matemáticas y diagramas casi estáticos | ilustraciones SVG de `dibujar.py` animadas desde `escenas.json` |

En modo película, cada proyecto define `pelicula/personajes.js` (poses completas y dibujos a pincel) y
`pelicula/escenas.js` (una función por escena, sincronizada con las palabras de la voz). El puente
`kit-shorts-vectoriales/skills/shorts-vectoriales/scripts/pelicula/kit.js` aporta el fondo, los
titulares, los focos y el sistema de poses.

Para revisar antes del render final:

```bash
python3 $S/pelicula.py proyectos/17-abejas --grid 48        # hoja de 48 cuadros
python3 $S/pelicula.py proyectos/17-abejas --en 12.5,40     # cuadros en esos segundos
```

## Estilo del canal

- Duración de **2 a 3 minutos**, de 12 a 18 escenas, con datos verificados y fuentes en `escenas.json`.
- **Fondo negro** con retícula tenue, titulares gruesos y **una sola palabra en naranja**.
- **Sin subtítulos completos**: solo «focos», las palabras clave en el momento en que la voz las dice.
- **Nada estático**: todo respira, parpadea o se mueve mientras se habla.
- Dibujos que se reconozcan a primera vista, sin marcas, logotipos ni personajes con derechos de autor.
- Audio a −14 LUFS con pico de −1 dBTP o menos.

## Convenciones

- Las carpetas de `proyectos/` se numeran por orden de creación: `01-…`, `02-…`; un video nuevo toma el
  número siguiente.
- Cada proyecto guarda su `escenas.json`, la película, la voz, el audio, revisiones, la miniatura y el
  MP4 final. Ocupan mucho espacio y por eso no se suben a GitHub.

## Videos producidos

| # | Video | Duración |
|---|---|---|
| 01 | Por qué el tiempo va de 60 en 60 (piloto) | 0:46 |
| 02 | Prueba del kit (mismo tema) | 0:45 |
| 03 | RGB y CMYK: tres colores para engañar a tu ojo | 2:36 |
| 04 | Por qué los ritmos latinos te hacen moverte | 2:07 |
| 05 | Burro: el falso amigo que es mantequilla | 2:10 |
| 06 | Por qué no todos los mamíferos tienen pulgares | 2:20 |
| 07 | Cómo funciona la cancelación activa de ruido | 2:11 |
| 08 | Por qué las calabazas son de Halloween | 2:03 |
| 09 | Por qué dormimos y por qué los gatos duermen tanto | 2:15 |
| 10 | Por qué los videojuegos antiguos se veían mejor | 1:59 |
| 11 | Por qué usamos el teclado QWERTY | 2:02 |
| 12 | Qué es blockchain y cómo funciona | 2:07 |
| 13 | Cómo funciona SPEI del Banco de México | 2:03 |
| 14 | Por qué el alcohol te marea | 2:03 |
| 15 | Las mujeres causan más accidentes: ¿mito o dato? | 2:14 |
| 16 | Por qué el cielo es azul | 2:07 |

Del 01 al 05 se hicieron con vectores de EffectCraft; del 06 en adelante, con animación dibujada a mano.

## Limitaciones

- Claude no puede escuchar el audio: la mezcla se valida con medidas objetivas y conviene escuchar
  cada video antes de publicarlo.
- La alineación de la voz es local: precisa por frase, con unos ±0.2 s por palabra.
- El modelo gratuito de Fish Audio a veces responde «sin crédito» un rato; el script reintenta solo.

## Créditos

- Skill `hand-drawn-canvas-animation`: de [alesha-pro/tools](https://github.com/alesha-pro/tools), licencia MIT
  (origen y versión en `kit-shorts-vectoriales/skills/hand-drawn-canvas-animation/ORIGEN.md`).
- Secuencias de galope de Eadweard Muybridge (*Descriptive Zoopraxography*, 1893), dominio público.
- Voz: [Fish Audio](https://fish.audio). Apps de producción: ArtCraft (Learning Machines LLC).
