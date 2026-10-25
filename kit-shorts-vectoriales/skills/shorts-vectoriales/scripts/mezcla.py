"""Mezcla el audio en SoundCraft y exporta el video final con FilmCraft.

Uso: python3 mezcla.py <proyecto>
Requiere: voz/, subtitulos/palabras.json, audio/ (sfx.py) y animacion/animacion.mp4.
Salida: audio/mezcla.scraft (sesión editable), audio/mezcla_final.wav, montaje/final.fcproj y
<proyecto>/<slug>.mp4. Imprime LUFS integrados y true peak.

Cadena:
- Voz: EQ (HPF 85 Hz, −2.5 dB en 320 Hz, +2.5 dB en 3.5 kHz, +1.5 dB de aire) → compresor 3:1.
- Música: ducking estilo sidechain escrito como automatización de volumen (el compresor de
  SoundCraft no acepta clave externa), siguiendo la envolvente de la voz.
- Efectos: whoosh en cada corte, pop en cada texto/número que aparece, pop grave en capas con
  "golpe", tic-tac bajo capas con "tictac", más los "sfx" explícitos de cada escena.
- Master: maximizador; su umbral es el "empuje" que se itera hasta −14 LUFS con techo −1 dBTP
  (el trim de entrada del master no afecta al bounce).
"""
import json, math, os, re, struct, subprocess, sys, wave
from comun import Proyecto, cli, correr

if len(sys.argv) < 2:
    sys.exit(__doc__)
p = Proyecto(sys.argv[1])
cfg = {"objetivo_lufs": -14.0, "techo_dbtp": -1.0, "musica_db": -13.0,
       "whoosh_db": -14.0, "pops_db": -9.0, "tictac_db": -16.0, **p.spec.get("mezcla", {})}
SC, FC = cli("soundcraft"), cli("filmcraft")
TOTAL, INI, TIEMPOS = p.total, p.inicios, p.tiempos
ts = lambda s: f"{int(s // 60)}:{s % 60:06.3f}"
AUD = lambda n: p.ruta("audio", n)

# ── 1. Lista de efectos (archivo, pista, segundo, duración) ──
cues = [("whoosh.wav", max(s - 0.35, 0), None) for s in INI[1:]]
for n, esc in enumerate(p.escenas, 1):
    fin = p.fin_escena(n)
    for c in esc.get("capas", []):
        t0 = p.instante(n, c.get("desde"))
        if c.get("golpe"):
            cues.append(("pop_grave.wav", t0, None))
        if c.get("tictac"):
            cues.append(("tictac.wav", t0, fin - t0))
        if c.get("entrada") == "pop":
            cues.append(("pop.wav", t0, None))
    for t in esc.get("tarjetas", []):
        cues.append(("pop.wav", p.instante(n, t.get("desde")), None))
    for t in esc.get("titulares", [])[1:]:
        cues.append(("pop.wav", p.instante(n, t.get("desde")), None))
    for t in esc.get("textos", []):
        cues.append(("pop.wav", p.instante(n, t.get("desde")), None))
    an = esc.get("anillo")
    if an:
        cuenta = {}
        for k, pal in enumerate(an.get("palabras", [])):
            cuenta[pal] = cuenta.get(pal, 0) + 1
            cues.append(("pop.wav", p.dicho(n, pal, cuenta[pal] + an.get("saltar", {}).get(pal, 0)), None))
    for f in esc.get("focos", []):                       # película dibujada: un pop por palabra clave
        f = {"palabra": f} if isinstance(f, str) else f
        cues.append(("pop.wav", p.instante(n, f.get("desde", f["palabra"])), None))
    for s in esc.get("sfx", []):
        cues.append((s["tipo"] + ".wav", p.instante(n, s.get("desde")), s.get("duracion")))
PISTA = {"whoosh.wav": "Whoosh", "pop.wav": "Pops", "pop_grave.wav": "Pops", "tictac.wav": "Tictac"}


def recorta(origen, destino, segundos):
    with wave.open(origen) as f:
        prm, datos = f.getparams(), f.readframes(int(segundos * f.getframerate()))
    with wave.open(destino, "w") as g:
        g.setparams(prm); g.writeframes(datos)


# ── 2. Sesión de SoundCraft ──
cmds = []
c = lambda i, prm: cmds.append(f"{i} {json.dumps(prm, ensure_ascii=False)}")
c("track.new", {"kind": "audio", "format": "mono", "name": "Voz"})
for e, s in zip(TIEMPOS, INI):
    c("file.import_audio", {"path": p.ruta(e["archivo"]), "track": "Voz", "at": ts(s), "new_tracks": False})
c("mix.insert", {"track": "Voz", "slot": 0, "plugin": "eq_7band", "params": {
    "hpf_on": 1, "hpf_freq": 85, "low_mid_freq": 320, "low_mid_gain": -2.5, "low_mid_q": 1.0,
    "high_mid_freq": 3500, "high_mid_gain": 2.5, "high_mid_q": 1.0, "high_shelf_freq": 10000, "high_shelf_gain": 1.5}})
c("mix.insert", {"track": "Voz", "slot": 1, "plugin": "compressor", "params": {
    "threshold": -24, "ratio": 3, "attack": 8, "release": 90, "knee": 4, "makeup": 4}})

