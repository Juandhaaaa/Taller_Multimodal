# Taller: Entrada multimodal y audio

Desarrollo de Aplicaciones con IA. Visión (imágenes) y audio (transcripción) aplicados al dominio del proyecto.

## 1. Preparación

```bash
cd taller_multimodal
python -m venv .venv
# Windows:  .venv\Scripts\activate      Mac/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # en Windows: copy .env.example .env
```

Edita `.env` y pon tu clave en `GROQ_API_KEY` (créala en https://console.groq.com/keys).
**El archivo `.env` está en `.gitignore`: nunca lo subas.**

### Variables de entorno

| Variable | Obligatoria | Por defecto |
|---|---|---|
| `GROQ_API_KEY` | Sí | — |
| `MODEL_VISION` | No | `qwen/qwen3.8-27b` |
| `MODEL_AUDIO` | No | `whisper-large-v3-turbo` |
| `MODEL_TEXT` | No | `llama-3.3-70b-versatile` |

## 2. Adaptar al dominio

1. Pon tus imágenes en `imagenes/` (mínimo 5) y tus audios en `audios/` (mínimo 4, de 10 a 30 s).
2. Edita `config_dominio.json`: dominio, rutas de imágenes, preguntas y los campos del esquema (mínimo 5).
3. Edita `audios/metadata.json`: quién habla, si hay ruido y qué dijeron exactamente.

## 3. Ejecución

| Punto | Comando |
|---|---|
| 1.1 Pregunta sobre una imagen | `python p1_1_pregunta_imagen.py` |
| 1.2 Extracción estructurada | `python p1_2_extraccion_estructurada.py` (1ª vez crea `ground_truth.json`; llénalo con los valores reales y vuelve a ejecutar) |
| 1.3 Varias imágenes | `python p1_3_varias_imagenes.py` |
| 1.4 Error provocado | `python p1_4_error_provocado.py modelo_sin_vision` (otros: `mime_mal`, `muchas_imagenes`, `imagen_enorme`, `todos`) |
| 2.1 Transcripción | `python p2_1_transcripcion.py` (opcional `--con-vocabulario`) |
| 2.2 Audio → transcripción → respuesta | `python p2_2_respuesta_desde_audio.py` |

Cada script imprime el resultado en consola (para las capturas del informe) y guarda un `.md` en `resultados/`.

## 4. Límites a tener en cuenta

- Visión (Groq): máx. 3 imágenes y 20 MB por solicitud.
- Audio (Groq, plan gratuito): hasta 25 MB; formatos wav, mp3, m4a, ogg, webm.

## 5. Estructura

```
taller_multimodal/
├── config_dominio.json     # lo único que hay que adaptar
├── utils.py                # cliente, base64, validaciones comunes
├── p1_1 ... p1_4           # Parte 1: visión
├── p2_1, p2_2              # Parte 2: audio
├── imagenes/  audios/      # material del dominio
└── resultados/             # salidas generadas
```
