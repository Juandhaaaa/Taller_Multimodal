"""1.2 Extraccion estructurada de 3 imagenes con validacion de JSON y % de aciertos.
Uso: python p1_2_extraccion_estructurada.py
Primera vez: genera ground_truth.json (plantilla). Llenalo con los valores REALES
que lees en cada imagen y vuelve a ejecutar para obtener el porcentaje de aciertos.
"""
import json

from utils import (MODELO_VISION, RAIZ, bloque_imagen, cargar_config, extraer_json,
                   get_client, guardar, ruta)

cfg = cargar_config()["p1_2"]
CAMPOS = cfg["campos"]
IMAGENES = cfg["imagenes"]
TIPOS = {"string": str, "number": (int, float), "boolean": bool}


def validar(datos, campos) -> list[str]:
    """Devuelve la lista de problemas del JSON (vacia si cumple el esquema)."""
    if not isinstance(datos, dict):
        return ["La respuesta no es un objeto JSON"]
    problemas = []
    for c in campos:
        n, t = c["nombre"], c["tipo"]
        if n not in datos:
            problemas.append(f"Falta el campo '{n}'")
            continue
        v = datos[n]
        if v is None:
            continue  # null = el modelo indica que no se ve en la imagen
        if t == "number" and isinstance(v, bool):
            problemas.append(f"'{n}' deberia ser number y es boolean")
        elif not isinstance(v, TIPOS[t]):
            problemas.append(f"'{n}' deberia ser {t} y es {type(v).__name__}")
    extras = set(datos) - {c["nombre"] for c in campos}
    if extras:
        problemas.append(f"Campos no esperados: {sorted(extras)}")
    return problemas


def construir_prompt() -> str:
    lineas = [f'- "{c["nombre"]}" ({c["tipo"]}): {c["descripcion"]}' for c in CAMPOS]
    return (
        "Extrae de la imagen los siguientes campos y responde UNICAMENTE con un objeto JSON "
        "valido (sin texto adicional ni markdown). Si un campo no es legible o no aparece, "
        "usa null. Los campos number deben ser numeros sin unidades.\n\n" + "\n".join(lineas)
    )


def extraer(client, img):
    mensajes = [{"role": "user", "content": [
        {"type": "text", "text": construir_prompt()}, bloque_imagen(img)]}]
    try:
        r = client.chat.completions.create(
            model=MODELO_VISION, messages=mensajes, temperature=0,
            response_format={"type": "json_object"})
    except Exception as e:  # el modelo/proveedor puede no soportar json_object
        print(f"  (json_object no disponible: {type(e).__name__}; reintentando sin ese modo)")
        r = client.chat.completions.create(model=MODELO_VISION, messages=mensajes, temperature=0)
    return r.choices[0].message.content


def normalizar(v):
    if isinstance(v, str):
        return " ".join(v.lower().split())
    return v


def iguales(real, extraido) -> bool:
    if real is None or extraido is None:
        return real is None and extraido is None
    if isinstance(real, (int, float)) and isinstance(extraido, (int, float)) \
            and not isinstance(real, bool) and not isinstance(extraido, bool):
        return abs(float(real) - float(extraido)) < 1e-6
    return normalizar(real) == normalizar(extraido)


client = get_client()
extraidos = {}
for rel in IMAGENES:
    print(f"\n=== {rel} ===")
    crudo = extraer(client, ruta(rel))
    print("Respuesta cruda:", crudo.strip())
    try:
        datos = extraer_json(crudo)
    except Exception as e:
        print(f"  JSON INVALIDO: {e}")
        extraidos[rel] = None
        continue
    problemas = validar(datos, CAMPOS)
    if problemas:
        print("  El JSON NO cumple el esquema:")
        for p in problemas:
            print("   -", p)
        extraidos[rel] = None if not isinstance(datos, dict) else datos
    else:
        print("  JSON valido segun el esquema.")
        extraidos[rel] = datos

(RAIZ / "resultados" / "1_2_extraidos.json").write_text(
    json.dumps(extraidos, ensure_ascii=False, indent=2), encoding="utf-8")

# ---- comparacion con la verdad (ground truth) ----
gt_path = RAIZ / "ground_truth.json"
if not gt_path.exists():
    plantilla = {rel: {c["nombre"]: None for c in CAMPOS} for rel in IMAGENES}
    gt_path.write_text(json.dumps(plantilla, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSe creo {gt_path.name}. Llenalo con los valores REALES de cada imagen "
          "y ejecuta de nuevo para calcular el porcentaje de aciertos.")
    raise SystemExit

gt = json.loads(gt_path.read_text(encoding="utf-8"))
filas, aciertos, total = [], 0, 0
for rel in IMAGENES:
    for c in CAMPOS:
        n = c["nombre"]
        real = gt.get(rel, {}).get(n)
        ext = (extraidos.get(rel) or {}).get(n, "(sin JSON valido)")
        ok = iguales(real, ext)
        aciertos += ok
        total += 1
        filas.append(f"| {rel.split('/')[-1]} | {n} | {real} | {ext} | {'Sí' if ok else 'No'} |")

pct = 100 * aciertos / total if total else 0
tabla = ("| Imagen | Campo | Valor real | Valor extraído | ¿Correcto? |\n|---|---|---|---|---|\n"
         + "\n".join(filas))
resumen = f"\n**Porcentaje de aciertos:** {aciertos} de {total} campos = {pct:.1f} %"
print("\n" + tabla + resumen)
guardar("1_2_tabla_aciertos.md", tabla + "\n" + resumen + "\n")
