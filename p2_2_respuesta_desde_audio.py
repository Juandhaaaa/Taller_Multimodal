"""2.2 Flujo completo: audio -> transcripcion -> respuesta del modelo.
Uso: python p2_2_respuesta_desde_audio.py
Si todavia no existe resultados/transcripciones.json, transcribe los audios primero.
"""
import json

from utils import (EXT_AUDIO, MODELO_AUDIO, MODELO_TEXTO, RAIZ, cargar_config, get_client,
                   guardar, limpiar_respuesta, transcribir)

cfg = cargar_config()
client = get_client()
ruta_json = RAIZ / "resultados" / "transcripciones.json"

if ruta_json.exists():
    transcripciones = json.loads(ruta_json.read_text(encoding="utf-8"))
else:
    transcripciones = []
    for a in sorted(p for p in (RAIZ / "audios").iterdir() if p.suffix.lower() in EXT_AUDIO):
        t = transcribir(client, a)
        transcripciones.append({"archivo": a.name, "texto": t["texto"], "duracion": t["duracion"]})

SISTEMA = (f"Eres un asistente experto en {cfg['dominio']}. Responde en español de forma clara "
           "y concisa (maximo 5 lineas). Si la pregunta no es clara, dilo.")

filas = []
for t in transcripciones:
    print(f"\n{'=' * 60}\nAUDIO: {t['archivo']}  ({MODELO_AUDIO} -> {MODELO_TEXTO})")
    print(f"Transcripcion: {t['texto']}")
    r = client.chat.completions.create(
        model=MODELO_TEXTO,
        messages=[{"role": "system", "content": SISTEMA}, {"role": "user", "content": t["texto"]}],
        temperature=0.2,
    )
    resp = limpiar_respuesta(r.choices[0].message.content)
    print(f"Respuesta:\n{resp}")
    filas.append(f"| {t['archivo']} | {t['texto']} | {resp.replace(chr(10), ' ')} |  |")

tabla = ("| Audio | Transcripción enviada | Respuesta del modelo | ¿Correcta y pertinente? |\n"
         "|---|---|---|---|\n" + "\n".join(filas))
guardar("2_2_respuestas.md", tabla + "\n")
