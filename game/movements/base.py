from abc import ABC, abstractmethod


class Movimiento(ABC):
    @abstractmethod
    def paso(self, objeto, dt: float) -> None:
        """Modifica objeto.x / objeto.y avanzando dt segundos (dt real)."""
