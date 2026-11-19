from .base import Movimiento


class Quieto(Movimiento):
    """Se queda donde aparece."""

    def paso(self, objeto, dt: float) -> None:
        pass
