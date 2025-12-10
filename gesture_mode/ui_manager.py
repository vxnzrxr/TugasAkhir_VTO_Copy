"""
UI Manager Module
Manages UI elements within the video frame.
"""
import cv2
import numpy as np


class UIElement:
    """Base class for UI elements in the video frame."""

    def __init__(self, x, y, width, height, label=""):
        """
        Initialize a UI element.

        Args:
            x: X-coordinate of the top-left corner
            y: Y-coordinate of the top-left corner
            width: Width of the element
            height: Height of the element
            label: Text label for the element
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.active = False
        self.selected = False

    def contains_point(self, point):
        """
        Check if the element contains a point.

        Args:
            point: (x, y) coordinates to check

        Returns:
            True if the element contains the point, False otherwise
        """
        if point is None:
            return False

        x, y = point
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def render(self, frame):
        """
        Render the UI element on the frame.

        Args:
            frame: BGR frame to render on

        Returns:
            Modified frame
        """
        raise NotImplementedError("Subclasses must implement render()")


class Button(UIElement):
    """Button UI element."""

    def __init__(self, x, y, width, height, label="", color=(200, 200, 200)):
        """Initialize a button."""
        super().__init__(x, y, width, height, label)
        self.color = color
        self.text_color = (0, 0, 0)  # Black text

    def render(self, frame):
        """Render the button on the frame."""
        # Draw button background
        color = self.color
        if self.selected:
            # Darken color when selected
            color = tuple(max(0, c - 50) for c in self.color)
        elif self.active:
            # Brighten color when active (hovered)
            color = tuple(min(255, c + 30) for c in self.color)

        cv2.rectangle(frame, (self.x, self.y),
                      (self.x + self.width, self.y + self.height),
                      color, -1)  # Filled rectangle

        # Draw button border
        border_color = (50, 50, 50)  # Dark gray
        cv2.rectangle(frame, (self.x, self.y),
                      (self.x + self.width, self.y + self.height),
                      border_color, 2)  # Border

        # Draw button text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(self.label, font, 0.6, 2)
        text_x = self.x + (self.width - text_size[0]) // 2
        text_y = self.y + (self.height + text_size[1]) // 2
        cv2.putText(frame, self.label, (text_x, text_y),
                    font, 0.6, self.text_color, 2)

        return frame


class ColorSelector(UIElement):
    """Color selector UI element with color swatches."""

    def __init__(self, x, y, width, height, colors=None):
        """Initialize a color selector."""
        super().__init__(x, y, width, height, "Colors")

        if colors is None:
            self.colors = {
                "Black": (0, 0, 0),
                "Blue": (255, 0, 0),
                "Red": (0, 0, 255),
                "Green": (0, 255, 0),
                "Yellow": (0, 255, 255),
                "White": (255, 255, 255)
            }
        else:
            self.colors = colors

        self.selected_color = "Black"

        # Create color swatches
        self.swatches = []
        self._create_swatches()

    def _create_swatches(self):
        """Create color swatch buttons."""
        swatch_width = min(80, (self.width - 20) // len(self.colors))
        swatch_height = 30
        swatch_y = self.y + 40

        # Reset swatches
        self.swatches = []

        # Create new swatches
        x_offset = self.x + 10
        for color_name, color_value in self.colors.items():
            swatch = Button(x_offset, swatch_y, swatch_width, swatch_height,
                            color_name, color_value)
            swatch.selected = (color_name == self.selected_color)
            self.swatches.append((color_name, swatch))
            x_offset += swatch_width + 5

    def contains_point(self, point):
        """
        Check if the color selector or any of its swatches contain a point.

        Args:
            point: (x, y) coordinates to check

        Returns:
            True if the element contains the point, False otherwise
        """
        if super().contains_point(point):
            return True

        for _, swatch in self.swatches:
            if swatch.contains_point(point):
                return True

        return False

    def handle_click(self, point):
        """
        Handle a click event.

        Args:
            point: (x, y) coordinates of the click

        Returns:
            True if a color was selected, False otherwise
        """
        for color_name, swatch in self.swatches:
            if swatch.contains_point(point):
                self.selected_color = color_name
                self._update_selection()
                return True

        return False

    def _update_selection(self):
        """Update the selection state of the swatches."""
        for color_name, swatch in self.swatches:
            swatch.selected = (color_name == self.selected_color)

    def update(self, point):
        """
        Update the active state of the color selector and its swatches.

        Args:
            point: Current cursor position
        """
        for _, swatch in self.swatches:
            swatch.active = swatch.contains_point(point)

    def render(self, frame):
        """Render the color selector on the frame."""
        # Draw the panel background
        cv2.rectangle(frame, (self.x, self.y),
                      (self.x + self.width, self.y + self.height),
                      (240, 240, 240), -1)  # Light gray background

        # Draw panel border
        cv2.rectangle(frame, (self.x, self.y),
                      (self.x + self.width, self.y + self.height),
                      (150, 150, 150), 2)  # Gray border

        # Draw panel title
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, self.label, (self.x + 10, self.y + 25),
                    font, 0.7, (0, 0, 0), 2)

        # Draw color swatches
        for _, swatch in self.swatches:
            frame = swatch.render(frame)

        # Draw selected color info
        selected_text = f"Selected: {self.selected_color}"
        cv2.putText(frame, selected_text, (self.x + 10, self.y + self.height - 15),
                    font, 0.6, (0, 0, 0), 2)

        return frame


class StyleSelector(UIElement):
    """Style selector UI element with style buttons."""

    def __init__(self, x, y, width, height, styles=None):
        """Initialize a style selector."""
        super().__init__(x, y, width, height, "Styles")

        if styles is None:
            self.styles = ["Rectangle", "Round", "Aviator"]
        else:
            self.styles = styles

        self.selected_style = self.styles[0]

        # Create style buttons
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        """Create style option buttons."""
        button_width = self.width - 20
        button_height = 30

        # Reset buttons
        self.buttons = []

        # Create new buttons
        y_offset = self.y + 40
        for style in self.styles:
            button = Button(self.x + 10, y_offset,
                            button_width, button_height, style)
            button.selected = (style == self.selected_style)
            self.buttons.append((style, button))
            y_offset += button_height + 10

    def contains_point(self, point):
        """
        Check if the style selector or any of its buttons contain a point.

        Args:
            point: (x, y) coordinates to check

        Returns:
            True if the element contains the point, False otherwise
        """
        if super().contains_point(point):
            return True

        for _, button in self.buttons:
            if button.contains_point(point):
                return True

        return False

    def handle_click(self, point):
        """
        Handle a click event.

        Args:
            point: (x, y) coordinates of the click

        Returns:
            True if a style was selected, False otherwise
        """
        for style, button in self.buttons:
            if button.contains_point(point):
                self.selected_style = style
                self._update_selection()
                return True

        return False

    def _update_selection(self):
        """Update the selection state of the buttons."""
        for style, button in self.buttons:
            button.selected = (style == self.selected_style)

    def update(self, point):
        """
        Update the active state of the style selector and its buttons.

        Args:
            point: Current cursor position
        """
        for _, button in self.buttons:
            button.active = button.contains_point(point)

    def render(self, frame):
        """Render the style selector on the frame."""
        # Draw the panel background
        cv2.rectangle(frame, (self.x, self.y),
                      (self.x + self.width, self.y + self.height),
                      (240, 240, 240), -1)  # Light gray background

        # Draw panel border
        cv2.rectangle(frame, (self.x, self.y),
                      (self.x + self.width, self.y + self.height),
                      (150, 150, 150), 2)  # Gray border

        # Draw panel title
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, self.label, (self.x + 10, self.y + 25),
                    font, 0.7, (0, 0, 0), 2)

        # Draw style buttons
        for _, button in self.buttons:
            frame = button.render(frame)

        # Draw selected style info
        selected_text = f"Selected: {self.selected_style}"
        cv2.putText(frame, selected_text, (self.x + 10, self.y + self.height - 15),
                    font, 0.6, (0, 0, 0), 2)

        return frame


class InstructionPanel(UIElement):
    """Panel showing usage instructions."""

    def __init__(self, x, y, width, height):
        """Initialize an instruction panel."""
        super().__init__(x, y, width, height, "Instructions")

    def render(self, frame):
        """Render the instruction panel on the frame."""
        # Draw the panel background
        cv2.rectangle(frame, (self.x, self.y),
                      (self.x + self.width, self.y + self.height),
                      (240, 240, 240), -1)  # Light gray background

        # Draw panel border
        cv2.rectangle(frame, (self.x, self.y),
                      (self.x + self.width, self.y + self.height),
                      (150, 150, 150), 2)  # Gray border

        # Draw panel title
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, self.label, (self.x + 10, self.y + 25),
                    font, 0.7, (0, 0, 0), 2)

        # Draw instructions
        instructions = [
            "Hand Gestures:",
            "- Index finger: Move cursor",
            "- Index + Middle: Click",
            "",
            "Select a style and color",
            "for the virtual glasses",
            "",
            "Press 'Q' to quit"
        ]

        y_offset = self.y + 50
        line_height = 25
        for line in instructions:
            cv2.putText(frame, line, (self.x + 10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            y_offset += line_height

        return frame


class UIManager:
    """Manages UI elements in the video frame."""

    def __init__(self):
        """Initialize the UI manager."""
        # Available styles and colors
        self.styles = ["Rectangle", "Round", "Aviator"]
        self.colors = {
            "Black": (0, 0, 0),
            "Blue": (255, 0, 0),
            "Red": (0, 0, 255),
            "Green": (0, 255, 0),
            "Yellow": (0, 255, 255),
            "White": (255, 255, 255)
        }

        # Current selections
        self.current_style = self.styles[0]
        self.current_color = "Black"

        # UI elements
        self.elements = []

        # Create UI elements (will be positioned appropriately when first frame is received)
        self.ui_initialized = False

        # Click cooldown to prevent multiple clicks
        self.click_cooldown = 0
        self.cooldown_frames = 15  # Number of frames to wait between clicks

    def _initialize_ui(self, frame_width, frame_height):
        """Initialize UI elements based on frame dimensions."""
        # Panel dimensions
        panel_width = 200
        panel_height = 200
        margin = 20

        # Create style selector
        style_selector = StyleSelector(
            margin, margin,
            panel_width, panel_height,
            self.styles
        )

        # Create color selector
        color_selector = ColorSelector(
            margin, margin + panel_height + margin,
            panel_width, panel_height,
            self.colors
        )

        # Create instruction panel
        instruction_panel = InstructionPanel(
            margin, frame_height - margin - panel_height,
            panel_width, panel_height
        )

        # Add elements
        # self.elements = [style_selector, color_selector, instruction_panel]
        self.elements = [style_selector, color_selector]

        self.ui_initialized = True

    def update(self, frame, gesture, cursor_pos):
        """
        Update the UI state based on gesture and cursor position.

        Args:
            frame: The current video frame
            gesture: The current hand gesture
            cursor_pos: The current cursor position
        """
        # Initialize UI if not already done
        if not self.ui_initialized and frame is not None:
            frame_height, frame_width = frame.shape[:2]
            self._initialize_ui(frame_width, frame_height)

        # Update active state of UI elements
        for element in self.elements:
            if hasattr(element, 'update'):
                element.update(cursor_pos)

        # Handle gestures
        if gesture == "left_click" and cursor_pos and self.click_cooldown <= 0:
            # Handle click
            for element in self.elements:
                if hasattr(element, 'handle_click'):
                    if element.handle_click(cursor_pos):
                        # Update current selections
                        if isinstance(element, StyleSelector):
                            self.current_style = element.selected_style
                        elif isinstance(element, ColorSelector):
                            self.current_color = element.selected_color

                        # Set cooldown
                        self.click_cooldown = self.cooldown_frames
                        break

        # Update cooldown
        if self.click_cooldown > 0:
            self.click_cooldown -= 1

    def render(self, frame):
        """
        Render all UI elements on the frame.

        Args:
            frame: The video frame to render on

        Returns:
            The frame with UI elements rendered
        """
        # Initialize UI if not already done
        if not self.ui_initialized:
            frame_height, frame_width = frame.shape[:2]
            self._initialize_ui(frame_width, frame_height)

        # Render all UI elements
        for element in self.elements:
            frame = element.render(frame)

        return frame
