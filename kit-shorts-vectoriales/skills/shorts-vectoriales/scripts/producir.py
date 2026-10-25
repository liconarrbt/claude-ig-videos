"""Ejecuta el pipeline completo (o desde un paso) para un proyecto.

Uso: python3 producir.py <proyecto> [--desde voz|alinear|dibujar|animacion|sfx|mezcla|miniatura] [--hasta …]

Pasos: voz → alinear → dibujar (el dibujar.py del proyecto) → animacion → sfx → mezcla → miniatura
Cambiar la voz o la narración: --desde voz. Cambiar textos/capas: --desde animacion.
Cambiar solo niveles de audio: --desde mezcla.
"""
import os, subprocess, sys

KIT = os.path.dirname(os.path.abspath(__file__))
PASOS = ["voz", "alinear", "dibujar", "animacion", "sfx", "mezcla", "miniatura"]

if len(sys.argv) < 2:
    sys.exit(__doc__)
proy = os.path.abspath(sys.argv[1])
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
desde, hasta = PASOS.index(arg("--desde", "voz")), PASOS.index(arg("--hasta", "miniatura"))

for paso in PASOS[desde:hasta + 1]:
    print(f"\n━━ {paso} ━━", flush=True)
    if paso == "dibujar":
        script = os.path.join(proy, "dibujar.py")
        cmd = [sys.executable, "-I", script, proy]
    else:
        cmd = [sys.executable, os.path.join(KIT, f"{paso}.py"), proy]
        if paso == "animacion" and os.path.exists(os.path.join(proy, "pelicula", "pelicula.html")):
            # película dibujada a mano (skill hand-drawn-canvas-animation) en lugar de EffectCraft
            cmd = [sys.executable, os.path.join(KIT, "pelicula.py"), proy]
        elif paso == "animacion":
            cmd += ["--cuadros", "auto"]
        if paso == "sfx" and os.path.exists(os.path.join(proy, "musica.py")):
            # el proyecto trae su propia música: el kit solo sintetiza los efectos
            if subprocess.run(cmd + ["--solo-efectos"]).returncode:
                sys.exit("El paso 'sfx' falló")
            cmd = [sys.executable, "-I", os.path.join(proy, "musica.py"), proy]
    if subprocess.run(cmd).returncode:
        sys.exit(f"El paso '{paso}' falló. Corrige y reanuda con: --desde {paso}")
print("\nListo. Revisa revision/cuadros.png, el .mp4 final y miniatura/miniatura.jpg")
