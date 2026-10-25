---
name: shorts-vectoriales
description: Produce videos divulgativos verticales animados con ilustraciones vectoriales de línea (estilo canales tipo Stupy Doo — fondo negro, titulares gruesos con una palabra en naranja, dibujos que se trazan solos, subtítulos palabra por palabra) usando las apps de ArtCraft (VectorCraft, EffectCraft, FilmCraft, PhotoCraft, SoundCraft) y voz de Fish Audio. Úsala siempre que el usuario quiera crear, rehacer o modificar un short/reel/TikTok animado, un video explicativo con "datos curiosos", animaciones vectorizadas con guion de IA, o cambiar voz, textos, subtítulos, efectos o música de un short ya hecho con este kit — aunque no mencione ArtCraft ni la palabra "skill".
---

# Shorts vectoriales con ArtCraft

Un short se describe en un archivo `escenas.json` y se produce con scripts que conducen las CLIs
de ArtCraft en modo headless. Todo lo que debe ocurrir "cuando la voz dice X" se ancla a palabras,
así que cambiar la voz o la narración no rompe la sincronía: basta re-ejecutar desde ese paso.

Scripts en `scripts/` (ruta del kit: el directorio de esta skill). Requisitos e instalación:
`../../README.md` e `../../instalar.sh`.

## Flujo de trabajo

1. **Idea y guion** → lee `references/guion.md`. Escribe la narración por escenas: por defecto 2–3 min
   (12–18 escenas) según la complejidad; corto de 35–60 s solo si lo piden y verifica cada dato; lo que sea hipótesis se dice como hipótesis. Si el usuario quiere
   ayuda solo con el guion, la skill `guion-shorts-divulgacion` cubre eso en detalle.
2. **Proyecto** → `python3 scripts/nuevo_proyecto.py <carpeta> "<Título>"` y rellena `escenas.json`
   según `references/escenas-json.md` (titulares, capas, textos, anillos, efectos, miniatura).
3. **Ilustraciones** → edita `dibujar.py` del proyecto con la biblioteca `scripts/vc.py`
   (ver `references/ilustracion.md`). Córrelo y **mira** `revision/ilustraciones.png` antes de seguir:
   es mucho más barato corregir un dibujo aquí que tras renderizar.
4. **Producción** → `python3 scripts/producir.py <carpeta>` ejecuta voz → alinear → dibujar →
   animacion → sfx → mezcla → miniatura. Para reanudar o rehacer un tramo: `--desde <paso>`.
5. **Revisión** → mira `revision/cuadros.png` (un cuadro por escena), la miniatura y comprueba las
   medidas de `audio/mezcla_medidas.json` (≈ −14 LUFS, true peak ≤ −1 dBTP). Si algo se ve mal,
   corrige `escenas.json` o `dibujar.py` y re-ejecuta desde el paso afectado.

| Cambio pedido | Re-ejecutar |
|---|---|
| Otra voz / narración distinta | `--desde voz` (cambia `voz.id` o `narracion`) |
| Textos, titulares, capas, tiempos | `--desde animacion` |
| Un dibujo | `--desde dibujar` |
| Niveles de música/efectos | `--desde mezcla` (bloque `"mezcla"` en escenas.json) |
| Miniatura | `--desde miniatura --hasta miniatura` |

## Por qué está hecho así (para decidir bien en casos nuevos)

- **Nada estático.** Una imagen quieta mientras la voz habla hace perder la atención. Toda capa
  ondula y respira por defecto, y se insertan pulsos si una escena pasa ~3 s sin novedad; revisa el
  informe "máximo sin cambio nuevo" y añade elementos o `pulsos`/`temblor` donde haga falta
  (ver "Nada estático" en `references/escenas-json.md`).
- **Ancla a palabras, no a segundos.** Las voces de Fish varían ±15 % de duración entre tomas y
  voces; un tiempo fijo se desincroniza. Usa `"desde": "palabra"` siempre que algo ilustre lo que se dice.
