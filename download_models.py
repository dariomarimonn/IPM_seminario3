import os
import urllib.request

MODELOS = {
    "pose_landmarker_full.task": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task",
    "hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
}
CARPETA = os.path.join(os.path.dirname(__file__), "models")

os.makedirs(CARPETA, exist_ok=True)
for nombre, url in MODELOS.items():
    destino = os.path.join(CARPETA, nombre)
    if os.path.exists(destino):
        print(f"{nombre} ya existe.")
    else:
        urllib.request.urlretrieve(url, destino)
        print(f"{nombre} descargado.")
