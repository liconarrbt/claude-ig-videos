"""Compone el avatar (800×800) y el banner (2560×1440) de Curiosart en PhotoCraft.
Corre: python3 componer.py   (antes: python3 dibujar_marca.py)"""
import json, os, subprocess, sys

sys.path.insert(0, os.path.expanduser("~/Documents/Artcarft/kit-shorts-vectoriales/skills/shorts-vectoriales/scripts"))
from comun import cli, correr

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.expanduser("~/Documents/Artcarft/proyectos")
VC, PC = cli("vectorcraft"), cli("photocraft")
FUENTE, ESTILO, O = "Avenir Next Condensed", "Heavy", "#FF6A1A"
os.makedirs(os.path.join(AQUI, "png"), exist_ok=True)

SVG = {
    "emblema": f"{AQUI}/ilustraciones/emblema.svg",
    "reticula_banner": f"{AQUI}/ilustraciones/reticula_banner.svg",
    "reticula_avatar": f"{AQUI}/ilustraciones/reticula_avatar.svg",
    "reloj": f"{PROY}/prueba-kit/ilustraciones/reloj.svg",
    "tablilla": f"{PROY}/prueba-kit/ilustraciones/tablilla.svg",
    "ojo": f"{PROY}/rgb-cmy/ilustraciones/ojo.svg",
    "herradura": f"{PROY}/rgb-cmy/ilustraciones/herradura.svg",
    "impresora": f"{PROY}/rgb-cmy/ilustraciones/impresora.svg",
    "cartuchos": f"{PROY}/rgb-cmy/ilustraciones/cartuchos.svg",
    "luz_r": f"{PROY}/rgb-cmy/ilustraciones/luz_r.svg",
    "luz_g": f"{PROY}/rgb-cmy/ilustraciones/luz_g.svg",
    "luz_b": f"{PROY}/rgb-cmy/ilustraciones/luz_b.svg",
}
png = lambda n: f"{AQUI}/png/{n}.png"
for n, ruta in SVG.items():
    correr([VC, "convert", ruta, png(n)])


def capa(n, x, y, escala, opacidad=None, modo=None):
    out = ["--cmd", "file.placeEmbedded", "--params", json.dumps({"path": png(n), "center": [x, y], "scale": escala})]
    props = {k: v for k, v in (("opacity", opacidad), ("blend", modo)) if v is not None}
    if props:
        out += ["--cmd", "layer.setProps", "--params", json.dumps(props)]
    return out


def texto(t, box, tam, color, align="left"):
    return ["--cmd", "type.create", "--params", json.dumps({
        "box": box, "text": t, "align": align, "font": FUENTE, "fontStyle": ESTILO, "size": tam, "color": color,
        "leading": round(tam * 0.95)})]


def componer(nombre, ancho, alto, args, acentos=()):
    pcraft = f"{AQUI}/{nombre}.pcraft"
    out = correr([PC, "run", "--new", json.dumps({"width": ancho, "height": alto}),
                  "--cmd", "layer.newFillLayer.solidColor", "--params", json.dumps({"color": "#000000"}), *args, "--out", pcraft])
    capas = [json.loads(l)["result"]["layer"] for l in out.splitlines() if '"type.create"' in l]
    for idx, inicio, fin in acentos:                      # colorea parte de un texto (la "ART" de CURIOSART)
        correr([PC, "run", pcraft, "--cmd", "type.setStyle", "--params",
                json.dumps({"layer": capas[idx], "range": [inicio, fin], "color": O}), "--out", pcraft])
    correr([PC, "convert", pcraft, f"{AQUI}/{nombre}.png"])
    correr([PC, "convert", f"{AQUI}/{nombre}.png", f"{AQUI}/{nombre}.jpg", "--quality", "92"])
    print(nombre, "→", f"{AQUI}/{nombre}.png")


# ── Avatar: el emblema centrado (YouTube lo recorta en círculo) ──
componer("avatar", 800, 800, [
    *capa("reticula_avatar", 400, 400, 100),
    *capa("emblema", 418, 400, 92),          # +18 px: compensa el hueco de la C a la derecha
])

# ── Banner: 2560×1440. Zona segura (visible en todo dispositivo): 1546×423 centrada → x 507–2053, y 508–931 ──
deco = [
    # izquierda: arriba/abajo solo se ven en TV; el centro también en escritorio
    *capa("reloj", 285, 300, 40, 0.5), *capa("tablilla", 285, 1150, 40, 0.5),
    *capa("luz_r", 225, 690, 34, 0.85, "Screen"), *capa("luz_g", 345, 690, 34, 0.85, "Screen"), *capa("luz_b", 285, 790, 34, 0.85, "Screen"),
    # derecha
    *capa("herradura", 2280, 300, 40, 0.5), *capa("ojo", 2280, 1150, 40, 0.5),
    *capa("impresora", 2280, 715, 44, 0.85), *capa("cartuchos", 2280, 715, 44, 0.85),
]
componer("banner", 2560, 1440, [
    *capa("reticula_banner", 1280, 720, 100),
    *deco,
    *capa("emblema", 735, 720, 46),
    *texto("CURIOSART", [960, 545, 1100, 260], 220, "#FFFFFF"),
    *texto("CURIOSIDADES QUE SE DIBUJAN SOLAS", [966, 800, 1090, 80], 52, "#BBBBBB"),
], acentos=[(0, 6, 9)])
