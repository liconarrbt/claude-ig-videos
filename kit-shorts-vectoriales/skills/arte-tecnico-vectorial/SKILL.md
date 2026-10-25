---
name: arte-tecnico-vectorial
description: Criterios de dirección técnica de arte para ilustración vectorial paramétrica (VectorCraft), geometría 3D proyectada (isométrica/axonométrica) y cinemática con easing, escalonado y partículas (EffectCraft). Úsala siempre que vayas a dibujar, corregir o animar ilustraciones vectoriales — en especial dentro del kit de shorts vectoriales — para que los dibujos se lean bien, tengan paleta controlada, profundidad correcta y movimiento orgánico, aunque el usuario solo diga "mejora los dibujos" o "que se vea más pro".
---

# Arte técnico vectorial (VectorCraft + 3D + EffectCraft)

Guía de calidad para quien dibuja y anima. Se aplica sobre el kit de shorts vectoriales:
biblioteca de dibujo `../shorts-vectoriales/scripts/vc.py`, animación `../shorts-vectoriales/scripts/animacion.py`.
Referencia de cómo se ve "bien": `../shorts-vectoriales/references/ilustracion.md` y `estilo.md`.

## 1. Dibujo vectorial (VectorCraft)

**Planifica antes de trazar.** Lienzo base del kit: 900×900, centro `(450, 450)` = pivote de la capa
en EffectCraft (todo lo que rote o se escale lo hace alrededor de ese punto). Escribe en un comentario
el bounding box aproximado de cada pieza.

**Orden de capas (Z estricto), de atrás hacia delante:**
1. Fondo / lienzo (lo pone el tema: retícula oscura o libreta).
2. Siluetas y masas base (relleno de color base).
3. Oclusión y sombras propias (relleno del tono de sombra; `fill=NEGRO` = color del papel para tapar).
4. Geometría media y articulaciones (patas, orejas, uniones).
5. Detalles: líneas de corte, pliegues, brillos (trazo fino, tono de luz o acento).

**Primitivas antes que curvas libres.** Rectángulos redondeados, elipses, arcos y polígonos regulares
(`d.rect`, `shape.ellipse`, `shape.polygon`, `polar/radial`) para todo lo geométrico. Curvas solo para
siluetas orgánicas, y entonces con `suave()` (Catmull-Rom → Bézier) a partir de puntos de control bien
espaciados: así no aparecen picos ni dobleces. Toda forma cerrada termina en su nodo de origen (`suave(p, True)`, `Z`).

**Color controlado.** Nada de primarios puros saturados (`#FF0000`, `#00FF00`, `#0000FF`) salvo que el
tema lo exija físicamente (p. ej. demostrar mezcla aditiva de luz RGB, donde el rojo puro *es* el dato).
Por cada material define cuatro tonos:
- **Base** · **Sombra** (más fría y algo más saturada) · **Luz** (más cálida y clara) · **Acento** (el naranja del canal).
Ejemplo madera: base `#C9955B`, sombra `#8E5E3B`, luz `#E8C38E`. Trazos con `cap/join: round` (ya por defecto en `style()`).

**Legibilidad.** Antes de animar, mira el dibujo **ensamblado** (`hoja_contactos` o un compuesto de capas)
y pregúntate "¿se reconoce sin el texto?". Si no, añade los rasgos identificadores (orejas largas y borla
en un burro; cuernos y hocico en una vaca; mapas con coordenadas reales vía `proyeccion()`).

## 2. Geometría 3D en un motor 2D

**Sistema de coordenadas explícito.** Escena right-handed: X derecha, Y arriba, Z hacia el visor. Cada
objeto complejo define su origen local `(0,0,0)` antes de transformarse.

**TRS en orden canónico:** escala → rotación → traslación (evita cizallas).

**Jerarquía:** padre → hijos; los hijos heredan la transformación (en EffectCraft, misma `pos/escala`
y misma `semilla` para que se muevan juntos, o `layer.setParent`).

**Isométrica** (para cajas, edificios, tablas, pirámides):

    screenX = (x − z)·cos 30°        screenY = −y + (x + z)·sin 30°    (en pantalla y crece hacia abajo)

