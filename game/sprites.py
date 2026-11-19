from pathlib import Path

import cv2

MODOS = ("fija", "bucle", "progreso")


class Animacion:
    """Fotogramas de una animación y cómo se dibujan."""

    def __init__(self, frames, modo: str = "fija", escala: float = 1.0,
                 giro: float = 0.0, fps: float = 12.0, ajustar: bool = False,
                 invertir: bool = False):
        if modo not in MODOS:
            raise ValueError(f"Modo de animación desconocido: {modo!r} (válidos: {MODOS})")
        self.frames = frames        # BGRA
        self.modo = modo
        self.escala = escala
        self.giro = giro            # °/s
        self.fps = fps
        self.ajustar = ajustar      # escala con obj.progreso
        self.invertir = invertir    # modo progreso al revés

    def fotograma(self, edad: float, avance: float):
        n = len(self.frames)
        if self.modo == "bucle":
            i = int(edad * self.fps) % n
        elif self.modo == "progreso":
            p = 1.0 - avance if self.invertir else avance
            i = min(int(p * n), n - 1)
        else:
            i = 0
        return self.frames[i]


class SpriteTipo:
    """Estado → Animacion; un estado sin entrada usa la de ACTIVO."""

    def __init__(self, animaciones: dict):
        if "ACTIVO" not in animaciones:
            raise ValueError("Cada tipo necesita al menos una animación para el estado ACTIVO")
        self._animaciones = animaciones

    def para(self, estado: str) -> Animacion:
        return self._animaciones.get(estado, self._animaciones["ACTIVO"])


def cargar_sprites(carpeta: Path, tipo: str, descriptores: dict) -> SpriteTipo:
    """descriptores = FICHAS[tipo]["animaciones"]."""
    leidas = {}
    animaciones = {}
    for estado, d in descriptores.items():
        d = dict(d)
        nombre = d.pop("carpeta")
        if nombre not in leidas:
            leidas[nombre] = _leer_frames(carpeta / tipo / nombre)
        animaciones[estado] = Animacion(leidas[nombre], **d)
    return SpriteTipo(animaciones)


def _leer_frames(ruta: Path) -> list:
    frames = [cv2.imread(str(r), cv2.IMREAD_UNCHANGED) for r in sorted(ruta.glob("*.png"))]
    if not frames or any(f is None for f in frames):
        raise FileNotFoundError(f"Fotogramas vacíos o corruptos en {ruta}")
    return frames
