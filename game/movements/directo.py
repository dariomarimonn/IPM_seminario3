import math
from typing import Callable, Optional

from .base import Movimiento

class HaciaObjetivo(Movimiento):
    """Línea recta hacia el objetivo, a velocidad px/s."""

    def __init__(self, obtener_objetivo: Callable[[], Optional[tuple[float, float]]], velocidad: float):
        self._obtener_objetivo = obtener_objetivo
        self._velocidad = velocidad

    def paso(self, objeto, dt: float) -> None:
        objetivo = self._obtener_objetivo()
        if objetivo is None:
            return                                   # sin objetivo: quieto

        dx = objetivo[0] - objeto.x
        dy = objetivo[1] - objeto.y
        distancia = math.hypot(dx, dy)
        avance = self._velocidad * dt

        if distancia <= avance:                      # llega este frame
            objeto.x, objeto.y = objetivo
            return

        objeto.x += dx / distancia * avance
        objeto.y += dy / distancia * avance
