"""Ilustraciones de "Por qué los ritmos latinos te hacen moverte" (VectorCraft).
Las piezas que giran (pie, brazo del metrónomo, manecillas, aguja) tienen su pivote en el centro
del lienzo (450, 450): EffectCraft rota cada capa alrededor de ese punto.
Corre: python3 dibujar.py <esta carpeta>"""
import math, os, sys
sys.path.insert(0, os.environ.get("KIT_SHORTS", os.path.expanduser(
    "~/Documents/Artcarft/kit-shorts-vectoriales/skills/shorts-vectoriales/scripts")))
from vc import Doc, polar, radial, hoja_contactos, O, W, G, NEGRO, C

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
AZ, AM, GR = "#3D7BFF", "#FFD23F", "#BBBBBB"
CLAVE = [0, 3, 6, 10, 12]                       # clave de son 3-2 en 16 corcheas (2 compases)


def pts(lst):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in lst)


import random
random.seed(7)


def suave(p, cerrado=False):
    """Curva suave (Catmull-Rom → Bézier) que pasa por los puntos: trazo orgánico, no poligonal."""
    if cerrado:
        p = [p[-1]] + p + [p[0], p[1]]
    else:
        p = [p[0]] + p + [p[-1]]
    d = f"M{p[1][0]:.1f} {p[1][1]:.1f}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + (" Z" if cerrado else "")


def dentro(pt, poly):
    x, y, c = pt[0], pt[1], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


# 1 · Pie: zapatilla de perfil con calcetín (pivote en el talón = centro del lienzo) + suelo + notas
d = Doc()
d.style(W, 5).path("M432 452 L792 452 Q834 452 834 428 Q834 406 810 402 L432 402 Q408 402 408 427 Q408 452 432 452 Z")   # suela
d.style(G, 3)
for x in range(450, 800, 30):
    d.line(x, 440, x + 10, 452)                                                                 # dibujo de la suela
d.line(420, 418, 826, 418)                                                                      # entresuela
d.style(W, 5).path("M416 402 C400 350 400 300 418 262 Q470 284 535 252 L552 210 Q568 196 586 212 L592 242 "
                   "C660 290 740 330 800 358 Q838 378 828 402 Z")                                    # empeine y talón
d.style(G, 3).path("M733 402 Q740 360 796 356")                                                 # puntera
d.style(G, 3).path("M418 262 Q478 330 458 402")                                                 # contrafuerte del talón
d.style(G, 3).path("M478 390 C548 372 606 336 668 306"); d.path("M492 402 C560 386 620 352 690 318")   # franjas laterales
ojal = [(565 + k * 34, 252 + k * 16) for k in range(5)]
d.style(W, 3)
for (x1, y1), (x2, y2) in zip(ojal, ojal[1:]):
    d.line(x1 - 8, y1 + 14, x2 + 8, y2 - 14); d.line(x1 + 8, y1 - 14, x2 - 8, y2 + 14)       # cordones cruzados
d.style(W, 2, fill=NEGRO)
for x, y in ojal:
    d.circle(x - 8, y + 14, 9); d.circle(x + 8, y - 14, 9)                                     # ojales
d.style(W, 3).path("M560 236 C520 200 540 180 566 222"); d.path("M566 222 C600 186 620 206 576 236")    # lazo
d.style(W, 5).path("M422 262 L418 200 L528 196 L535 252")                                      # calcetín
d.style(G, 2)
for x in range(436, 526, 14):
    d.line(x, 203, x + 1, 226)                                                                  # elástico
d.save(P, "pie")
d = Doc(); d.style(G, 3).line(120, 456, 800, 456); d.save(P, "suelo")
d = Doc()
for x, y in ((250, 180), (650, 130)):
    d.style(O, 5, fill=O).add("shape.ellipse", x=x - 30, y=y + 70, width=50, height=36, rotation=-20)
    d.style(O, 6).line(x + 16, y + 80, x + 16, y - 20)
    d.path(f"M{x + 16} {y - 20} Q{x + 60} {y} {x + 46} {y + 40}")
d.save(P, "notas")

# 2 · Cerebro de perfil (frente a la izquierda) con los surcos que definen sus lóbulos
CONTORNO = [(185, 455), (150, 380), (155, 300), (195, 225), (265, 170), (350, 135), (445, 122), (540, 130), (625, 160),
            (695, 210), (740, 280), (752, 355), (730, 420), (690, 455), (640, 470), (585, 495), (520, 522), (450, 535),
            (380, 530), (330, 505), (312, 472), (270, 466)]
