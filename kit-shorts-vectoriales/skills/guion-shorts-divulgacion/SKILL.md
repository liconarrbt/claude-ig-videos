---
name: guion-shorts-divulgacion
description: Escribe guiones verificados para shorts/reels/TikToks de divulgación con datos curiosos (gancho, escenas, titulares con palabra de acento, notas de fuentes) y los entrega listos como escenas.json del kit de shorts vectoriales. Úsala cuando el usuario pida ideas de videos, un guion, temas para un piloto, "un dato curioso sobre X", reescribir una narración o adaptar un tema a formato de short animado, aunque todavía no quiera producir el video.
---

# Guiones para shorts de divulgación

Lee `../shorts-vectoriales/references/guion.md` (fórmula, escritura para voz, rigor) y, si el guion
va a producirse, `../shorts-vectoriales/references/escenas-json.md`.

## Pasos

1. **Elige el ángulo**: el dato debe contradecir algo que la gente cree, y tener un objeto
   dibujable. Si el usuario pide ideas, ofrece 6–8 en tabla (titular con palabra de acento,
   ilustración, color de acento, gancho de 2 s) y recomienda una explicando por qué.
2. **Investiga y verifica** con búsqueda web cada dato (fechas, cifras, nombres). Marca lo dudoso
   como hipótesis en la narración ("una teoría dice…"). Nunca inventes una cita o un estudio.
3. **Escribe la narración** en 6–8 párrafos (una escena cada uno), 110–150 palabras en total.
4. **Para cada escena** define: titular (2–6 palabras en MAYÚSCULAS, una en acento), ilustración
   (qué se dibuja y qué se mueve) y qué aparece cuando se dice qué palabra.
5. **Entrega**:
   - una tabla legible (escena · titular · ilustración · narración) para que el usuario apruebe, y
   - si va a producirse, el `escenas.json` con `"fuentes"` y con cada `desde` apuntando a palabras
     que de verdad están en la narración (el script de animación se detiene si no las encuentra).

## Por qué importan estos detalles

- El gancho decide la retención: si los 2 primeros segundos no sorprenden, el resto no se ve.
- Las apariciones ancladas a palabras exigen que esas palabras existan y no se repitan de forma
  ambigua en la escena: escribe pensando en dónde anclarás cada elemento.
- Los errores factuales destruyen la credibilidad del canal; la verificación vale más que el estilo.
