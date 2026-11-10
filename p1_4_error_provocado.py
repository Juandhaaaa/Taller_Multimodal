"""1.4 Errores provocados a proposito.
Uso: python p1_4_error_provocado.py [caso]
Casos: mime_mal | muchas_imagenes | modelo_sin_vision | imagen_enorme | todos (por defecto)
Elige UNO para el informe y explica su causa con el mensaje que muestre la API.
"""
import os
import sys

from utils import MODELO_VISION, RAIZ, bloque_imagen, cargar_config, get_client, ruta

cfg = cargar_config()["p1_4"]
client = get_client()
valida = ruta(cfg["imagen_valida"])
PREG = "Describe brevemente la imagen."


def llamar(modelo, imagenes_bloques):
    return client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": [{"type": "text", "text": PREG}, *imagenes_bloques]}],
        max_tokens=100,
    )


def caso_mime_mal():
    # Declaramos un tipo que NO corresponde al archivo (p. ej. jpg declarado como gif/pdf)
    return llamar(MODELO_VISION, [bloque_imagen(valida, mime="application/pdf")])


def caso_muchas_imagenes():
    return llamar(MODELO_VISION, [bloque_imagen(valida) for _ in range(4)])  # limite = 3


def caso_modelo_sin_vision():
    return llamar(cfg["modelo_sin_vision"], [bloque_imagen(valida)])


def caso_imagen_enorme():
    from PIL import Image
    destino = RAIZ / "resultados" / "_imagen_enorme_temp.png"
    print("Generando imagen de ruido de ~27 MB (puede tardar unos segundos)...")
    Image.frombytes("RGB", (3000, 3000), os.urandom(3000 * 3000 * 3)).save(destino)
    print(f"Tamano: {destino.stat().st_size / 1024 / 1024:.1f} MB")
    try:
        return llamar(MODELO_VISION, [bloque_imagen(destino)])
    finally:
        destino.unlink(missing_ok=True)


CASOS = {
    "mime_mal": caso_mime_mal,
    "muchas_imagenes": caso_muchas_imagenes,
    "modelo_sin_vision": caso_modelo_sin_vision,
    "imagen_enorme": caso_imagen_enorme,
}

elegido = sys.argv[1] if len(sys.argv) > 1 else "todos"
if elegido != "todos" and elegido not in CASOS:
    raise SystemExit(f"Caso invalido. Opciones: {list(CASOS)} o 'todos'")

for nombre in (CASOS if elegido == "todos" else [elegido]):
    print(f"\n{'=' * 60}\nCASO: {nombre}\n{'=' * 60}")
    try:
        r = CASOS[nombre]()
        print("La API NO devolvio error. Respuesta:", r.choices[0].message.content[:200])
    except Exception as e:
        print(f"Tipo de excepcion: {type(e).__name__}")
        print(f"Codigo HTTP: {getattr(e, 'status_code', 'n/d')}")
        print(f"Mensaje de la API:\n{e}")