CEREBELO = [(575, 500), (640, 478), (700, 470), (737, 500), (732, 545), (690, 577), (630, 586), (580, 566), (558, 530)]
SURCO = "#A8A8A8"


def ondula(p, amp=7, cada=26, semilla=0):
    """Añade un serpenteo suave perpendicular al trazo (los surcos no son rectos)."""
    rnd = random.Random(semilla); out = []
    for (x1, y1), (x2, y2) in zip(p, p[1:]):
        largo = math.hypot(x2 - x1, y2 - y1); n = max(1, int(largo / cada))
        nx, ny = -(y2 - y1) / largo, (x2 - x1) / largo
        for k in range(n):
            t = k / n; w = amp * math.sin((len(out) + 1) * 1.9) * rnd.uniform(0.6, 1.0)
            out.append((x1 + (x2 - x1) * t + nx * w, y1 + (y2 - y1) * t + ny * w))
    return out + [p[-1]]


CENTRAL = [(470, 124), (456, 180), (470, 232), (448, 290), (458, 340), (432, 392)]
SILVIO = [(316, 470), (380, 448), (450, 416), (530, 382), (585, 366), (612, 372)]
SURCOS = [
    [(414, 136), (400, 190), (410, 240), (392, 296), (398, 344), (376, 404)],          # precentral
    [(528, 134), (514, 186), (526, 236), (506, 292), (512, 336), (494, 372)],          # postcentral
    [(404, 205), (340, 210), (272, 230), (214, 262)],                                  # frontal superior
    [(394, 300), (322, 318), (252, 344), (192, 372)],                                  # frontal inferior
    [(348, 494), (430, 470), (520, 440), (600, 420), (664, 428)],                      # temporal superior
    [(392, 522), (470, 506), (560, 482), (642, 456), (690, 444)],                      # temporal inferior
    [(520, 252), (575, 252), (630, 268), (676, 304), (706, 356)],                      # intraparietal
    [(612, 176), (638, 222), (630, 252)], [(700, 384), (726, 414)], [(668, 418), (716, 440)],   # parietal/occipital
    [(340, 452), (328, 410)], [(386, 436), (368, 396)],                                # opérculo frontal
    [(300, 175), (318, 214)], [(220, 300), (262, 290)], [(560, 330), (606, 318), (640, 336)],
    [(250, 196), (262, 236)], [(176, 330), (214, 322)], [(300, 262), (346, 252)], [(286, 390), (330, 372)],   # secundarios frontales
    [(566, 196), (582, 232)], [(660, 236), (700, 262)], [(726, 300), (712, 330)], [(600, 300), (640, 290)],  # parietales/occipitales
]
d = Doc()
d.style(W, 4).path("M505 520 C512 580 520 640 530 705"); d.path("M556 512 C566 580 570 640 574 705")   # tronco
d.style(W, 5, fill=NEGRO).path(suave(CEREBELO, True))
d.style(SURCO, 3)
for k in range(4):                                                                              # láminas del cerebelo
    d.path(suave(ondula([(578 + k * 4, 512 + k * 15), (650, 498 + k * 19), (726, 506 + k * 17)], 4, 18, 40 + k)))
d.style(W, 6, fill=NEGRO).path(suave(CONTORNO, True))
d.style(SURCO, 3)
for i, s_ in enumerate(SURCOS):
    d.path(suave(ondula(s_, 6, 24, i)))
d.style(W, 4).path(suave(ondula(SILVIO, 5, 30, 99)))                                            # cisura de Silvio
d.style(W, 4).path(suave(ondula(CENTRAL, 4, 30, 98)))                                           # surco central
d.save(P, "cerebro")
# área motora suplementaria: franja alta del lóbulo frontal, delante del surco precentral
d = Doc(); d.style(O, 4, fill=O).path(suave([(296, 158), (350, 137), (410, 127), (408, 168), (356, 180), (308, 198)], True)); d.save(P, "zona_sma")
# ganglios basales (en profundidad): núcleo caudado en forma de C + putamen, con línea discontinua
d = Doc()
d.style(O, 6, dash=[10, 8]).path(suave([(470, 300), (430, 262), (372, 262), (338, 298), (344, 344), (380, 368)]))   # caudado
d.style(O, 4, fill=O).path(suave([(392, 318), (440, 302), (478, 322), (470, 360), (420, 372), (388, 352)], True))  # putamen
d.save(P, "zona_gb")

