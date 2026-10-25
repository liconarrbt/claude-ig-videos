"""Alinea el texto de cada escena con su audio, sin servicios externos: detecta voz/silencio,
asigna las pausas largas a la puntuación y reparte las palabras por sílabas.
Escribe subtitulos/palabras.json (lo usan animacion.py y mezcla.py) y subtitulos/palabras.srt.

Uso: python3 alinear.py <proyecto>
Precisión: buena a nivel de frase; dentro de una frase una palabra puede desviarse unas décimas.
"""
import json, os, re, struct, wave


def silabas(w):
    if w.isdigit():  # "1793" ≈ "mil setecientos noventa y tres": ~2.5 sílabas por cifra
        return max(2, round(len(w) * 2.5))
    w = w.lower()
    # cada grupo vocálico ≈ una sílaba; los hiatos con tilde cuentan doble
    grupos = re.findall(r"[aeiouáéíóúü]+", w)
    n = sum(1 + len(re.findall(r"[íú][aeo]|[aeo][íú]", g)) for g in grupos)
    return max(n, 1)


def tramos_voz(path, ventana=0.01, umbral_rel=0.06, hueco_min=0.09, voz_min=0.05):
    with wave.open(path) as f:
        sr, ch, sw, n = f.getframerate(), f.getnchannels(), f.getsampwidth(), f.getnframes()
        raw = f.readframes(n)
    assert sw == 2, "se esperaba PCM de 16 bits"
    muestras = struct.unpack(f"<{len(raw)//2}h", raw)[::ch]
    paso = int(sr * ventana)
    rms = []
    for i in range(0, len(muestras), paso):
        b = muestras[i:i + paso]
        rms.append((sum(x * x for x in b) / max(len(b), 1)) ** 0.5)
    umbral = max(rms) * umbral_rel
    tramos, ini = [], None
    for k, v in enumerate(rms + [0]):
        if v >= umbral and ini is None:
            ini = k
        elif v < umbral and ini is not None:
            tramos.append([ini * ventana, k * ventana]); ini = None
    unidos = []
    for t in tramos:  # une huecos cortos (oclusivas, respiraciones breves)
        if unidos and t[0] - unidos[-1][1] < hueco_min:
            unidos[-1][1] = t[1]
        else:
            unidos.append(t)
    return [t for t in unidos if t[1] - t[0] >= voz_min], len(muestras) / sr


def mapear(tramos, frac):
    """Convierte una fracción del tiempo con voz en un instante real del audio."""
    total = sum(b - a for a, b in tramos)
    obj = frac * total
    for a, b in tramos:
        if obj <= b - a + 1e-9:
            return a + obj
        obj -= b - a
    return tramos[-1][1]


if __name__ == "__main__":
    from comun import proyecto_desde_argv
    _p = proyecto_desde_argv()
    BASE = _p.dir
    tiempos = _p.tiempos
    salida, inicio = [], 0.0
    for e in tiempos:
        tramos, dur = tramos_voz(os.path.join(BASE, e["archivo"]))
        palabras = e["texto"].replace("…", "… ").split()
        pesos = [silabas(re.sub(r"[^\wáéíóúüñ]", "", p.lower()) or "a") for p in palabras]
        total = sum(pesos)
        cortes_txt = [sum(pesos[:k + 1]) / total for k in range(len(palabras) - 1)]  # fin de cada palabra
        puntuada = [bool(re.search(r"[,.;:…?!]$", p)) for p in palabras[:-1]]
        # Cada pausa larga del audio se asigna a la frontera entre palabras más cercana,
        # prefiriendo las que llevan puntuación; así las frases arrancan cuando arranca la voz.
        voz_total = sum(b - a for a, b in tramos)
        huecos, acc = [], 0.0
        for (a0, b0), (a1, b1) in zip(tramos, tramos[1:]):
            acc += b0 - a0
            if a1 - b0 >= 0.15:
                huecos.append((a1 - b0, acc / voz_total, b0, a1))
        elegidos = {}
        for largo, frac, b0, a1 in sorted(huecos, reverse=True):
            mejor = min((abs(c - frac) - (0.12 if puntuada[k] else 0), k) for k, c in enumerate(cortes_txt) if k not in elegidos)[1]
            if all((k < mejor) == (elegidos[k][0] < b0) for k in elegidos):  # mantiene el orden
                elegidos[mejor] = (b0, a1)
        # reparte por sílabas dentro de cada bloque entre pausas elegidas
        limites = [(-1, tramos[0][0])] + sorted((k, v) for k, v in elegidos.items()) + [(len(palabras) - 1, tramos[-1][1])]
        for (k0, v0), (k1, v1) in zip(limites, limites[1:]):
            t0 = v0[1] if isinstance(v0, tuple) else v0
            t1 = v1[0] if isinstance(v1, tuple) else v1
            sub = [[max(a, t0), min(b, t1)] for a, b in tramos if b > t0 and a < t1] or [[t0, t1]]
            ws = list(range(k0 + 1, k1 + 1))
            tot, acum = sum(pesos[i] for i in ws), 0
            for i in ws:
                a = mapear(sub, acum / tot); acum += pesos[i]
                b = mapear(sub, acum / tot)
                salida.append({"escena": e["escena"], "palabra": palabras[i], "inicio": round(inicio + a, 3), "fin": round(inicio + b, 3)})
        inicio += e["duracion"]
        print(f"escena {e['escena']}: {len(palabras)} palabras, {len(tramos)} tramos de voz")

    os.makedirs(os.path.join(BASE, "subtitulos"), exist_ok=True)
    json.dump(salida, open(os.path.join(BASE, "subtitulos", "palabras.json"), "w"), indent=1, ensure_ascii=False)

    def ts(s):
        h, r = divmod(s, 3600); m, r = divmod(r, 60)
        return f"{int(h):02}:{int(m):02}:{int(r):02},{int(round((r % 1) * 1000)):03}"

    with open(os.path.join(BASE, "subtitulos", "palabras.srt"), "w") as f:
        for i, w in enumerate(salida, 1):
            f.write(f"{i}\n{ts(w['inicio'])} --> {ts(w['fin'])}\n{w['palabra']}\n\n")
    print("total", len(salida), "palabras")
