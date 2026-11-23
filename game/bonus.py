"""Bonus temporal: mientras está activo, su zona del jugador absorbe los objetos que entran.

Lo usan el agujero negro (cuadrilátero de los dedos) y la barrera (segmento entre las palmas).
Lógica pura (sin OpenCV ni config): recibe la zona del frame y la lista de objetos.
"""
import math


class Bonus:
    def __init__(self, duracion: float | None, t_estable: float = 0.0, solo_amenazas: bool = False):
        self._duracion = duracion        # None = permanente
        self._t_estable = t_estable      # s que el gesto debe ser válido seguido antes de absorber
        self.solo_amenazas = solo_amenazas   # el motor decide qué es una amenaza
        self._restante = 0.0
        self._valido = 0.0               # s seguidos con el gesto válido
        self.edad = 0.0                  # s desde que se activó (para la animación)
        self.zona = None                 # zona que absorbe este frame, o None

    @property
    def activo(self) -> bool:
        return self._restante > 0

    @property
    def restante(self) -> float:
        return self._restante

    @property
    def fraccion(self) -> float:
        """Parte de la duración que queda (0-1); 1 si es permanente."""
        if self._duracion is None:
            return 1.0 if self.activo else 0.0
        return max(0.0, self._restante / self._duracion)

    def activar(self) -> None:
        """Al coger su objeto. Si ya estaba activo, reinicia la duración."""
        self._restante = math.inf if self._duracion is None else self._duracion
        self.edad = 0.0

    def actualizar(self, dt: float, zona) -> None:
        """zona: la zona de este frame, o None si el gesto no es válido."""
        self._restante -= dt
        self.edad += dt
        if not self.activo:
            self._valido, self.zona = 0.0, None
            return
        self._valido = self._valido + dt if zona is not None else 0.0
        self.zona = zona if self._valido >= self._t_estable else None

    def absorber(self, objetos) -> list:
        """Hace desaparecer los objetos tocables cuyo punto está dentro de la zona. Devuelve los absorbidos."""
        if self.zona is None:
            return []
        absorbidos = [o for o in objetos if o.tocable and self.zona.contiene(o.posicion)]
        for o in absorbidos:
            o.desaparecer()
        return absorbidos
