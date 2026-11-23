import math

from .base import Movimiento


class Ondulado(Movimiento):
    """Va hacia el objetivo oscilando de lado a lado.

    Un punto base avanza en línea recta hacia el objetivo y el objeto oscila alrededor de él,
    en perpendicular al rumbo. La oscilación se apaga al acercarse, para que acabe llegando.
    """

    def __init__(self, obtener_objetivo, velocidad: float, amplitud: float, frecuencia: float):
        self._obtener_objetivo = obtener_objetivo
        self._velocidad = velocidad            # px/s del punto base
        self._amplitud = amplitud              # px a cada lado; el signo elige hacia dónde empieza
        self._w = 2 * math.pi * frecuencia     # rad/s
        self._t = 0.0
        self._base = None                      # punto que va directo; se fija en el primer paso

    def paso(self, objeto, dt: float) -> None:
        self._t += dt
        objetivo = self._obtener_objetivo()
        if objetivo is None:
            return
        bx, by = self._base or (objeto.x, objeto.y)
        dx, dy = objetivo[0] - bx, objetivo[1] - by
        d = math.hypot(dx, dy)
        if d <= self._velocidad * dt:          # llega este frame
            self._base = objetivo
            objeto.x, objeto.y = objetivo
            return
        ux, uy = dx / d, dy / d
        bx, by = bx + ux * self._velocidad * dt, by + uy * self._velocidad * dt
        self._base = (bx, by)

        a = abs(self._amplitud)
        apagado = min(1.0, (d / (2 * a))) if a else 0.0       # se apaga en los últimos 2·amplitud px
        desvio = self._amplitud * apagado * math.sin(self._w * self._t)
        objeto.x, objeto.y = bx - uy * desvio, by + ux * desvio  # (-uy, ux): perpendicular al rumbo
