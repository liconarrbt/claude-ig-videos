"""Renderiza la película dibujada a mano de un proyecto (skill hand-drawn-canvas-animation) → animacion/animacion.mp4.

El proyecto tiene pelicula/pelicula.html con sus escenas en Canvas 2D. Este script:
  1. copia a pelicula/ los módulos de la skill (core, studio, cels, roto) y el puente kit.js;
  2. escribe pelicula/tiempos.js con los tiempos de la voz (escenas, palabras, titulares y focos de escenas.json);
  3. escribe pelicula/vectores.js con los SVG de ilustraciones/ (diagramas de VectorCraft) como data URLs;
  4. renderiza con render.mjs de la skill y copia el MP4 a animacion/animacion.mp4.

Uso:
  python3 pelicula.py <proyecto>                    # render completo
  python3 pelicula.py <proyecto> --grid 24          # hoja de 24 cuadros (revision/pelicula-grid.jpg)
  python3 pelicula.py <proyecto> --strip 480,24     # cuadros consecutivos para revisar movimiento
  python3 pelicula.py <proyecto> --en 41.5,73       # cuadros en esos segundos
  python3 pelicula.py <proyecto> --solo-datos       # solo regenera tiempos.js/vectores.js
"""
import base64, glob, json, os, shutil, subprocess, sys
from comun import Proyecto, correr

SKILL = os.path.expanduser(os.environ.get("HAND_DRAWN_SKILL", "~/.claude/skills/hand-drawn-canvas-animation"))
KIT = os.path.dirname(os.path.abspath(__file__))
FPS = 24

if len(sys.argv) < 2:
    sys.exit(__doc__)
p = Proyecto(sys.argv[1])
args = sys.argv[2:]
arg = lambda k: args[args.index(k) + 1] if k in args else None
D = os.path.join(p.dir, "pelicula")
film = os.path.join(D, "pelicula.html")
if not os.path.exists(film):
    sys.exit(f"Falta {film} (copia la plantilla del kit: scripts/pelicula/plantilla.html)")

# 1. módulos
for src in ["assets/core.js", "assets/studio.js", "assets/cels.js", "assets/roto.js", "assets/materials.js"]:
    shutil.copy(os.path.join(SKILL, src), D)
shutil.copy(os.path.join(KIT, "pelicula", "kit.js"), D)
if os.path.exists(os.path.join(SKILL, "examples/gallop-clips.js")) and not os.path.exists(os.path.join(D, "muybridge.js")):
    shutil.copy(os.path.join(SKILL, "examples/gallop-clips.js"), os.path.join(D, "muybridge.js"))   # Muybridge 1893, dominio público

# 2. tiempos
INI = p.inicios
escenas = []
for n, esc in enumerate(p.escenas, 1):
    a, b = INI[n - 1], p.fin_escena(n)
    pal = [{"w": w["palabra"], "t0": round(w["inicio"] - a, 3), "t1": round(w["fin"] - a, 3)} for w in p.palabras if w["escena"] == n]
    tits = [{**{k: v for k, v in t.items() if k != "desde"}, "t": round(p.instante(n, t.get("desde")) - a, 3)} for t in esc.get("titulares", [])]
    fos = []
    for f in esc.get("focos", []):
        f = {"palabra": f} if isinstance(f, str) else dict(f)
        t0 = round(p.instante(n, f.get("desde", f["palabra"])) - a, 3)
        fos.append({"texto": f.get("texto", f["palabra"]).upper(), "t0": t0, "color": f.get("color", "tiza"),
                    **{k: f[k] for k in ("tam", "y") if k in f}})
    for k, f in enumerate(fos):                            # cada foco dura hasta el siguiente (máx 2.2 s) o el fin de la escena
        sig = fos[k + 1]["t0"] if k + 1 < len(fos) else b - a
        f["t1"] = round(min(sig - 0.05, f["t0"] + 2.2, b - a), 3)
    escenas.append({"n": n, "ini": round(a, 3), "dur": round(b - a, 3), "palabras": pal, "titulares": tits, "focos": fos})
open(os.path.join(D, "tiempos.js"), "w").write(
    "// generado por pelicula.py — no editar\nconst TIEMPOS = " + json.dumps({"total": p.total, "escenas": escenas}, ensure_ascii=False) + ";\n")

# 3. vectores
lineas = ["// generado por pelicula.py — no editar"]
for svg in sorted(glob.glob(os.path.join(p.dir, "ilustraciones", "*.svg"))):
    nombre = os.path.splitext(os.path.basename(svg))[0]
    datos = base64.b64encode(open(svg, "rb").read()).decode()
    lineas.append(f'registerVector({json.dumps(nombre)}, "data:image/svg+xml;base64,{datos}");')
open(os.path.join(D, "vectores.js"), "w").write("\n".join(lineas) + "\n")
print(f"película: {len(escenas)} escenas, {p.total} s, {len(lineas) - 1} vectores")
if "--solo-datos" in args:
    sys.exit(0)

# 4. render
render = [shutil.which("node") or "node", os.path.join(SKILL, "scripts", "render.mjs"), film, "--ar", "9:16", "--width", str(p.estilo["ancho"])]
out = os.path.join(D, "out")
if arg("--grid") or arg("--strip"):
    modo = "--grid" if arg("--grid") else "--strip"
    correr(render + [modo, arg(modo), "--out", out])
    hecho = glob.glob(os.path.join(out, "pelicula-grid.jpg" if modo == "--grid" else f"pelicula-strip-{arg('--strip').split(',')[0]}.jpg"))[0]
    dest = p.ruta("revision", os.path.basename(hecho)); shutil.copy(hecho, dest); print("revisión:", dest)
elif arg("--en"):
    cuadros = [str(round(float(t) * FPS)) for t in arg("--en").split(",")]
    correr(render + ["--only", ",".join(cuadros), "--out", out])
    print("cuadros:", [os.path.join(out, "pelicula-frames", f"{int(c):04d}.png") for c in cuadros])
else:
    r = subprocess.run(render + ["--out", out])
    if r.returncode:
        sys.exit("El render de la película falló")
    shutil.copy(os.path.join(out, "pelicula.mp4"), p.ruta("animacion", "animacion.mp4"))
    shutil.copy(os.path.join(out, "pelicula-contact.jpg"), p.ruta("revision", "pelicula-contacto.jpg"))
    shutil.rmtree(os.path.join(out, "pelicula-frames"), ignore_errors=True)    # los PNG ocupan mucho; el MP4 basta
    print("animación:", p.ruta("animacion", "animacion.mp4"))
