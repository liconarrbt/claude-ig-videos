"""Biblioteca para dibujar ilustraciones de línea en VectorCraft (headless) y exportar SVG.

Cada proyecto tiene su propio `dibujar.py` que importa esta biblioteca:

    import sys; sys.path.insert(0, "<kit>/scripts")
    from vc import Doc, polar, radial, O, W, G, C
    d = Doc(); d.style(W, 5).circle(C, C, 760); d.save(proyecto, "reloj")

Convenciones del estilo (ver references/estilo.md):
- Lienzo de 900×900 px con el centro en (450, 450): EffectCraft lo centra en la posición de la capa.
- Solo trazos (sin relleno) para que la animación de "dibujado" (trim paths) funcione;
  relleno negro únicamente para ocultar lo que queda detrás (p. ej. dedos detrás de la palma).
- Blanco para la estructura, naranja (acento) para lo importante, gris para guías.
"""
import json, math, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import cli, ESTILO, aplicar_tema

# Si el script se llama con la carpeta del proyecto (python3 dibujar.py <proyecto>), se aplica su tema:
# en "libreta", W es tinta grafito y NEGRO es el color del papel (lo que tapa lo de atrás).
_esc = os.path.join(sys.argv[1], "escenas.json") if len(sys.argv) > 1 else ""
if _esc and os.path.exists(_esc):
    ESTILO.update(aplicar_tema(json.load(open(_esc)).get("estilo", {})))
O, W, G = ESTILO["acento"], ESTILO["blanco"], ESTILO["linea_gris"]
NEGRO = ESTILO["papel"]
C = 450  # centro del lienzo de 900 px


class Doc:
    """Acumula comandos de VectorCraft y los ejecuta de una vez al guardar.

    Importante: VectorCraft aplica pintura a lo seleccionado, y cada forma nueva queda seleccionada;
    por eso style() deselecciona antes de cambiar color/grosor (si no, recolorearía la última forma).
    """

    def __init__(self, w=900, h=900):
        self.w, self.h = w, h
        self.cmds = [("file.new", {"width": w, "height": h, "units": "Pixels"})]

    def style(self, color, weight, fill=None, dash=None):
        self.cmds += [
            ("select.none", {}),
            ("paint.setFill", fill if isinstance(fill, dict) else {"color": fill} if fill else {"none": True}),
            ("paint.setStroke", {"color": color}),
            ("stroke.set", {"weight": weight, "cap": "round", "join": "round", "dash": dash}),
        ]
        return self

    def sombra_suelo(self, cx, cy, w, h, color="#7A5A2E", opacidad=22):
        """Sombra de contacto: elipse plana bajo el objeto (lo 'apoya' en el suelo)."""
        self.style(color, 1, fill=color).add("shape.ellipse", x=cx - w / 2, y=cy - h / 2, width=w, height=h)
        return self.add("object.setProps", opacity=opacidad)

    def add(self, cmd, **p):
        self.cmds.append((cmd, p))
        return self

    # formas habituales
    def circle(self, cx, cy, d):
        return self.add("shape.ellipse", x=cx - d / 2, y=cy - d / 2, width=d, height=d)

    def rect(self, x, y, w, h, radius=0, rotation=0):
        return self.add("shape.rectangle", x=x, y=y, width=w, height=h, radius=radius, rotation=rotation)

    def line(self, x1, y1, x2, y2):
        return self.add("shape.line", x1=x1, y1=y1, x2=x2, y2=y2)

    def path(self, d):
        """Trazado con datos SVG ('M x y L … A … Z')."""
        return self.add("path.create", d=d, anchors=[])

    def polygon(self, cx, cy, radius, sides=6, rotation=0):
        return self.add("shape.polygon", cx=cx, cy=cy, radius=radius, sides=sides, rotation=rotation)

    def save(self, proyecto_dir, name):
        """Exporta ilustraciones/<name>.svg y .vectorcraft (editable en la app)."""
        out = os.path.join(proyecto_dir, "ilustraciones")
        os.makedirs(out, exist_ok=True)
        args = [cli("vectorcraft"), "run"]
        for cmd, p in self.cmds:
            args += ["--cmd", cmd, "--params", json.dumps(p)]
        base = os.path.join(out, name)
        args += ["--export", base + ".svg", "--export", base + ".vectorcraft"]
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{name}: {r.stderr or r.stdout[-800:]}")
        print(f"{name}: {len(self.cmds)} comandos")


