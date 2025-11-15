"""
Main menu state.

Initial screen with title, high score, and start button.
"""

import pygame

from ..utils import config
from .base_state import BaseState


class MenuState(BaseState):
    """
    Main menu state displayed on game start.

    Shows title, high score, and a start button to begin playing.
    """

    def __init__(self, game: "Game") -> None:
        """
        Initialize the menu state.

        Args:
            game: Reference to the main Game object
        """
        super().__init__(game)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 96)
        self.menu_font = game.asset_manager.get_font("menu")
        self.info_font = game.asset_manager.get_font("hud")
        
        # Button
        self.button_rect = pygame.Rect(0, 0, 300, 80)
        self.button_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 100)
        self.button_hovered = False
        
        # Background
        self.background = game.asset_manager.get_sprite("background")

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle menu input events.

        Args:
            events: List of pygame events from this frame
        """
        mouse_pos = pygame.mouse.get_pos()
        self.button_hovered = self.button_rect.collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.button_hovered:
                    # Start button clicked
                    self._start_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    # Also start with spacebar or enter
                    self._start_game()

    def _start_game(self) -> None:
        """Transition to playing state."""
        from .playing_state import PlayingState
        self.game.current_state.exit()
        self.game.current_state = PlayingState(self.game)
        self.game.current_state.enter()

    def update(self, dt: float) -> None:
        """
        Update menu state.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Menu doesn't need updating
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """
        Render the menu screen.

        Args:
            screen: Pygame surface to draw on
        """
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw title
        title_text = "VOIDRUNNER"
        title_surface = self.title_font.render(title_text, True, config.COLOR_BLUE)
        title_rect = title_surface.get_rect()
        title_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 3)
        
        # Title shadow
        shadow_surface = self.title_font.render(title_text, True, config.COLOR_BLACK)
        shadow_rect = shadow_surface.get_rect()
        shadow_rect.center = (title_rect.centerx + 4, title_rect.centery + 4)
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)
        
        # Draw high score
        high_score = self.game.data_manager.get_high_score()
        high_score_text = f"High Score: {high_score}"
        high_score_surface = self.menu_font.render(high_score_text, True, config.COLOR_YELLOW)
        high_score_rect = high_score_surface.get_rect()
        high_score_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        screen.blit(high_score_surface, high_score_rect)
        
        # Draw start button
        button_color = config.COLOR_GREEN if self.button_hovered else config.COLOR_GRAY
        pygame.draw.rect(screen, button_color, self.button_rect, border_radius=10)
        pygame.draw.rect(screen, config.COLOR_WHITE, self.button_rect, 3, border_radius=10)
        
        # Button text
        button_text = "START GAME"
        button_surface = self.menu_font.render(button_text, True, config.COLOR_WHITE)
        button_text_rect = button_surface.get_rect()
        button_text_rect.center = self.button_rect.center
        screen.blit(button_surface, button_text_rect)
        
        # Draw controls hint
        controls_text = "Press SPACE or click to start"
        controls_surface = self.info_font.render(controls_text, True, config.COLOR_GRAY)
        controls_rect = controls_surface.get_rect()
        controls_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 50)
        screen.blit(controls_surface, controls_rect)

