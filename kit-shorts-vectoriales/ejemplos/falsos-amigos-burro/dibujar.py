"""Ilustraciones de "Burro: el falso amigo que es mantequilla" (VectorCraft).
Corre: python3 dibujar.py <esta carpeta>"""
import math, os, sys
sys.path.insert(0, os.environ.get("KIT_SHORTS", os.path.expanduser(
    "~/Documents/Artcarft/kit-shorts-vectoriales/skills/shorts-vectoriales/scripts")))
from vc import Doc, polar, radial, hoja_contactos, suave, O, W, G, NEGRO, C

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
# Paleta por material — base · sombra (más fría) · luz (más cálida); tinta W y papel NEGRO vienen del tema
MANT, MANT_S, MANT_L = "#FFCF4A", "#E0A22E", "#FFE48C"
PAN, PAN_S, PAN_L = "#E3A95C", "#B9783A", "#F2CB8E"
BURRO_B, BURRO_S, BURRO_L, CASCO = "#B9AFA1", "#8D8477", "#DAD2C4", "#4E443B"
VACA_B, VACA_MANCHA, VACA_HOCICO, CUERNO = "#F6F0E4", "#5C4636", "#E8A9A0", "#E9DAB4"
QUESO, QUESO_S, QUESO_L = "#F4C24C", "#D6992B", "#FAD97E"
METAL, METAL_S = "#B9C3C9", "#8D98A0"
GC = G


def cerrado(d, pts):
    d.path(suave(pts, True))


# ── Burro de perfil (mira a la derecha): orejas largas, crin corta, cola con borla, cascos ──
d = Doc()
d.style(W, 4, fill=BURRO_S); cerrado(d, [(618, 292), (590, 175), (606, 150), (634, 200), (644, 284)])   # oreja de atrás
d.style(W, 4, fill=BURRO_B); cerrado(d, [(640, 286), (664, 168), (684, 150), (690, 196), (666, 296)])   # oreja de delante
d.style(GC, 2); d.line(612, 270, 606, 190); d.line(660, 272, 676, 190)                                  # interior de las orejas
d.style(GC, 4)
for x in (300, 545):                                                                                    # patas del lado lejano (sombra)
    d.style(GC, 3, fill=BURRO_S).path(f"M{x - 12} 515 L{x - 8} 760 L{x + 10} 760 L{x + 14} 515 Z"); d.style(GC, 3, fill=CASCO).rect(x - 14, 760, 28, 22, radius=4)
d.style(W, 4).path("M205 432 C176 500 168 560 172 612")                                              # cola
for dx in (-14, -6, 2, 10):
    d.line(172, 606, 172 + dx * 1.6, 662)                                                               # borla
d.style(W, 5, fill=BURRO_B)
CUERPO = [(205, 425), (250, 398), (330, 386), (420, 388), (510, 390), (555, 370), (595, 325), (625, 292),
          (655, 285), (690, 330), (718, 385), (712, 420), (680, 428), (640, 412), (605, 430), (585, 472),
          (560, 520), (500, 542), (420, 548), (330, 544), (270, 532), (222, 500), (200, 460)]
cerrado(d, CUERPO)
for x in (275, 520):                                                                                    # patas del lado cercano
    d.style(W, 5, fill=BURRO_B).path(f"M{x - 16} 515 L{x - 11} 760 L{x + 11} 760 L{x + 16} 515")
    d.style(W, 4, fill=CASCO).rect(x - 15, 760, 30, 24, radius=4)                                      # cascos
d.style(GC, 3)
for k in range(7):                                                                                      # crin
    x, y = 530 + k * 14, 380 - k * 14
    d.line(x, y, x - 14, y - 18)
d.style(BURRO_L, 1, fill=BURRO_L).path(suave([(686, 352), (712, 384), (708, 414), (684, 420), (676, 384)], True))   # hocico claro
d.style(GC, 3).path("M690 356 C700 372 704 392 698 412")
d.style(W, 3).path("M686 418 Q700 424 712 414")                                                         # boca
d.style(W, 2, fill=W).circle(652, 322, 14); d.style(BURRO_L, 1, fill="#FFFDF4").circle(656, 318, 5)    # ojo con brillo
d.style(W, 3).add("shape.ellipse", x=700, y=388, width=12, height=8)                                    # fosa nasal
d.style(BURRO_L, 1, fill=BURRO_L).path(suave([(300, 488), (400, 515), (500, 498), (480, 535), (330, 530)], True))   # vientre claro
d.style(GC, 3).path("M300 470 C360 500 440 505 500 482")
d.save(P, "burro")

