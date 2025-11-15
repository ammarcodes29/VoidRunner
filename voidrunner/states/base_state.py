"""
Abstract base class for game states.

All game states (Menu, Playing, Paused, GameOver) inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from ..game import Game


class BaseState(ABC):
    """
    Abstract base class for all game states.

    Each state represents a distinct mode of the game (menu, playing, paused, etc.)
    and implements its own update/draw/input logic.
    """

    def __init__(self, game: "Game") -> None:
        """
        Initialize the base state.

        Args:
            game: Reference to the main Game object
        """
        self.game = game

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle pygame events for this state.

        Args:
            events: List of pygame events from this frame
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update state logic.

        Args:
            dt: Delta time in seconds since last frame
        """
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """
        Render the state to the screen.

        Args:
            screen: Pygame surface to draw on
        """
        pass

    def enter(self) -> None:
        """
        Called when entering this state.

        Override this method to perform setup when transitioning to this state.
        """
        pass

    def exit(self) -> None:
        """
        Called when leaving this state.

        Override this method to perform cleanup when transitioning away from this state.
        """
        pass

