"""
Unit tests for Player class.

Tests player movement, shooting, damage, and health management.
"""

import pytest
import pygame

from voidrunner.entities.player import Player
from voidrunner.utils import config


class TestPlayerInitialization:
    """Test player initialization."""

    def test_player_initializes_with_correct_position(self, player_instance):
        """Player should initialize at the specified position."""
        assert player_instance.position.x == 400
        assert player_instance.position.y == 300

    def test_player_initializes_with_max_lives(self, player_instance):
        """Player should start with maximum lives."""
        assert player_instance.lives == config.PLAYER_MAX_LIVES
        assert player_instance.max_lives == config.PLAYER_MAX_LIVES

    def test_player_initializes_with_max_health(self, player_instance):
        """Player should start with maximum health."""
        assert player_instance.health == config.PLAYER_MAX_HEALTH
        assert player_instance.max_health == config.PLAYER_MAX_HEALTH

    def test_player_initializes_not_invincible(self, player_instance):
        """Player should not be invincible at start."""
        assert player_instance.invincible is False
        assert player_instance.invincibility_timer == 0.0


class TestPlayerMovement:
    """Test player movement mechanics."""

    def _create_key_state(self, pressed_keys):
        """Create a mock key state object that behaves like pygame.key.get_pressed()."""
        class MockKeyState:
            def __init__(self, pressed):
                self.pressed = pressed
            
            def __getitem__(self, key):
                return self.pressed.get(key, False)
        
        return MockKeyState(pressed_keys)

    def test_player_moves_up(self, player_instance):
        """Player should move up when W or UP is pressed."""
        keys = self._create_key_state({pygame.K_w: True})
        
        player_instance._handle_movement(1.0, keys)
        
        # Should move up (negative Y)
        assert player_instance.velocity.y < 0

    def test_player_moves_down(self, player_instance):
        """Player should move down when S or DOWN is pressed."""
        keys = self._create_key_state({pygame.K_s: True})
        
        player_instance._handle_movement(1.0, keys)
        
        # Should move down (positive Y)
        assert player_instance.velocity.y > 0

    def test_player_moves_left(self, player_instance):
        """Player should move left when A or LEFT is pressed."""
        keys = self._create_key_state({pygame.K_a: True})
        
        player_instance._handle_movement(1.0, keys)
        
        # Should move left (negative X)
        assert player_instance.velocity.x < 0

    def test_player_moves_right(self, player_instance):
        """Player should move right when D or RIGHT is pressed."""
        keys = self._create_key_state({pygame.K_d: True})
        
        player_instance._handle_movement(1.0, keys)
        
        # Should move right (positive X)
        assert player_instance.velocity.x > 0

    def test_player_stays_within_screen_bounds(self, player_instance):
        """Player should not move outside screen boundaries."""
        # Move to left edge
        player_instance.position.x = 0
        player_instance._constrain_to_screen()
        assert player_instance.position.x >= player_instance.rect.width // 2

        # Move to right edge
        player_instance.position.x = config.SCREEN_WIDTH + 100
        player_instance._constrain_to_screen()
        assert player_instance.position.x <= config.SCREEN_WIDTH - player_instance.rect.width // 2

        # Move to top edge
        player_instance.position.y = 0
        player_instance._constrain_to_screen()
        assert player_instance.position.y >= player_instance.rect.height // 2

        # Move to bottom edge
        player_instance.position.y = config.SCREEN_HEIGHT + 100
        player_instance._constrain_to_screen()
        assert player_instance.position.y <= config.SCREEN_HEIGHT - player_instance.rect.height // 2


