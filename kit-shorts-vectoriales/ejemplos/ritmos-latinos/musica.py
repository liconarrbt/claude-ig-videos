"""Música del video: un groove latino sintetizado (100 BPM, clave de son 3-2) cuyo arreglo sigue
a la narración — en la escena del metrónomo solo suena un metrónomo, en la de la clave solo la
clave, y cada instrumento entra cuando la voz lo nombra. Todo sintetizado aquí, sin muestras.

La animación usa el mismo tempo y fase (t=0 = primer tiempo del compás 1), así que las manecillas
y los destellos de los dibujos caen con la música.
Corre: python3 musica.py <proyecto>     → audio/musica.wav
"""
import array, json, math, os, random, sys, wave

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
SR, BPM = 44100, 100
PASO = 60 / BPM / 2                      # una corchea = 0.3 s; 16 pasos = 2 compases
TAU = 2 * math.pi
random.seed(100)

tiempos = json.load(open(f"{P}/voz/tiempos.json"))
palabras = json.load(open(f"{P}/subtitulos/palabras.json"))
inicios, t = [], 0.0
for e in tiempos:
    inicios.append(t); t += e["duracion"]
TOTAL = round(t + 0.6, 2)
N = int(TOTAL * SR)
L, R = [0.0] * N, [0.0] * N


def dicho(esc, pal, n=1):
    k = 0
    for w in palabras:
        if w["escena"] == esc and w["palabra"].lower().strip(",.:;¿?…") == pal:
            k += 1
            if k == n:
                return w["inicio"]
    raise SystemExit(f"no encuentro {pal} en escena {esc}")


ESC = lambda n: inicios[n - 1]                            # inicio de la escena n (1-based)


def suma(señal, t0, gan=1.0, pan=0.0):
    i0 = int(t0 * SR)
    gl, gr = gan * min(1, 1 - pan), gan * min(1, 1 + pan)
    for k, v in enumerate(señal):
        j = i0 + k
        if j >= N: break
        L[j] += v * gl; R[j] += v * gr


# ── instrumentos (cada uno devuelve una lista de muestras) ──
def clave():
    n = int(0.09 * SR)
    return [(math.sin(TAU * 2450 * i / SR) * 0.8 + math.sin(TAU * 1720 * i / SR) * 0.4) * math.exp(-i / SR * 60)
            + random.uniform(-1, 1) * 0.3 * math.exp(-i / SR * 400) for i in range(n)]


def conga(tipo):
    n = int(0.35 * SR); out = []; fase = 0.0
    for i in range(n):
        s = i / SR
        if tipo == "abierto":
            f = 190 + 50 * math.exp(-s * 30); fase += TAU * f / SR
            out.append(math.sin(fase) * math.exp(-s * 9))
        else:                                              # slap: más agudo, seco, con ruido
            f = 340 + 120 * math.exp(-s * 60); fase += TAU * f / SR
            out.append(math.sin(fase) * math.exp(-s * 22) * 0.8 + random.uniform(-1, 1) * 0.5 * math.exp(-s * 70))
    return out


def campana(acento):
    n = int(0.18 * SR)
    return [(1.0 if acento else 0.7) * (0.6 * math.copysign(1, math.sin(TAU * 562 * i / SR)) + 0.4 * math.copysign(1, math.sin(TAU * 845 * i / SR)))
            * math.exp(-i / SR * 24) * 0.35 for i in range(n)]


def guiro(largo):
    n = int((0.24 if largo else 0.09) * SR); lp = 0.0; out = []
    for i in range(n):
        s = i / SR
        lp += 0.35 * (random.uniform(-1, 1) - lp)
        out.append((random.uniform(-1, 1) - lp) * (0.5 + 0.5 * math.sin(TAU * 38 * s)) * min(1, s * 60) * math.exp(-s * 6) * 0.5)
    return out


def bajo(f, dur=0.5, sub=0.0):
    n = int(dur * SR)
    return [(math.sin(TAU * f * i / SR) + 0.35 * math.sin(TAU * 2 * f * i / SR) + sub * math.sin(TAU * f / 2 * i / SR))
            * min(1, i / SR * 80) * math.exp(-i / SR * 3.2) for i in range(n)]


def piano(frecs, dur=0.22):
    n = int(dur * SR)
    return [sum(math.sin(TAU * f * i / SR) + 0.3 * math.sin(TAU * 2 * f * i / SR) * math.exp(-i / SR * 12) for f in frecs)
            / len(frecs) * min(1, i / SR * 300) * math.exp(-i / SR * 9) for i in range(n)]


def click(f, dur=0.03):
    n = int(dur * SR)
    return [math.sin(TAU * f * i / SR) * math.exp(-i / SR * 160) for i in range(n)]


CACHE = {k: v for k, v in (("clave", clave()), ("abierto", conga("abierto")), ("slap", conga("slap")),
                           ("camp_a", campana(True)), ("camp", campana(False)), ("g_l", guiro(True)), ("g_c", guiro(False)),
                           ("met_a", click(1650)), ("met", click(1200)))}

# ── patrones en 16 corcheas (2 compases) ──
PAT = {"clave": [0, 3, 6, 10, 12], "slap": [2, 6, 10, 14], "abierto": [7, 15],
       "campana": [0, 2, 4, 6, 8, 10, 12, 14], "guiro": [0, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15],
       "bajo": [3, 6, 11, 14], "piano": [1, 3, 4, 6, 9, 11, 12, 14]}
