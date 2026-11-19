from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Landmark(IntEnum):
    """Índices de MediaPipe Pose usados en el juego."""
    NARIZ = 0
    OREJA_IZQ = 7
    OREJA_DER = 8
    HOMBRO_IZQ = 11
    HOMBRO_DER = 12
    CODO_IZQ = 13
    CODO_DER = 14
    MUNECA_IZQ = 15
    MUNECA_DER = 16
    MENIQUE_IZQ = 17
    MENIQUE_DER = 18
    INDICE_IZQ = 19
    INDICE_DER = 20
    PULGAR_IZQ = 21
    PULGAR_DER = 22


class HandLandmark(IntEnum):
    """Los 21 puntos de HandLandmarker."""
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


# Un tipo nuevo = una entrada aquí + su carpeta en assets/<tipo>/.
FICHAS = {
    "bomba": {
        "radio": 70,             # px, solo dibujo
        "movimiento": "directo",
        "velocidad": 100,        # px/s
        "t_aparecer": 1.0,       # s
        "t_desaparecer": 0.45,   # s
        "cara": "quitar_vida",
        "palma": "eliminar",
        # estado sin entrada → usa la de ACTIVO
        "animaciones": {
            "ACTIVO":         {"carpeta": "normal", "modo": "fija", "giro": 90, "ajustar": True},
            "DESAPARECIENDO": {"carpeta": "salida", "modo": "progreso", "escala": 1.5},
        },
    },
    "manzana": {
        "radio": 60,
        "movimiento": "quieto",
        "velocidad": 0,
        "t_aparecer": 0.8,
        "t_desaparecer": 0.4,
        "cara": None,
        "palma": "dar_puntos",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal"},
            "DESAPARECIENDO": {"carpeta": "aparecer", "modo": "progreso", "invertir": True},
        },
    },
    "galaxia": {
        "radio": 80,
        "movimiento": "espiral",
        "velocidad": 35,         # px/s hacia el objetivo
        "giro_orbital": 40,      # °/s alrededor del objetivo
        "t_aparecer": 0.5,
        "t_desaparecer": 0.5,
        "cara": None,
        "palma": "eliminar",
        # mismo giro en todas para que no salte al cambiar de estado
        "animaciones": {
            "APARECIENDO":    {"carpeta": "desaparecer", "modo": "progreso", "invertir": True, "giro": 120},
            "ACTIVO":         {"carpeta": "normal", "giro": 120},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso", "giro": 120},
        },
    },
    "corazon": {
        "radio": 55,
        "movimiento": "quieto",
        "velocidad": 0,
        "t_aparecer": 0.4,
        "t_desaparecer": 0.4,
        "cara": None,
        "palma": "curar",
        "animaciones": {
            "APARECIENDO":    {"carpeta": "aparecer", "modo": "progreso"},
            "ACTIVO":         {"carpeta": "normal"},
            "DESAPARECIENDO": {"carpeta": "desaparecer", "modo": "progreso"},
        },
    },
}


@dataclass(frozen=True)
class Config:
    # Modelos
    models_dir: Path = BASE_DIR / "models"
    assets_dir: Path = BASE_DIR / "assets"
    model_name: str = "pose_landmarker_full.task"
    num_poses: int = 1
    hand_model_name: str = "hand_landmarker.task"
    num_hands: int = 2

    # Cámara (resolución pedida; la real puede variar)
    camera_index: int = 0
    camera_width: int = 1280
    camera_height: int = 720
    mirror: bool = True

    # Ventana
    window_name: str = "Seminario 3"
    exit_key: int = 27            # ESC

    @property
    def model_path(self) -> Path:
        return self.models_dir / self.model_name

    @property
    def hand_model_path(self) -> Path:
        return self.models_dir / self.hand_model_name


config = Config()