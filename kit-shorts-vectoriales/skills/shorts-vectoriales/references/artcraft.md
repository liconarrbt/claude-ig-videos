# ArtCraft: CLIs, MCP y trampas conocidas

Las CLIs viven en `~/Applications/craft-cli/<app>/<app>-cli-<versión>-macos-universal/` (o en
`$CRAFT_CLI_DIR`). `comun.cli("<app>")` encuentra la más reciente. Todas están firmadas y
notarizadas por Learning Machines LLC (DJ6XS33FX8). Cada una lista sus comandos con
`<app>-cli commands` y la mayoría los describe con `describe <id>`.

Versiones probadas: PhotoCraft 0.10.0 · VectorCraft 0.13.1 · EffectCraft 0.11.1 · FilmCraft 0.9.0 · SoundCraft 0.5.0.

## MCP

Cada CLI tiene `mcp` (JSON-RPC por stdio). Registro en `~/.claude.json` → `mcpServers` (lo hace
`instalar.sh`). PhotoCraft, VectorCraft y EffectCraft aceptan `--automation-read-root/--automation-write-root`
para confinar archivos; FilmCraft y SoundCraft no. Los MCP solo cargan al **iniciar** una sesión.
Los scripts del kit usan las CLIs directamente (más deterministas y reproducibles que el MCP).

## VectorCraft
- `run --cmd ID --params JSON … --export a.svg --export a.vectorcraft`.
- Pintura aplica a la selección → `select.none` antes de cambiar `paint.setFill/setStroke`.
- `convert in.svg out.png [--scale N]` para previsualizar.

## EffectCraft
- `script archivo.jsx`: modelo de objetos estilo After Effects + `app.run(id, params)` para cualquier comando.
- Hay que hacer `comp.openInViewer()` antes de `edit.pasteSvg` ("no composition is open").
- `edit.pasteSvg` convierte el SVG en una capa de formas; `layer.addShapeItem {kind:"trim"}` añade
  trim paths y se anima con expresión en `contents/trim/end`.
- Texto de párrafo: su posición por defecto ya es el centro de la caja con el ancla en (0,0) — no
  toques el ancla, solo `transform/position`.
- Expresiones con `inPoint`/`outPoint` funcionan: animar con expresiones evita lidiar con interpolación de keyframes.
- `render` escribe su progreso en stderr (stdout vacío). `render-frame --time t --max-side N` para revisar.
- Fuentes: `text.fonts` lista las del sistema (Avenir Next Condensed, Futura, DIN Condensed, Impact…) e Inter incluida.

## FilmCraft
- `run archivo.jsonl` (un `{"id","params"}` por línea). Los elementos importados se numeran 1..N en orden.
- `timeline.place {item, track:"V1"|"A1", seconds, insert:false, audio:false|video:false, duration(ticks)}`;
  254016000000 ticks por segundo.
- El volumen de pista (`timeline.setTrack volumeDb`) no aparece en `inspect`: usa `clip.audioGain`.
- `export <ruta> --format h264 --range entire`. `render --seconds t --out f.png --scale 0.33` para revisar.
- `probe` no muestra el audio de un mp4 propio de forma clara: `afinfo archivo.mp4` sí.

## PhotoCraft
- Las imágenes abren como "Background" bloqueado: `layer.new.layerFromBackground` antes de borrar a transparente.
- `run --new '{"width","height"}' --cmd … --out f.png|.pcraft` (al exportar PNG se aplana).
- `type.create` devuelve el id de capa; `type.setStyle {layer, range, color}` colorea una parte.

## SoundCraft
- `script archivo.txt [--save s.scraft]` con una línea `ID JSON` por comando; `run --cmd 'ID=JSON'`.
- Los IDs de parámetros de plugins no se documentan ni aparecen en `--inspect`, y los desconocidos se
  **ignoran en silencio**. Encontrados con `strings` sobre el binario:
  - dinámica (compressor, maximizer, de_esser): `threshold ratio attack release knee makeup ceiling lookahead`
  - eq_7band: `hpf_on hpf_freq low_shelf_gain/freq/q low_mid_freq/gain/q mid_freq/gain/q high_mid_freq/gain/q high_shelf_gain/freq/q lpf_on lpf_freq`
  - Verifica siempre con el LUFS que devuelve `file.bounce_mix`.
- El compresor no tiene entrada de sidechain externa → el ducking se hace con `automation.set_point` en volumen.
- `mix.trim` en el master no afecta al bounce; el umbral del `maximizer` sí (bajarlo = más nivel).
- El track master recibe nombre automático: refiérelo por id (lo devuelve `track.new`).
- `file.bounce_mix` devuelve `lufs`, `peak_db` y `true_peak_db`.

## Fish Audio
- `POST https://api.fish.audio/v1/tts`, cabecera `model`. Sin crédito de API los modelos de pago
  dan 402: `s2.1-pro-free` funciona. La transcripción (`/v1/asr`) también exige crédito.
- Los WAV vienen en streaming con longitud indefinida en la cabecera: lee `len(raw)`, no `getnframes()`.
- Buscar voces: `GET https://api.fish.audio/model?language=es&sort_by=task_count` — evita las que imitan a personas reales.
