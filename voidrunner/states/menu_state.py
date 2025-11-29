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
        
        # Fonts (reduced sizes)
        self.title_font = game.asset_manager.load_font(64)  # Was 96
        self.menu_font = game.asset_manager.get_font("menu")
        self.info_font = game.asset_manager.get_font("hud")
        self.button_font = game.asset_manager.load_font(24)  # Smaller text for buttons
        
        # Buttons (wider to fit text)
        self.start_button_rect = pygame.Rect(0, 0, 360, 70)
        self.start_button_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 100)
        
        self.leaderboard_button_rect = pygame.Rect(0, 0, 360, 70)
        self.leaderboard_button_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 190)
        
        self.logout_button_rect = pygame.Rect(0, 0, 200, 50)
        self.logout_button_rect.bottomright = (config.SCREEN_WIDTH - 20, config.SCREEN_HEIGHT - 20)
        
        # Mouse tracking
        self.mouse_pos = (0, 0)
        
        # Background
        self.background = game.asset_manager.get_sprite("background")

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle menu input events.

        Args:
            events: List of pygame events from this frame
        """
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.start_button_rect.collidepoint(event.pos):
                        self._start_game()
                    elif self.leaderboard_button_rect.collidepoint(event.pos):
                        self._show_leaderboard()
                    elif self.logout_button_rect.collidepoint(event.pos):
                        self._logout()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    # Start with spacebar or enter
                    self._start_game()
                elif event.key == pygame.K_l:
                    # View leaderboard with L key
                    self._show_leaderboard()
                elif event.key == pygame.K_ESCAPE:
                    # Logout with ESC
                    self._logout()

    def _start_game(self) -> None:
        """Transition to playing state."""
        from .playing_state import PlayingState
        self.game.current_state.exit()
        self.game.current_state = PlayingState(self.game)
        self.game.current_state.enter()

    def _show_leaderboard(self) -> None:
        """Transition to leaderboard state."""
        from .leaderboard_state import LeaderboardState
        self.game.current_state.exit()
        self.game.current_state = LeaderboardState(self.game)
        self.game.current_state.enter()

    def _logout(self) -> None:
        """Logout and return to login screen."""
        from .login_state import LoginState
        self.game.data_manager.logout()
        self.game.current_state.exit()
        self.game.current_state = LoginState(self.game)
        self.game.current_state.enter()

    def update(self, dt: float) -> None:
        """
        Update menu state.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Change cursor to hand when hovering over buttons
        if (self.start_button_rect.collidepoint(self.mouse_pos) or
            self.leaderboard_button_rect.collidepoint(self.mouse_pos) or
            self.logout_button_rect.collidepoint(self.mouse_pos)):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

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
        title_rect.center = (config.SCREEN_WIDTH // 2, 120)
        
        # Title shadow
        shadow_surface = self.title_font.render(title_text, True, config.COLOR_BLACK)
        shadow_rect = shadow_surface.get_rect()
        shadow_rect.center = (title_rect.centerx + 4, title_rect.centery + 4)
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)
        
        # Draw username
        username = self.game.data_manager.get_current_username()
        username_text = f"Player: {username}"
        username_surface = self.info_font.render(username_text, True, config.COLOR_WHITE)
        username_rect = username_surface.get_rect()
        username_rect.center = (config.SCREEN_WIDTH // 2, 220)
        screen.blit(username_surface, username_rect)
        
        # Draw high score
        high_score = self.game.data_manager.get_high_score()
        high_score_text = f"Your High Score: {high_score}"
        high_score_surface = self.menu_font.render(high_score_text, True, config.COLOR_YELLOW)
        high_score_rect = high_score_surface.get_rect()
        high_score_rect.center = (config.SCREEN_WIDTH // 2, 280)
        screen.blit(high_score_surface, high_score_rect)
        
        # Draw Start Game button
        self._draw_button(screen, "START GAME", self.start_button_rect, config.COLOR_GREEN)
        
        # Draw Leaderboard button
        self._draw_button(screen, "LEADERBOARD", self.leaderboard_button_rect, config.COLOR_BLUE)
        
        # Draw Logout button (smaller, in corner)
        self._draw_small_button(screen, "Logout", self.logout_button_rect, config.COLOR_RED)

    def _draw_button(self, screen: pygame.Surface, text: str, 
                    rect: pygame.Rect, color: tuple) -> None:
        """Draw a main menu button."""
        is_hovering = rect.collidepoint(self.mouse_pos)
        
        if is_hovering:
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, config.COLOR_WHITE, rect, 3, border_radius=10)
            text_color = config.COLOR_WHITE
        else:
            # Draw with transparent fill
            fill_surface = pygame.Surface((rect.width, rect.height))
            fill_surface.set_alpha(100)
            fill_surface.fill(color)
            screen.blit(fill_surface, rect.topleft)
            pygame.draw.rect(screen, color, rect, 2, border_radius=10)
            text_color = config.COLOR_WHITE
        
        # Button text (use smaller font)
        button_surface = self.button_font.render(text, True, text_color)
        button_text_rect = button_surface.get_rect(center=rect.center)
        screen.blit(button_surface, button_text_rect)

    def _draw_small_button(self, screen: pygame.Surface, text: str, 
                          rect: pygame.Rect, color: tuple) -> None:
        """Draw a small button (for logout)."""
        is_hovering = rect.collidepoint(self.mouse_pos)
        
        if is_hovering:
            pygame.draw.rect(screen, color, rect, border_radius=8)
            text_color = config.COLOR_WHITE
        else:
            pygame.draw.rect(screen, config.COLOR_BLACK, rect, border_radius=8)
            pygame.draw.rect(screen, color, rect, 2, border_radius=8)
            text_color = color
        
        # Button text
        button_surface = self.info_font.render(text, True, text_color)
        button_text_rect = button_surface.get_rect(center=rect.center)
        screen.blit(button_surface, button_text_rect)

