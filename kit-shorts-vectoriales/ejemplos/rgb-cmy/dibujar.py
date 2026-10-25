"""Ilustraciones de "RGB y CMYK: tres colores para engañar a tu ojo" (VectorCraft).
Corre: python3 dibujar.py <esta carpeta>"""
import math, os, random, sys
sys.path.insert(0, os.environ.get("KIT_SHORTS", os.path.expanduser(
    "~/Documents/Artcarft/kit-shorts-vectoriales/skills/shorts-vectoriales/scripts")))
from vc import Doc, polar, radial, hoja_contactos, O, W, G, NEGRO, C

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
random.seed(3)

R, V, A = "#FF0000", "#00FF00", "#0000FF"            # luz pura (mezcla aditiva exacta)
RL, VL, AL = "#FF3B30", "#2FD25A", "#3D7BFF"          # rojo/verde/azul para líneas y curvas
CI, MA, AM, K = "#00AEEF", "#EC008C", "#FFF200", "#1A1A1A"   # tintas de proceso
D = "#1A1A1A"                                          # línea oscura para escenas sobre papel


def espectral(nm):
    """Color aproximado de una longitud de onda visible (algoritmo de Dan Bruton)."""
    if nm < 440:   r, g, b = -(nm - 440) / 60, 0, 1
    elif nm < 490: r, g, b = 0, (nm - 440) / 50, 1
    elif nm < 510: r, g, b = 0, 1, -(nm - 510) / 20
    elif nm < 580: r, g, b = (nm - 510) / 70, 1, 0
    elif nm < 645: r, g, b = 1, -(nm - 645) / 65, 0
    else:          r, g, b = 1, 0, 0
    f = 0.3 + 0.7 * (nm - 380) / 40 if nm < 420 else (0.3 + 0.7 * (780 - nm) / 80 if nm > 700 else 1)
    return "#%02X%02X%02X" % tuple(int(255 * (c * f) ** 0.8) for c in (r, g, b))


def flecha(d, x1, y1, x2, y2, punta=22):
    d.line(x1, y1, x2, y2)
    a = math.atan2(y2 - y1, x2 - x1)
    for s in (-1, 1):
        d.line(x2, y2, x2 - punta * math.cos(a + s * 0.45), y2 - punta * math.sin(a + s * 0.45))


def onda(d, x1, x2, y, amp, periodo):
    pts = [(x, y + amp * math.sin((x - x1) / periodo * 2 * math.pi)) for x in range(int(x1), int(x2) + 1, 4)]
    d.path("M" + " L".join(f"{x:.1f} {yy:.1f}" for x, yy in pts))


def disco(d, color, diam):
    d.style(color, 1, fill=color).circle(C, C, diam)


# 1 · Teléfono + lupa con subpíxeles
d = Doc()
d.style(W, 5).rect(270, 40, 360, 800, radius=60)
d.style(G, 2).rect(295, 100, 310, 680, radius=20)
d.style(W, 4).rect(410, 62, 80, 14, radius=7)
d.save(P, "telefono")
d = Doc()
d.style(W, 3).rect(430, 250, 40, 40)
d.style(G, 2, dash=[4, 8]); d.line(430, 290, 330, 430); d.line(470, 290, 570, 430)
d.style(W, 5, fill=NEGRO).circle(C, 560, 300)
for fila in range(3):
    for col in range(3):
        x0, y0 = 360 + col * 62, 470 + fila * 62
        for k, color in enumerate((R, V, A)):
            d.style(color, 1, fill=color).rect(x0 + k * 18, y0, 13, 52, radius=3)
d.save(P, "subpixeles")

