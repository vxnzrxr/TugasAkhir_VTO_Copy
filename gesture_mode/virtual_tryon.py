"""
Virtual Try-On Application
Main application class that handles camera, UI, and rendering.
"""
import cv2
import time
import numpy as np
from .face_detection import FaceDetector
from .hand_gesture import HandGestureDetector
from .glasses_renderer import GlassesRenderer
from .ui_manager import UIManager

class VirtualTryOnApp:
    """Main Virtual Try-On application class with gesture-based UI."""
    
    def __init__(self):
        """Initialize the application."""
        # Initialize components
        self.face_detector = FaceDetector()
        self.gesture_detector = HandGestureDetector()
        self.glasses_renderer = GlassesRenderer()
        
        # UI Manager for handling UI elements
        self.ui_manager = UIManager()
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open webcam.")
        
        # Set webcam resolution (optional)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Performance tracking
        self.prev_time = 0
        self.fps = 0
        
        # Application state
        self.running = True
        
    def process_frame(self, frame):
        """
        Process a single frame from the webcam.
        
        Args:
            frame: BGR frame from the camera
            
        Returns:
            Processed frame with UI and virtual items
        """
        # Flip the frame horizontally for a more natural view
        frame = cv2.flip(frame, 1)
        
        # Calculate FPS
        current_time = time.time()
        self.fps = 1/(current_time - self.prev_time) if (current_time - self.prev_time) > 0 else 60
        self.prev_time = current_time
        
        # Process hand gestures for UI control
        hand_landmarks, gesture, finger_position = self.gesture_detector.process_frame(frame)
        
        # Detect face for glasses placement
        face_landmarks, face_data = self.face_detector.detect_face(frame)
        
        # Update UI state based on hand gesture
        self.ui_manager.update(frame, gesture, finger_position)
        
        # Render UI elements
        frame = self.ui_manager.render(frame)
        
        # If face is detected, render glasses
        if face_data:
            current_style = self.ui_manager.current_style
            current_color = self.ui_manager.current_color
            frame = self.glasses_renderer.render(frame, face_data, current_style, current_color)
        
        # Display hand cursor
        if finger_position:
            cv2.circle(frame, finger_position, 10, (0, 255, 0), -1)  # Green circle for cursor
        
        # Add FPS counter
        cv2.putText(frame, f"FPS: {int(self.fps)}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame
    
    def apply_gesture(self, gesture, frame, finger_position=None):
        """
        Method tambahan untuk memproses gesture dari aplikasi Kiosk.
        """
        # Update state UI berdasarkan gesture
        self.ui_manager.update(frame, gesture, finger_position)
        
        # Render elemen UI ke frame (jika diperlukan visualisasi di Kiosk)
        # Note: Ini akan menggambar langsung ke variable 'frame' karena numpy array mutable
        self.ui_manager.render(frame)
        
        # Jika ada posisi jari, gambar cursor visual
        if finger_position:
            cv2.circle(frame, finger_position, 10, (0, 255, 0), -1)
    
    def run(self):
        """Run the main application loop."""
        while self.running:
            # Read a frame from the webcam
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Process the frame
            processed_frame = self.process_frame(frame)
            
            # Display the result
            cv2.imshow('Virtual Try-On', processed_frame)
            
            # Check for keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):  # Esc or q to quit
                self.running = False
        
        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()
        
        # Cleanup
        self.face_detector.release()