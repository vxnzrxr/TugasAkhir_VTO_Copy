"""
Hand Gesture Detection Module
Detects hand gestures for UI interaction.
"""
import cv2
import mediapipe as mp
import math
import numpy as np

class HandGestureDetector:
    """Detects hand position and gestures."""
    
    def __init__(self):
        """Initialize the hand gesture detector."""
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Movement smoothing parameters
        self.smoothing_factor = 0.5
        self.prev_position = None
        
        # Debouncing variables
        self.last_gesture = "none"
        self.gesture_cooldown = 0
        self.cooldown_frames = 5 
        
    def get_finger_state(self, landmarks, joints):
        """
        Determine if a finger is extended or not.
        Returns: 1 if extended (lurus), 0 if flexed (tekuk)
        """
        # --- LOGIKA JEMPOL (THUMB) ---
        if joints == [1, 2, 3, 4]:  
            # Cek jarak Tip Jempol (4) ke Base Kelingking (17)
            # Jika jauh, berarti jempol terbuka
            thumb_tip = landmarks[4]
            pinky_mcp = landmarks[17]
            
            dist_thumb_pinky = math.hypot(thumb_tip.x - pinky_mcp.x, thumb_tip.y - pinky_mcp.y)
            
            # Normalisasi dengan ukuran telapak tangan
            wrist = landmarks[0]
            middle_mcp = landmarks[9]
            palm_size = math.hypot(wrist.x - middle_mcp.x, wrist.y - middle_mcp.y)
            
            # Threshold: Jika jarak jempol-kelingking > 90% lebar telapak -> Open
            return 1 if dist_thumb_pinky > (palm_size * 0.9) else 0

        # --- LOGIKA JARI LAIN (TELUNJUK s/d KELINGKING) ---
        else:
            # Menggunakan posisi Y relative terhadap pip (sendi tengah)
            tip_y = landmarks[joints[3]].y
            pip_y = landmarks[joints[1]].y 
            
            # Jika Tip lebih tinggi (nilai y lebih kecil) dari PIP -> Lurus
            return 1 if tip_y < pip_y else 0

    def identify_gesture(self, finger_states):
        """
        Identify the gesture based on finger states.
        """
        # Gestur Pointing: Hanya Telunjuk Lurus
        is_pointing = (
            finger_states['index'] == 1 and 
            finger_states['middle'] == 0 and 
            finger_states['ring'] == 0 and 
            finger_states['pinky'] == 0
        )
        
        # Gestur Selecting (Spider-man/Rock-on): Jempol, Telunjuk, Kelingking Lurus
        is_selecting = (
            finger_states['thumb'] == 1 and
            finger_states['index'] == 1 and
            finger_states['middle'] == 0 and
            finger_states['ring'] == 0 and
            finger_states['pinky'] == 1
        )

        if is_selecting:
            return 'selecting'
        elif is_pointing:
            return 'pointing' # <-- Nama gestur ini yang dicari oleh tombol
        else:
            return 'none'
        
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        results = self.hands.process(rgb_frame)
        
        hand_landmarks = None
        cursor_position = None
        gesture = "none"
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            
            self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            # Cek status setiap jari
            finger_states = {
                'thumb': self.get_finger_state(landmarks, [1, 2, 3, 4]),
                'index': self.get_finger_state(landmarks, [5, 6, 7, 8]),
                'middle': self.get_finger_state(landmarks, [9, 10, 11, 12]),
                'ring': self.get_finger_state(landmarks, [13, 14, 15, 16]),
                'pinky': self.get_finger_state(landmarks, [17, 18, 19, 20])
            }
            
            # Hitung posisi cursor (ujung telunjuk)
            index_finger_tip = landmarks[8]
            cursor_x = int(index_finger_tip.x * w)
            cursor_y = int(index_finger_tip.y * h)
            
            if self.prev_position:
                cursor_x = int(self.smoothing_factor * cursor_x + (1 - self.smoothing_factor) * self.prev_position[0])
                cursor_y = int(self.smoothing_factor * cursor_y + (1 - self.smoothing_factor) * self.prev_position[1])
            
            cursor_position = (cursor_x, cursor_y)
            self.prev_position = cursor_position
            
            # Identifikasi Gestur
            current_gesture = self.identify_gesture(finger_states)
            
            # Debouncing logic
            if current_gesture != self.last_gesture:
                self.gesture_cooldown += 1
                if self.gesture_cooldown > 2: 
                    gesture = current_gesture
                    self.last_gesture = current_gesture
                    self.gesture_cooldown = 0
                else:
                    gesture = self.last_gesture
            else:
                self.gesture_cooldown = 0
                gesture = self.last_gesture

        return hand_landmarks, gesture, cursor_position