# 3 · Línea de tiempo + golpes
d = Doc()
d.style(W, 4).line(100, 450, 800, 450); d.line(800, 450, 778, 436); d.line(800, 450, 778, 464)
d.style(G, 3)
for x in (200, 350, 500, 650):
    d.line(x, 430, x, 470)
d.save(P, "linea_tiempo")
d = Doc(); d.style(W, 4, fill=W).circle(C, C, 90); d.save(P, "golpe")
d = Doc(); d.style(O, 6, dash=[10, 10]).circle(C, C, 96); d.save(P, "golpe_pred")

# 4 · Metrónomo (pivote del brazo en el centro)
d = Doc()
d.style(W, 5).path("M370 70 L530 70 L650 600 L250 600 Z")
d.style(W, 5).rect(220, 600, 460, 50, radius=10)
d.style(G, 3)
for k in range(9):
    y = 140 + k * 30
    d.line(440, y, 460, y)
d.style(W, 4, fill=NEGRO).circle(C, C, 22)
d.save(P, "metronomo")
d = Doc()
d.style(W, 8).line(450, 450, 450, 100)
d.style(O, 4, fill=O).rect(420, 190, 60, 46, radius=6)
d.save(P, "metronomo_brazo")

# 5 · Rejilla de 2 compases (16 corcheas) con golpes sincopados y el hueco del primer tiempo
celda = lambda k: (90 + (k % 8) * 90 + 45, 360 if k < 8 else 520)
d = Doc()
d.style(G, 2)
for k in range(16):
    x, y = celda(k)
    d.rect(x - 38, y - 38, 76, 76, radius=8)
d.style(W, 3)
for k in range(0, 16, 2):                       # marcas de pulso (negras)
    x, y = celda(k); d.line(x, y - 58, x, y - 46)
d.save(P, "rejilla")
d = Doc(); d.style(W, 3, fill=W)
for k in CLAVE:
    x, y = celda(k); d.circle(x, y, 52)
d.save(P, "sinc_golpes")
# el golpe que llega antes: fantasma punteado donde "debía" caer (paso 4) → flecha limpia al paso 3
d = Doc(); x1, y1 = celda(4); x0, _ = celda(3)
d.style(G, 3, dash=[7, 7]).circle(x1, y1, 52)                                                   # dónde se esperaba
ctrl = ((x0 + x1) / 2, y1 - 120); fin = (x0 + 6, y1 - 50)
d.style(O, 5).path(f"M{x1 - 4} {y1 - 50} Q{ctrl[0]} {ctrl[1]} {fin[0]} {fin[1]}")
ang = math.atan2(fin[1] - ctrl[1], fin[0] - ctrl[0])                                            # punta alineada con la curva
pa = [(fin[0] + 8 * math.cos(ang), fin[1] + 8 * math.sin(ang))] + \
     [(fin[0] - 24 * math.cos(ang + s_) , fin[1] - 24 * math.sin(ang + s_)) for s_ in (0.5, -0.5)]
d.style(O, 2, fill=O).path(f"M{pa[0][0]:.1f} {pa[0][1]:.1f} L{pa[1][0]:.1f} {pa[1][1]:.1f} L{pa[2][0]:.1f} {pa[2][1]:.1f} Z")
d.save(P, "sinc_flecha")
d = Doc(); x, y = celda(8); d.style(O, 6, dash=[10, 9]).circle(x, y, 64); d.save(P, "sinc_hueco")

# 6 · U invertida (síncopa vs ganas de bailar) + puntos
d = Doc()
d.style(W, 3); d.line(120, 720, 800, 720); d.line(120, 720, 120, 120)
d.style(W, 6).path("M160 690 Q450 -120 780 690")
d.save(P, "curva_u")
for nombre, (x, y), color, dd in (("punto_poca", (248, 483), W, 40), ("punto_mucha", (682, 483), W, 40), ("punto_medio", (460, 285), O, 64)):
    d = Doc(); d.style(color, 3, fill=color).circle(x, y, dd); d.save(P, nombre)

# 7 · Collar de la clave: 16 pasos en círculo, los 5 golpes y la manecilla (pivote al centro)
d = Doc()
d.style(G, 2).circle(C, C, 640)
d.style(W, 3)
for k in range(16):
    x, y = polar(320, k * 22.5); d.circle(x, y, 26)
d.style(W, 5); radial(d, 345, 380, 0); radial(d, 345, 380, 180)          # inicio de cada compás
d.save(P, "clave_collar")
d = Doc()
golpes = [polar(320, k * 22.5) for k in CLAVE]
d.style(O, 3).path(pts(golpes) + " Z")
d.style(O, 3, fill=O)
for x, y in golpes:
    d.circle(x, y, 64)
