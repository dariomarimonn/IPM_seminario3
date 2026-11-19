
from enum import Enum, auto


class Estado(Enum):
    APARECIENDO = auto()
    ACTIVO = auto()
    DESAPARECIENDO = auto()
    ELIMINADO = auto()


class Objeto:
    def __init__(self, x: float, y: float, radio: float, t_aparecer: float, t_desaparecer: float, movimiento: str, tipo=""):
        self.x = float(x)
        self.y = float(y)
        self.radio = radio
        self.tipo = tipo
        self.angulo = 0.0
        self._t_aparecer = t_aparecer          # segundos
        self._t_desaparecer = t_desaparecer    # segundos
        self._estado = Estado.APARECIENDO
        self._t_estado = 0.0                   # tiempo en el estado actual
        self.movimiento = movimiento


    @property
    def estado(self) -> Estado:
        return self._estado

    @property
    def vivo(self) -> bool:
        """False cuando ya se puede quitar de la lista."""
        return self._estado is not Estado.ELIMINADO

    @property
    def tocable(self) -> bool:
        """Solo se puede golpear / hace daño cuando está ACTIVO."""
        return self._estado is Estado.ACTIVO

    @property
    def posicion(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    @property
    def progreso(self) -> float:
        """0..1 dentro de APARECIENDO (sube) o DESAPARECIENDO (baja); 1 si ACTIVO.
        Sirve para escala, transparencia o el fotograma de una animación."""
        if self._estado is Estado.APARECIENDO:
            return 1.0 if self._t_aparecer <= 0 else min(1.0, self._t_estado / self._t_aparecer)
        if self._estado is Estado.DESAPARECIENDO:
            return 0.0 if self._t_desaparecer <= 0 else 1.0 - min(1.0, self._t_estado / self._t_desaparecer)
        return 1.0 if self._estado is Estado.ACTIVO else 0.0

    # ciclo de vida 
    def actualizar(self, dt: float) -> None:
        """Avanza el reloj del estado y, si está ACTIVO, llama a _mover."""
        self._t_estado += dt
        if self._estado is Estado.APARECIENDO and self._t_estado >= self._t_aparecer:
            self._cambiar(Estado.ACTIVO)
        elif self._estado is Estado.DESAPARECIENDO and self._t_estado >= self._t_desaparecer:
            self._cambiar(Estado.ELIMINADO)
        if self._estado is Estado.ACTIVO:
            self._mover(dt)

    def desaparecer(self) -> None:
        """Inicia la animación de salida (golpeado, absorbido, fuera de pantalla...)."""
        if self._estado in (Estado.APARECIENDO, Estado.ACTIVO):
            self._cambiar(Estado.DESAPARECIENDO)

    def _cambiar(self, nuevo: Estado) -> None:
        self._estado = nuevo
        self._t_estado = 0.0

    def _mover(self, dt):                 
        self.movimiento.paso(self, dt)
    