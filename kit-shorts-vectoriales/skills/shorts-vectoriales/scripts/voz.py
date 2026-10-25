"""Narración por escena con Fish Audio → voz/escenaN.wav + voz/tiempos.json.

Uso: python3 voz.py <proyecto> [--escenas 4,7]   (solo regenera esas escenas; el resto se conserva)
La voz y la velocidad salen de escenas.json → "voz": {"id": "...", "velocidad": 1.1}.
La clave se lee de FISHAUDIO_API_KEY: entorno, un archivo .env en el proyecto o en alguna carpeta superior, o ~/.zshrc.
"""
import json, os, re, subprocess, time, urllib.error, urllib.request
from comun import proyecto_desde_argv

VOZ_POR_DEFECTO = "d047b6a8f24f4d56ba818b08dbd9d089"  # "nicho de horror 2": narrador masculino, serio
MODELOS = ["s2.1-pro", "s2.1-pro-free"]  # sin crédito de API, el de pago responde 402 y se usa el gratuito

p = proyecto_desde_argv()
cfg = p.spec.get("voz", {})
voz, velocidad = cfg.get("id", VOZ_POR_DEFECTO), cfg.get("velocidad", 1.1)
def clave_env(desde):
    """Busca FISHAUDIO_API_KEY en un .env desde `desde` hacia arriba (sin imprimirla nunca)."""
    d = os.path.abspath(desde)
    while True:
        f = os.path.join(d, ".env")
        if os.path.isfile(f):
            for linea in open(f, encoding="utf-8"):
                k, _, v = linea.strip().partition("=")
                if k.strip() == "FISHAUDIO_API_KEY" and v.strip():
                    return v.strip().strip('"').strip("'")
        if os.path.dirname(d) == d:
            return ""
        d = os.path.dirname(d)


key = os.environ.get("FISHAUDIO_API_KEY") or clave_env(p.dir) or clave_env(os.path.dirname(os.path.abspath(__file__))) or subprocess.run(
    ["zsh", "-ic", 'printf %s "$FISHAUDIO_API_KEY"'], capture_output=True, text=True).stdout
if not key:
    raise SystemExit("Falta FISHAUDIO_API_KEY (ponla en un .env: FISHAUDIO_API_KEY=..., o expórtala en ~/.zshrc)")


def tts(texto):
    body = json.dumps({"text": texto, "reference_id": voz, "format": "wav", "latency": "normal",
                       "prosody": {"speed": velocidad}, "language": "es"}).encode()
    for intento in range(5):                 # el modelo gratuito a veces responde 402 un rato: se reintenta con espera
        for modelo in MODELOS:
            req = urllib.request.Request("https://api.fish.audio/v1/tts", data=body, headers={
                "Authorization": "Bearer " + key, "Content-Type": "application/json", "model": modelo})
            try:
                return urllib.request.urlopen(req, timeout=180).read(), modelo
            except urllib.error.HTTPError as e:
                if e.code != 402:
                    raise SystemExit(f"Fish Audio {e.code}: {e.read()[:300]}")
        print(f"  Fish Audio 402 en ambos modelos; reintento en {10 * 2 ** intento} s", flush=True)
        time.sleep(10 * 2 ** intento)
    raise SystemExit("Fish Audio: sin crédito ni en el modelo gratuito")


import sys
solo = {int(x) for x in sys.argv[sys.argv.index("--escenas") + 1].split(",")} if "--escenas" in sys.argv else None
previos = {e["escena"]: e for e in json.load(open(p.ruta("voz", "tiempos.json")))} if solo and os.path.exists(p.ruta("voz", "tiempos.json")) else {}
out = []
for i, esc in enumerate(p.escenas, 1):
    if solo and i not in solo and i in previos and previos[i]["texto"] == esc["narracion"]:
        out.append(previos[i]); continue
    audio, modelo = tts(esc["narracion"])
    archivo = f"voz/escena{i}.wav"
    open(p.ruta(archivo), "wb").write(audio)
    info = subprocess.run(["afinfo", p.ruta(archivo)], capture_output=True, text=True).stdout
    dur = float(re.search(r"estimated duration: ([\d.]+)", info).group(1))
    out.append({"escena": i, "archivo": archivo, "duracion": round(dur, 3), "texto": esc["narracion"]})
    print(f"escena {i}: {dur:5.2f} s  ({modelo})  {esc['narracion'][:50]}")
json.dump(out, open(p.ruta("voz", "tiempos.json"), "w"), indent=1, ensure_ascii=False)
print(f"total {sum(o['duracion'] for o in out):.2f} s · voz {voz}")