class TestPlayerShooting:
    """Test player shooting mechanics."""

    def test_player_can_shoot_initially(self, player_instance):
        """Player should be able to shoot at start."""
        assert player_instance.can_shoot() is True

    def test_player_cannot_shoot_during_cooldown(self, player_instance):
        """Player should not be able to shoot during cooldown."""
        # Shoot once
        player_instance.shoot()
        assert player_instance.can_shoot() is False

    def test_shoot_creates_bullet(self, player_instance):
        """Shooting should create a bullet moving upward."""
        bullet = player_instance.shoot()
        
        assert bullet is not None
        assert bullet.owner == "player"
        assert bullet.velocity.y < 0  # Moving upward

    def test_cooldown_decreases_over_time(self, player_instance):
        """Shoot cooldown should decrease with delta time."""
        player_instance.shoot()
        initial_cooldown = player_instance.shoot_cooldown
        
        player_instance._update_shooting_cooldown(0.1)
        
        assert player_instance.shoot_cooldown < initial_cooldown


class TestPlayerDamage:
    """Test player damage and health mechanics."""

    def test_take_damage_reduces_health(self, player_instance):
        """Damage should reduce health."""
        initial_health = player_instance.health
        initial_lives = player_instance.lives
        
        player_instance.take_damage(25)
        
        assert player_instance.health < initial_health
        assert player_instance.lives == initial_lives  # Should not lose life yet

    def test_take_damage_loses_life_when_health_depleted(self, player_instance):
        """Should lose a life when health is depleted."""
        initial_lives = player_instance.lives
        
        # Deplete all health
        player_instance.take_damage(100)
        
        assert player_instance.lives < initial_lives
        assert player_instance.health == config.PLAYER_MAX_HEALTH  # Health resets

    def test_take_damage_triggers_invincibility(self, player_instance):
        """Taking damage should trigger invincibility frames."""
        player_instance.take_damage(1)
        
        assert player_instance.invincible is True
        assert player_instance.invincibility_timer > 0

    def test_invincible_player_ignores_damage(self, player_instance):
        """Invincible player should not take damage."""
        player_instance.invincible = True
        initial_health = player_instance.health
        initial_lives = player_instance.lives
        
        player_instance.take_damage(100)
        
        assert player_instance.health == initial_health
        assert player_instance.lives == initial_lives

    def test_take_damage_returns_true_when_all_lives_lost(self, player_instance):
        """take_damage should return True when all lives are lost."""
        player_instance.lives = 1
        player_instance.health = 1
        
        died = player_instance.take_damage(50)
        
        assert died is True
        assert player_instance.lives == 0

    def test_take_damage_resets_kill_streak(self, player_instance):
        """Taking damage should reset kill streak."""
        player_instance.kill_streak = 10
        
        player_instance.take_damage(1)
        
        assert player_instance.kill_streak == 0

    def test_is_alive_returns_true_with_lives(self, player_instance):
        """is_alive should return True when lives > 0."""
        assert player_instance.is_alive() is True

    def test_is_alive_returns_false_without_lives(self, player_instance):
        """is_alive should return False when lives <= 0."""
        player_instance.lives = 0
        assert player_instance.is_alive() is False


class TestPlayerKillStreak:
    """Test kill streak mechanics."""

    def test_kill_streak_increments(self, player_instance):
        """Kill streak should increment when enemy is killed."""
        initial_streak = player_instance.kill_streak
        
        player_instance.add_kill_to_streak()
        
        assert player_instance.kill_streak == initial_streak + 1

    def test_kill_streak_starts_at_zero(self, player_instance):
        """Kill streak should start at 0."""
        assert player_instance.kill_streak == 0


class TestPlayerHealthRegen:
    """Test health regeneration."""

    def test_health_does_not_regen_immediately(self, player_instance):
        """Health should not regenerate immediately after damage."""
        player_instance.health = 50
        player_instance.time_since_damage = 0.0
        
        player_instance._update_health_regen(1.0)
        
        # Should not regen yet (need 5 seconds delay)
        assert player_instance.health == 50

    def test_health_does_not_exceed_max(self, player_instance):
        """Health should not regenerate beyond max."""
        player_instance.health = config.PLAYER_MAX_HEALTH
        player_instance.time_since_damage = 10.0
        
        player_instance._update_health_regen(10.0)
        
        assert player_instance.health == config.PLAYER_MAX_HEALTH