c("track.new", {"kind": "audio", "format": "stereo", "name": "Musica"})
c("file.import_audio", {"path": AUD("musica.wav"), "track": "Musica", "at": ts(0), "new_tracks": False})
# ducking: seguidor de envolvente de la voz (umbral −40 dBFS, 4:1, máx. 12 dB, ataque 40 ms, release 300 ms)
PASO = 0.01
nivel = [-90.0] * int(TOTAL / PASO + 1)
for e, s in zip(TIEMPOS, INI):
    with wave.open(p.ruta(e["archivo"])) as f:
        sr, ch = f.getframerate(), f.getnchannels()
        raw = f.readframes(f.getnframes())  # los WAV de Fish traen longitud indefinida en la cabecera
    x = struct.unpack(f"<{len(raw) // 2}h", raw)[::ch]
    v = int(sr * PASO)
    for k in range(0, len(x) - v, v):
        rms = math.sqrt(sum(m * m for m in x[k:k + v]) / v) / 32768
        i = int((s + k / sr) / PASO)
        if i < len(nivel):
            nivel[i] = max(nivel[i], 20 * math.log10(max(rms, 1e-5)))
gr, ultimo = 0.0, None
for i, lv in enumerate(nivel):
    obj = min(12.0, max(0.0, (lv + 40.0) * 0.75))
    gr += (obj - gr) * (1 - math.exp(-PASO / (0.04 if obj > gr else 0.30)))
    val = round(cfg["musica_db"] - gr, 1)
    if i % 4 == 0 and (ultimo is None or abs(val - ultimo) >= 0.5):
        c("automation.set_point", {"track": "Musica", "param": "volume", "at": ts(i * PASO), "value": val}); ultimo = val

for nombre, db in (("Whoosh", cfg["whoosh_db"]), ("Pops", cfg["pops_db"]), ("Tictac", cfg["tictac_db"])):
    c("track.new", {"kind": "audio", "format": "mono", "name": nombre})
    c("mix.volume", {"tracks": [nombre], "db": db})
for k, (archivo, seg, dur) in enumerate(sorted(cues, key=lambda q: q[1])):
    ruta = AUD(archivo)
    if dur:
        ruta = AUD(f"_recorte_{k}.wav"); recorta(AUD(archivo), ruta, dur)
    c("file.import_audio", {"path": ruta, "track": PISTA.get(archivo, "Pops"), "at": ts(seg), "new_tracks": False})
c("track.new", {"kind": "master", "format": "stereo"})

# el master recibe un nombre automático: se averigua su id con una pasada previa
prueba = correr([SC, "run", *sum((["--cmd", l.replace(" ", "=", 1)] for l in cmds), [])])
MASTER = json.loads(prueba.strip().splitlines()[-1].split(": ", 1)[1])["tracks"][0]
SESION, MEZCLA = AUD("mezcla.scraft"), AUD("mezcla_final.wav")


def bounce(empuje, margen):
    lineas = cmds + [
        f'mix.insert {json.dumps({"track": MASTER, "slot": 0, "plugin": "maximizer", "params": {"threshold": -round(empuje, 2), "ceiling": cfg["techo_dbtp"] - round(margen, 2)}})}',
        f'file.bounce_mix {json.dumps({"path": MEZCLA, "format": "wav", "bit_depth": 24, "end": ts(TOTAL)})}']
    guion = AUD("mezcla_script.txt")
    open(guion, "w").write("\n".join(lineas) + "\n")
    out = correr([SC, "script", guion, "--save", SESION])
    return json.loads([l for l in out.splitlines() if l.startswith("file.bounce_mix")][-1].split(": ", 1)[1])


empuje, margen = 6.0, 0.4
for intento in range(6):
    m = bounce(empuje, margen)
    print(f"mezcla {intento + 1}: empuje {empuje:.1f} dB, techo −{margen:.2f} → {m['lufs']:.2f} LUFS, true peak {m['true_peak_db']:.2f} dBTP")
    if abs(cfg["objetivo_lufs"] - m["lufs"]) <= 0.3 and m["true_peak_db"] <= cfg["techo_dbtp"]:
        break
    if m["true_peak_db"] > cfg["techo_dbtp"]:        # los picos entre muestras rebasan el techo: bajarlo lo que sobra
        margen += m["true_peak_db"] - cfg["techo_dbtp"] + 0.1
    empuje = max(0.0, empuje + cfg["objetivo_lufs"] - m["lufs"])

# ── 3. FilmCraft: video + mezcla → MP4 final ──
slug = re.sub(r"[^a-z0-9]+", "_", p.spec.get("titulo", "short").lower().translate(str.maketrans("áéíóúñü", "aeiounu"))).strip("_")
final = os.path.join(p.dir, f"{slug}.mp4")
L = [("file.newProject", {"name": slug}),
     ("file.import", {"paths": [p.ruta("animacion", "animacion.mp4"), MEZCLA]}),
     ("file.newSequence", {"name": slug, "width": p.estilo["ancho"], "height": p.estilo["alto"], "fps": p.estilo["fps"], "video": 1, "audio": 1}),
     ("timeline.place", {"item": 1, "track": "V1", "seconds": 0, "insert": False, "audio": False}),
     ("timeline.place", {"item": 2, "track": "A1", "seconds": 0, "insert": False, "video": False}),
     ("file.saveAs", {"path": p.ruta("montaje", "final.fcproj")})]
jl = p.ruta("montaje", "final.jsonl")
open(jl, "w").write("\n".join(json.dumps({"id": k, "params": v}, ensure_ascii=False) for k, v in L) + "\n")
out = correr([FC, "--compact", "run", jl])
if '"ok":false' in out:
    sys.exit(out)
correr([FC, "--project", p.ruta("montaje", "final.fcproj"), "export", final, "--format", "h264", "--range", "entire"])
json.dump({"lufs": m["lufs"], "true_peak_db": m["true_peak_db"], "empuje_db": empuje, "efectos": len(cues), "video": final},
          open(AUD("mezcla_medidas.json"), "w"), indent=1)
print("video final:", final)