- **Algoritmo del pintor:** ordena las caras por profundidad media (baricentro) y dibuja de lejos a cerca.
- **Sombreado por normales:** luz principal a 45°; intensidad = max(0, N·L). Cara superior = tono de luz,
  cara frontal = base, cara lateral = sombra.

## 3. Cinemática (EffectCraft)

- **Tiempo, no cuadros:** todo se calcula con `time`, `inPoint` o `t` normalizado 0→1 (así lo hacen las
  expresiones del kit). Bucles con funciones armónicas cerradas en 2π (`sin(ωt)`), sin saltos.
- **Easing según intención:** entradas *ease-out* (el kit usa cúbica), salidas *ease-in*, impactos y
  rebotes *back-out/elastic* con sobreimpulso controlado (`"entrada": "pop"`). Nada lineal en movimientos orgánicos.
- **Escalonado (staggering):** las piezas secundarias entran 0.05–0.2 s después de la principal
  (`"desde": {"palabra": "x", "t": 0.12}`). Da superposición y acción retardada.
- **Partículas:** piensa en *spawn* (origen ligado al emisor, dispersión, velocidad, vida), *update*
  (gravedad, arrastre, turbulencia senoidal) y *render* (`"modo": "add"/"screen"` para energía y luz,
  `"multiply"` para humo o polvo; escala e opacidad que mueren hacia 0).

## 4. Protocolo al recibir un encargo de dibujo o animación

1. **Plan técnico breve:** lienzo y bounding boxes, paleta indexada (hex), capas/nodos, línea temporal
   (duración, easing, escalonado, emisores).
2. **Código modular** en el `dibujar.py` del proyecto (funciones por objeto, nombres semánticos, sin
   dependencias no declaradas) y parámetros de animación en `escenas.json`.
3. **Verificación visual** del ensamblado antes de producir, y de cuadros clave después.

## 5. Acabado en EffectCraft (probado en 0.11.1)

Efectos que existen y funcionan en headless (nombres de After Effects en `effect.apply`):
`Drop Shadow` (`color, opacity, direction, distance, softness`), `Fractal Noise` (`transform/scale`,
`contrast`, `complexity`, `evolution`), `CC Vignette` (`amount`), `Gaussian Blur`, `Glow`.
Desenfoque de movimiento: `comp.motionBlur = true` + `layer.setSwitch {switch:"motionBlur", value:true}`.
Grano, viñeta y desenfoque multiplican el tiempo de render (~10 núcleos al 100 % durante muchos minutos) y
el peso del MP4: no los actives por defecto. Lo que más profesionaliza es el **movimiento**, no la textura:
personajes con rig (partes con pivote, acción retardada, parpadeo), entradas con rebote y titulares por palabra
— ver "Movimiento profesional" y "Rigs" en `references/escenas-json.md`.
Pivote de una capa: `transform/anchor` (no `anchorPoint`); hija con `layer.setParent {compensate:false}`.
El kit los aplica con `estilo.acabado` (ver "Acabado de cámara" en `references/escenas-json.md`).
Referencia general de las CLIs/MCP: skills comunitarias https://github.com/Vinciux99/artcraft-claude-skills
(escritas para EffectCraft 0.9.x: verifica cada comando con `describe_command` antes de usarlo).

## 6. Animación dibujada a mano (skill `hand-drawn-canvas-animation`)

Skill de terceros instalada en `../hand-drawn-canvas-animation/` (MIT, ver su `ORIGEN.md`). Es otro motor
(Canvas 2D + Chrome + ffmpeg) para cortos dibujados a mano; úsala cuando el usuario pida explícitamente ese
estilo o un corto fuera del kit. Sus criterios sí aplican a los shorts del kit:
- **Poses completas antes que rig:** planifica claves y intermedios de la acción principal (anticipación,
  contacto, peso, reacción); un rig solo ayuda, la pose la carga el dibujo.
- **Exposición intencional:** dibujos sostenidos "a dos" (12 dibujos/s) o más leen como hechos a mano;
  el temblor de línea (boil) debe tener propósito, no estar siempre igual.
- **Trazos estables:** semilla fija por dibujo; un dibujo sostenido conserva sus trazos.
- **Jerarquía de línea:** contorno más grueso que el detalle interior, con presión, afinado y huecos.
- **QA de movimiento:** revisa tiras de cuadros consecutivos alrededor de contactos y acciones rápidas,
  no solo cuadros sueltos.
