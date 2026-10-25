"""Marca de Curiosart (VectorCraft): emblema, retícula del banner y piezas decorativas.
Corre: python3 dibujar_marca.py"""
import math, os, sys
sys.path.insert(0, os.path.expanduser("~/Documents/Artcarft/kit-shorts-vectoriales/skills/shorts-vectoriales/scripts"))
from vc import Doc, polar, radial, O, W, G, NEGRO, C

P = os.path.dirname(os.path.abspath(__file__))

# Emblema: aro de reloj abierto (una "C" con marcas, guiño al estilo de los videos) + "?" en naranja.
d = Doc()
hueco = (55, 125)                           # la C se abre hacia la derecha (90° = derecha)
a, b = polar(330, hueco[1]), polar(330, hueco[0] + 360)
d.style(W, 26).path(f"M{a[0]:.1f} {a[1]:.1f} A330 330 0 1 1 {b[0]:.1f} {b[1]:.1f}")
libre = lambda ang, m: not (hueco[0] - m <= ang <= hueco[1] + m)
d.style(W, 6)
for k in range(60):
    if libre(k * 6, 4) and k % 5:
        radial(d, 270, 288, k * 6)
d.style(O, 12)
for ang in range(0, 360, 30):                                    # marcas mayores en acento
    if libre(ang, 4):
        radial(d, 244, 288, ang)
d.style(O, 40).path("M370 345 C 370 255, 530 255, 530 345 C 530 410, 450 410, 450 480 L 450 505")   # "?"
d.style(O, 4, fill=O).circle(450, 590, 50)
d.save(P, "emblema")

# Retícula de 60 px a tamaño de banner
d = Doc(2560, 1440)
d.style("#1E1E1E", 1).add("shape.rectangularGrid", x=0, y=0, width=2560, height=1440, rows=24, columns=43)
d.save(P, "reticula_banner")
d = Doc(800, 800)
d.style("#1E1E1E", 1).add("shape.rectangularGrid", x=0, y=0, width=800, height=800, rows=13, columns=13)
d.save(P, "reticula_avatar")
