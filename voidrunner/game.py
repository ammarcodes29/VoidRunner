"""
Main game orchestrator.

Manages the game loop, state management, and core systems.
"""

import logging
import sys

import pygame

from .managers.asset_manager import AssetManager
from .managers.data_manager import DataManager
from .states.login_state import LoginState
from .utils import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Game:
    """
    Main game class that orchestrates all systems.

    Manages the game loop, state transitions, and core subsystems.
    """

    def __init__(self) -> None:
        """Initialize the game and all subsystems."""
        logger.info("Initializing VoidRunner...")
        
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Create window
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(config.WINDOW_TITLE)
        
        # Clock for frame rate control
        self.clock = pygame.time.Clock()
        self.running = False
        
        # Load assets
        logger.info("Loading assets...")
        self.asset_manager = AssetManager()
        
        # Initialize data manager for high scores
        logger.info("Loading data manager...")
        self.data_manager = DataManager()
        
        # Initialize game state
        self.current_state = None
        self.debug_mode = config.DEBUG_MODE
        
        logger.info("Initialization complete!")

    def run(self) -> None:
        """
        Run the main game loop.

        Maintains 60 FPS and handles events, updates, and rendering.
        """
        logger.info("Starting game loop...")
        self.running = True
        
        # Start with login state
        self.current_state = LoginState(self)
        self.current_state.enter()
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(config.FPS) / 1000.0  # Convert to seconds
            
            # Handle events
            events = pygame.event.get()
            self._handle_global_events(events)
            
            if self.current_state:
                self.current_state.handle_events(events)
            
            # Update
            if self.current_state:
                self.current_state.update(dt)
            
            # Draw
            self.screen.fill(config.COLOR_BLACK)
            if self.current_state:
                self.current_state.draw(self.screen)
            
            # Draw debug info
            if self.debug_mode and config.SHOW_FPS:
                self._draw_fps()
            
            # Update display
            pygame.display.flip()
        
        # Cleanup
        self._quit()

    def _handle_global_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle game-wide events.

        Args:
            events: List of pygame events
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Global key bindings
                if event.key == pygame.K_F3:
                    # Toggle debug mode
                    self.debug_mode = not self.debug_mode
                    logger.info(f"Debug mode: {self.debug_mode}")
                elif event.key == pygame.K_ESCAPE:
                    # Handle escape in game over state
                    if hasattr(self.current_state, 'game_over') and self.current_state.game_over:
                        self.running = False
                elif event.key == pygame.K_r:
                    # Restart game or return to menu
                    if hasattr(self.current_state, 'game_over') and self.current_state.game_over:
                        self._return_to_menu()

    def _return_to_menu(self) -> None:
        """Return to main menu."""
        logger.info("Returning to menu...")
        if self.current_state:
            self.current_state.exit()
        from .states.menu_state import MenuState
        self.current_state = MenuState(self)
        self.current_state.enter()

    def _draw_fps(self) -> None:
        """Draw FPS counter in debug mode with background for visibility."""
        # Use a larger, more visible font
        fps_font = self.asset_manager.load_font(32)
        fps = self.clock.get_fps()
        
        # Color based on performance
        if fps >= 55:
            color = config.COLOR_GREEN
        elif fps >= 40:
            color = config.COLOR_YELLOW
        else:
            color = config.COLOR_RED
        
        # Format with proper spacing
        fps_text = f"FPS: {fps:5.1f}"
        text_surface = fps_font.render(fps_text, True, color)
        
        # Position in bottom-left with some padding
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = (config.HUD_MARGIN, config.SCREEN_HEIGHT - config.HUD_MARGIN)
        
        # Draw semi-transparent black background for visibility
        padding = 5
        bg_rect = pygame.Rect(
            text_rect.left - padding,
            text_rect.top - padding,
            text_rect.width + padding * 2,
            text_rect.height + padding * 2
        )
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill(config.COLOR_BLACK)
        self.screen.blit(bg_surface, bg_rect.topleft)
        
        # Draw the FPS text
        self.screen.blit(text_surface, text_rect)

    def _quit(self) -> None:
        """Clean up and quit the game."""
        logger.info("Shutting down...")
        pygame.quit()
        sys.exit()


def main() -> None:
    """Entry point for the game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()

