"""
Glasses Renderer Module
Renders virtual glasses on the face.
"""
import cv2
import numpy as np

class GlassesRenderer:
    """Renders virtual glasses on a face."""
    
    def __init__(self):
        """Initialize the glasses renderer."""
        # Define available glasses styles
        self.styles = ["Rectangle", "Round", "Aviator"]
        
        # Define available colors (BGR format)
        self.colors = {
            "Black": (0, 0, 0),
            "Blue": (255, 0, 0),
            "Red": (0, 0, 255),
            "Green": (0, 255, 0),
            "Yellow": (0, 255, 255),
            "White": (255, 255, 255)
        }
        
    def render(self, frame, face_data, style, color):
        """
        Render glasses on the face.
        
        Args:
            frame: BGR frame from the camera
            face_data: Dictionary with face dimensions and points
            style: Style of glasses to render
            color: Color of glasses to render
            
        Returns:
            Frame with rendered glasses
        """
        if not face_data:
            return frame
            
        # Get face dimensions
        points = face_data["points"]
        dimensions = face_data["dimensions"]
        
        # Create a copy of the frame for overlay
        overlay = frame.copy()
        
        # Get the center point between the eyes and glasses width
        eye_center_x = dimensions["eye_center"][0]
        eye_center_y = dimensions["eye_center"][1]
        glasses_width = int(dimensions["eyes_distance"] * 1.5)
        glasses_height = int(glasses_width * 0.35)
        
        # Get the color
        bgr_color = self.colors.get(color, (0, 0, 0))  # Default to black
        
        # Render glasses based on style
        if style == "Rectangle":
            self._draw_rectangle_glasses(overlay, eye_center_x, eye_center_y, 
                                        glasses_width, glasses_height, bgr_color)
        elif style == "Round":
            self._draw_round_glasses(overlay, eye_center_x, eye_center_y, 
                                    glasses_width, glasses_height, bgr_color)
        elif style == "Aviator":
            self._draw_aviator_glasses(overlay, eye_center_x, eye_center_y, 
                                      glasses_width, glasses_height, bgr_color)
        
        # Blend the overlay with the original frame
        alpha = 0.8  # Transparency factor
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
        
    def _draw_rectangle_glasses(self, frame, eye_center_x, eye_center_y, 
                              glasses_width, glasses_height, color):
        """Draw rectangular glasses."""
        left_eye_x = eye_center_x - glasses_width // 4
        right_eye_x = eye_center_x + glasses_width // 4
        
        # Draw left lens
        cv2.rectangle(frame,
                     (left_eye_x - glasses_width // 8, eye_center_y - glasses_height // 2),
                     (left_eye_x + glasses_width // 8, eye_center_y + glasses_height // 2),
                     color, 2)
        
        # Draw right lens
        cv2.rectangle(frame,
                     (right_eye_x - glasses_width // 8, eye_center_y - glasses_height // 2),
                     (right_eye_x + glasses_width // 8, eye_center_y + glasses_height // 2),
                     color, 2)
        
        # Draw bridge
        cv2.line(frame,
                (left_eye_x + glasses_width // 8, eye_center_y),
                (right_eye_x - glasses_width // 8, eye_center_y),
                color, 2)
        
        # Draw temples (arms)
        temple_length = glasses_width // 2
        
        cv2.line(frame,
                (left_eye_x - glasses_width // 8, eye_center_y),
                (left_eye_x - glasses_width // 8 - temple_length, eye_center_y + temple_length // 2),
                color, 2)
        
        cv2.line(frame,
                (right_eye_x + glasses_width // 8, eye_center_y),
                (right_eye_x + glasses_width // 8 + temple_length, eye_center_y + temple_length // 2),
                color, 2)
    
    def _draw_round_glasses(self, frame, eye_center_x, eye_center_y, 
                          glasses_width, glasses_height, color):
        """Draw round glasses."""
        left_eye_x = eye_center_x - glasses_width // 4
        right_eye_x = eye_center_x + glasses_width // 4
        lens_radius = glasses_width // 8
        
        # Draw left lens
        cv2.circle(frame,
                  (left_eye_x, eye_center_y),
                  lens_radius,
                  color, 2)
        
        # Draw right lens
        cv2.circle(frame,
                  (right_eye_x, eye_center_y),
                  lens_radius,
                  color, 2)
        
        # Draw bridge
        cv2.line(frame,
                (left_eye_x + lens_radius, eye_center_y),
                (right_eye_x - lens_radius, eye_center_y),
                color, 2)
        
        # Draw temples (arms)
        temple_length = glasses_width // 2
        
        cv2.line(frame,
                (left_eye_x - lens_radius, eye_center_y),
                (left_eye_x - lens_radius - temple_length, eye_center_y + temple_length // 2),
                color, 2)
        
        cv2.line(frame,
                (right_eye_x + lens_radius, eye_center_y),
                (right_eye_x + lens_radius + temple_length, eye_center_y + temple_length // 2),
                color, 2)
    
    def _draw_aviator_glasses(self, frame, eye_center_x, eye_center_y, 
                            glasses_width, glasses_height, color):
        """Draw aviator glasses."""
        left_eye_x = eye_center_x - glasses_width // 4
        right_eye_x = eye_center_x + glasses_width // 4
        
        # Left lens (teardrop shape)
        left_lens_points = np.array([
            [left_eye_x - glasses_width // 8, eye_center_y - glasses_height // 2],
            [left_eye_x + glasses_width // 8, eye_center_y - glasses_height // 2],
            [left_eye_x + glasses_width // 10, eye_center_y + glasses_height // 2],
            [left_eye_x - glasses_width // 6, eye_center_y + glasses_height // 3]
        ], np.int32)
        left_lens_points = left_lens_points.reshape((-1, 1, 2))
        cv2.polylines(frame, [left_lens_points], True, color, 2)
        
        # Right lens (teardrop shape)
        right_lens_points = np.array([
            [right_eye_x - glasses_width // 8, eye_center_y - glasses_height // 2],
            [right_eye_x + glasses_width // 8, eye_center_y - glasses_height // 2],
            [right_eye_x + glasses_width // 6, eye_center_y + glasses_height // 3],
            [right_eye_x - glasses_width // 10, eye_center_y + glasses_height // 2]
        ], np.int32)
        right_lens_points = right_lens_points.reshape((-1, 1, 2))
        cv2.polylines(frame, [right_lens_points], True, color, 2)
        
        # Draw bridge
        cv2.line(frame,
                (left_eye_x + glasses_width // 8, eye_center_y - glasses_height // 4),
                (right_eye_x - glasses_width // 8, eye_center_y - glasses_height // 4),
                color, 2)
        
        # Draw temples (arms)
        temple_length = glasses_width // 2
        
        cv2.line(frame,
                (left_eye_x - glasses_width // 8, eye_center_y - glasses_height // 4),
                (left_eye_x - glasses_width // 8 - temple_length, eye_center_y + temple_length // 3),
                color, 2)
        
        cv2.line(frame,
                (right_eye_x + glasses_width // 8, eye_center_y - glasses_height // 4),
                (right_eye_x + glasses_width // 8 + temple_length, eye_center_y + temple_length // 3),
                color, 2)
