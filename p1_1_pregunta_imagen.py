"""1.1 Pregunta sobre una imagen local (base64).
Uso: python p1_1_pregunta_imagen.py [ruta_imagen] [pregunta]
"""
import sys

from utils import MODELO_VISION, bloque_imagen, cargar_config, get_client, guardar, limpiar_respuesta, ruta

cfg = cargar_config()["p1_1"]
img = ruta(sys.argv[1]) if len(sys.argv) > 1 else ruta(cfg["imagen"])
pregunta = sys.argv[2] if len(sys.argv) > 2 else cfg["pregunta"]

client = get_client()
resp = client.chat.completions.create(
    model=MODELO_VISION,
    messages=[{
        "role": "user",
        "content": [{"type": "text", "text": pregunta}, bloque_imagen(img)],
    }],
    temperature=0.2,
)
respuesta = limpiar_respuesta(resp.choices[0].message.content)

print(f"Modelo:   {MODELO_VISION}")
print(f"Imagen:   {img.name}")
print(f"Pregunta: {pregunta}")
print(f"\nRespuesta:\n{respuesta}")

guardar("1_1_pregunta_imagen.md",
        f"# 1.1 Pregunta sobre una imagen\n\n- Modelo: {MODELO_VISION}\n- Imagen: {img.name}\n"
        f"- Pregunta: {pregunta}\n\n## Respuesta\n\n{respuesta}\n")