d.save(P, "clave_golpes")
d = Doc(); d.style(W, 6); radial(d, 0, 285, 0); d.style(W, 4, fill=W).circle(C, C, 26); d.save(P, "manecilla")
d = Doc(); d.style(W, 5); radial(d, 0, 360, 0); d.style(W, 4, fill=W).circle(C, C, 26); d.save(P, "manecilla_grande")

# 8 · Anillos: cada instrumento en su órbita (mismo ciclo de 16 corcheas)
ANILLOS = [("anillo_clave", 340, CLAVE, O, 46), ("anillo_conga", 275, [2, 6, 7, 10, 14, 15], W, 34),
           ("anillo_campana", 212, [0, 2, 4, 6, 8, 10, 12, 14], AM, 28),
           ("anillo_guiro", 152, [0, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15], GR, 20), ("anillo_bajo", 92, [3, 6, 11, 14], AZ, 26)]
for nombre, r, hits, color, dd in ANILLOS:
    d = Doc()
    d.style(G, 2).circle(C, C, 2 * r)
    d.style(color, 2, fill=color)
    for k in hits:
        x, y = polar(r, k * 22.5); d.circle(x, y, dd)
    d.save(P, nombre)

# 9 · Tumbao: un compás de 8 corcheas, el bajo en "2-y" y "4", el 1 vacío
cel = lambda k: (90 + k * 90 + 45, 400)
d = Doc(); d.style(G, 2)
for k in range(8):
    x, y = cel(k); d.rect(x - 38, y - 38, 76, 76, radius=8)
d.style(W, 3)
for k in range(0, 8, 2):
    x, y = cel(k); d.line(x, y - 58, x, y - 46)
d.save(P, "tumbao_barra")
d = Doc(); d.style(AZ, 3, fill=AZ)
for k in (3, 6):
    x, y = cel(k); d.rect(x - 30, y - 30, 60, 60, radius=12)
d.save(P, "tumbao_notas")
d = Doc(); x, y = cel(0); d.style(O, 6, dash=[10, 9]).circle(x, y, 70); d.save(P, "tumbao_hueco")

# 10 · Altavoz de graves, ondas y público
d = Doc()
d.style(W, 5).rect(330, 110, 240, 360, radius=14)
d.style(W, 4).circle(450, 220, 160); d.style(G, 3).circle(450, 220, 70)
d.style(W, 4).circle(450, 380, 110); d.style(G, 3).circle(450, 380, 46)
d.save(P, "altavoz")
d = Doc(); d.style(AZ, 4, dash=[12, 10])
for r in (230, 300, 370):
    a1, a2 = polar(r, 205, 450, 290), polar(r, 335, 450, 290)
    d.path(f"M{a1[0]:.1f} {a1[1]:.1f} A{r} {r} 0 0 1 {a2[0]:.1f} {a2[1]:.1f}")
    a1, a2 = polar(r, 25, 450, 290), polar(r, 155, 450, 290)
    d.path(f"M{a1[0]:.1f} {a1[1]:.1f} A{r} {r} 0 0 1 {a2[0]:.1f} {a2[1]:.1f}")
d.save(P, "ondas_graves")
d = Doc(); d.style(W, 4)
for k, x in enumerate(range(130, 800, 105)):
    y = 640
    d.circle(x, y, 40); d.line(x, y + 20, x, y + 120); d.line(x, y + 120, x - 22, y + 180); d.line(x, y + 120, x + 22, y + 180)
    if k % 2:
        d.line(x, y + 45, x - 34, y - 10); d.line(x, y + 45, x + 34, y - 10)      # brazos arriba
    else:
        d.line(x, y + 45, x - 34, y + 90); d.line(x, y + 45, x + 34, y + 90)
d.save(P, "publico")

# 11 · Oído interno: canales semicirculares (equilibrio) + cóclea
d = Doc()
d.style(W, 5).circle(360, 300, 200)
d.style(W, 5).add("shape.ellipse", x=420, y=150, width=130, height=230, rotation=30)
d.style(W, 5).add("shape.ellipse", x=280, y=380, width=240, height=110, rotation=-20)
d.style(O, 5).add("shape.spiral", cx=600, cy=540, radius=120, decay=80, segments=10)
d.style(G, 3); d.line(700, 470, 840, 420); d.line(705, 500, 845, 470)
d.save(P, "oido")