- **Solo trazos en las ilustraciones.** La animación de "dibujado" usa trim paths sobre trazos;
  los rellenos aparecen de golpe. Rellena de negro solo para tapar lo que queda detrás.
- **Un único color de acento por video.** Es lo que da identidad al formato; el resto es blanco/gris.
- **Subtítulos entre el titular y la ilustración (y≈618).** La franja inferior (y > 1530) la tapan
  el título y los botones de Shorts/TikTok.
- **El alineado es local** (detección de voz + sílabas) porque la transcripción de Fish requiere
  crédito de API. Es preciso a nivel de frase; si una palabra concreta queda desfasada, ajusta su
  `desde` con `{"palabra": "x", "t": 0.2}`.

## Calidad del dibujo y la animación

Antes de dibujar o animar, aplica la skill `arte-tecnico-vectorial` (capas de atrás hacia delante,
primitivas antes que curvas, paleta base/sombra/luz/acento, caras iluminadas en objetos 3D, easing y
escalonado). Para otro look, usa un tema: `"estilo": {"tema": "libreta"}`.

## Antes de entregar

- Revisa visualmente cuadros e ilustraciones (no basta con que el script termine sin errores).
- No puedes escuchar el audio: dilo al usuario y entrégale las medidas objetivas.
- Evita voces de Fish que imiten a personas reales (busca descripciones genéricas de narrador).
- Gotchas de cada CLI (por qué algo no funciona como se espera): `references/artcraft.md`.
- Audio, ducking y normalización: `references/audio.md`.
- Formato largo (tarjetas de cita, fondos claros, modos de fusión, un "mundo" continuo): `references/formato-largo.md`.
- Para temas de color/luz usa `"modo": "add"` (luz) y `"multiply"` (tinta): EffectCraft calcula la mezcla real.

## Modo película dibujada a mano (preferido para animar)

Para personajes y acciones orgánicas usa la skill `hand-drawn-canvas-animation` dentro del kit:
la voz, la alineación, la mezcla y la miniatura siguen igual, pero la animación la dibuja una película
en Canvas 2D. Los vectores (VectorCraft) quedan para matemáticas, diagramas y cosas de poco movimiento.
Fondo negro con la retícula del canal; sin subtítulos completos: solo **focos** (palabras clave).

- Proyecto: `pelicula/pelicula.html` + `pelicula/personajes.js` (poses completas: generadores con
  topología fija → intermedios asistidos) + `pelicula/escenas.js` (`ESCENAS[n](c, tau, i, E)`).
  Ejemplo completo: `proyectos/06-pulgares/pelicula/`.
- `escenas.json`: `"subtitulos": false`, sin `estilo.tema`; por escena `titulares` y `focos`
  (`"pulgar"` o `{"palabra": "x", "texto": "…", "color": "acento"}`). Las capas vectoriales van en la película.
- `scripts/pelicula.py <proyecto>` copia los módulos, escribe `tiempos.js` y `vectores.js`, renderiza
  y deja `animacion/animacion.mp4`; `producir.py` lo usa solo si existe `pelicula/pelicula.html`.
  Revisión: `--grid 48`, `--strip INICIO,24` (cuadros consecutivos: obligatorio para juzgar movimiento), `--en 12.5,40`.
- Puente `scripts/pelicula/kit.js`: `dicho(E, 'palabra')` (segundo local en que la voz la dice), `titulares`,
  `focos`, `rotulo`, `circuloMano`, `subrayado`, `flecha`, `vector`/`vectorVivo`, `pose`, `actuar`
  (claves → intermedios en dos), `entre`, `dibujaPose` (con capas de profundidad y caché).
- Movimiento real: el caballo de Muybridge (1893, dominio público) va en `muybridge.js` (`rotoAt`).
- Gotchas: los nombres globales chocan entre scripts clásicos (prefija los tuyos); `Math.pow` de base
  negativa da NaN (pose() avisa qué trazo); `dibujaPose` cachea por pose y escala: no generes una escala distinta por cuadro.