# 1b · Impresora (cuerpo con relleno negro para tapar la hoja mientras sale), cartuchos y hoja impresa
d = Doc()
d.style(G, 3, fill=NEGRO).path("M270 380 L320 190 L580 190 L630 380 Z")        # hoja en la bandeja de entrada
d.style(W, 5, fill=NEGRO).rect(150, 380, 600, 270, radius=30)                   # cuerpo
d.style(W, 4).rect(250, 420, 400, 110, radius=10)                               # ventana de cartuchos
d.style(W, 4).line(230, 590, 670, 590)                                          # ranura de salida
d.style(G, 3); d.circle(700, 430, 22); d.circle(700, 490, 22)                   # botones
d.style(W, 5).path("M200 650 L170 720 L730 720 L700 650")                       # bandeja de salida
d.save(P, "impresora")
d = Doc()
for k, c in enumerate((CI, MA, AM, "#2A2A2A")):
    d.style(W if k == 3 else c, 2, fill=c).rect(272 + k * 92, 434, 70, 82, radius=8)
d.save(P, "cartuchos")
d = Doc()
d.style(W, 3, fill="#F4F2EC").rect(300, 590, 300, 230, radius=4)
for k, c in enumerate((CI, MA, AM)):
    d.style(c, 1, fill=c).rect(330, 615 + k * 40, 240, 26, radius=3)
d.style("#BBBBBB", 3); d.line(330, 750, 520, 750); d.line(330, 780, 470, 780)
d.save(P, "hoja_impresa")

# 2 · Ojo en corte + conos
cx, cy = 430, 360
d = Doc()
d.style(W, 5).circle(cx, cy, 560)
d.style(W, 4).path(f"M170 230 A190 190 0 0 0 170 490")                    # córnea
d.style(W, 4).add("shape.ellipse", x=200, y=280, width=60, height=160)    # cristalino
d.style(G, 2, dash=[6, 10]); d.line(0, 300, 230, 330); d.line(230, 330, 705, 360); d.line(0, 420, 230, 390); d.line(230, 390, 705, 360)
a1, a2 = polar(278, 50, cx, cy), polar(278, 130, cx, cy)
d.style(O, 10).path(f"M{a1[0]:.1f} {a1[1]:.1f} A278 278 0 0 1 {a2[0]:.1f} {a2[1]:.1f}")   # retina
d.style(W, 5); d.line(700, 330, 860, 300); d.line(700, 390, 860, 420)     # nervio óptico
d.save(P, "ojo")
d = Doc()
d.style(G, 2, dash=[4, 8]); d.line(690, 420, 660, 640); d.line(690, 420, 240, 640)
for x, color in ((240, AL), (450, VL), (660, RL)):
    d.style(color, 6).path(f"M{x - 34} 820 L{x} 660 L{x + 34} 820 Z")
    d.style(color, 4, fill=color).circle(x, 850, 34)
d.save(P, "conos")

# 3 · Curvas de sensibilidad + franja del espectro
X = lambda nm: 100 + (nm - 380) * 700 / 320
d = Doc()
d.style(W, 3).line(90, 650, 810, 650)
d.style(G, 2)
for nm in range(400, 701, 50):
    d.line(X(nm), 650, X(nm), 665)
d.line(X(380), 650, X(380), 665)
for pico, sig, color in ((420, 28, AL), (530, 45, VL), (560, 52, RL)):
    pts = []
    for nm in range(380, 701, 4):
        s = sig * (0.8 if nm < pico else 1.15)
        pts.append((X(nm), 650 - 430 * math.exp(-((nm - pico) / s) ** 2 / 2)))
    d.style(color, 6).path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts))
d.save(P, "curvas")
d = Doc()
for nm in range(380, 700, 5):
    c = espectral(nm + 2.5)
    d.style(c, 0.5, fill=c).rect(X(nm), 420, X(nm + 5) - X(nm) + 0.6, 60)
d.save(P, "espectro")

# 4 · Proyectores de Maxwell + lazo
d = Doc()
d.style(W, 5).rect(200, 120, 500, 300, radius=8)
for x, color in ((250, R), (450, V), (650, A)):
    d.style(W, 4).rect(x - 60, 700, 120, 90, radius=10)
    d.style(color, 6).circle(x, 690, 44)
    d.style(color, 2, dash=[6, 8]); d.line(x - 20, 670, 205, 415); d.line(x + 20, 670, 695, 415)
