# Dibujar ilustraciones con vc.py (VectorCraft)

Cada proyecto tiene `dibujar.py`. Ejemplo real y completo: `../../ejemplos/sexagesimal/dibujar.py`
(reloj, tablilla cuneiforme, divisores, mano con falanges, día/noche, reloj decimal).

```python
from vc import Doc, polar, radial, esfera, reticula, hoja_contactos, O, W, G, NEGRO, C
d = Doc()                              # lienzo 900×900, centro C = 450
d.style(W, 5).circle(C, C, 760)        # style(color, grosor, fill=None, dash=None)
d.style(O, 9); radial(d, 318, 372, 0)  # marca radial a 0° (arriba)
d.style(G, 2, dash=[2, 12]).line(...)  # guía punteada
d.path("M100 100 L200 150 A40 40 0 1 0 260 200 Z")   # datos SVG
d.rect(x, y, w, h, radius=40, rotation=-38)
d.save(P, "nombre")                    # → ilustraciones/nombre.svg + .vectorcraft
```

Ayudas: `polar(r, grados)` (0° arriba, horario), `radial(doc, r1, r2, grados)`,
`esfera(doc, marcas=60, mayores_cada=5)`, `reticula(P)`, `hoja_contactos(P, nombres, salida)`.

## Reglas que ahorran tiempo

- **Llama a `style()` antes de cada grupo de formas.** VectorCraft pinta lo seleccionado y cada
  forma nueva queda seleccionada: cambiar color sin deseleccionar recolorea la última forma.
  `style()` ya deselecciona.
- **Solo trazos.** El efecto de dibujado (trim paths) solo anima trazos. Usa `fill=NEGRO` cuando
  una forma debe tapar a otra (dibuja primero lo de atrás, luego lo de delante con relleno negro).
- **Piezas que se mueven por separado = SVG separados** (manecillas, una X que cae, una flecha):
  EffectCraft convierte cada SVG en una capa, y las capas se animan independientes.
  Mantén el mismo lienzo 900×900 y centro para que se superpongan alineadas.
- **Grosores**: estructura 4–5 px, marcas principales 8–9 px, detalles 2–3 px, énfasis 14–26 px.
- **Revisa la hoja de contactos** (`revision/ilustraciones.png`) con la herramienta de lectura de
  imágenes antes de animar: solapamientos y elementos amontonados se ven al instante.
- Los números y textos van mejor como capas de texto de EffectCraft (`textos`, `anillo`) que
  dentro del SVG: se pueden sincronizar con la voz y quedan nítidos.

## Recetas

- **Reloj**: `esfera(d)` + manecillas en SVG aparte con `rotacion` en la capa.
- **Diagrama radial** (divisores, ciclos): círculo central + N círculos con `polar(340, k*360/N)`
  + radios punteados; los números con `anillo`.
- **Objeto esquemático** (mano, insecto, edificio): rectángulos redondeados + líneas de pliegue en
  gris + puntos de acento en lo que la narración cuenta.
- **Mapa/ruta**: contorno simplificado en blanco + trayecto en acento con `dibujo` largo (2–3 s).
- **Tachado/negación**: X gruesa en acento como capa aparte con `golpe: true`.

## Que se entienda lo que es (lecciones del cerebro, el pie y el mapa)

Un esquema demasiado simple no se reconoce. Dibuja los **rasgos que identifican** al objeto:
- **Anatomía/objetos**: contorno con `suave()` (curvas orgánicas) + los rasgos clave. Cerebro: lóbulo
  frontal, cisura de Silvio, surco central, cerebelo con láminas, tronco, y circunvoluciones como curvas en
  S repartidas sin amontonarse (`dentro()` para que queden dentro, distancia mínima entre trazos).
  Zapato: suela gruesa con dibujo, cordones cruzados con ojales, puntera, talón, calcetín.
- **Mapas**: nunca a ojo. Usa coordenadas reales (lon, lat) de las costas con `proyeccion()` y `suave()`;
  encuadra para que se vean las masas reconocibles (golfos, penínsulas) y etiqueta océano y regiones.
- Revisa el dibujo **ensamblado** (capas superpuestas como se verán), no cada SVG por separado.

## Volumen (probado: VectorCraft → SVG → EffectCraft)

- `fill=grad(luz, base, sombra)`: degradado lineal a 45° (sombra abajo-izquierda → luz arriba-derecha),
  ajustado al contorno de cada objeto. `grad_radial(centro, borde)` para esferas, ojos y burbujas.
- `d.sombra_suelo(cx, cy, w, h)`: elipse semitransparente de contacto bajo el objeto.
- Brillos: trazo corto claro en el borde que mira a la luz. Sombras planas de tarjetas: misma forma desplazada con `object.setProps opacity`.
- **No uses** perfiles de grosor variable (`stroke.widthProfile`): se exportan como relleno y rompen el trazo animado.
- Personajes con rig: genera también un `<nombre>_rig.svg` ensamblado (partes + cuerpo) para la hoja de
  contactos y la **miniatura** (que no anima las partes). Ejemplo: `ensamblar()` en `proyectos/05-falsos-amigos-burro/dibujar.py`.
