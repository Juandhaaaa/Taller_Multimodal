"""Utilidades compartidas por todos los scripts del taller."""
import base64
import json
import mimetypes
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

RAIZ = Path(__file__).parent
load_dotenv(RAIZ / ".env")

MODELO_VISION = os.getenv("MODEL_VISION", "qwen/qwen3.8-27b")
MODELO_AUDIO = os.getenv("MODEL_AUDIO", "whisper-large-v3-turbo")
MODELO_TEXTO = os.getenv("MODEL_TEXT", "llama-3.3-70b-versatile")

EXT_AUDIO = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac", ".mp4", ".mpeg", ".mpga"}
LIMITE_AUDIO_MB = 25


def get_client() -> Groq:
    clave = os.getenv("GROQ_API_KEY")
    if not clave or clave.startswith("pon_aqui"):
        sys.exit("ERROR: define GROQ_API_KEY en el archivo .env (copia .env.example como .env).")
    return Groq(api_key=clave)


def cargar_config() -> dict:
    with open(RAIZ / "config_dominio.json", encoding="utf-8") as f:
        return json.load(f)


def ruta(rel: str) -> Path:
    """Convierte una ruta relativa al proyecto en ruta absoluta."""
    return RAIZ / rel


def mime_de(archivo: Path) -> str:
    mime, _ = mimetypes.guess_type(str(archivo))
    return mime or "image/jpeg"


def data_url(archivo: Path, mime: str | None = None) -> str:
    """Lee una imagen local y la devuelve como data URL base64."""
    if not archivo.exists():
        sys.exit(f"ERROR: no existe la imagen {archivo}. Ponla en la carpeta imagenes/.")
    b64 = base64.b64encode(archivo.read_bytes()).decode("utf-8")
    return f"data:{mime or mime_de(archivo)};base64,{b64}"


def bloque_imagen(archivo: Path, mime: str | None = None) -> dict:
    return {"type": "image_url", "image_url": {"url": data_url(archivo, mime)}}


def limpiar_respuesta(texto: str) -> str:
    """Quita bloques <think>...</think> que algunos modelos de razonamiento incluyen."""
    return re.sub(r"<think>.*?</think>", "", texto or "", flags=re.DOTALL).strip()


def extraer_json(texto: str):
    """Intenta convertir la respuesta del modelo en JSON. Lanza ValueError si no puede."""
    texto = limpiar_respuesta(texto)
    texto = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", texto, flags=re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise ValueError("La respuesta no contiene un JSON valido")


def guardar(nombre: str, contenido: str) -> Path:
    destino = RAIZ / "resultados" / nombre
    destino.write_text(contenido, encoding="utf-8")
    print(f"\n[guardado en {destino.relative_to(RAIZ)}]")
    return destino


def transcribir(client: Groq, archivo: Path, vocabulario: str | None = None) -> dict:
    """Transcribe un audio con Whisper. Devuelve {texto, duracion}."""
    mb = archivo.stat().st_size / (1024 * 1024)
    if mb > LIMITE_AUDIO_MB:
        raise ValueError(f"{archivo.name} pesa {mb:.1f} MB y supera el limite de {LIMITE_AUDIO_MB} MB")
    args = dict(
        file=(archivo.name, archivo.read_bytes()),
        model=MODELO_AUDIO,
        language="es",
        response_format="verbose_json",
        temperature=0.0,
    )
    if vocabulario:
        args["prompt"] = vocabulario
    r = client.audio.transcriptions.create(**args)
    return {"texto": r.text.strip(), "duracion": getattr(r, "duration", None)}
