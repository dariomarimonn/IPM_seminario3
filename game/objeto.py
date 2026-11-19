from enum import Enum, auto

from .movements.base import Movimiento


class Estado(Enum):
    APARECIENDO = auto()
    ACTIVO = auto()
    DESAPARECIENDO = auto()
    ELIMINADO = auto()


class Objeto:
    """Punto con posición, tipo y ciclo de vida; se mueve con su Movimiento."""

    def __init__(self, x: float, y: float, radio: float, t_aparecer: float, t_desaparecer: float,
                 movimiento: Movimiento, tipo: str = ""):
        self.x = float(x)
        self.y = float(y)
        self.radio = radio
        self.tipo = tipo
        self.edad = 0.0                        # segundos vivo
        self._t_aparecer = t_aparecer
        self._t_desaparecer = t_desaparecer
        self._estado = Estado.APARECIENDO
        self._t_estado = 0.0
        self.movimiento = movimiento

    @property
    def estado(self) -> Estado:
        return self._estado

    @property
    def vivo(self) -> bool:
        return self._estado is not Estado.ELIMINADO

    @property
    def tocable(self) -> bool:
        return self._estado is Estado.ACTIVO

    @property
    def posicion(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    @property
    def avance(self) -> float:
        """0→1 dentro del estado actual; 1 en ACTIVO y ELIMINADO."""
        if self._estado is Estado.APARECIENDO:
            return self._fraccion(self._t_aparecer)
        if self._estado is Estado.DESAPARECIENDO:
            return self._fraccion(self._t_desaparecer)
        return 1.0

    @property
    def progreso(self) -> float:
        """Sube al aparecer, baja al desaparecer; 1 en ACTIVO."""
        if self._estado is Estado.APARECIENDO:
            return self.avance
        if self._estado is Estado.DESAPARECIENDO:
            return 1.0 - self.avance
        return 1.0 if self._estado is Estado.ACTIVO else 0.0

    def _fraccion(self, duracion: float) -> float:
        return 1.0 if duracion <= 0 else min(1.0, self._t_estado / duracion)

    def actualizar(self, dt: float) -> None:
        self.edad += dt
        self._t_estado += dt
        if self._estado is Estado.APARECIENDO and self._t_estado >= self._t_aparecer:
            self._cambiar(Estado.ACTIVO)
        elif self._estado is Estado.DESAPARECIENDO and self._t_estado >= self._t_desaparecer:
            self._cambiar(Estado.ELIMINADO)
        if self._estado is Estado.ACTIVO:
            self._mover(dt)

    def desaparecer(self) -> None:
        if self._estado in (Estado.APARECIENDO, Estado.ACTIVO):
            self._cambiar(Estado.DESAPARECIENDO)

    def _cambiar(self, nuevo: Estado) -> None:
        self._estado = nuevo
        self._t_estado = 0.0

    def _mover(self, dt: float) -> None:
        self.movimiento.paso(self, dt)