d.save(P, "proyectores")
d = Doc()
d.style(O, 6)
d.path("M450 270 C 360 190, 300 220, 320 270 C 300 320, 360 350, 450 270 Z")
d.path("M450 270 C 540 190, 600 220, 580 270 C 600 320, 540 350, 450 270 Z")
d.path("M440 280 L400 380 M460 280 L500 380")
for k, color in enumerate((RL, VL, AL)):
    d.style(color, 3); d.line(330, 245 + k * 14, 445, 262 + k * 6); d.line(455, 262 + k * 6, 570, 245 + k * 14)
d.style(O, 5, fill=O).circle(450, 272, 26)
d.save(P, "lazo")

# 4b · La cinta escocesa de Maxwell separada en canales R, G, B.
# Cada canal se suma en pantalla con modo 'add': rojo → rojo+verde → color completo.
BASE_T, VERDE_T, AMAR_T, AZUL_T, BLANCO_T = (205, 35, 45), (40, 175, 85), (250, 220, 60), (60, 100, 230), (240, 240, 230)
VERT = [(40, 70, VERDE_T), (110, 122, AMAR_T), (180, 215, AZUL_T), (262, 292, VERDE_T), (330, 340, BLANCO_T), (380, 410, AZUL_T)]
HORI = [(18, 40, VERDE_T), (56, 64, AMAR_T), (80, 102, AZUL_T)]


