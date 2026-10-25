"""Crea la carpeta de un proyecto nuevo con escenas.json y dibujar.py de plantilla.

Uso: python3 nuevo_proyecto.py <carpeta> "<Título del short>"
"""
import json, os, sys

KIT = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) < 3:
    sys.exit(__doc__)
carpeta, titulo = os.path.abspath(sys.argv[1]), sys.argv[2]
if os.path.exists(os.path.join(carpeta, "escenas.json")):
    sys.exit(f"{carpeta} ya tiene escenas.json; no lo sobrescribo")
os.makedirs(carpeta, exist_ok=True)

escenas = {
    "titulo": titulo,
    "voz": {"id": "d047b6a8f24f4d56ba818b08dbd9d089", "velocidad": 1.1},
    "escenas": [
        {"narracion": "Gancho: una pregunta o dato que contradiga lo que todos creen.",
         "titulares": [{"texto": "TITULAR CON UNA PALABRA CLAVE", "acento": "CLAVE"}],
         "capas": [{"svg": "ilustracion1", "dibujo": 1.2, "empuje": 0.06}]},
        {"narracion": "Explicación con un dato concreto que la voz menciona.",
         "titulares": [{"texto": "SEGUNDO TITULAR", "acento": "SEGUNDO"}],
         "capas": [{"svg": "ilustracion1", "dibujo": 0, "empuje": 0.04}],
         "textos": [{"texto": "DATO · FUENTE · AÑO", "desde": "dato"}]},
    ],
    "miniatura": {"texto": "PREGUNTA\nCORTA", "acento": "CORTA", "ilustraciones": ["ilustracion1"]},
}
json.dump(escenas, open(os.path.join(carpeta, "escenas.json"), "w"), indent=2, ensure_ascii=False)

open(os.path.join(carpeta, "dibujar.py"), "w").write(f'''"""Ilustraciones de este proyecto (VectorCraft). Corre: python3 dibujar.py <esta carpeta>"""
import os, sys
sys.path.insert(0, os.environ.get("KIT_SHORTS", {KIT!r}))
from vc import Doc, polar, radial, esfera, hoja_contactos, O, W, G, NEGRO, C

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))

# Lienzo de 900×900, centro (450, 450). Solo trazos: blanco = estructura, O = acento, G = guías.
d = Doc()
esfera(d)                                  # ejemplo: una esfera de reloj
d.style(O, 4, fill=O).circle(C, C, 26)
d.save(P, "ilustracion1")

hoja_contactos(P, ["ilustracion1"], os.path.join(P, "revision", "ilustraciones.png"))
''')
print(f"Proyecto creado en {carpeta}\n  1) escribe la narración y las escenas en escenas.json\n"
      f"  2) dibuja las ilustraciones en dibujar.py\n  3) python3 {KIT}/producir.py {carpeta}")
