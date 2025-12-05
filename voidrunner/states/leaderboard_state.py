"""
Leaderboard state showing global high scores.
"""

import pygame
import logging
from typing import TYPE_CHECKING

from .base_state import BaseState
from ..utils import config

if TYPE_CHECKING:
    from ..game import Game

logger = logging.getLogger(__name__)


class LeaderboardState(BaseState):
    """
    Displays global leaderboard with all users' high scores.
    """

    def __init__(self, game: "Game") -> None:
        """Initialize the leaderboard state."""
        super().__init__(game)
        
        # Fonts (reduced sizes)
        self.title_font = game.asset_manager.load_font(48)  # Was 72
        self.header_font = game.asset_manager.load_font(28)  # Was 40
        self.score_font = game.asset_manager.load_font(22)   # Was 32
        self.button_font = game.asset_manager.load_font(28)  # Was 42
        
        # Background
        self.background = game.asset_manager.get_sprite("background")
        
        # Mouse tracking
        self.mouse_pos = (0, 0)
        self.back_button_rect = pygame.Rect(0, 0, 0, 0)
        
        # Load leaderboard data
        self.leaderboard_data = []
        self._load_leaderboard()

    def _load_leaderboard(self) -> None:
        """Load leaderboard data from database."""
        self.leaderboard_data = self.game.data_manager.get_global_leaderboard(limit=10)
        logger.info(f"Loaded {len(self.leaderboard_data)} entries for leaderboard")

    def enter(self) -> None:
        """Called when entering this state."""
        logger.info("Entering LeaderboardState")
        # Refresh leaderboard data when entering
        self._load_leaderboard()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle input events."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                    self._return_to_menu()
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.back_button_rect.collidepoint(event.pos):
                        self._return_to_menu()

    def _return_to_menu(self) -> None:
        """Return to main menu."""
        from .menu_state import MenuState
        self.exit()
        self.game.current_state = MenuState(self.game)
        self.game.current_state.enter()

    def update(self, dt: float) -> None:
        """Update state and handle cursor changes."""
        # Change cursor to hand when hovering over back button
        if self.back_button_rect.collidepoint(self.mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the leaderboard screen."""
        # Draw background with dark overlay
        screen.blit(self.background, (0, 0))
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(config.COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("GLOBAL LEADERBOARD", True, config.COLOR_YELLOW)
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 60))
        screen.blit(title, title_rect)
        
        # Header
        header_y = 130
        rank_header = self.header_font.render("Rank", True, config.COLOR_BLUE)
        player_header = self.header_font.render("Player", True, config.COLOR_BLUE)
        score_header = self.header_font.render("Score", True, config.COLOR_BLUE)
        
        screen.blit(rank_header, (100, header_y))
        screen.blit(player_header, (250, header_y))
        screen.blit(score_header, (550, header_y))
        
        # Draw line under header
        pygame.draw.line(screen, config.COLOR_BLUE, (80, header_y + 50), 
                        (config.SCREEN_WIDTH - 80, header_y + 50), 2)
        
        # Display leaderboard entries
        y_start = 200
        current_username = self.game.data_manager.get_current_username()
        
        if not self.leaderboard_data:
            # No scores yet
            no_scores = self.score_font.render("No scores yet! Be the first!", 
                                              True, config.COLOR_GRAY)
            no_scores_rect = no_scores.get_rect(center=(config.SCREEN_WIDTH // 2, 300))
            screen.blit(no_scores, no_scores_rect)
        else:
            for i, entry in enumerate(self.leaderboard_data):
                y = y_start + (i * 40)
                
                # Highlight current user's entry
                is_current_user = entry['username'] == current_username
                if is_current_user:
                    # Draw highlight background
                    highlight_rect = pygame.Rect(70, y - 5, config.SCREEN_WIDTH - 140, 38)
                    pygame.draw.rect(screen, config.COLOR_BLUE, highlight_rect, border_radius=5)
                    pygame.draw.rect(screen, config.COLOR_WHITE, highlight_rect, 2, border_radius=5)
                    text_color = config.COLOR_WHITE
                else:
                    text_color = config.COLOR_GRAY if i % 2 == 0 else config.COLOR_WHITE
                
                # Rank
                rank_text = f"#{i + 1}"
                if i == 0:
                    rank_color = config.COLOR_YELLOW
                elif i == 1:
                    rank_color = (192, 192, 192)  # Silver
                elif i == 2:
                    rank_color = (205, 127, 50)   # Bronze
                else:
                    rank_color = text_color
                
                rank_surface = self.score_font.render(rank_text, True, rank_color)
                screen.blit(rank_surface, (100, y))
                
                # Username
                username_text = entry['username']
                if is_current_user:
                    username_text = f"→ {username_text}"
                username_surface = self.score_font.render(username_text, True, text_color)
                screen.blit(username_surface, (250, y))
                
                # Score
                score_surface = self.score_font.render(str(entry['score']), True, text_color)
                screen.blit(score_surface, (550, y))
        
        # Back button
        self._draw_back_button(screen)

    def _draw_back_button(self, screen: pygame.Surface) -> None:
        """Draw the back button."""
        button_width = 200
        button_height = 50
        button_x = config.SCREEN_WIDTH // 2 - button_width // 2
        button_y = config.SCREEN_HEIGHT - 80
        
        self.back_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Check if hovering
        is_hovering = self.back_button_rect.collidepoint(self.mouse_pos)
        
        # Draw button
        if is_hovering:
            pygame.draw.rect(screen, config.COLOR_BLUE, self.back_button_rect, border_radius=8)
            pygame.draw.rect(screen, config.COLOR_WHITE, self.back_button_rect, 3, border_radius=8)
            text_color = config.COLOR_WHITE
        else:
            pygame.draw.rect(screen, config.COLOR_BLACK, self.back_button_rect, border_radius=8)
            pygame.draw.rect(screen, config.COLOR_BLUE, self.back_button_rect, 2, border_radius=8)
            text_color = config.COLOR_BLUE
        
        # Button text
        text = self.button_font.render("Back to Menu", True, text_color)
        text_rect = text.get_rect(center=self.back_button_rect.center)
        screen.blit(text, text_rect)

    def exit(self) -> None:
        """Called when exiting this state."""
        logger.info("Exiting LeaderboardState")

