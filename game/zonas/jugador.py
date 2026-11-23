"""Junta todas las zonas del jugador de un frame."""
from dataclasses import dataclass, field

from .agujero import agujero, dedos_manos, dedos_pose
from .cuerpo import barrera, cara, escala_hombros, juntas, palmas
from .formas import Circulo, Poligono, Segmento


@dataclass(frozen=True)
class ZonasJugador:
    cara: Circulo | None = None          # None si no hay pose
    palmas: list[Circulo] = field(default_factory=list)
    agujero: Poligono | None = None      # None si el gesto no es válido
    barrera: Segmento | None = None      # entre las palmas; solo cuenta con su bonus activo
    juntas: Circulo | None = None        # entre las palmas si están cerca: coger con las dos manos

    def todas(self) -> list:
        return [z for z in (self.cara, *self.palmas, self.agujero, self.barrera, self.juntas) if z is not None]


def calcular_zonas(puntos: dict | None, tamanos: dict, manos: dict | None = None) -> ZonasJugador:
    """Recalcula las zonas desde la pose. Sin pose (o pose degenerada) → sin zonas.
    Si se pasan `manos` (HandTracker), el agujero sale de sus puntas de dedos en vez de la pose."""
    if not puntos:
        return ZonasJugador()
    escala = escala_hombros(puntos)
    if escala < 1:
        return ZonasJugador()
    return ZonasJugador(
        cara=cara(puntos, escala, tamanos["radio_cara"]),
        palmas=palmas(puntos, escala, tamanos["radio_palma"]),
        agujero=agujero(dedos_manos(manos) if manos is not None else dedos_pose(puntos), escala, tamanos["agujero_area_min"],
                        tamanos["agujero_area_max"], tamanos["agujero_lado_min"]),
        barrera=barrera(puntos, escala, tamanos["barrera_grosor"]),
        juntas=juntas(puntos, escala, tamanos["juntas_radio"], tamanos["juntas_max"]),
    )
