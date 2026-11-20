"""Zonas simples del cuerpo: escala de referencia, cara y palmas."""
import math

from config import Landmark
from .formas import Circulo

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
    return [Circulo(_media([puntos[p] for p in lado]), radio * escala) for lado in PALMAS]


def _media(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