def cinta(d, ox, oy, s, canal=None):
    """Dibuja la cinta (banda a cuadros + nudo + colas) en coordenadas locales 440×200, escala s.
    canal 0/1/2 = solo esa componente de color (como la placa tras su filtro); None = color real."""
    def pinta(rgb):
        if canal is not None:
            rgb = tuple(v if i == canal else 0 for i, v in enumerate(rgb))
        c = "#%02X%02X%02X" % rgb
        d.style(c, 0.5, fill=c)
    xs = sorted({0, 440, *[v for a, b, _ in VERT for v in (a, b)]})
    ys = sorted({0, 120, *[v for a, b, _ in HORI for v in (a, b)]})
    color_en = lambda lst, v: next((c for a, b, c in lst if a <= v < b), BASE_T)
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            w, h = color_en(VERT, (x0 + x1) / 2), color_en(HORI, (y0 + y1) / 2)
            pinta(tuple((a + b) // 2 for a, b in zip(w, h)))
            d.rect(ox + x0 * s, oy + y0 * s, (x1 - x0) * s + 0.4, (y1 - y0) * s + 0.4)
    pt = lambda x, y: f"{ox + x * s:.1f} {oy + y * s:.1f}"
    pinta(BASE_T); d.path(f"M{pt(205, 120)} L{pt(235, 120)} L{pt(175, 235)} L{pt(135, 222)} Z")
    d.path(f"M{pt(205, 120)} L{pt(235, 120)} L{pt(305, 222)} L{pt(265, 235)} Z")
    pinta((150, 20, 30)); d.rect(ox + 196 * s, oy - 14 * s, 48 * s, 148 * s, radius=6 * s)


PROY = [(250, 0, R, "r"), (450, 1, V, "g"), (650, 2, A, "b")]
for x, canal, color, sufijo in PROY:
    d = Doc(); cinta(d, 230, 155, 1.0, canal); d.save(P, f"sep_{sufijo}")            # su canal en la pantalla
    d = Doc(); cinta(d, x - 48, 718, 0.22, canal); d.save(P, f"placa_{sufijo}")       # la placa dentro del proyector
    d = Doc(); d.style(color, 1, fill=color).path(f"M{x - 18} 678 L{x + 18} 678 L695 418 L205 418 Z")
    d.save(P, f"haz_{sufijo}")                                                         # cono de luz
d = Doc(); cinta(d, 230, 155, 1.0); d.save(P, "cinta_color")                           # referencia (miniatura/revisión)

# 5 · Círculos de luz (se mezclan con modo 'add' en EffectCraft)
for nombre, color in (("luz_r", R), ("luz_g", V), ("luz_b", A)):
    d = Doc(); disco(d, color, 440); d.save(P, nombre)

# 6 · Píxeles (degradado tipo atardecer) + píxel naranja ampliado
d = Doc()
for fila in range(6):
    for col in range(6):
        x0, y0 = 105 + col * 118, 105 + fila * 118
        t = (fila * 6 + col) / 35
        niveles = (1.0, max(0.0, 0.85 - t), 0.25 + 0.6 * (1 - t) * (fila < 2))
        for k, (base, nivel) in enumerate(zip(((255, 0, 0), (0, 255, 0), (0, 0, 255)), niveles)):
            c = "#%02X%02X%02X" % tuple(int(v * nivel) for v in base)
            d.style(c if nivel > 0.05 else "#222222", 1, fill=c).rect(x0 + k * 32, y0, 24, 92, radius=4)
d.save(P, "pixeles")
d = Doc()
d.style(W, 5, fill=NEGRO).rect(270, 270, 360, 360, radius=12)
for k, (c, fill) in enumerate(((R, R), ("#008000", "#008000"), ("#3D7BFF", None))):
    d.style(c, 4, fill=fill).rect(315 + k * 98, 300, 76, 300, radius=10)
d.save(P, "pixel_naranja")

# 7 · Amarillo puro vs rojo + verde, y respuesta de los conos (idéntica)
d = Doc()
d.style("#FFE500", 6); onda(d, 110, 370, 200, 34, 58)
d.style(RL, 6); onda(d, 530, 790, 160, 34, 70)
d.style(VL, 6); onda(d, 530, 790, 250, 34, 52)
d.style(W, 3); flecha(d, 240, 290, 240, 360); flecha(d, 660, 310, 660, 360)
d.save(P, "amarillo")
d = Doc()
for x0 in (150, 570):
    d.style(W, 3).line(x0 - 20, 680, x0 + 200, 680)
    for k, (alto, color) in enumerate(((270, RL), (190, VL), (8, AL))):
        d.style(color, 3, fill=color).rect(x0 + k * 64, 680 - alto, 46, alto, radius=4)
d.style(W, 12); d.line(410, 520, 490, 520); d.line(410, 565, 490, 565)
d.save(P, "barras_conos")

# 8 · Papel: la luz blanca entra, la tinta cian se come el rojo (líneas oscuras: escena sobre papel)
d = Doc()
d.style(D, 4, fill="#FFFFFF").path("M120 700 L600 700 L780 540 L300 540 Z")
d.style(D, 3, fill=CI).path("M250 650 L520 650 L620 565 L350 565 Z")
for k, color in enumerate((RL, "#1FA845", "#2F5BFF")):
    d.style(color, 6); d.line(140 + k * 40, 160, 400 + k * 30, 600)
    if k:
        flecha(d, 400 + k * 30, 600, 680 + k * 40, 180)
d.style(RL, 7); d.line(400, 560, 440, 610); d.line(440, 560, 400, 610)
d.save(P, "papel")

# 9–10 · Tintas (se mezclan con 'multiply') + mancha café de CMY real
for nombre, color in (("tinta_c", CI), ("tinta_m", MA), ("tinta_y", AM)):
    d = Doc(); disco(d, color, 440); d.save(P, nombre)
d = Doc()
pts = [polar(70 + 18 * math.sin(k * 1.7) + random.uniform(-8, 8), k * 30) for k in range(12)]
dpath = f"M{pts[0][0]:.1f} {pts[0][1]:.1f} " + " ".join(
    f"Q{(pts[i][0] + pts[(i + 1) % 12][0]) / 2 + random.uniform(-10, 10):.1f} {(pts[i][1] + pts[(i + 1) % 12][1]) / 2 + random.uniform(-10, 10):.1f} {pts[(i + 1) % 12][0]:.1f} {pts[(i + 1) % 12][1]:.1f}"
    for i in range(12)) + " Z"
d.style("#3A2E28", 1, fill="#3A2E28").path(dpath)
d.save(P, "mancha_cafe")

# 11 · Muestras: "negro" de CMY vs negro K
d = Doc()
d.style(D, 3, fill="#3A2E28").rect(110, 420, 260, 260, radius=10)
d.style(D, 3, fill="#0A0A0A").rect(530, 420, 260, 260, radius=10)
d.save(P, "muestras_negro")

# 12 · Semitonos: rejillas de puntos de cada tinta con su ángulo (se superponen en 'multiply')
def semitono(nombre, color, angulo, tono):
    d = Doc(); paso = 36; a = math.radians(angulo)
    d.style(color, 0.5, fill=color)
    for i in range(-14, 15):
        for j in range(-14, 15):
            x = C + paso * (i * math.cos(a) - j * math.sin(a))
            y = C + paso * (i * math.sin(a) + j * math.cos(a))
            if (x - C) ** 2 + (y - C) ** 2 > 330 ** 2:
                continue
            r = 17 * tono((x - 120) / 660, (y - 120) / 660)
            if r > 1.5:
                d.circle(x, y, 2 * r)
    d.save(P, nombre)

semitono("puntos_y", AM, 0, lambda u, v: 0.25 + 0.7 * v)
semitono("puntos_c", CI, 15, lambda u, v: 0.15 + 0.75 * u)
semitono("puntos_m", MA, 75, lambda u, v: 0.85 - 0.7 * u)
semitono("puntos_k", K, 45, lambda u, v: max(0.0, 0.6 - 1.4 * math.hypot(u - 0.5, v - 0.5)))

# 13–14 · Diagrama de cromaticidad CIE 1931: herradura (colores visibles) y gamuts
LOCUS = [(380, .1741, .0050), (450, .1566, .0177), (460, .1440, .0297), (470, .1241, .0578), (475, .1096, .0868),
         (480, .0913, .1327), (485, .0687, .2007), (490, .0454, .2950), (495, .0235, .4127), (500, .0082, .5384),
         (505, .0039, .6548), (510, .0139, .7502), (515, .0389, .8120), (520, .0743, .8338), (525, .1142, .8262),
         (530, .1547, .8059), (540, .2296, .7543), (550, .3016, .6923), (560, .3731, .6245), (570, .4441, .5547),
         (580, .5125, .4866), (590, .5752, .4242), (600, .6270, .3725), (610, .6658, .3340), (620, .6915, .3083),
         (630, .7079, .2920), (650, .7260, .2740), (700, .7347, .2653)]
XY = lambda x, y: (80 + x * 950, 830 - y * 900)
d = Doc()
d.style(G, 2); d.line(80, 830, 820, 830); d.line(80, 830, 80, 40)
pts = [XY(x, y) for _, x, y in LOCUS]
d.style(W, 5).path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts))
d.style(G, 3, dash=[8, 10]).line(*pts[-1], *pts[0])            # línea de los púrpuras (no espectrales)
for nm, x, y in LOCUS[1:-1]:
    c = espectral(nm)
    d.style(c, 1, fill=c).circle(*XY(x, y), 18)
