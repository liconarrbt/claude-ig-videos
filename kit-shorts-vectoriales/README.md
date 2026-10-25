# Kit de shorts vectoriales

Produce videos verticales de divulgación con ilustraciones de línea que se dibujan solas, titulares
con una palabra en color de acento, subtítulos palabra por palabra, voz de IA, efectos y música —
todo con las apps de **ArtCraft** controladas por código y **Fish Audio** para la voz.

Ejemplo producido con el kit: `ejemplos/sexagesimal/` → "Por qué el tiempo va de 60 en 60" (45 s).

## Requisitos

| Requisito | Para qué | Cómo conseguirlo |
|---|---|---|
| macOS (probado en 15+/26) | las CLIs son binarios universales de macOS; `afinfo` mide audio | — |
| Python 3.10+ | los scripts del kit (solo biblioteca estándar) | `brew install python` |
| **VectorCraft CLI** 0.13.1 | dibujar ilustraciones → SVG | `./instalar.sh --descargar` |
| **EffectCraft CLI** 0.11.1 | animación, subtítulos, render | ″ |
| **FilmCraft CLI** 0.9.0 | montaje y exportación MP4 | ″ |
| **PhotoCraft CLI** 0.10.0 | miniatura y hojas de revisión | ″ |
| **SoundCraft CLI** 0.5.0 | mezcla, ducking, normalización LUFS | ″ |
| Cuenta de **Fish Audio** + API key | narración (el modelo gratuito `s2.1-pro-free` basta) | https://fish.audio → API keys; `FISHAUDIO_API_KEY=…` en un `.env` (en la raíz del repositorio; está en `.gitignore`) o `export` en `~/.zshrc` |
| Fuente Avenir Next Condensed | titulares (incluida en macOS) | o cambia `estilo.fuente` |
| Claude Code (app de escritorio o CLI) | usar las skills y los MCP | https://claude.com/claude-code |

Opcional: crédito de API en Fish Audio (modelos de voz de pago y transcripción con marcas de tiempo
reales); las apps de escritorio de ArtCraft para abrir y retocar a mano los archivos que genera el
kit (`.vectorcraft`, `.ecproj`, `.fcproj`, `.pcraft`, `.scraft`).

## Instalación

```bash
cd kit-shorts-vectoriales
chmod +x instalar.sh
./instalar.sh --descargar
```

El instalador: verifica requisitos, descarga las CLIs que falten desde GitHub (storytold/*) y
comprueba que estén firmadas y notarizadas por Learning Machines LLC, registra los cinco servidores
MCP en `~/.claude.json` (con copia de seguridad) e instala las skills como enlaces en
`~/.claude/skills/`. Después abre una sesión nueva de Claude.

## Uso con Claude (recomendado)

Pide en lenguaje natural, por ejemplo:

> Haz un short sobre por qué las abejas construyen hexágonos, con voz de narrador serio y acento amarillo.

La skill `shorts-vectoriales` guía el proceso: guion verificado → `escenas.json` → ilustraciones →
voz → animación → mezcla → miniatura, revisando cuadros clave en cada paso.

## Uso manual

```bash
S=kit-shorts-vectoriales/skills/shorts-vectoriales/scripts
python3 $S/nuevo_proyecto.py proyectos/abejas "Por qué las abejas hacen hexágonos"
# edita proyectos/abejas/escenas.json y proyectos/abejas/dibujar.py
python3 $S/producir.py proyectos/abejas            # todo el pipeline (~2 min)
python3 $S/producir.py proyectos/abejas --desde animacion   # rehacer desde un paso
```

## Contenido

```
kit-shorts-vectoriales/
├── README.md                     este archivo (requisitos e instalación)
├── instalar.sh                   instalador / verificador
├── ejemplos/sexagesimal/         escenas.json + dibujar.py de un short completo
└── skills/
    ├── shorts-vectoriales/       skill principal: pipeline completo
    │   ├── SKILL.md
    │   ├── references/           estilo, guion, escenas.json, ilustración, audio, ArtCraft, formato largo
    │   └── scripts/              comun · nuevo_proyecto · voz · alinear · vc · animacion · sfx · mezcla · miniatura · producir
    ├── guion-shorts-divulgacion/ ideas y guiones verificados → escenas.json
    ├── ilustracion-vectorcraft/  dibujo de línea con VectorCraft
    ├── mezcla-soundcraft/        mezcla y masterización con SoundCraft
    ├── arte-tecnico-vectorial/   criterios de arte: capas, paleta, 3D isométrico, easing, partículas
    └── hand-drawn-canvas-animation/  (terceros, MIT) cortos dibujados a mano en Canvas 2D
```

## Salidas de un proyecto

| Carpeta / archivo | Contenido |
|---|---|
| `<titulo>.mp4` | video final 1080×1920, 30 fps, −14 LUFS |
| `miniatura/` | miniatura .jpg/.png y .pcraft editable |
| `revision/` | hoja de ilustraciones y cuadros clave para revisar |
| `voz/`, `subtitulos/` | narración por escena, tiempos por palabra, `.srt` para YouTube |
| `ilustraciones/` | SVG y `.vectorcraft` editables |
| `animacion/` | proyecto de EffectCraft y render sin audio |
| `audio/` | efectos, música, sesión de SoundCraft, mezcla final y medidas |
| `montaje/` | proyecto de FilmCraft |

## Limitaciones conocidas

- La alineación de subtítulos es local (sin transcripción): precisa por frase, ±0.2 s por palabra.
- Claude no puede escuchar el audio: la mezcla se valida con medidas (LUFS, true peak, stems).
- Los IDs de parámetros de SoundCraft no están documentados (ver `references/artcraft.md`).
- El formato largo (tarjetas de cita, pantalla de estudio) está analizado pero aún no automatizado
  (`references/formato-largo.md`).