# 12 · Velocímetro de tempo (60–180 BPM, banda 100–130) + aguja en 120 + huellas
ang = lambda bpm: (bpm - 120) * 1.5
d = Doc()
a1, a2 = polar(300, -90), polar(300, 90)
d.style(W, 5).path(f"M{a1[0]:.1f} {a1[1]:.1f} A300 300 0 0 1 {a2[0]:.1f} {a2[1]:.1f}")
b1, b2 = polar(270, ang(100)), polar(270, ang(130))
d.style(O, 22).path(f"M{b1[0]:.1f} {b1[1]:.1f} A270 270 0 0 1 {b2[0]:.1f} {b2[1]:.1f}")
d.style(W, 3)
for bpm in range(60, 181, 10):
    radial(d, 300, 330 if bpm % 30 else 345, ang(bpm))
d.save(P, "velocimetro")
d = Doc(); d.style(W, 7); radial(d, 0, 250, ang(120)); d.style(W, 4, fill=W).circle(C, C, 30); d.save(P, "aguja")
for k in range(4):
    d = Doc()
    x, y = (380 if k % 2 == 0 else 520), 1570 - k * 0 + 0  # (posición final la da 'pos' implícito: lienzo centrado)
    cx, cy = (390 if k % 2 == 0 else 510), 760 - k * 120
    d.style(W, 4, fill="#2A2A2A").add("shape.ellipse", x=cx - 38, y=cy - 70, width=76, height=140, rotation=-8 if k % 2 == 0 else 8)
    for j in range(4):
        d.style(W, 2, fill=W).circle(cx - 28 + j * 19, cy - 88 - (j == 0) * 6, 16 - 2 * j)
    d.save(P, f"huella_{k}")

