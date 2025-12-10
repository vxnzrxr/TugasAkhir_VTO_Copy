# gesture_mode/__init__.py
from .hand_gesture import HandGestureDetector
from .virtual_tryon import VirtualTryOnApp
import cv2

def run_gesture_mode():
    detector = HandGestureDetector()
    vto = VirtualTryOnApp()

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Deteksi gesture
        gesture = detector.detect(frame)

        # Update virtual try-on sesuai gesture
        vto.apply_gesture(gesture, frame)

        cv2.imshow("Gesture Mode", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
