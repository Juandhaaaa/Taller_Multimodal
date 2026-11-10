"""1.3 Varias imagenes (2 o 3) en una sola solicitud.
Uso: python p1_3_varias_imagenes.py
"""
from utils import MODELO_VISION, bloque_imagen, cargar_config, get_client, guardar, limpiar_respuesta, ruta

cfg = cargar_config()["p1_3"]
imagenes = cfg["imagenes"]
pregunta = cfg["pregunta"]
if not 2 <= len(imagenes) <= 3:
    raise SystemExit("Usa 2 o 3 imagenes en p1_3 (el limite del modelo es 3 por solicitud).")

contenido = [{"type": "text", "text": pregunta}]
for rel in imagenes:
    contenido.append(bloque_imagen(ruta(rel)))

client = get_client()
resp = client.chat.completions.create(
    model=MODELO_VISION, messages=[{"role": "user", "content": contenido}],
    temperature=0.2, max_tokens=800)
respuesta = limpiar_respuesta(resp.choices[0].message.content)

print(f"Imagenes: {imagenes}\nPregunta: {pregunta}\n\nRespuesta:\n{respuesta}")
guardar("1_3_varias_imagenes.md",
        f"# 1.3 Varias imágenes\n\n- Imágenes: {imagenes}\n- Pregunta: {pregunta}\n\n## Respuesta\n\n{respuesta}\n")