def polar(r, deg, cx=C, cy=C):
    """Punto a radio r y ángulo deg (0° = arriba, sentido horario)."""
    a = math.radians(deg - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def radial(doc, r1, r2, deg, cx=C, cy=C):
    """Segmento radial entre r1 y r2 (marcas de reloj, rayos, radios de una telaraña)."""
    x1, y1 = polar(r1, deg, cx, cy)
    x2, y2 = polar(r2, deg, cx, cy)
    return doc.line(x1, y1, x2, y2)


def esfera(doc, marcas=60, mayores_cada=5, d=760):
    """Esfera de reloj: aro blanco, aro guía gris, marcas menores blancas y mayores en acento."""
    r = d / 2
    doc.style(W, 5).circle(C, C, d)
    doc.style(G, 2).circle(C, C, d - 70)
    doc.style(W, 3)
    for i in range(marcas):
        if i % mayores_cada:
            radial(doc, r - 28, r - 8, i * 360 / marcas)
    doc.style(O, 9)
    for i in range(0, marcas, mayores_cada):
        radial(doc, r - 62, r - 8, i * 360 / marcas)
    return doc


def reticula(proyecto_dir, paso=60, color=None):
    """Fondo de retícula a tamaño de cuadro (lo usa animacion.py si no existe)."""
    d = Doc(ESTILO["ancho"], ESTILO["alto"])
    d.style(color or ESTILO["reticula"], 1).add(
        "shape.rectangularGrid", x=0, y=0, width=ESTILO["ancho"], height=ESTILO["alto"],
        rows=ESTILO["alto"] // paso, columns=ESTILO["ancho"] // paso)
    d.save(proyecto_dir, "fondo_reticula")


def libreta(proyecto_dir, paso=60, margen_x=150):
    """Fondo de libreta rayada a tamaño de cuadro: renglones azules, margen rojo y perforaciones."""
    a, h = ESTILO["ancho"], ESTILO["alto"]
    d = Doc(a, h)
    d.style(ESTILO["reticula"], 2)
    for y in range(240, h, paso):
        d.line(0, y, a, y)
    d.style(ESTILO.get("margen", "#E2796B"), 3).line(margen_x, 0, margen_x, h)
    d.style(ESTILO["linea_gris"], 2, fill="#F3E3A6")
    for y in range(160, h, 320):
        d.circle(60, y, 34)
    d.save(proyecto_dir, "fondo_libreta")


def fondo(proyecto_dir):
    """Crea el dibujo de fondo del tema si no existe."""
    nombre = ESTILO.get("fondo_svg", "fondo_reticula")
    if not os.path.exists(os.path.join(proyecto_dir, "ilustraciones", nombre + ".svg")):
        (libreta if nombre == "fondo_libreta" else reticula)(proyecto_dir)
    return nombre


def grad(luz, base, sombra, angulo=45):
    """Relleno con volumen: sombra abajo-izquierda → base → luz arriba-derecha (luz principal a 45°).
    Cada objeto nuevo ajusta el degradado a su propio contorno."""
    return {"gradient": {"kind": "linear", "angle": angulo,
                         "stops": [{"offset": 0, "color": sombra}, {"offset": 0.5, "color": base}, {"offset": 1, "color": luz}]}}


def grad_radial(centro, borde):
    """Relleno esférico (ovillo, burbujas, ojos): claro en el centro, oscuro en el borde."""
    return {"gradient": {"kind": "radial", "stops": [{"offset": 0, "color": centro}, {"offset": 1, "color": borde}]}}


def hoja_contactos(proyecto_dir, nombres, salida, columnas=3, celda=600):
    """PNG con las ilustraciones sobre negro para revisarlas de un vistazo (VectorCraft → PhotoCraft)."""
    tmp = os.path.join(proyecto_dir, "revision", "png")
    os.makedirs(tmp, exist_ok=True)
    filas = (len(nombres) + columnas - 1) // columnas
    args = [cli("photocraft"), "run", "--new", json.dumps({"width": columnas * celda, "height": filas * celda}),
            "--cmd", "layer.newFillLayer.solidColor", "--params", json.dumps({"color": ESTILO["fondo"]})]
    for i, n in enumerate(nombres):
        png = os.path.join(tmp, n + ".png")
        subprocess.run([cli("vectorcraft"), "convert", os.path.join(proyecto_dir, "ilustraciones", n + ".svg"), png],
                       capture_output=True)
        cx, cy = celda // 2 + (i % columnas) * celda, celda // 2 + (i // columnas) * celda
        args += ["--cmd", "file.placeEmbedded", "--params",
                 json.dumps({"path": png, "scale": round(celda / 900 * 95), "center": [cx, cy]})]
    subprocess.run(args + ["--out", salida], capture_output=True)
    print("hoja de contactos:", salida)


def suave(p, cerrado=False):
    """Datos SVG de una curva suave (Catmull-Rom → Bézier) que pasa por los puntos.
    Úsala para contornos orgánicos (cerebros, costas, animales): se ve dibujado a mano, no poligonal."""
    p = ([p[-1]] + p + [p[0], p[1]]) if cerrado else ([p[0]] + p + [p[-1]])
    d = f"M{p[1][0]:.1f} {p[1][1]:.1f}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + (" Z" if cerrado else "")


def dentro(pt, poly):
    """¿Está el punto dentro del polígono? (para repartir texturas dentro de un contorno)."""
    x, y, c = pt[0], pt[1], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def proyeccion(lon0, lon1, lat0, lat1, ancho=900, y0=190):
    """Equirectangular para mapas con coordenadas reales: devuelve f(lon, lat) → (x, y) en el lienzo."""
    k = ancho / (lon1 - lon0)
    return lambda lon, lat: ((lon - lon0) * k, (lat0 - lat) * k + y0)