# ── Cabeza de vaca de frente: cuernos, orejas, manchas, hocico con fosas ──
d = Doc()
d.style(W, 3, fill=CUERNO); cerrado(d, [(352, 255), (300, 190), (262, 152), (282, 168), (330, 215), (372, 250)])   # cuernos
cerrado(d, [(548, 255), (600, 190), (638, 152), (618, 168), (570, 215), (528, 250)])
d.style(W, 4, fill=VACA_B); cerrado(d, [(345, 290), (240, 270), (220, 300), (255, 325), (345, 320)])       # orejas
cerrado(d, [(555, 290), (660, 270), (680, 300), (645, 325), (555, 320)])
d.style(W, 5, fill=VACA_B); cerrado(d, [(340, 250), (450, 228), (560, 250), (575, 330), (548, 430), (520, 505), (380, 505), (352, 430), (325, 330)])
d.style(W, 3, fill=VACA_MANCHA); cerrado(d, [(470, 250), (530, 262), (548, 320), (505, 340), (472, 300)])     # mancha
d.style(W, 3, fill=VACA_MANCHA); cerrado(d, [(352, 360), (390, 350), (395, 400), (360, 420)])
d.style(W, 2, fill=W); d.circle(400, 350, 18); d.circle(500, 350, 18)                                       # ojos
d.style(W, 5, fill=VACA_HOCICO); cerrado(d, [(360, 480), (450, 462), (540, 480), (556, 540), (520, 590), (380, 590), (344, 540)])  # hocico
d.style(W, 4, fill=VACA_MANCHA); d.add("shape.ellipse", x=395, y=520, width=34, height=44); d.add("shape.ellipse", x=471, y=520, width=34, height=44)
d.style(GC, 3).path("M410 236 Q430 210 450 236 Q470 210 490 236")                                       # mechón
d.save(P, "vaca")

# ── Queso en cuña con agujeros ──
d = Doc()
d.style(W, 5, fill=QUESO); d.path("M260 470 L640 470 L640 600 L260 600 Z")                          # cara frontal (base)
d.style(W, 5, fill=QUESO_L); d.path("M260 470 L640 470 L520 330 Z")                                  # cara superior (luz)
d.style(W, 5); d.line(640, 600, 640, 470)
d.style(QUESO_S, 3, fill=QUESO_S)
for cx, cy, r in ((330, 530, 22), (430, 560, 16), (540, 520, 26), (600, 575, 12), (470, 500, 10)):
    d.circle(cx, cy, 2 * r)
d.add("shape.ellipse", x=480, y=420, width=40, height=18); d.add("shape.ellipse", x=420, y=448, width=26, height=12)
d.save(P, "queso")

# ── Panino tipo chapata abierta, con mantequilla untada ──
d = Doc()
d.style(W, 5, fill=PAN); d.path(suave([(140, 530), (170, 455), (300, 410), (450, 398), (600, 410), (730, 455), (760, 530)]) + " Z")   # pan de arriba
d.style(GC, 4)
for x in (260, 360, 460, 560, 650):
    d.path(f"M{x} 455 Q{x + 30} 430 {x + 55} 440")                                                   # cortes del pan
d.style(MANT_S, 3, fill=MANT); d.path(suave([(150, 540), (300, 556), (450, 548), (600, 560), (750, 540), (752, 566), (600, 586), (450, 576), (300, 588), (148, 566)], True))
d.style(W, 5, fill=PAN_S); d.path(suave([(140, 580), (450, 572), (760, 580), (745, 640), (450, 652), (155, 640)], True))   # pan de abajo
d.save(P, "panino")

# ── Barra de mantequilla con papel abierto y cuchillo ──
d = Doc()
d.style(W, 5, fill=MANT_L); d.path("M230 470 L560 470 L680 390 L350 390 Z")                         # cara de arriba (luz)
d.style(W, 5, fill=MANT); d.path("M230 470 L560 470 L560 580 L230 580 Z")                           # frente (base)
d.style(W, 5, fill=MANT_S); d.path("M560 470 L680 390 L680 500 L560 580 Z")                         # lateral (sombra)
d.style(GC, 2, fill="#F4EFE4"); d.path("M230 520 L560 520 L560 580 L230 580 Z"); d.path("M560 520 L680 440 L680 500 L560 580 Z")   # papel
d.style(GC, 3); d.path("M230 520 L560 520 L680 440")                                                # borde del papel
d.style(W, 4).path("M330 400 C340 340 400 330 420 360")                                             # rizo de mantequilla
d.style(W, 4, fill=METAL); d.path("M600 250 L760 170 L775 190 L620 275 Z"); d.style(W, 6).line(610, 262, 530, 305)   # cuchillo
d.save(P, "mantequilla")

