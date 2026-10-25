# Audio: voz, alineación, efectos y mezcla

## Voz (voz.py)
- Fish Audio, una petición por escena → duraciones exactas por escena (`voz/tiempos.json`).
- Voz por defecto: "nicho de horror 2" (`d047b6a8f24f4d56ba818b08dbd9d089`), narrador masculino serio.
  Otra probada: "voz de locutor k" (`3f45a7fd7a614655a61eb7027b955783`).
- Velocidad 1.1 da el ritmo ágil del formato; este narrador apenas hace pausas (0.1–0.3 s).

## Alineación (alinear.py)
- Sin servicios externos: detecta tramos de voz (RMS en ventanas de 10 ms), asigna las pausas
  ≥ 0.15 s a la frontera entre palabras más cercana (prefiriendo puntuación) y reparte cada bloque
  por sílabas. Resultado: `subtitulos/palabras.json` y `.srt` (subible a YouTube).
- Si hay crédito en Fish, la transcripción `/v1/asr` con `ignore_timestamps=false` da marcas por palabra reales.

## Efectos (sfx.py)
Sintetizados desde cero (sin muestras de terceros → sin problemas de derechos):
whoosh (ruido con pasa-banda que barre), pop (seno con caída de tono), pop grave (golpe),
tic-tac (clics alternos) y música ambiental en La menor a 90 BPM (pad Am–F–C–G, arpegio, bajo).
Para música propia (biblioteca de audio de YouTube, Pixabay…): guárdala como `audio/musica.wav`
y corre `sfx.py --solo-efectos`.

## Mezcla (mezcla.py, SoundCraft)
- Voz: EQ (HPF 85 Hz, −2.5 dB @ 320 Hz, +2.5 dB @ 3.5 kHz, +1.5 dB shelf 10 kHz) → compresor 3:1,
  −24 dB, 8/90 ms, makeup +4.
- Música: ducking estilo sidechain como automatización: seguidor de envolvente de la voz
  (umbral −40 dBFS, 4:1, máx. 12 dB, ataque 40 ms, release 300 ms) → ≈400 puntos de volumen.
  Con narradores sin pausas, un ducking "encendido/apagado" dejaría la música baja todo el tiempo;
  el seguidor la deja respirar en los microsilencios.
- Niveles por defecto (bloque `"mezcla"`): música −13, whoosh −14, pops −9, tic-tac −16 dB.
- Master: maximizador con techo −1.2 dB; su umbral se itera hasta −14 ± 0.3 LUFS → true peak ≈ −1.1 dBTP.
- Resultado medido en el ejemplo: voz −14.5 LUFS vs música −31.7 (≈17 dB de separación).

No se puede escuchar el resultado desde aquí: entrega siempre las medidas y pide al usuario que lo
escuche. Para comparar stems, silencia pistas con `mix.mute {"tracks":[…],"value":true}` y rebota.
