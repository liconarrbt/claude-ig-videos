# Formato largo (2–3 min): análisis del video de referencia

Referencia: "La telaraña es parte de la mente" (720×1280, 60 fps, 2:36). Diferencias con el short:

## Estructura
- **Un mundo continuo**: un solo sujeto (la telaraña y la araña) que evoluciona durante todo el
  video — se construye, vibra, se mide, se compara — en lugar de una ilustración nueva por escena.
  La "cámara" se acerca, se aleja y recorre el dibujo.
- Bloques de 20–30 s con un mini-gancho cada uno ("¿DÓNDE TERMINA UNA MENTE?").
- Cierre con pregunta abierta en el titular ("¿SE COME UN PEDAZO DE SU MENTE?").

## Recursos visuales nuevos
- **Tarjetas de cita**: recuadro blanco pequeño con barra de color a la izquierda, texto monoespaciado:
  "TAKESHI WATANABE · Japón · 2000", "Peakall · 1971". Aparecen al nombrar al investigador.
- **Pantalla de estudio**: cambio a fondo crema (#F2EFE6) con fichas de papers (título, revista,
  año, autores y país) y el dibujo en negro: rompe el ritmo y da autoridad.
- **Diagramas superpuestos**: regla con medida ("10 cm"), barra de nivel ("TENSIÓN"), recuadros de
  selección, "2+2=4" escrito a mano con un lápiz que aparece.
- **Dos acentos**: rojo-naranja para el sujeto, verde lima para lo que "fluye" (vibración, señal),
  azul para etiquetas de categoría.
- **Subtítulos clave** (1–3 palabras, no transcripción completa) en el tercio inferior.
- Brillo/halo rojo detrás del sujeto en los momentos clave.

## Ya implementado en el kit (probado en ejemplos/rgb-cmy)
- `tarjetas` (citas), `fondo` por escena con cambio automático a textos oscuros, `hasta`,
  `entrada: "pop"`, `desde_pos` (deslizar), `modo` de fusión, `color_acento` por titular.

## Cómo abordarlo con el kit
- Escenas más largas con varias `capas` que entran por `desde` (el mismo SVG base con detalles
  añadidos en capas separadas), `empuje` mayor y `pos`/`escala` distintos para simular cámara.
- Pantalla de estudio: escena con `"fondo": "#F2EFE6"` + ilustraciones dibujadas con línea oscura
  (#1A1A1A) + `tarjetas` para las fichas de papers.
- Pendiente: halo/brillo detrás del sujeto y "cámara" que recorre un único dibujo grande.
