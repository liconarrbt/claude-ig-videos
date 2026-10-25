"""Ilustraciones del short "Por qué el tiempo va de 60 en 60" (VectorCraft).
Corre: python3 dibujar.py <carpeta del proyecto>"""
import math, os, sys
sys.path.insert(0, os.environ.get("KIT_SHORTS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "skills", "shorts-vectoriales", "scripts")))
from vc import Doc, polar, radial, esfera, reticula, hoja_contactos, O, W, G, C

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))

# 1 · Reloj (esfera) + manecillas en capa aparte para girarlas en EffectCraft
d = Doc(); esfera(d); d.style(O, 4, fill=O).circle(C, C, 26); d.save(P, "reloj")
d = Doc(); d.style(W, 14); radial(d, 0, 210, 300); d.style(O, 8); radial(d, 0, 300, 0); d.save(P, "reloj_manecillas")

# 2 · Tablilla de arcilla con numerales babilónicos (cuñas verticales = 1, cheurones = 10)
d = Doc()
d.style(W, 5).add("shape.rectangle", x=215, y=100, width=470, height=700, radius=70)
d.style(G, 2).add("shape.rectangle", x=243, y=128, width=414, height=644, radius=50)
d.style(G, 2).path("M560 100 L540 170 L575 230 L548 300")

def cuna(doc, x, y):  # cuña vertical: cabeza triangular + cola
    doc.path(f"M{x-11} {y} L{x+11} {y} L{x} {y+18} Z M{x} {y+18} L{x} {y+44}")

def cheuron(doc, x, y):  # cuña de diez
    doc.path(f"M{x+20} {y+4} L{x-12} {y+26} L{x+20} {y+48}")

# filas: 1, 12, 15, 20, 30, 59  (decenas, unidades)
filas = [(0, 1), (1, 2), (1, 5), (2, 0), (3, 0), (5, 9)]
d.style(O, 4)
for row, (dec, uni) in enumerate(filas):
    y, x = 160 + row * 98, 285
    for _ in range(dec):
        cheuron(d, x, y); x += 30
    x += 18
    arriba = uni if uni <= 5 else (uni + 1) // 2
    for k in range(uni):
        fila, col = (0, k) if k < arriba else (1, k - arriba)
        cuna(d, x + col * 30, y + fila * 50)
d.save(P, "tablilla")

# 3 · Divisores de 60: 60 al centro, 12 divisores alrededor
d = Doc()
d.style(G, 2, dash=[2, 12])
for i in range(12):
    radial(d, 165, 285, i * 30)
d.style(O, 7).circle(C, C, 300)
d.style(W, 4)
for i in range(12):
    x, y = polar(340, i * 30)
    d.circle(x, y, 108)
d.save(P, "divisores")

# 4 · Mano esquemática con las 12 falanges marcadas
d = Doc()
dedos = [(318, 210), (408, 150), (498, 175), (588, 250)]  # (centro x, punta y)
d.style(W, 5, fill="#000000")
for cx, top in dedos:
    d.add("shape.rectangle", x=cx - 40, y=top, width=80, height=520 - top, radius=40)
d.add("shape.rectangle", x=175, y=470, width=82, height=235, radius=41, rotation=-38)
d.style(W, 5, fill="#000000").add("shape.rectangle", x=268, y=470, width=370, height=330, radius=90)
d.style(G, 3)
for cx, top in dedos:
    seg = (490 - top) / 3
    for k in (1, 2):
        d.line(cx - 28, top + seg * k, cx + 28, top + seg * k)
d.style(O, 4, fill=O)
for cx, top in dedos:
    seg = (490 - top) / 3
    for k in range(3):
        d.circle(cx, top + seg * (k + 0.5), 24)
d.save(P, "mano")

# 5 · Día y noche: 12 horas de luz (arriba) + 12 de noche (abajo)
d = Doc()
d.style(W, 5).circle(C, C, 760)
d.style(O, 6)
for i in range(13):
    radial(d, 270, 372, -90 + i * 15)
d.style(W, 3)
for i in range(1, 12):
    radial(d, 300, 372, 90 + i * 15)
d.style(G, 2).line(80, C, 820, C)
d.style(O, 6).circle(C, 330, 90)
for i in range(8):
    a = math.radians(i * 45)
    d.line(C + 62 * math.cos(a), 330 + 62 * math.sin(a), C + 88 * math.cos(a), 330 + 88 * math.sin(a))
d.style(W, 5).path("M478 528 A48 48 0 1 0 478 632 A38 38 0 1 1 478 528 Z")
d.save(P, "dia_noche")

# 6 · Reloj decimal francés (10 horas) + la X en capa aparte
d = Doc()
d.style(W, 5).circle(C, C, 760)
d.style(W, 2)
for i in range(100):
    if i % 10:
        radial(d, 356, 372, i * 3.6)
d.style(O, 9)
for i in range(10):
    radial(d, 312, 372, i * 36)
d.style(W, 10); radial(d, 0, 250, 72)
d.style(O, 4, fill=O).circle(C, C, 26)
d.save(P, "reloj_decimal")
d = Doc(); d.style(O, 26); d.line(190, 190, 710, 710); d.line(710, 190, 190, 710); d.save(P, "reloj_decimal_x")

# Fondo: retícula de 60 px (guiño a la base 60)
reticula(P)

hoja_contactos(P, ["reloj", "tablilla", "divisores", "mano", "dia_noche", "reloj_decimal"],
               os.path.join(P, "revision", "ilustraciones.png"))