d.save(P, "herradura")
d = Doc()
tri = [XY(.64, .33), XY(.30, .60), XY(.15, .06)]                # primarios sRGB
d.style(O, 6).path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in tri) + " Z")
d.save(P, "gamut_rgb")
d = Doc()
hexa = [XY(.15, .22), XY(.25, .54), XY(.44, .51), XY(.62, .33), XY(.46, .23), XY(.19, .13)]  # CMYK aproximado
d.style("#00C8FF", 5, dash=[14, 10]).path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in hexa) + " Z")
d.save(P, "gamut_cmyk")

# 15 · El magenta une los extremos del espectro (no está en él)
d = Doc()
d.style("#FF2BD6", 10).path(f"M{X(380) + 6:.1f} 490 C {X(380):.1f} 760, {X(700):.1f} 760, {X(700) - 6:.1f} 490")
d.style("#FF2BD6", 3, fill="#FF2BD6").circle(450, 692, 64)
d.save(P, "puente_magenta")

hoja_contactos(P, ["telefono", "subpixeles", "ojo", "conos", "curvas", "espectro", "proyectores", "lazo",
                   "pixeles", "pixel_naranja", "amarillo", "barras_conos", "papel", "mancha_cafe",
                   "muestras_negro", "puntos_c", "herradura", "gamut_rgb", "gamut_cmyk", "puente_magenta"],
               os.path.join(P, "revision", "ilustraciones.png"), columnas=5, celda=360)
