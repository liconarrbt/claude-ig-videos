---
name: ilustracion-vectorcraft
description: Dibuja ilustraciones vectoriales de línea (diagramas técnicos, relojes, mapas, animales y objetos esquemáticos, iconos) con VectorCraft en modo headless mediante código, exportando SVG/PNG/.vectorcraft listos para animar. Úsala cuando el usuario pida dibujar, diseñar o corregir una ilustración, icono, logo de línea o diagrama vectorial con VectorCraft/ArtCraft, o cuando un short del kit necesite ilustraciones nuevas.
---

# Ilustración de línea con VectorCraft

Biblioteca: `../shorts-vectoriales/scripts/vc.py`. Guía completa con reglas y recetas:
`../shorts-vectoriales/references/ilustracion.md`. Estilo del formato:
`../shorts-vectoriales/references/estilo.md`. Ejemplo real: `../../ejemplos/sexagesimal/dibujar.py`.

## Pasos

1. Bocetea mentalmente la composición en el lienzo de 900×900 (centro 450,450): un sujeto central
   grande, estructura en blanco, lo importante en el color de acento, guías en gris.
2. Escribe el dibujo en `dibujar.py` (o un script propio) con `Doc`, `style`, formas y `save`.
   Separa en SVG distintos las piezas que deban moverse por separado.
3. Ejecuta y genera la hoja de contactos (`hoja_contactos`). **Mírala** con la herramienta de
   lectura de imágenes: busca solapamientos, elementos amontonados, grosores desiguales, formas que
   se ven detrás de otras.
4. Corrige y repite hasta que se lea claro a tamaño de móvil. Explica al usuario qué cambiaste.

## Fuera del kit

Para un logo o icono suelto, exporta también PNG con
`vectorcraft-cli convert in.svg out.png --scale 2`. Para SVG con texto real usa
`text.create`; para que se vea igual en cualquier equipo, `convert --outline-text`.

## Por qué

VectorCraft aplica la pintura a la selección y cada forma nueva queda seleccionada: sin
`select.none` (lo hace `style()`) se recolorea la última forma. Y los rellenos no se animan con el
efecto de dibujado: por eso todo es trazo salvo lo que tapa.
