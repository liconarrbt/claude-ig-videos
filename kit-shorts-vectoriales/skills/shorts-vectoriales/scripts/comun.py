"""Utilidades compartidas del kit: rutas de las CLIs, estilo, lectura del proyecto y tiempos.

Un proyecto es una carpeta con `escenas.json` (la especificación del short). Los demás scripts
leen ese archivo y escriben sus resultados en subcarpetas del proyecto (voz/, subtitulos/, …).
"""
import glob, json, os, subprocess, sys

KIT = os.path.dirname(os.path.abspath(__file__))
APPS = os.path.expanduser(os.environ.get("CRAFT_CLI_DIR", "~/Applications/craft-cli"))


def cli(app):
    """Ruta del ejecutable `<app>-cli` más reciente dentro de ~/Applications/craft-cli/<app>/."""
    hallados = sorted(glob.glob(os.path.join(APPS, app, f"{app}-cli-*", f"{app}-cli")))
    if not hallados:
        sys.exit(f"No encuentro {app}-cli en {APPS}/{app}/ — corre instalar.sh del kit")
    return hallados[-1]


# ── Estilo por defecto (cada proyecto puede sobrescribirlo en escenas.json → "estilo") ──
ESTILO = {
    "ancho": 1080, "alto": 1920, "fps": 30,
    "fondo": "#000000", "reticula": "#1E1E1E",
    "acento": "#FF6A1A", "blanco": "#FFFFFF", "gris": "#BBBBBB", "linea_gris": "#5A5A5A",
    "fuente": "Avenir Next Condensed", "estilo_fuente": "Heavy",
    "titular_y": 340, "titular_tam": 120,
    "ilustracion_pos": [540, 1130],
    "subtitulo_y": 618, "subtitulo_tam": 76,
    "papel": "#000000",                 # relleno que "tapa" lo de atrás (= color del fondo)
    "fondo_svg": "fondo_reticula",      # dibujo de fondo a pantalla completa
    # acabado de cámara (EffectCraft): desenfoque de movimiento, grano de papel (opacidad %), viñeta
    # (cantidad 0–100) y sombra suave bajo las ilustraciones (opacidad %, solo capas sin "modo")
    "acabado": {"desenfoque": False, "grano": 0, "vineta": 0, "sombra": 0, "sombra_color": "#000000"},
}

# Temas: cambian fondo, tinta y papel a la vez (las líneas "blancas" pasan a ser la tinta del tema).
TEMAS = {
    "libreta": {"fondo": "#FFF3C4", "papel": "#FFF3C4", "blanco": "#2B2925", "gris": "#5E584C",
                "linea_gris": "#8A8478", "reticula": "#A9CBE8", "margen": "#E2796B", "fondo_svg": "fondo_libreta",
                "acabado": {"sombra": 25, "sombra_color": "#7A5A2E"}},
}


def aplicar_tema(spec_estilo):
    """Estilo efectivo = ESTILO + tema (si hay) + ajustes sueltos del proyecto."""
    base = dict(ESTILO)
    for capa in (TEMAS.get(spec_estilo.get("tema"), {}), {k: v for k, v in spec_estilo.items() if k != "tema"}):
        acabado = {**base["acabado"], **capa.get("acabado", {})}   # "acabado" se mezcla clave a clave
        base.update(capa); base["acabado"] = acabado
    return base


class Proyecto:
    def __init__(self, carpeta):
        self.dir = os.path.abspath(carpeta)
        ruta = os.path.join(self.dir, "escenas.json")
        if not os.path.exists(ruta):
            sys.exit(f"Falta {ruta} — créalo con nuevo_proyecto.py")
        self.spec = json.load(open(ruta))
        self.escenas = self.spec["escenas"]
        self.estilo = aplicar_tema(self.spec.get("estilo", {}))

    def ruta(self, *partes):
        p = os.path.join(self.dir, *partes)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    # ── tiempos (requieren voz.py y alinear.py) ──
    @property
    def tiempos(self):
        return json.load(open(self.ruta("voz", "tiempos.json")))

    @property
    def palabras(self):
        return json.load(open(self.ruta("subtitulos", "palabras.json")))

    @property
    def inicios(self):
        t, out = 0.0, []
        for e in self.tiempos:
            out.append(round(t, 3)); t += e["duracion"]
        return out

    @property
    def total(self):
        return round(sum(e["duracion"] for e in self.tiempos) + 0.6, 2)

    def dicho(self, escena, palabra, n=1):
        """Segundo (absoluto) en que la voz dice `palabra` (su n-ésima aparición) en la escena (1-based)."""
        limpia = lambda w: w.lower().strip(",.:;¿?¡!…\"'()")
        vistos = 0
        for w in self.palabras:
            if w["escena"] == escena and limpia(w["palabra"]) == limpia(palabra):
                vistos += 1
                if vistos == n:
                    return w["inicio"]
        sys.exit(f"escena {escena}: la voz no dice '{palabra}' (aparición {n}). Revisa 'desde' en escenas.json")

    def instante(self, escena, desde):
        """Resuelve un 'desde' de escenas.json a segundos absolutos.
        None → inicio de la escena · "palabra" · {"palabra": "x", "n": 2} · {"t": 0.6} (relativo a la escena)."""
        ini = self.inicios[escena - 1]
        if desde is None:
            return ini
        if isinstance(desde, str):
            return self.dicho(escena, desde)
        if "palabra" in desde:
            return self.dicho(escena, desde["palabra"], desde.get("n", 1)) + desde.get("t", 0)
        return round(ini + desde.get("t", 0), 3)

    def fin_escena(self, escena):
        return self.inicios[escena] if escena < len(self.escenas) else self.total

    def color(self, nombre):
        return self.estilo.get(nombre, nombre)  # "acento", "gris", "blanco" o un #hex


def correr(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"Falló: {' '.join(map(str, args[:3]))} …\n{(r.stderr or r.stdout)[-2000:]}")
    return r.stdout


def proyecto_desde_argv():
    if len(sys.argv) < 2:
        sys.exit(f"Uso: python3 {os.path.basename(sys.argv[0])} <carpeta-del-proyecto>")
    return Proyecto(sys.argv[1])
