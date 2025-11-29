"""
Tests for different enemy types (Basic, Chaser, Zigzag).

Tests movement patterns and behaviors.
"""

import math
import pygame
import pytest

from voidrunner.entities.enemies.basic_enemy import BasicEnemy
from voidrunner.entities.enemies.chaser_enemy import ChaserEnemy
from voidrunner.entities.enemies.zigzag_enemy import ZigzagEnemy
from voidrunner.utils import config


class TestBasicEnemy:
    """Test suite for basic enemy."""

    @pytest.fixture
    def enemy_sprite(self):
        """Create test sprite."""
        pygame.init()
        return pygame.Surface((64, 64))

    def test_basic_enemy_moves_straight_down(self, enemy_sprite):
        """Test basic enemy moves only in downward direction."""
        enemy = BasicEnemy(400, 100, enemy_sprite)
        player_pos = pygame.Vector2(200, 500)
        
        initial_y = enemy.position.y
        initial_x = enemy.position.x
        
        # Update enemy
        for _ in range(10):
            enemy.update_behavior(0.016, player_pos)
            enemy.position += enemy.velocity * 0.016 * 60
        
        # Y should increase (move down)
        assert enemy.position.y > initial_y
        
        # X should not change significantly
        assert abs(enemy.position.x - initial_x) < 1.0

    def test_basic_enemy_can_shoot(self, enemy_sprite):
        """Test basic enemy has shooting enabled."""
        enemy = BasicEnemy(400, 100, enemy_sprite)
        assert enemy.can_shoot is True


class TestChaserEnemy:
    """Test suite for chaser enemy."""

    @pytest.fixture
    def enemy_sprite(self):
        """Create test sprite."""
        pygame.init()
        return pygame.Surface((64, 64))

    def test_chaser_follows_player(self, enemy_sprite):
        """Test chaser enemy moves toward player position."""
        enemy = ChaserEnemy(400, 100, enemy_sprite)
        player_pos = pygame.Vector2(200, 500)
        
        initial_distance = (enemy.position - player_pos).length()
        
        # Update enemy multiple times
        for _ in range(30):
            enemy.update_behavior(0.016, player_pos)
            enemy.position += enemy.velocity * 0.016 * 60
        
        final_distance = (enemy.position - player_pos).length()
        
        # Distance should decrease (moving closer to player)
        assert final_distance < initial_distance

    def test_chaser_has_oscillation(self, enemy_sprite):
        """Test chaser oscillates while chasing."""
        enemy = ChaserEnemy(400, 100, enemy_sprite)
        player_pos = pygame.Vector2(400, 500)  # Directly below
        
        x_positions = []
        
        # Track x positions over time
        for _ in range(60):
            enemy.update_behavior(0.016, player_pos)
            enemy.position += enemy.velocity * 0.016 * 60
            x_positions.append(enemy.position.x)
        
        # X should vary (oscillate), not stay constant
        assert max(x_positions) - min(x_positions) > 5.0

    def test_chaser_can_shoot(self, enemy_sprite):
        """Test chaser enemy has shooting enabled."""
        enemy = ChaserEnemy(400, 100, enemy_sprite)
        assert enemy.can_shoot is True


class TestZigzagEnemy:
    """Test suite for zigzag enemy."""

    @pytest.fixture
    def enemy_sprite(self):
        """Create test sprite."""
        pygame.init()
        return pygame.Surface((64, 64))

    def test_zigzag_moves_down(self, enemy_sprite):
        """Test zigzag enemy moves downward."""
        enemy = ZigzagEnemy(400, 100, enemy_sprite)
        player_pos = pygame.Vector2(200, 500)
        
        initial_y = enemy.position.y
        
        # Update enemy
        for _ in range(10):
            enemy.update_behavior(0.016, player_pos)
            enemy.position += enemy.velocity * 0.016 * 60
        
        # Y should increase (move down)
        assert enemy.position.y > initial_y

    def test_zigzag_oscillates_horizontally(self, enemy_sprite):
        """Test zigzag enemy oscillates left and right."""
        enemy = ZigzagEnemy(400, 100, enemy_sprite)
        player_pos = pygame.Vector2(200, 500)
        
        x_positions = []
        
        # Track x positions over time
        for _ in range(100):
            enemy.update_behavior(0.016, player_pos)
            enemy.position += enemy.velocity * 0.016 * 60
            x_positions.append(enemy.position.x)
        
        # X should oscillate (have both values above and below starting point)
        assert max(x_positions) > 400
        assert min(x_positions) < 400

    def test_zigzag_ignores_player_position(self, enemy_sprite):
        """Test zigzag movement doesn't track player."""
        enemy = ZigzagEnemy(400, 100, enemy_sprite)
        
        # Try two different player positions
        player_pos_left = pygame.Vector2(100, 500)
        player_pos_right = pygame.Vector2(700, 500)
        
        # Record movement with player on left
        positions_left = []
        for _ in range(50):
            enemy.update_behavior(0.016, player_pos_left)
            enemy.position += enemy.velocity * 0.016 * 60
            positions_left.append(enemy.position.x)
        
        # Reset enemy
        enemy2 = ZigzagEnemy(400, 100, enemy_sprite)
        enemy2.time_alive = 0
        
        # Record movement with player on right
        positions_right = []
        for _ in range(50):
            enemy2.update_behavior(0.016, player_pos_right)
            enemy2.position += enemy2.velocity * 0.016 * 60
            positions_right.append(enemy2.position.x)
        
        # Movement should be same regardless of player position
        assert positions_left == positions_right

    def test_zigzag_can_shoot(self, enemy_sprite):
        """Test zigzag enemy has shooting enabled."""
        enemy = ZigzagEnemy(400, 100, enemy_sprite)
        assert enemy.can_shoot is True


class TestEnemyDifficultyScaling:
    """Test suite for difficulty scaling on enemies."""

    @pytest.fixture
    def enemy_sprite(self):
        """Create test sprite."""
        pygame.init()
        return pygame.Surface((64, 64))

    def test_bullet_speed_multiplier(self, enemy_sprite):
        """Test enemies accept bullet speed multiplier."""
        enemy_normal = BasicEnemy(400, 100, enemy_sprite)
        enemy_scaled = BasicEnemy(400, 100, enemy_sprite, bullet_speed_multiplier=1.5)
        
        assert enemy_normal.bullet_speed_multiplier == 1.0
        assert enemy_scaled.bullet_speed_multiplier == 1.5

    def test_fire_rate_multiplier(self, enemy_sprite):
        """Test enemies accept fire rate multiplier."""
        enemy_normal = BasicEnemy(400, 100, enemy_sprite)
        enemy_scaled = BasicEnemy(400, 100, enemy_sprite, fire_rate_multiplier=0.8)
        
        assert enemy_normal.fire_rate_multiplier == 1.0
        assert enemy_scaled.fire_rate_multiplier == 0.8

    def test_scaled_bullets_faster(self, enemy_sprite):
        """Test scaled enemies create faster bullets."""
        enemy_normal = BasicEnemy(400, 100, enemy_sprite)
        enemy_scaled = BasicEnemy(400, 100, enemy_sprite, bullet_speed_multiplier=2.0)
        
        bullet_sprite = pygame.Surface((8, 8))
        
        bullet_normal = enemy_normal.create_bullet(bullet_sprite)
        bullet_scaled = enemy_scaled.create_bullet(bullet_sprite)
        
        # Scaled bullet should be faster
        assert bullet_scaled.velocity.length() > bullet_normal.velocity.length()

