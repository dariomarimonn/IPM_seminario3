from .movements import Espiral, HaciaObjetivo, Quieto
from .objeto import Objeto

MOVIMIENTOS = {
    "directo": lambda ficha, obtener_objetivo: HaciaObjetivo(obtener_objetivo, ficha["velocidad"]),
    "espiral": lambda ficha, obtener_objetivo: Espiral(obtener_objetivo, ficha["velocidad"], ficha["giro_orbital"]),
    "quieto": lambda ficha, obtener_objetivo: Quieto(),
}


def crear_objeto(ficha: dict, tipo: str, x: float, y: float, obtener_objetivo) -> Objeto:
    """Construye un Objeto desde su ficha de FICHAS."""
    movimiento = MOVIMIENTOS[ficha["movimiento"]](ficha, obtener_objetivo)
    return Objeto(x, y, ficha["radio"], ficha["t_aparecer"], ficha["t_desaparecer"], movimiento, tipo=tipo)
