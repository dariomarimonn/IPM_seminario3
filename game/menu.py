"""Pantalla principal: se elige una opción manteniendo una palma sobre su botón un tiempo."""
from .zonas import Circulo


class Menu:
    def __init__(self, claves: list[str], tamano: tuple[int, int], t_elegir: float, radio: float, altura: float):
        """Un botón en el centro de cada columna (todas del mismo ancho). radio: fracción del ancho;
        altura: fracción del alto."""
        ancho, alto = tamano
        n = len(claves)
        self.radio = radio * ancho              # px
        self.botones = {c: Circulo(((2 * i + 1) * ancho / (2 * n), altura * alto), self.radio)
                        for i, c in enumerate(claves)}
        self.progreso = {c: 0.0 for c in claves}    # 0-1: cuánto lleva cargado cada botón
        self._t_elegir = t_elegir

    def actualizar(self, dt: float, palmas) -> str | None:
        """Devuelve la clave elegida en este frame, o None. Sacar la palma vacía el botón."""
        for clave, boton in self.botones.items():
            dentro = any(boton.contiene(p.centro) for p in palmas)
            self.progreso[clave] = self.progreso[clave] + dt / self._t_elegir if dentro else 0.0
            if self.progreso[clave] >= 1.0:
                return clave
        return None
