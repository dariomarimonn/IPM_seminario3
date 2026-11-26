# Juego serio: Eras en tus manos

Práctica 2 de Interacción Persona-Máquina (Universidad de Alicante), hecha por Darío Marimón.

Es un juego controlado mediante la cámara y orientado a la rehabilitación del miembro superior. El jugador debe defender su cara de los enemigos que se acercan, deteniéndolos con la palma, y recoger premios con la mano correspondiente. Con ello se trabajan el rango de movimiento de los hombros, la coordinación de las dos manos, la lateralidad y el tiempo de reacción. Al acabar cada partida se muestran los aciertos y el tiempo de reacción de cada mano.

Hay tres niveles, las eras de la galaxia, la recolección y la ciencia, que se eligen en el menú manteniendo la palma sobre ellos durante un segundo.

## Instalación

Es necesario Python 3.10 o superior y una webcam. Las dependencias se encuentran en `requirements.txt`, con la versión fijada.

```bash
git clone https://github.com/dariomarimonn/IPM_seminario3.git
cd IPM_seminario3
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Descargar los modelos

```bash
python3 download_models.py
```

## Ejecución

Desde la raíz del repositorio y con el venv activado:

```bash
python3 main.py
```

En el menú se elige el nivel con la palma o con las teclas 1, 2 y 3. Durante la partida, M vuelve al menú, y si la cámara deja de ver al jugador el juego se pausa. Al acabar, R repite el nivel. ESC cierra el juego (con la ventana seleccionada).
