"""2.1 Transcripcion de todos los audios de la carpeta audios/.
Uso: python p2_1_transcripcion.py [--con-vocabulario]
(--con-vocabulario envia los terminos tecnicos de config_dominio.json como pista a Whisper;
 util para comparar con y sin pista y comentarlo en el informe.)
"""
import json
import sys

from utils import EXT_AUDIO, RAIZ, MODELO_AUDIO, cargar_config, get_client, guardar, transcribir

con_vocab = "--con-vocabulario" in sys.argv
vocab = cargar_config().get("vocabulario_audio") if con_vocab else None

meta_path = RAIZ / "audios" / "metadata.json"
meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

archivos = sorted(p for p in (RAIZ / "audios").iterdir() if p.suffix.lower() in EXT_AUDIO)
if not archivos:
    raise SystemExit("No hay audios en audios/. Graba al menos 4 (10-30 s) y ponlos ahi.")

client = get_client()
resultados, filas = [], []
for a in archivos:
    print(f"\nTranscribiendo {a.name} con {MODELO_AUDIO}...")
    try:
        t = transcribir(client, a, vocab)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue
    m = meta.get(a.name, {})
    dur = f"{t['duracion']:.1f}" if t["duracion"] else "n/d"
    print(f"  Duracion: {dur} s\n  Transcripcion: {t['texto']}")
    resultados.append({"archivo": a.name, "texto": t["texto"], "duracion": t["duracion"]})
    filas.append(f"| {a.name} | {m.get('hablante', '')} | {'con ruido' if m.get('ruido') else 'sin ruido'} "
                 f"| {dur} | {m.get('dijo', '')} | {t['texto']} |")

(RAIZ / "resultados" / "transcripciones.json").write_text(
    json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
tabla = ("| Audio | Hablante | Condición | Duración (s) | Lo que se dijo | Transcripción |\n"
         "|---|---|---|---|---|---|\n" + "\n".join(filas))
guardar("2_1_transcripciones.md", tabla + "\n")
