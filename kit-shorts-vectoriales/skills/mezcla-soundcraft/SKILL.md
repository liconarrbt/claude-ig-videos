---
name: mezcla-soundcraft
description: Mezcla y masteriza audio de video con SoundCraft (ArtCraft) en modo headless — EQ y compresión de voz, ducking de música bajo la narración, efectos de sonido, normalización a LUFS de plataforma (YouTube/TikTok −14 LUFS, −1 dBTP) y exportación — y sintetiza efectos y música sin derechos. Úsala cuando el usuario pida mejorar, remezclar, nivelar o normalizar el audio de un video o podcast, bajar/subir música o efectos, añadir whoosh/pops/música, o "que la voz se escuche mejor", aunque no nombre SoundCraft.
---

# Mezcla con SoundCraft

Referencias: `../shorts-vectoriales/references/audio.md` (cadena, niveles, por qué del ducking) y
la sección SoundCraft de `../shorts-vectoriales/references/artcraft.md` (IDs de parámetros y trampas).
Script de referencia que hace todo para un proyecto del kit: `../shorts-vectoriales/scripts/mezcla.py`.

## Pasos

1. **Sesión**: crea pistas (`track.new`), importa audio en su posición (`file.import_audio` con
   `track`, `at: "m:ss.mmm"`, `new_tracks: false`). Escribe los comandos en un archivo `ID JSON`
   por línea y ejecútalo con `soundcraft-cli script archivo.txt --save sesion.scraft`.
2. **Voz**: `mix.insert` eq_7band (HPF ~85 Hz, recorte en 250–400 Hz, presencia 3–4 kHz) y
   compressor (3:1, ataque 5–10 ms, release 80–120 ms).
3. **Música**: ducking con `automation.set_point` en `volume` siguiendo la envolvente de la voz
   (el compresor no tiene sidechain externo). Música ≈15–17 dB por debajo de la voz.
4. **Efectos**: pistas por tipo con `mix.volume`; evita que tapen sílabas importantes.
5. **Master**: maximizer con `ceiling` −1.2 y `threshold` negativo como empuje; rebota
   (`file.bounce_mix`) y ajusta el empuje hasta el LUFS objetivo (±0.3).
6. **Verifica con números**: LUFS integrados, true peak, y rebotes de stems con `mix.mute` para
   medir voz vs música. No puedes escuchar: entrega las medidas y pide al usuario que escuche.

## Por qué

- Los parámetros de plugin con ID desconocido se ignoran sin error: comprueba cada cambio con el
  LUFS/peak del rebote, no asumas que se aplicó.
- `mix.trim` en el master no afecta al bounce; el maximizador sí.
- Plataformas normalizan a −14 LUFS: entregar más fuerte no suena más fuerte, solo más comprimido;
  más bajo hace que la plataforma lo suba y pueda saturar los picos.
- Para efectos/música sin derechos: `../shorts-vectoriales/scripts/sfx.py` los sintetiza.
