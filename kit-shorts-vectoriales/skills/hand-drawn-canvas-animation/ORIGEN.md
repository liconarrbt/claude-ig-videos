# Origen

Skill de terceros, sin modificar: https://github.com/alesha-pro/tools/tree/main/skills/hand-drawn-canvas-animation
(commit 90e9662, 2026-09-28) · Licencia MIT © 2026 Alexey Fateev (ver LICENSE).

Dependencias (instaladas 2026-10-21): Node 26, Google Chrome, ffmpeg 9.0.2 (Homebrew) y `puppeteer-core`
en `scripts/node_modules` (`npm ci --ignore-scripts`, desde su package-lock). Prueba: `examples/sketchbook-bird.html`
→ MP4 1920×1080, 24 fps, 144 cuadros, 6 s, en ~10 s.

    node scripts/render.mjs examples/sketchbook-bird.html --look pencil --grid 12 --out /tmp/vista
    node scripts/render.mjs <pelicula.html> --out <carpeta>

Sus principios de dibujo y movimiento también se aplican al kit (ver arte-tecnico-vectorial §6).
