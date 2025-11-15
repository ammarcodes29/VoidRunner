"""
Unit tests for Enemy classes.

Tests enemy behavior, movement, damage, and shooting.
"""

import pytest
import pygame

from voidrunner.entities.enemies.basic_enemy import BasicEnemy
from voidrunner.utils import config


class TestBasicEnemyInitialization:
    """Test BasicEnemy initialization."""

    def test_enemy_initializes_with_correct_position(self, basic_enemy_instance):
        """Enemy should initialize at the specified position."""
        assert basic_enemy_instance.position.x == 400
        assert basic_enemy_instance.position.y == 100

    def test_enemy_initializes_with_correct_health(self, basic_enemy_instance):
        """Enemy should start with configured health."""
        assert basic_enemy_instance.health == config.BASIC_ENEMY_HEALTH
        assert basic_enemy_instance.max_health == config.BASIC_ENEMY_HEALTH

    def test_enemy_initializes_with_correct_score_value(self, basic_enemy_instance):
        """Enemy should have correct point value."""
        assert basic_enemy_instance.score_value == config.BASIC_ENEMY_POINTS

    def test_basic_enemy_can_shoot(self, basic_enemy_instance):
        """BasicEnemy should be able to shoot."""
        assert basic_enemy_instance.can_shoot is True


class TestBasicEnemyMovement:
    """Test BasicEnemy movement behavior."""

    def test_basic_enemy_moves_downward(self, basic_enemy_instance):
        """BasicEnemy should move straight down."""
        initial_y = basic_enemy_instance.position.y
        player_pos = pygame.Vector2(400, 500)
        
        basic_enemy_instance.update(1.0, player_pos)
        
        # Should move down (positive Y)
        assert basic_enemy_instance.position.y > initial_y

    def test_basic_enemy_velocity_is_downward(self, basic_enemy_instance):
        """BasicEnemy velocity should be positive Y."""
        assert basic_enemy_instance.velocity.x == 0
        assert basic_enemy_instance.velocity.y > 0


class TestEnemyDamage:
    """Test enemy damage mechanics."""

    def test_take_damage_reduces_health(self, basic_enemy_instance):
        """Taking damage should reduce enemy health."""
        initial_health = basic_enemy_instance.health
        
        basic_enemy_instance.take_damage(1)
        
        assert basic_enemy_instance.health < initial_health

    def test_take_damage_returns_true_when_health_depleted(self, basic_enemy_instance):
        """take_damage should return True when enemy dies."""
        basic_enemy_instance.health = 1
        
        died = basic_enemy_instance.take_damage(1)
        
        assert died is True
        assert basic_enemy_instance.health <= 0

    def test_take_damage_returns_false_when_enemy_survives(self, basic_enemy_instance):
        """take_damage should return False when enemy survives."""
        basic_enemy_instance.health = 10
        
        died = basic_enemy_instance.take_damage(1)
        
        assert died is False
        assert basic_enemy_instance.health > 0


class TestEnemyShooting:
    """Test enemy shooting mechanics."""

    def test_enemy_creates_bullet_moving_down(self, basic_enemy_instance, mock_bullet_sprite):
        """Enemy bullet should move downward."""
        bullet = basic_enemy_instance.create_bullet(mock_bullet_sprite)
        
        assert bullet is not None
        assert bullet.owner == "enemy"
        assert bullet.velocity.y > 0  # Moving down

    def test_should_shoot_respects_cooldown(self, basic_enemy_instance):
        """Enemy should not shoot during cooldown."""
        basic_enemy_instance.shoot_timer = 1.0
        
        assert basic_enemy_instance.should_shoot() is False


class TestEnemyDespawning:
    """Test enemy off-screen despawning."""

    def test_enemy_despawns_when_below_screen(self, basic_enemy_instance):
        """Enemy should despawn when far below screen."""
        basic_enemy_instance.position.y = config.SCREEN_HEIGHT + 100
        basic_enemy_instance.rect.center = (
            int(basic_enemy_instance.position.x),
            int(basic_enemy_instance.position.y),
        )
        
        assert basic_enemy_instance._is_off_screen() is True

    def test_enemy_does_not_despawn_on_screen(self, basic_enemy_instance):
        """Enemy should not despawn while on screen."""
        basic_enemy_instance.position.y = config.SCREEN_HEIGHT // 2
        basic_enemy_instance.rect.center = (
            int(basic_enemy_instance.position.x),
            int(basic_enemy_instance.position.y),
        )
        
        assert basic_enemy_instance._is_off_screen() is False

