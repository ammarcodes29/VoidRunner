"""
Utility helper functions.

Common functions used across the codebase.
"""

import math
import random
from typing import Tuple

import pygame


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between a minimum and maximum.

    Args:
        value: The value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        The clamped value
    """
    return max(min_value, min(value, max_value))


def distance(pos1: pygame.Vector2, pos2: pygame.Vector2) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        pos1: First position vector
        pos2: Second position vector

    Returns:
        Distance in pixels
    """
    return pos1.distance_to(pos2)


def normalize_vector(vector: pygame.Vector2) -> pygame.Vector2:
    """
    Normalize a vector to unit length.

    Args:
        vector: Vector to normalize

    Returns:
        Normalized vector (length 1) or zero vector if input is zero
    """
    if vector.length() == 0:
        return pygame.Vector2(0, 0)
    return vector.normalize()


def random_position_off_screen(
    screen_width: int, screen_height: int, margin: int = 50
) -> Tuple[float, float]:
    """
    Generate a random position just off-screen (above the visible area).

    Args:
        screen_width: Width of the screen
        screen_height: Height of the screen
        margin: Distance above screen to spawn

    Returns:
        Tuple of (x, y) coordinates
    """
    x = random.uniform(0, screen_width)
    y = -margin
    return (x, y)


def lerp(start: float, end: float, t: float) -> float:
    """
    Linear interpolation between two values.

    Args:
        start: Starting value
        end: Ending value
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated value
    """
    return start + (end - start) * t


def screen_shake_offset(intensity: int) -> Tuple[int, int]:
    """
    Generate random offset for screen shake effect.

    Args:
        intensity: Maximum shake distance in pixels

    Returns:
        Tuple of (dx, dy) offsets
    """
    dx = random.randint(-intensity, intensity)
    dy = random.randint(-intensity, intensity)
    return (dx, dy)


def angle_to_target(
    from_pos: pygame.Vector2, to_pos: pygame.Vector2
) -> float:
    """
    Calculate angle in radians from one position to another.

    Args:
        from_pos: Starting position
        to_pos: Target position

    Returns:
        Angle in radians
    """
    direction = to_pos - from_pos
    return math.atan2(direction.y, direction.x)


def wrap_text(
    text: str, font: pygame.font.Font, max_width: int
) -> list[str]:
    """
    Wrap text to fit within a maximum width.

    Args:
        text: Text to wrap
        font: Pygame font object
        max_width: Maximum width in pixels

    Returns:
        List of text lines
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        line_text = " ".join(current_line)
        if font.size(line_text)[0] > max_width:
            if len(current_line) == 1:
                # Word is too long, force it
                lines.append(line_text)
                current_line = []
            else:
                # Remove last word and start new line
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines

