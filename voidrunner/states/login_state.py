"""
Login/Signup state for user authentication.
"""

import pygame
import logging
from typing import TYPE_CHECKING

from .base_state import BaseState
from ..utils import config

if TYPE_CHECKING:
    from ..game import Game

logger = logging.getLogger(__name__)


class LoginState(BaseState):
    """
    Handles user authentication (login/signup).
    """

    def __init__(self, game: "Game") -> None:
        """Initialize the login state."""
        super().__init__(game)
        
        self.mode = "menu"  # "menu", "login", "signup"
        self.username_input = ""
        self.password_input = ""
        self.message = ""
        self.message_color = config.COLOR_WHITE
        self.active_field = "username"  # "username" or "password"
        
        # Fonts
        self.title_font = game.asset_manager.load_font(72)
        self.menu_font = game.asset_manager.load_font(48)
        self.input_font = game.asset_manager.load_font(36)
        self.message_font = game.asset_manager.load_font(28)
        self.button_font = game.asset_manager.load_font(42)
        
        # Mouse tracking
        self.mouse_pos = (0, 0)
        
        # Button rectangles (will be set during draw)
        self.login_button_rect = pygame.Rect(0, 0, 0, 0)
        self.signup_button_rect = pygame.Rect(0, 0, 0, 0)
        self.quit_button_rect = pygame.Rect(0, 0, 0, 0)
        self.submit_button_rect = pygame.Rect(0, 0, 0, 0)
        self.back_button_rect = pygame.Rect(0, 0, 0, 0)
        self.username_field_rect = pygame.Rect(0, 0, 0, 0)
        self.password_field_rect = pygame.Rect(0, 0, 0, 0)

    def enter(self) -> None:
        """Called when entering this state."""
        logger.info("Entering LoginState")
        self.message = "Welcome to VoidRunner!"

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle input events."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.mode == "menu":
                    self._handle_menu_input(event)
                elif self.mode in ["login", "signup"]:
                    self._handle_form_input(event)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)

    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input in menu mode."""
        if event.key == pygame.K_1:
            self.mode = "login"
            self.message = "Enter your credentials"
            self.message_color = config.COLOR_WHITE
            self._clear_inputs()
        elif event.key == pygame.K_2:
            self.mode = "signup"
            self.message = "Create a new account"
            self.message_color = config.COLOR_WHITE
            self._clear_inputs()
        elif event.key == pygame.K_ESCAPE:
            # Quit game
            self.game.running = False

    def _handle_form_input(self, event: pygame.event.Event) -> None:
        """Handle input in login/signup forms."""
        if event.key == pygame.K_ESCAPE:
            self.mode = "menu"
            self._clear_inputs()
            self.message = "Welcome to VoidRunner!"
            self.message_color = config.COLOR_WHITE
            
        elif event.key == pygame.K_TAB:
            # Switch between username and password fields
            self.active_field = "password" if self.active_field == "username" else "username"
            
        elif event.key == pygame.K_RETURN:
            # Submit form
            if self.mode == "login":
                self._attempt_login()
            elif self.mode == "signup":
                self._attempt_signup()
                
        elif event.key == pygame.K_BACKSPACE:
            # Delete character
            if self.active_field == "username":
                self.username_input = self.username_input[:-1]
            else:
                self.password_input = self.password_input[:-1]
                
        else:
            # Add character
            char = event.unicode
            if char.isprintable():
                if self.active_field == "username":
                    if len(self.username_input) < config.MAX_USERNAME_LENGTH:
                        self.username_input += char
                else:
                    self.password_input += char

    def _attempt_login(self) -> None:
        """Try to log in with entered credentials."""
        success, message = self.game.data_manager.login(
            self.username_input, 
            self.password_input
        )
        
        if success:
            self.message_color = config.COLOR_GREEN
            self.message = message
            # Transition to menu after successful login
            from .menu_state import MenuState
            self.game.current_state = MenuState(self.game)
            self.game.current_state.enter()
        else:
            self.message_color = config.COLOR_RED
            self.message = message
            self.password_input = ""

    def _attempt_signup(self) -> None:
        """Try to create account with entered credentials."""
        success, message = self.game.data_manager.signup(
            self.username_input,
            self.password_input
        )
        
        if success:
            self.message_color = config.COLOR_GREEN
            self.message = message + " Please log in."
            self.mode = "login"
            self._clear_inputs()
        else:
            self.message_color = config.COLOR_RED
            self.message = message

    def _clear_inputs(self) -> None:
        """Clear input fields."""
        self.username_input = ""
        self.password_input = ""
        self.active_field = "username"

    def _handle_mouse_click(self, pos: tuple[int, int]) -> None:
        """Handle mouse click events."""
        if self.mode == "menu":
            # Check menu button clicks
            if self.login_button_rect.collidepoint(pos):
                self.mode = "login"
                self.message = "Enter your credentials"
                self.message_color = config.COLOR_WHITE
                self._clear_inputs()
            elif self.signup_button_rect.collidepoint(pos):
                self.mode = "signup"
                self.message = "Create a new account"
                self.message_color = config.COLOR_WHITE
                self._clear_inputs()
            elif self.quit_button_rect.collidepoint(pos):
                self.game.running = False
        
        elif self.mode in ["login", "signup"]:
            # Check input field clicks
            if self.username_field_rect.collidepoint(pos):
                self.active_field = "username"
            elif self.password_field_rect.collidepoint(pos):
                self.active_field = "password"
            elif self.submit_button_rect.collidepoint(pos):
                # Submit form
                if self.mode == "login":
                    self._attempt_login()
                elif self.mode == "signup":
                    self._attempt_signup()
            elif self.back_button_rect.collidepoint(pos):
                self.mode = "menu"
                self._clear_inputs()
                self.message = "Welcome to VoidRunner!"
                self.message_color = config.COLOR_WHITE

    def update(self, dt: float) -> None:
        """Update state and handle cursor changes."""
        # Check if mouse is over any clickable element
        is_hovering = False
        
        if self.mode == "menu":
            if (self.login_button_rect.collidepoint(self.mouse_pos) or
                self.signup_button_rect.collidepoint(self.mouse_pos) or
                self.quit_button_rect.collidepoint(self.mouse_pos)):
                is_hovering = True
        elif self.mode in ["login", "signup"]:
            if (self.username_field_rect.collidepoint(self.mouse_pos) or
                self.password_field_rect.collidepoint(self.mouse_pos) or
                self.submit_button_rect.collidepoint(self.mouse_pos) or
                self.back_button_rect.collidepoint(self.mouse_pos)):
                is_hovering = True
        
        # Change cursor to hand when hovering over clickable elements
        if is_hovering:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the login screen."""
        screen.fill(config.COLOR_BLACK)
        
        if self.mode == "menu":
            self._draw_menu(screen)
        elif self.mode in ["login", "signup"]:
            self._draw_form(screen)

    def _draw_menu(self, screen: pygame.Surface) -> None:
        """Draw main menu."""
        # Title
        title = self.title_font.render("VOIDRUNNER", True, config.COLOR_BLUE)
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Message
        msg = self.message_font.render(self.message, True, config.COLOR_WHITE)
        msg_rect = msg.get_rect(center=(config.SCREEN_WIDTH // 2, 250))
        screen.blit(msg, msg_rect)
        
        # Draw buttons
        self._draw_button(screen, "Login", 320, "login")
        self._draw_button(screen, "Sign Up", 400, "signup")
        self._draw_button(screen, "Quit", 480, "quit")

    def _draw_form(self, screen: pygame.Surface) -> None:
        """Draw login/signup form."""
        # Title
        title_text = "LOGIN" if self.mode == "login" else "SIGN UP"
        title = self.title_font.render(title_text, True, config.COLOR_BLUE)
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # Message
        msg = self.message_font.render(self.message, True, self.message_color)
        msg_rect = msg.get_rect(center=(config.SCREEN_WIDTH // 2, 180))
        screen.blit(msg, msg_rect)
        
        # Username field
        self._draw_input_field(
            screen, 
            "Username:", 
            self.username_input,
            250,
            self.active_field == "username",
            "username"
        )
        
        # Password field
        self._draw_input_field(
            screen,
            "Password:",
            "*" * len(self.password_input),  # Hide password
            320,
            self.active_field == "password",
            "password"
        )
        
        # Submit button
        submit_text = "Login" if self.mode == "login" else "Sign Up"
        self._draw_form_button(screen, submit_text, 400, "submit")
        
        # Back button
        self._draw_form_button(screen, "Back", 470, "back")
        
        # Instructions (smaller, at bottom)
        instruction_text = "Click fields to type, or use TAB to switch"
        text = self.message_font.render(instruction_text, True, config.COLOR_GRAY)
        rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, 540))
        screen.blit(text, rect)

    def _draw_input_field(self, screen: pygame.Surface, label: str, 
                         value: str, y: int, is_active: bool, field_name: str) -> None:
        """Draw an input field."""
        # Label
        label_text = self.input_font.render(label, True, config.COLOR_WHITE)
        label_rect = label_text.get_rect(midright=(config.SCREEN_WIDTH // 2 - 20, y))
        screen.blit(label_text, label_rect)
        
        # Input box
        box_rect = pygame.Rect(config.SCREEN_WIDTH // 2, y - 20, 250, 40)
        
        # Store rectangle for click detection
        if field_name == "username":
            self.username_field_rect = box_rect
        elif field_name == "password":
            self.password_field_rect = box_rect
        
        # Check if mouse is hovering
        is_hovering = box_rect.collidepoint(self.mouse_pos)
        
        # Determine box color
        if is_active:
            box_color = config.COLOR_BLUE
            fill_alpha = 40
        elif is_hovering:
            box_color = config.COLOR_BLUE
            fill_alpha = 20
        else:
            box_color = config.COLOR_DARK_GRAY
            fill_alpha = 0
        
        # Draw fill if hovering or active
        if fill_alpha > 0:
            fill_surface = pygame.Surface((box_rect.width, box_rect.height))
            fill_surface.set_alpha(fill_alpha)
            fill_surface.fill(config.COLOR_BLUE)
            screen.blit(fill_surface, box_rect.topleft)
        
        # Draw border
        pygame.draw.rect(screen, box_color, box_rect, 2)
        
        # Input text
        input_text = self.input_font.render(value, True, config.COLOR_WHITE)
        input_rect = input_text.get_rect(midleft=(box_rect.left + 10, box_rect.centery))
        screen.blit(input_text, input_rect)
        
        # Cursor blink
        if is_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_rect.right + 2
            pygame.draw.line(
                screen, 
                config.COLOR_WHITE,
                (cursor_x, box_rect.top + 5),
                (cursor_x, box_rect.bottom - 5),
                2
            )

    def _draw_button(self, screen: pygame.Surface, text: str, y: int, button_type: str) -> None:
        """Draw a clickable button for the main menu."""
        button_width = 280
        button_height = 60
        button_rect = pygame.Rect(
            config.SCREEN_WIDTH // 2 - button_width // 2,
            y - button_height // 2,
            button_width,
            button_height
        )
        
        # Store rectangle for click detection
        if button_type == "login":
            self.login_button_rect = button_rect
        elif button_type == "signup":
            self.signup_button_rect = button_rect
        elif button_type == "quit":
            self.quit_button_rect = button_rect
        
        # Check if mouse is hovering
        is_hovering = button_rect.collidepoint(self.mouse_pos)
        
        # Draw button background
        if is_hovering:
            # Lighter background on hover
            pygame.draw.rect(screen, config.COLOR_BLUE, button_rect)
            pygame.draw.rect(screen, config.COLOR_WHITE, button_rect, 3)
            text_color = config.COLOR_WHITE
        else:
            # Normal state
            pygame.draw.rect(screen, config.COLOR_BLACK, button_rect)
            pygame.draw.rect(screen, config.COLOR_BLUE, button_rect, 2)
            text_color = config.COLOR_WHITE
        
        # Draw text
        text_surface = self.menu_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
    
    def _draw_form_button(self, screen: pygame.Surface, text: str, y: int, button_type: str) -> None:
        """Draw a clickable button for forms."""
        button_width = 200
        button_height = 50
        button_rect = pygame.Rect(
            config.SCREEN_WIDTH // 2 - button_width // 2,
            y - button_height // 2,
            button_width,
            button_height
        )
        
        # Store rectangle for click detection
        if button_type == "submit":
            self.submit_button_rect = button_rect
        elif button_type == "back":
            self.back_button_rect = button_rect
        
        # Check if mouse is hovering
        is_hovering = button_rect.collidepoint(self.mouse_pos)
        
        # Draw button
        if button_type == "submit":
            if is_hovering:
                pygame.draw.rect(screen, config.COLOR_GREEN, button_rect)
                pygame.draw.rect(screen, config.COLOR_WHITE, button_rect, 3)
                text_color = config.COLOR_WHITE
            else:
                pygame.draw.rect(screen, config.COLOR_BLACK, button_rect)
                pygame.draw.rect(screen, config.COLOR_GREEN, button_rect, 2)
                text_color = config.COLOR_GREEN
        else:  # back button
            if is_hovering:
                pygame.draw.rect(screen, config.COLOR_GRAY, button_rect)
                pygame.draw.rect(screen, config.COLOR_WHITE, button_rect, 3)
                text_color = config.COLOR_WHITE
            else:
                pygame.draw.rect(screen, config.COLOR_BLACK, button_rect)
                pygame.draw.rect(screen, config.COLOR_GRAY, button_rect, 2)
                text_color = config.COLOR_GRAY
        
        # Draw text
        text_surface = self.button_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

    def exit(self) -> None:
        """Called when exiting this state."""
        logger.info("Exiting LoginState")