# ── Tachadura (X) ──
d = Doc(); d.style(O, 24); d.line(220, 220, 680, 680); d.line(680, 220, 220, 680); d.save(P, "tacha")

# ── Burbujas de diálogo: mismo texto, dos idiomas ──
d = Doc()
d.style(W, 5, fill="#FFFDF4").path("M120 260 Q120 240 140 240 L420 240 Q440 240 440 260 L440 410 Q440 430 420 430 L220 430 L160 490 L175 430 L140 430 Q120 430 120 410 Z")
d.style(O, 5, fill="#FFFDF4").path("M460 460 Q460 440 480 440 L760 440 Q780 440 780 460 L780 610 Q780 630 760 630 L725 630 L740 690 L680 630 L480 630 Q460 630 460 610 Z")
d.save(P, "burbujas")

# ── Iconos de los ejemplos ──
d = Doc()
d.style(W, 6).path("M150 750 L150 650 L300 650 L300 550 L450 550 L450 450 L600 450 L600 350 L750 350")   # escalera
d.style(O, 8); d.line(250, 450, 430, 250); d.line(430, 250, 370, 262); d.line(430, 250, 420, 310)
d.save(P, "escalera")
d = Doc()
d.style(W, 6).path(suave([(150, 450), (300, 330), (450, 300), (600, 330), (750, 450), (600, 570), (450, 600), (300, 570)], True))
d.style(W, 5).circle(450, 450, 230); d.style(O, 5, fill=O).circle(450, 450, 100)
d.style(W, 2, fill=W).circle(480, 420, 26)
d.save(P, "ojo_icono")
d = Doc()
d.style(W, 6).path("M170 470 L730 470 C720 620 600 700 450 700 C300 700 180 620 170 470 Z")          # cuenco
d.style(W, 5).line(380, 700, 360, 750); d.line(520, 700, 540, 750); d.line(330, 750, 570, 750)
d.style(O, 5)
for x in (340, 450, 560):
    d.path(f"M{x} 430 C{x - 30} 380 {x + 30} 340 {x} 290 C{x - 30} 240 {x + 30} 200 {x} 160")      # vapor
d.save(P, "sopa")

# ── Dos raíces que se juntan en una palabra ──
d = Doc()
d.style(O, 7).path(suave([(160, 830), (210, 700), (330, 560), (420, 420), (450, 260)]))
d.style(GC, 7).path(suave([(740, 830), (690, 700), (570, 560), (480, 420), (450, 260)]))
d.style(O, 3)
for x, y, dx in ((210, 700, -60), (330, 560, -70), (280, 640, 60)):
    d.path(f"M{x} {y} Q{x + dx * 0.5} {y + 30} {x + dx} {y + 60}")
d.style(GC, 3)
for x, y, dx in ((690, 700, 60), (570, 560, 70), (620, 640, -60)):
    d.path(f"M{x} {y} Q{x + dx * 0.5} {y + 30} {x + dx} {y + 60}")
d.save(P, "raices")
d = Doc(); d.style(W, 5, fill=NEGRO).rect(250, 30, 400, 140, radius=24); d.save(P, "nudo_burro")    # recuadro donde se juntan

# ── Tarro de ungüento + venda ──
d = Doc()
d.style(W, 5, fill="#E3ECEE"); d.path("M300 330 L600 330 L620 380 L610 690 Q600 720 570 720 L330 720 Q300 720 290 690 L280 380 Z")
d.style(W, 5, fill=PAN_S).rect(285, 280, 330, 60, radius=14)                                          # tapa
d.style(MANT, 4, fill=MANT); d.path("M300 390 Q450 360 600 390 L600 420 Q450 395 300 420 Z")          # mantequilla dentro
d.style(GC, 3).rect(340, 480, 220, 150, radius=10)                                                    # etiqueta
d.style(GC, 2); d.line(370, 530, 530, 530); d.line(370, 570, 500, 570)
d.save(P, "tarro")
d = Doc()
d.style(W, 5).circle(450, 450, 260); d.style(GC, 4).circle(450, 450, 120)
d.style(W, 5).path("M580 450 L800 450 L800 540 L560 540")
d.save(P, "venda")

# ── Cadena vertical de 4 cajas con flechas ──
d = Doc()
for k, y in enumerate((160, 340, 520, 700)):
    d.style(O if k == 3 else W, 5).rect(150, y - 55, 600, 110, radius=20)
    if k < 3:
        d.style(GC, 4).line(450, y + 60, 450, y + 120); d.line(450, y + 120, 432, y + 100); d.line(450, y + 120, 468, y + 100)
