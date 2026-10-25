"""Miniatura vertical en PhotoCraft: fondo negro + retícula, ilustración y titular gigante con acento.

Uso: python3 miniatura.py <proyecto>
Lee escenas.json → "miniatura": {"texto": "¿POR QUÉ 60\\nY NO 100?", "acento": "60",
                                 "ilustraciones": ["reloj", "reloj_manecillas"], "centro": [540, 1250], "tam": 200}
  cada ilustración puede ser un nombre o {"svg", "pos": [x, y], "escala": 100, "modo": "Screen"}
Salida: miniatura/miniatura.pcraft (capas editables), .png y .jpg
"""
import json, os
from comun import cli, correr, proyecto_desde_argv

p = proyecto_desde_argv()
m = p.spec.get("miniatura")
if not m:
    raise SystemExit('Falta "miniatura" en escenas.json')
E = p.estilo
VC, PC = cli("vectorcraft"), cli("photocraft")
png = lambda n: p.ruta("miniatura", "png", n + ".png")

ilus = [i if isinstance(i, dict) else {"svg": i} for i in m.get("ilustraciones", [])]
import vc
vc.ESTILO.update(E)
FONDO_SVG = vc.fondo(p.dir)
for n in [FONDO_SVG] + [i["svg"] for i in ilus]:
    escala = "1" if n == FONDO_SVG else str(m.get("escala_ilustracion", 1.1))
    correr([VC, "convert", p.ruta("ilustraciones", n + ".svg"), png(n), "--scale", escala])

cx, cy = m.get("centro", [540, 1250])
args = ["--new", json.dumps({"width": E["ancho"], "height": E["alto"]}),
        "--cmd", "layer.newFillLayer.solidColor", "--params", json.dumps({"color": E["fondo"]}),
        "--cmd", "file.placeEmbedded", "--params", json.dumps({"path": png(FONDO_SVG), "scale": 100, "center": [E["ancho"] // 2, E["alto"] // 2]})]
for i in ilus:  # {"svg", "pos": [x, y], "escala": %, "modo": "Screen"|"Multiply"|…}
    args += ["--cmd", "file.placeEmbedded", "--params", json.dumps({"path": png(i["svg"]), "scale": i.get("escala", 100), "center": i.get("pos", [cx, cy])})]
    if i.get("modo"):
        args += ["--cmd", "layer.setProps", "--params", json.dumps({"blend": i["modo"]})]
# ajusta el tamaño si la línea más larga no cabe en 1000 px (≈0.56 em por letra en la condensada gruesa)
tam = m.get("tam", 200)
larga = max(len(l) for l in m["texto"].split("\n"))
if larga * tam * 0.56 > 960:
    tam = int(960 / (larga * 0.56))
    print(f"miniatura: texto reducido a {tam} pt para que quepa '{max(m['texto'].split(chr(10)), key=len)}'")
m["tam"] = tam
args += ["--cmd", "type.create", "--params", json.dumps({
    "box": [40, 170, 1000, 560], "text": m["texto"], "name": "Titular", "align": "center",
    "font": E["fuente"], "fontStyle": E["estilo_fuente"], "size": m.get("tam", 200), "color": E["blanco"],
    "leading": round(m.get("tam", 200) * 0.95)})]
pcraft = p.ruta("miniatura", "miniatura.pcraft")
out = correr([PC, "run", *args, "--out", pcraft])
capa = [json.loads(l)["result"]["layer"] for l in out.splitlines() if '"type.create"' in l][-1]
if m.get("acento") and m["acento"] in m["texto"]:
    i = m["texto"].index(m["acento"])
    correr([PC, "run", pcraft, "--cmd", "type.setStyle", "--params",
            json.dumps({"layer": capa, "range": [i, i + len(m["acento"])], "color": E["acento"]}), "--out", pcraft])
correr([PC, "convert", pcraft, p.ruta("miniatura", "miniatura.png")])
correr([PC, "convert", p.ruta("miniatura", "miniatura.png"), p.ruta("miniatura", "miniatura.jpg"), "--quality", "92"])
print("miniatura:", p.ruta("miniatura", "miniatura.jpg"))
