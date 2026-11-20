"""Zona del agujero negro: cuadrilátero variable con pulgares e índices de ambas manos."""
import math

from config import HandLandmark, Landmark
from .formas import Poligono

DEDOS_POSE = (Landmark.INDICE_IZQ, Landmark.INDICE_DER, Landmark.PULGAR_DER, Landmark.PULGAR_IZQ)
DEDOS_MANO = (HandLandmark.THUMB_TIP, HandLandmark.INDEX_TIP)   # 4 y 8 de cada mano


def dedos_pose(puntos: dict) -> list:
    """Los 4 vértices desde la pose (aproximados: índice y pulgar de una mano caen muy juntos)."""
    return [puntos[p] for p in DEDOS_POSE]


def dedos_manos(manos: dict) -> list | None:
    """Los 4 vértices desde HandLandmarker (puntas de pulgar e índice); None si no hay dos manos."""
    if len(manos) < 2:
        return None
    return [mano[p] for mano in manos.values() for p in DEDOS_MANO]


def medir(vertices: list, escala: float) -> tuple[Poligono, dict]:
    """Cuadrilátero y sus medidas en anchos de hombros: área (hombros²) y lado más corto."""
    zona = Poligono(_ordenar(vertices))
    return zona, {"area": zona.area / escala ** 2, "lado": min(zona.lados) / escala}


def agujero(vertices: list | None, escala: float, area_min: float, area_max: float,
            lado_min: float) -> Poligono | None:
    """Polígono de los 4 dedos, o None si faltan dedos o el gesto no es válido."""
    if vertices is None:
        return None
    zona, m = medir(vertices, escala)
    if not area_min <= m["area"] <= area_max:
        return None                                      # dedos juntos o brazos demasiado abiertos
    if m["lado"] < lado_min:
        return None                                      # zona muy larga y estrecha
    return zona


def _ordenar(pts):
    """Ordena los vértices por ángulo alrededor de su centro: el contorno nunca se cruza,
    da igual qué mano sea cuál o si los pulgares van arriba o abajo."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return tuple(sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx)))