d.save(P, "cadena4")

# ── Radial: de butyrum a las lenguas + matraz ──
d = Doc()
d.style(O, 5).circle(450, 320, 220)
d.style(GC, 4, dash=[10, 10])
for x, y in ((130, 80), (770, 80), (130, 570), (770, 570)):
    ang = math.atan2(y - 320, x - 450)
    d.line(450 + 115 * math.cos(ang), 320 + 115 * math.sin(ang), x, y)
d.save(P, "radial")
d = Doc()
d.style(W, 6).path("M400 160 L400 380 L250 680 Q240 720 290 720 L610 720 Q660 720 650 680 L500 380 L500 160")
d.style(W, 5).line(380, 160, 520, 160)
d.style(MANT, 4, fill=MANT); d.path("M330 560 L570 560 L640 690 Q645 705 620 705 L280 705 Q255 705 262 690 Z")
d.style(G, 3)
for x, y in ((420, 620), (480, 650), (450, 590)):
    d.circle(x, y, 22)
d.style(GC, 4); d.path("M430 130 C400 90 460 60 430 20"); d.path("M480 120 C450 80 510 50 480 10")    # olor
d.save(P, "matraz")

# ── Interrogación, color rojizo y lana ──
d = Doc()
d.style(O, 40).path("M340 330 C340 200 560 200 560 330 C560 420 450 420 450 520 L450 560")
d.style(O, 4, fill=O).circle(450, 670, 70)
d.save(P, "interrogacion")
d = Doc()                                                                                               # muestrario de color (tonos rojizos)
d.style(W, 5, fill=NEGRO).rect(300, 180, 300, 560, radius=16)
for k, c in enumerate(("#C8643C", "#A5452A", "#7A3020")):
    d.style(c, 2, fill=c).rect(325, 205 + k * 150, 250, 125, radius=6)
d.style(W, 3).line(325, 680, 520, 680); d.line(325, 710, 460, 710)
d.save(P, "muestra_rojiza")
d = Doc()                                                                                               # ovillo de lana con hebra suelta
d.style(W, 5, fill="#E9DCC4").circle(430, 430, 380)
d.style("#CDBB9C", 1, fill="#CDBB9C").path(suave([(560, 330), (615, 430), (585, 545), (480, 615), (520, 500), (560, 420)], True))   # sombra
d.style(GC, 3)
for k in range(5):
    d.path(f"M{270 + k * 18} {330 + k * 40} C{360 + k * 10} {250 + k * 30} {520 - k * 10} {290 + k * 30} {600 - k * 12} {380 + k * 35}")
for k in range(4):
    d.path(f"M{330 + k * 45} {270} C{300 + k * 50} {380} {330 + k * 50} {500} {400 + k * 40} {600}")
d.style(W, 4).path("M560 560 C620 640 700 600 720 680 C740 740 680 760 700 800")                    # hebra
d.save(P, "lana")

# ── Olla de risotto, cuchara (pivote en el centro) y vapor ──
d = Doc()
d.style(W, 6, fill=METAL); d.path("M180 470 L720 470 L690 720 Q680 760 640 760 L260 760 Q220 760 210 720 Z")
d.style(METAL_S, 1, fill=METAL_S).path("M560 480 L710 480 L684 716 Q676 748 640 750 L600 750 Z")      # sombra propia
d.style(W, 6); d.line(140, 500, 180, 500); d.line(720, 500, 760, 500)
d.style(MANT, 4)
for x, y in ((290, 500), (360, 520), (440, 498), (520, 518), (600, 500), (330, 545), (480, 545), (560, 548), (400, 562)):
    d.add("shape.ellipse", x=x - 14, y=y - 6, width=28, height=12, rotation=20)                        # arroz
d.save(P, "olla")
d = Doc(); d.style(W, 8).line(450, 450, 560, 120); d.style(W, 5, fill=NEGRO).add("shape.ellipse", x=405, y=430, width=70, height=110, rotation=-18); d.save(P, "cuchara")
d = Doc(); d.style(GC, 4)
for x in (300, 450, 600):
    d.path(f"M{x} 420 C{x - 30} 370 {x + 30} 330 {x} 280 C{x - 30} 230 {x + 30} 190 {x} 150")
d.save(P, "vapor")

hoja_contactos(P, ["burro", "vaca", "queso", "panino", "mantequilla", "burbujas", "escalera", "ojo_icono", "sopa",
                   "raices", "tarro", "cadena4", "radial", "matraz", "interrogacion", "lana", "muestra_rojiza", "olla"],
               os.path.join(P, "revision", "ilustraciones.png"), columnas=6, celda=320)
