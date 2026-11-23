"""Zonas simples del cuerpo: escala de referencia, cara, palmas y las zonas entre las dos palmas."""
import math

from config import Landmark
from .formas import Circulo, Segmento

PALMAS = ((Landmark.MUNECA_IZQ, Landmark.INDICE_IZQ, Landmark.MENIQUE_IZQ),
          (Landmark.MUNECA_DER, Landmark.INDICE_DER, Landmark.MENIQUE_DER))


def escala_hombros(puntos: dict) -> float:
    """Ancho de hombros en px: la unidad con la que se miden todas las zonas (crece al acercarse a la cámara)."""
    return math.dist(puntos[Landmark.HOMBRO_IZQ], puntos[Landmark.HOMBRO_DER])


def cara(puntos: dict, escala: float, radio: float) -> Circulo:
    """Círculo centrado en la nariz; `radio` en anchos de hombros."""
    return Circulo(puntos[Landmark.NARIZ], radio * escala)


def palmas(puntos: dict, escala: float, radio: float) -> list[Circulo]:
    """Un círculo por mano, centrado en la media de muñeca, índice y meñique."""
    return [Circulo(c, radio * escala) for c in _centros_palmas(puntos)]


def barrera(puntos: dict, escala: float, grosor: float) -> Segmento:
    """Segmento entre los centros de las dos palmas; `grosor` en anchos de hombros."""
    return Segmento(*_centros_palmas(puntos), grosor * escala)


def juntas(puntos: dict, escala: float, radio: float, separacion_max: float) -> Circulo | None:
    """Zona para coger algo con las dos manos: círculo entre las palmas, solo si están a menos de
    `separacion_max` (anchos de hombros); None si están separadas."""
    a, b = _centros_palmas(puntos)
    if math.dist(a, b) > separacion_max * escala:
        return None
    return Circulo(_media([a, b]), radio * escala)


def _centros_palmas(puntos):
    return [_media([puntos[p] for p in lado]) for lado in PALMAS]


def _media(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
