# game/sprites.py
from pathlib import Path

import cv2


class Animacion:
    def __init__(self, frames, escala=1.0):
        self.frames = frames  # imágenes BGRA
        self.escala = escala  # tamaño relativo al radio del objeto

    def por_progreso(self, p):
        """p en 0..1 → fotograma correspondiente."""
        i = min(int(p * len(self.frames)), len(self.frames) - 1)
        return self.frames[max(i, 0)]


def cargar_sprites(carpeta: Path, tipo: str, escalas: dict | None = None) -> dict:
    """Cada subcarpeta de carpeta/<tipo>/ es una animación (el nombre de la carpeta es su nombre)."""
    escalas = escalas or {}
    anims = {}
    for sub in sorted((carpeta / tipo).iterdir()):
        if not sub.is_dir():
            continue
        frames = [cv2.imread(str(r), cv2.IMREAD_UNCHANGED) for r in sorted(sub.glob("*.png"))]
        if not frames or any(f is None for f in frames):
            raise FileNotFoundError(f"Fotogramas vacíos o corruptos en {sub}")
        anims[sub.name] = Animacion(frames, escalas.get(sub.name, 1.0))
    if "normal" not in anims:
        raise FileNotFoundError(f"Falta la carpeta 'normal' en {carpeta / tipo}")
    return anims