# 13 · Fiesta: guirnalda con focos que se encienden alternados + pareja bailando
Q = lambda t: ((1 - t) ** 2 * 60 + 2 * t * (1 - t) * 450 + t ** 2 * 840, (1 - t) ** 2 * 170 + 2 * t * (1 - t) * 420 + t ** 2 * 170)
d = Doc(); d.style(GR, 3).path("M60 170 Q450 420 840 170"); d.save(P, "guirnalda")
for nombre, par, colores in (("focos_a", 0, (O, AM)), ("focos_b", 1, (AZ, "#FF2BD6"))):
    d = Doc()
    for k in range(par, 11, 2):
        x, y = Q(0.05 + k * 0.09)
        c = colores[(k // 2) % 2]
        d.style(c, 2, fill=c).add("shape.ellipse", x=x - 16, y=y + 6, width=32, height=44)
    d.save(P, nombre)
d = Doc(); d.style(W, 5)
for x, brazo in ((360, 1), (540, -1)):
    d.circle(x, 470, 70); d.line(x, 505, x, 680); d.line(x, 680, x - 40, 800); d.line(x, 680, x + 50, 790)
    d.line(x, 560, x + brazo * 70, 520 if brazo > 0 else 600)
d.line(430, 520, 470, 600)                           # manos unidas
d.save(P, "pareja")

hoja_contactos(P, ["pie", "notas", "cerebro", "zona_sma", "linea_tiempo", "metronomo", "metronomo_brazo", "rejilla",
                   "sinc_golpes", "curva_u", "clave_collar", "clave_golpes", "anillo_conga", "anillo_campana",
                   "tumbao_barra", "tumbao_notas", "altavoz", "ondas_graves", "publico", "oido", "velocimetro",
                   "aguja", "huella_0", "guirnalda", "focos_a", "pareja"],
               os.path.join(P, "revision", "ilustraciones.png"), columnas=6, celda=320)

# 7b · Mapa del Atlántico con coordenadas reales (equirectangular: lon −100…20, lat 35…−35)
M = lambda lon, lat: ((lon + 92) * 7.5, (35 - lat) * 7.5 + 190)              # lon −92…28
COSTA_N_AM = [(-97.5, 25.9), (-94, 29.5), (-90, 29.1), (-89, 30.3), (-85, 29.7), (-83, 29), (-81.8, 26.3), (-80.4, 25.2),
              (-80.1, 26.9), (-81.3, 30.2), (-80.9, 32.1), (-78, 33.8), (-76, 35.2), (-75.6, 36.5)]
COSTA_S_AM = [(-97.5, 25.9), (-97.7, 22), (-96, 19), (-94.5, 18.2), (-91, 18.7), (-90.4, 21.3), (-87, 21.5), (-87.5, 18),
              (-88.3, 16), (-84, 15.8), (-83.3, 14), (-83.6, 11), (-81.5, 9), (-79.5, 9.4), (-77.5, 8.6), (-75.5, 10.5),
              (-71.5, 12.4), (-68, 10.5), (-62, 10.7), (-60, 8.5), (-57, 6), (-52, 5), (-50, 0), (-44, -2.5), (-38.5, -3.7),
              (-35, -6), (-35, -9), (-37.5, -12.5), (-39, -17), (-40.5, -21), (-42, -23), (-47, -25), (-48.5, -28),
              (-50, -31), (-52, -33), (-53.5, -34.5)]
PACIFICO_S_AM = [(-79.5, 9.4), (-80, 7.5), (-78.5, 3), (-80, -1), (-81, -5), (-79, -8), (-77, -12), (-74, -15.5), (-71, -18),
                 (-70.3, -22), (-70.5, -27), (-71.5, -32), (-71.6, -35)]
CUBA = [(-84.9, 21.9), (-83, 22.9), (-81, 23.2), (-79, 22.6), (-77, 21.5), (-75, 20.4), (-74.1, 20.2), (-74.6, 19.9),
        (-77.5, 19.9), (-78.2, 20.9), (-80.5, 22), (-82.5, 22.2)]
LA_ESPANOLA = [(-74.4, 19.8), (-72, 19.9), (-70, 19.7), (-68.4, 18.6), (-69, 18.2), (-71.5, 17.6), (-74.4, 18.4)]
AFRICA = [(28, 31.3), (20, 30.8), (19, 30.3), (15.5, 31.5), (11, 33.5), (11, 37.2), (10, 35.8), (5, 36.8), (-1, 35.7), (-6, 35.8), (-9.6, 30.5), (-13.2, 27.7), (-17, 21), (-16.8, 19),
          (-17.4, 14.7), (-15, 11), (-13.3, 9), (-11.5, 7), (-7.5, 4.4), (-4, 5.2), (0, 5.6), (2.6, 6.3), (5, 5.5),
          (6.5, 4.3), (8.5, 4.5), (9.6, 3), (9.3, 0), (9, -2), (11.8, -5), (12.3, -6), (13.3, -9), (12.5, -13.5),
          (11.8, -17.2), (14.4, -22.6), (15.2, -27), (16.5, -28.6), (18.3, -34), (20, -34.8), (25, -34), (28, -33)]
IBERIA = [(-8.9, 42), (-9.5, 39), (-8.9, 37), (-6, 36.9), (-5.6, 36), (-2, 36.7), (0, 38.7), (0.5, 40.5), (3.2, 42),
          (-1.5, 43.4), (-8, 43.7), (-9.3, 43)]
en_px = lambda lista: [M(*q) for q in lista]
d = Doc()
d.style(W, 4)
for costa in (COSTA_N_AM, COSTA_S_AM, AFRICA):
    d.path(suave(en_px(costa)))
d.style(G, 3).path(suave(en_px(PACIFICO_S_AM)))
d.style(W, 4).path(suave(en_px(IBERIA), True))
d.style(W, 3).path(suave(en_px(LA_ESPANOLA), True))
d.style(O, 5, fill=O).path(suave(en_px(CUBA), True))                                            # Cuba en acento
d.style(G, 2, dash=[3, 9]).line(*M(-92, 0), *M(28, 0))                                        # ecuador
d.save(P, "mapa")
a1, a2, a3 = M(4, 3.5), M(-35, 24), M(-73, 21)
d = Doc(); d.style(O, 5, dash=[14, 12]).path(f"M{a1[0]:.1f} {a1[1]:.1f} Q{a2[0]:.1f} {a2[1] - 120:.1f} {a3[0]:.1f} {a3[1]:.1f}")
d.line(a3[0], a3[1], a3[0] + 30, a3[1] - 12); d.line(a3[0], a3[1], a3[0] + 18, a3[1] + 24)
d.save(P, "ruta")

# 8b · Tres contra dos: dos filas que comparten el mismo ciclo
d = Doc(); d.style(G, 3)
for y in (370, 590):
    d.line(200, y, 820, y); d.line(250, y - 30, 250, y + 30); d.line(750, y - 30, 750, y + 30)
d.save(P, "filas_32")
d = Doc(); d.style(O, 3, fill=O).circle(C, C, 76); d.save(P, "dot_o")
d = Doc(); d.style(AZ, 3, fill=AZ).circle(C, C, 76); d.save(P, "dot_b")