nota = lambda m: 440 * 2 ** ((m - 69) / 12)
ACORDES = [(45, (57, 60, 64)), (50, (57, 62, 65)), (52, (56, 59, 64)), (45, (57, 60, 64))]   # Am Dm E Am (raíz, voces)

# ── arreglo: qué suena en cada momento (escenas 1-based, palabras de la narración) ──
TODO = {"clave", "conga", "campana", "guiro", "bajo", "piano"}


def arreglo(t):
    """Devuelve (instrumentos activos, ganancia, extras) para el instante t."""
    if t < ESC(4):                         return TODO, 1.0, set()
    if t < ESC(5):                         return set(), 2.6, {"metronomo"}          # demostraciones: más fuerte
    if t < ESC(6):                         return ({"clave"} if t >= dicho(5, "golpe") else set()), 2.4, {"metronomo"}
    if t < ESC(7):                         return {"clave", "bajo", "campana"}, 0.9, set()
    if t < ESC(8):                         return {"clave"}, 2.6, set()
    if t < ESC(9):                         return {"clave", "campana", "conga"}, 1.4, set()
    if t < ESC(10):
        act = {"clave"}
        for inst, pal in (("conga", "conga"), ("campana", "campana"), ("guiro", "güiro"), ("bajo", "bajo")):
            if t >= dicho(9, pal): act.add(inst)
        return act, 1.1, set()
    if t < ESC(11):                        return set(), 1.3, {"tres_dos"}
    if t < ESC(12):                        return {"clave", "bajo"}, 1.1, {"bajo_fuerte"}
    if t < ESC(13):                        return TODO, 1.0, {"sub"}
    if t < ESC(14):                        return {"bajo", "campana"}, 1.2, set()
    return TODO, 1.0, set()


paso_total = int(TOTAL / PASO)
for n in range(paso_total):
    t0 = n * PASO
    k = n % 16
    act, g, extra = arreglo(t0)
    raiz, voces = ACORDES[(n // 8) % 4]
    sig_raiz = ACORDES[((n // 8) + 1) % 4][0]
    if "clave" in act and k in PAT["clave"]:              suma(CACHE["clave"], t0, 0.55 * g, 0.2)
    if "conga" in act:
        if k in PAT["slap"]:                              suma(CACHE["slap"], t0, 0.42 * g, -0.45)
        if k in PAT["abierto"]:                           suma(CACHE["abierto"], t0, 0.6 * g, -0.45)
    if "campana" in act and k in PAT["campana"]:          suma(CACHE["camp_a" if k % 4 == 0 else "camp"], t0, 0.3 * g, 0.5)
    if "guiro" in act and k in PAT["guiro"]:              suma(CACHE["g_l" if k % 4 == 0 else "g_c"], t0, 0.28 * g, -0.6)
    if "bajo" in act and k in PAT["bajo"]:
        f = nota(raiz if k % 8 == 3 else sig_raiz)        # tumbao: en el "4" ya anticipa el acorde siguiente
        suma(bajo(f, 0.55, 0.6 if "sub" in extra else 0.0), t0, (0.55 if "bajo_fuerte" in extra else 0.5) * g, 0.0)
    if "piano" in act and k in PAT["piano"]:              suma(piano([nota(m) for m in voces]), t0, 0.16 * g, 0.1)
    if "metronomo" in extra and k % 2 == 0:               suma(CACHE["met_a" if k % 8 == 0 else "met"], t0, 0.5 * g, 0.0)

# Tres contra dos: en ciclos de 2 pulsos, 3 golpes agudos contra 2 graves (como los puntos del dibujo)
ciclo = 2 * 60 / BPM
c = math.ceil(ESC(10) / ciclo) * ciclo
while c < ESC(11) - 0.05:
    for j in range(3): suma(click(1320, 0.06), c + j * ciclo / 3, 0.45, 0.35)
    for j in range(2): suma(conga("abierto"), c + j * ciclo / 2, 0.6, -0.35)
    c += ciclo

# golpe final de toda la banda y fundidos
fin = (int((TOTAL - 1.2) / (8 * PASO))) * 8 * PASO
for inst in ("clave", "abierto", "camp_a"):
    suma(CACHE[inst], fin, 0.7)
suma(bajo(nota(45), 1.2, 0.5), fin, 0.7)
for i in range(N):
    s = i / SR
    gfade = min(1, s / 1.0) * min(1, (TOTAL - s) / 1.2) if s < fin + 0.1 else min(1, (TOTAL - s) / 1.2) * math.exp(-(s - fin) * 1.5)
    L[i] *= gfade; R[i] *= gfade

m = max(1e-9, max(max(abs(v) for v in L), max(abs(v) for v in R)))
datos = array.array("h")
for l, r in zip(L, R):
    datos.append(int(l / m * 0.7 * 32767)); datos.append(int(r / m * 0.7 * 32767))
os.makedirs(f"{P}/audio", exist_ok=True)
with wave.open(f"{P}/audio/musica.wav", "w") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(datos.tobytes())
print(f"musica.wav: {TOTAL:.1f} s · {BPM} BPM · arreglo según {len(tiempos)} escenas")
