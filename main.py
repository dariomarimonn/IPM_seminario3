import time
import cv2

from config import config
from game import Camera, PoseTracker, HandTracker, draw_points, draw_hands


def main() -> None:
    camera = Camera(config.camera_index, config.camera_width,
                    config.camera_height, config.mirror)
    pose = PoseTracker(str(config.model_path), config.num_poses)
    hands = HandTracker(str(config.hand_model_path), config.num_hands)

    t_prev = time.time()
    try:
        while True:
            frame = camera.read()
            if frame is None:
                break

            points = pose.process(frame)
            manos = hands.process(frame)

            if points:
                draw_points(frame, points)
            draw_hands(frame, manos)

            ahora = time.time()
            fps = 1 / (ahora - t_prev)
            t_prev = ahora
            cv2.putText(frame, f"FPS: {fps:.0f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            cv2.imshow(config.window_name, frame)
            if cv2.waitKey(1) & 0xFF == config.exit_key:
                break
    finally:
        hands.close()
        pose.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()