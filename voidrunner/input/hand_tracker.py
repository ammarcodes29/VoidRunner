"""
Hand tracking module using MediaPipe.

Provides gesture recognition for CV game mode controls.
"""

import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

logger = logging.getLogger(__name__)


class HandTracker:
    """
    Handles webcam capture and hand gesture recognition.
    
    Uses MediaPipe to detect hands and interpret gestures for game control:
    - Movement hand (left): Position-based virtual joystick
    - Shooting hand (right): Open/closed fist for shooting
    """
    
    # Hand landmark indices
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    
    # Knuckle indices (MCP joints)
    INDEX_MCP = 5
    MIDDLE_MCP = 9
    RING_MCP = 13
    PINKY_MCP = 17
    
    # Additional thumb landmarks
    THUMB_CMC = 1  # Base of thumb
    THUMB_MCP = 2
    THUMB_IP = 3
    
    # Hand bone connections for debug drawing
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),      # thumb
        (0, 5), (5, 6), (6, 7), (7, 8),      # index
        (0, 9), (9, 10), (10, 11), (11, 12), # middle
        (0, 13), (13, 14), (14, 15), (15, 16), # ring
        (0, 17), (17, 18), (18, 19), (19, 20), # pinky
        (5, 9), (9, 13), (13, 17)            # palm
    ]

    def __init__(self, model_path: Optional[str] = None) -> None:
        """
        Initialize the hand tracker.
        
        Args:
            model_path: Path to hand_landmarker.task model file.
                       If None, searches in common locations.
        """
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError(
                "MediaPipe is not installed. Install with: "
                "pip install mediapipe opencv-python"
            )
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.detector: Optional[vision.HandLandmarker] = None
        self.last_frame: Optional[np.ndarray] = None
        self.frame_width = 640
        self.frame_height = 480
        
        # Control state
        self.movement = (0.0, 0.0)  # (dx, dy) normalized -1 to 1
        self.shooting = False
        self.hands_detected = 0
        
        # Dead zone for movement (center area where no movement occurs)
        self.dead_zone = 0.15  # 15% from center
        
        # Find and load the model
        self._model_path = self._find_model(model_path)
        
    def _find_model(self, model_path: Optional[str]) -> Path:
        """
        Find the hand landmarker model file.
        
        Args:
            model_path: Explicit path or None to search
            
        Returns:
            Path to the model file
            
        Raises:
            FileNotFoundError: If model cannot be found
        """
        if model_path and Path(model_path).exists():
            return Path(model_path)
        
        # Search common locations
        search_paths = [
            Path(__file__).parent.parent / "assets" / "models" / "hand_landmarker.task",
            Path.cwd() / "hand_landmarker.task",
            Path.cwd() / "voidrunner" / "assets" / "models" / "hand_landmarker.task",
            Path.home() / "hand_landmarker.task",
        ]
        
        for path in search_paths:
            if path.exists():
                logger.info(f"Found hand landmarker model at: {path}")
                return path
        
        raise FileNotFoundError(
            "Could not find hand_landmarker.task model file. "
            "Please download from MediaPipe and place in voidrunner/assets/models/ "
            "or specify path explicitly."
        )

    def start(self) -> bool:
        """
        Start the webcam and initialize the hand detector.
        
        Returns:
            True if successfully started, False otherwise
        """
        try:
            # Initialize webcam
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logger.error("Failed to open webcam")
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            
            # Initialize MediaPipe hand detector
            base_options = python.BaseOptions(
                model_asset_path=str(self._model_path)
            )
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=2
            )
            self.detector = vision.HandLandmarker.create_from_options(options)
            
            logger.info("Hand tracker started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start hand tracker: {e}")
            self.release()
            return False

    def update(self) -> dict:
        """
        Process a frame and update control state.
        
        Returns:
            Dictionary with control state:
            - movement: (dx, dy) tuple, -1 to 1 for each axis
            - shooting: bool, True if shooting gesture detected
            - hands_detected: int, number of hands detected (0-2)
        """
        if self.cap is None or self.detector is None:
            return {
                'movement': (0.0, 0.0),
                'shooting': False,
                'hands_detected': 0
            }
        
        success, frame = self.cap.read()
        if not success:
            return {
                'movement': self.movement,
                'shooting': self.shooting,
                'hands_detected': self.hands_detected
            }
        
        # Flip horizontally for mirror effect (more intuitive)
        frame = cv2.flip(frame, 1)
        self.last_frame = frame.copy()
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect hands
        result = self.detector.detect(mp_image)
        
        # Reset state
        self.movement = (0.0, 0.0)
        self.shooting = False
        self.hands_detected = 0
        
        if result.hand_landmarks:
            self.hands_detected = len(result.hand_landmarks)
            
            # Process each detected hand
            left_hand = None
            right_hand = None
            
            # Determine which hand is left vs right by x position
            # (after mirror flip, left hand appears on right side of frame)
            for i, hand_landmarks in enumerate(result.hand_landmarks):
                wrist_x = hand_landmarks[self.WRIST].x
                
                # Handedness from MediaPipe (if available)
                if result.handedness and i < len(result.handedness):
                    hand_label = result.handedness[i][0].category_name
                    if hand_label == "Left":
                        left_hand = hand_landmarks
                    else:
                        right_hand = hand_landmarks
                else:
                    # Fallback: use position (left side of frame = movement)
                    if wrist_x < 0.5:
                        if left_hand is None:
                            left_hand = hand_landmarks
                    else:
                        if right_hand is None:
                            right_hand = hand_landmarks
            
            # Process movement hand (left hand)
            if left_hand:
                self.movement = self._get_movement(left_hand)
            
            # Process shooting hand (right hand)
            if right_hand:
                self.shooting = self._is_fist(right_hand)
        
        return {
            'movement': self.movement,
            'shooting': self.shooting,
            'hands_detected': self.hands_detected
        }

    def _get_movement(self, hand_landmarks) -> tuple[float, float]:
        """
        Calculate movement direction from hand gestures.
        
        Controls:
        - UP/DOWN: Hand Y position (move hand up/down in camera view)
        - LEFT: Thumb sticking out
        - RIGHT: Index finger pointing up
        - DIAGONALS: Combine vertical position with finger gestures
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            (dx, dy) tuple normalized to -1 to 1
        """
        # --- VERTICAL MOVEMENT: Hand Y position ---
        wrist_y = hand_landmarks[self.WRIST].y
        
        # Convert to -1 (up) to 1 (down) range
        dy = (wrist_y - 0.5) * 2
        
        # Apply dead zone for vertical
        if abs(dy) < self.dead_zone:
            dy = 0.0
        dy = max(-1.0, min(1.0, dy))
        
        # --- HORIZONTAL MOVEMENT: Finger gestures ---
        dx = 0.0
        
        # Check for index finger pointing (RIGHT movement)
        if self._is_index_pointing(hand_landmarks):
            dx = 1.0
        # Check for thumb out (LEFT movement)
        elif self._is_thumb_out(hand_landmarks):
            dx = -1.0
        
        return (dx, dy)

    def _is_index_pointing(self, hand_landmarks) -> bool:
        """
        Detect if index finger is pointing up (other fingers curled).
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            True if index finger is pointing up
        """
        # Index finger must be extended (tip above MCP)
        index_extended = hand_landmarks[self.INDEX_TIP].y < hand_landmarks[self.INDEX_MCP].y
        
        if not index_extended:
            return False
        
        # Other fingers (middle, ring, pinky) should be curled
        middle_curled = hand_landmarks[self.MIDDLE_TIP].y > hand_landmarks[self.MIDDLE_MCP].y
        ring_curled = hand_landmarks[self.RING_TIP].y > hand_landmarks[self.RING_MCP].y
        pinky_curled = hand_landmarks[self.PINKY_TIP].y > hand_landmarks[self.PINKY_MCP].y
        
        # At least 2 of the other 3 fingers should be curled
        curled_count = sum([middle_curled, ring_curled, pinky_curled])
        
        return curled_count >= 2

    def _is_thumb_out(self, hand_landmarks) -> bool:
        """
        Detect if thumb is sticking out to the side.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            True if thumb is extended outward
        """
        # Get thumb tip and index MCP (base of index finger)
        thumb_tip_x = hand_landmarks[self.THUMB_TIP].x
        index_mcp_x = hand_landmarks[self.INDEX_MCP].x
        wrist_x = hand_landmarks[self.WRIST].x
        
        # Thumb should be far from index finger horizontally
        # (account for mirrored view - thumb sticks out to the right in camera = left in game)
        thumb_distance = abs(thumb_tip_x - index_mcp_x)
        
        # Thumb must be extended significantly (more than 10% of frame width)
        thumb_extended = thumb_distance > 0.10
        
        # Also check that thumb tip is to the left of wrist (in mirrored view)
        # This ensures thumb is sticking OUT, not just curled
        thumb_out_direction = thumb_tip_x < wrist_x
        
        # Additionally, check that index finger is NOT pointing (to avoid conflict)
        index_not_pointing = not self._is_index_pointing(hand_landmarks)
        
        return thumb_extended and thumb_out_direction and index_not_pointing

    def _is_fist(self, hand_landmarks) -> bool:
        """
        Detect if hand is making a fist (shooting gesture).
        
        Checks if fingertips are below their respective knuckles.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            True if fist detected, False otherwise
        """
        # Check each finger (excluding thumb which moves differently)
        fingers_curled = 0
        
        finger_tips = [self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        finger_mcps = [self.INDEX_MCP, self.MIDDLE_MCP, self.RING_MCP, self.PINKY_MCP]
        
        for tip, mcp in zip(finger_tips, finger_mcps):
            # In image coordinates, y increases downward
            # If tip.y > mcp.y, finger is curled
            if hand_landmarks[tip].y > hand_landmarks[mcp].y:
                fingers_curled += 1
        
        # Consider it a fist if at least 3 fingers are curled
        return fingers_curled >= 3

    def get_debug_frame(self) -> Optional[np.ndarray]:
        """
        Get the current frame with hand landmarks drawn.
        
        Returns:
            Annotated BGR frame or None if no frame available
        """
        if self.last_frame is None or self.detector is None:
            return None
        
        frame = self.last_frame.copy()
        h, w = frame.shape[:2]
        
        # Convert and detect again for drawing (or cache the result)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.detector.detect(mp_image)
        
        if result.hand_landmarks:
            for i, hand_landmarks in enumerate(result.hand_landmarks):
                # Determine color based on hand type
                if result.handedness and i < len(result.handedness):
                    hand_label = result.handedness[i][0].category_name
                    color = (0, 255, 0) if hand_label == "Left" else (0, 255, 255)
                else:
                    color = (0, 255, 0)
                
                # Draw landmarks
                for landmark in hand_landmarks:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 5, color, -1)
                
                # Draw connections
                for connection in self.HAND_CONNECTIONS:
                    start = hand_landmarks[connection[0]]
                    end = hand_landmarks[connection[1]]
                    start_point = (int(start.x * w), int(start.y * h))
                    end_point = (int(end.x * w), int(end.y * h))
                    cv2.line(frame, start_point, end_point, color, 2)
        
        # Draw control state overlay
        self._draw_control_overlay(frame)
        
        return frame

    def _draw_control_overlay(self, frame: np.ndarray) -> None:
        """Draw control state information on the frame."""
        h, w = frame.shape[:2]
        
        # Draw movement indicator
        center_x, center_y = w // 4, h - 60
        radius = 40
        
        # Draw joystick background
        cv2.circle(frame, (center_x, center_y), radius, (100, 100, 100), 2)
        
        # Draw joystick position
        dx, dy = self.movement
        indicator_x = int(center_x + dx * radius * 0.8)
        indicator_y = int(center_y + dy * radius * 0.8)
        cv2.circle(frame, (indicator_x, indicator_y), 10, (0, 255, 0), -1)
        
        # Draw shooting indicator
        shoot_x = w - 60
        shoot_color = (0, 0, 255) if self.shooting else (100, 100, 100)
        cv2.circle(frame, (shoot_x, center_y), 30, shoot_color, -1 if self.shooting else 2)
        cv2.putText(frame, "FIRE", (shoot_x - 20, center_y + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw hands detected
        text = f"Hands: {self.hands_detected}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw gesture hints
        gesture_y = 55
        if dx > 0:
            cv2.putText(frame, "INDEX -> RIGHT", (10, gesture_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        elif dx < 0:
            cv2.putText(frame, "THUMB -> LEFT", (10, gesture_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        else:
            cv2.putText(frame, "Gesture: NONE", (10, gesture_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

    def release(self) -> None:
        """Release webcam and cleanup resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.detector = None
        logger.info("Hand tracker released")

