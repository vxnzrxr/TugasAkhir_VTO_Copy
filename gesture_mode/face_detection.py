"""
Face Detection Module
Detects face landmarks for placing glasses.
"""
import cv2
import mediapipe as mp
import numpy as np
import time

class FaceDetector:
    """Detects facial landmarks using MediaPipe Face Mesh."""
    
    def __init__(self):
        """Initialize the face detector."""
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True
        )
        
        # For performance optimization
        self.last_detection_time = 0
        self.detection_interval = 0.03  # seconds (30 fps)
        
        # Store previous results for stability
        self.prev_landmarks = None
        self.prev_face_data = None
        
    def detect_face(self, frame):
        """
        Detect face landmarks in a frame.
        
        Args:
            frame: BGR frame from the camera
            
        Returns:
            A tuple containing (landmarks, face_data)
        """
        # Check if enough time has passed for new detection
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_interval:
            return self.prev_landmarks, self.prev_face_data
            
        self.last_detection_time = current_time
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        
        # Process the frame with MediaPipe
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None, None
            
        # Get the first detected face
        landmarks = results.multi_face_landmarks[0]
        self.prev_landmarks = landmarks
        
        # Convert landmarks to pixel coordinates
        face_data = self._extract_face_data(landmarks, w, h)
        self.prev_face_data = face_data
        
        return landmarks, face_data
    
    def _extract_face_data(self, landmarks, img_width, img_height):
        """
        Extract useful face data from landmarks.
        
        Args:
            landmarks: Face landmarks from MediaPipe
            img_width: Image width
            img_height: Image height
            
        Returns:
            Dictionary containing face dimensions and key points
        """
        # Convert normalized coordinates to pixel coordinates
        points = {}
        
        # Eyes
        points["left_eye"] = (int(landmarks.landmark[33].x * img_width),
                             int(landmarks.landmark[33].y * img_height))
        points["right_eye"] = (int(landmarks.landmark[263].x * img_width),
                              int(landmarks.landmark[263].y * img_height))
        
        # Nose
        points["nose_tip"] = (int(landmarks.landmark[4].x * img_width),
                             int(landmarks.landmark[4].y * img_height))
        points["nose_bridge"] = (int(landmarks.landmark[168].x * img_width),
                                int(landmarks.landmark[168].y * img_height))
        
        # Calculate face dimensions
        dimensions = {}
        dimensions["eye_center"] = ((points["left_eye"][0] + points["right_eye"][0]) // 2,
                                  (points["left_eye"][1] + points["right_eye"][1]) // 2)
        dimensions["eyes_distance"] = abs(points["right_eye"][0] - points["left_eye"][0])
        
        return {
            "points": points,
            "dimensions": dimensions
        }
        
    def release(self):
        """Release resources."""
        pass
