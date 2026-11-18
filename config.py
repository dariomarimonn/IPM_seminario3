from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR: Path = BASE_DIR / "assets"

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


FICHAS = {
    "bomba": {
        "imagen": "bomba.png",
        "radio": 20,
        "velocidad": 150,        # px/s
        "t_aparecer": 1.0,       # s
        "t_desaparecer": 0.3,    # s
        "cara": "quitar_vida",
        "palma": "eliminar",
    },
}


@dataclass(frozen=True)
class Config:
    # Modelos (cambia el nombre para usar lite o heavy)
    models_dir: Path = BASE_DIR / "models"
    model_name: str = "pose_landmarker_full.task"
    num_poses: int = 1
    hand_model_name: str = "hand_landmarker.task"
    num_hands: int = 2

    # Cámara: resolución que se le pide (la real puede variar)
    camera_index: int = 0
    camera_width: int = 1280
    camera_height: int = 720
    mirror: bool = True           # voltear la imagen como un espejo

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