"""Sintetiza desde cero (sin muestras externas, sin derechos de terceros) los efectos y la cama musical.
Salida en <proyecto>/audio/: whoosh.wav, pop.wav, pop_grave.wav, tictac.wav, musica.wav (44.1 kHz, 16 bits).

Uso: python3 sfx.py <proyecto>       (la música dura lo mismo que la narración + 0.6 s)
Para usar música propia: guarda audio/musica.wav y corre con --solo-efectos.
"""
import array, json, math, os, random, sys, wave
from comun import proyecto_desde_argv

_p = proyecto_desde_argv()
OUT = _p.ruta("audio", "x")[:-2]
SR = 44100
TAU = 2 * math.pi
random.seed(60)


def guardar(nombre, x, pico=0.89, estereo=None):
    m = max(1e-9, max(abs(v) for v in x))
    datos = array.array("h")
    if estereo is None:
        datos.extend(int(v / m * pico * 32767) for v in x)
        canales = 1
    else:  # estereo = segunda señal (derecha)
        m = max(m, max(abs(v) for v in estereo))
        for l, r in zip(x, estereo):
            datos.append(int(l / m * pico * 32767)); datos.append(int(r / m * pico * 32767))
        canales = 2
    with wave.open(os.path.join(OUT, nombre), "w") as f:
        f.setnchannels(canales); f.setsampwidth(2); f.setframerate(SR); f.writeframes(datos.tobytes())
    print(f"{nombre}: {len(x) / SR:.2f} s")


def whoosh(dur=0.7):
    """Ruido filtrado con un pasa-banda que barre de grave a agudo y vuelve, envolvente en campana."""
    n = int(dur * SR); y = []
    lp1 = lp2 = bp = 0.0
    for i in range(n):
        t = i / n
        env = math.sin(math.pi * t) ** 2.2
        fc = 300 + 3200 * math.sin(math.pi * t) ** 1.5   # barrido del filtro
        g = 1 - math.exp(-TAU * fc / SR)
        r = random.uniform(-1, 1)
        lp1 += g * (r - lp1); lp2 += g * (lp1 - lp2)    # pasa-bajos de 2 polos
        bp = lp1 - lp2                                   # ≈ pasa-banda
        y.append((bp * 3 + lp2 * 0.6) * env)
    return y


def pop(f0=900, f1=260, dur=0.14):
    """Seno con caída rápida de tono y transitorio de ruido: un 'plop' corto."""
    n = int(dur * SR); y = []; fase = 0.0
    for i in range(n):
        t = i / SR
        f = f1 + (f0 - f1) * math.exp(-t * 45)
        fase += TAU * f / SR
        env = math.exp(-t * 30) * min(1, t * 2000)
        click = random.uniform(-1, 1) * math.exp(-t * 900) * 0.25
        y.append(math.sin(fase) * env + click)
    return y


def tictac(dur=6.0, intervalo=0.5):
    """Tic-tac de reloj: clics agudos alternando tono (tic más agudo, tac más grave)."""
    n = int(dur * SR); y = [0.0] * n
    k = 0
    while k * intervalo < dur - 0.05:
        ini = int(k * intervalo * SR); f = 3400 if k % 2 == 0 else 2600
        for i in range(int(0.035 * SR)):
            if ini + i >= n: break
            t = i / SR
            env = math.exp(-t * 180)
            y[ini + i] += (math.sin(TAU * f * t) * 0.7 + math.sin(TAU * f * 2.3 * t) * 0.3 + random.uniform(-1, 1) * 0.3 * math.exp(-t * 600)) * env
        k += 1
    return y


def musica(dur):
    """Cama ambiental en La menor a 90 BPM: pad (Am–F–C–G), arpegio pulsado y bajo suave."""
    nota = lambda m: 440 * 2 ** ((m - 69) / 12)
    acordes = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]  # Am F C G
    negra = 60 / 90; compas = 4 * negra; por_acorde = 2 * compas
    n = int(dur * SR); L = [0.0] * n; R = [0.0] * n
    # pad: dos osciladores desafinados por nota, uno a cada lado (sensación estéreo)
    for idx in range(int(dur / por_acorde) + 1):
        t0 = idx * por_acorde; notas = acordes[idx % 4]
        a, b = int(max(0, t0 - 0.6) * SR), min(n, int((t0 + por_acorde + 0.6) * SR))
        for m in notas:
            for det, canal in ((-0.12, L), (0.12, R)):
                f = nota(m) * 2 ** (det / 12); w = TAU * f / SR
                for i in range(a, b):
                    t = i / SR - (t0 - 0.6)
                    env = min(1, t / 1.2) * min(1, ((t0 + por_acorde + 0.6) - i / SR) / 1.2)
                    ph = w * i
                    canal[i] += (math.sin(ph) + 0.18 * math.sin(3 * ph)) * env * 0.05
    # arpegio en corcheas: notas del acorde una octava arriba, ataque pulsado
    corchea = negra / 2; k = 0
    while k * corchea < dur:
        t0 = k * corchea; notas = acordes[int(t0 // por_acorde) % 4]
        m = (notas + tuple(x + 12 for x in notas))[[0, 1, 2, 4, 3, 1, 2, 5][k % 8]] + 12
        f = nota(m); ini = int(t0 * SR); pan = 0.5 + 0.35 * math.sin(k * 0.9)
        for i in range(int(0.45 * SR)):
            j = ini + i
            if j >= n: break
            t = i / SR
            v = (math.sin(TAU * f * t) + 0.3 * math.sin(TAU * 2 * f * t) * math.exp(-t * 20)) * math.exp(-t * 7) * min(1, t * 400) * 0.06
            L[j] += v * (1 - pan); R[j] += v * pan
        k += 1
    # bajo: fundamental en cada compás, seno suave
    for c in range(int(dur / compas) + 1):
        t0 = c * compas; f = nota(acordes[int(t0 // por_acorde) % 4][0] - 12)
        ini = int(t0 * SR)
        for i in range(int(compas * SR)):
            j = ini + i
            if j >= n: break
            t = i / SR
            v = math.sin(TAU * f * t) * math.exp(-t * 1.4) * min(1, t * 60) * 0.16
            L[j] += v; R[j] += v
    # fundido de entrada y salida
    for i in range(n):
        t = i / SR
        g = min(1, t / 1.5) * min(1, (dur - t) / 2.5)
        L[i] *= g; R[i] *= g
    return L, R


TOTAL = _p.total
guardar("whoosh.wav", whoosh())
guardar("pop.wav", pop())
guardar("pop_grave.wav", pop(f0=420, f1=70, dur=0.35))
guardar("tictac.wav", tictac())
if "--solo-efectos" not in sys.argv:
    Lm, Rm = musica(TOTAL)
    guardar("musica.wav", Lm, pico=0.7, estereo=Rm)
