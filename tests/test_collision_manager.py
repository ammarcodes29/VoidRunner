"""
Unit tests for CollisionManager.

Tests collision detection between bullets, enemies, and player.
"""

import pytest
import pygame
from unittest.mock import Mock, MagicMock

from voidrunner.managers.collision_manager import CollisionManager
from voidrunner.entities.bullet import Bullet
from voidrunner.entities.enemies.basic_enemy import BasicEnemy
from voidrunner.utils import config


@pytest.fixture
def collision_manager():
    """Create a CollisionManager instance with mocked asset manager."""
    mock_asset_manager = Mock()
    mock_asset_manager.play_sound = Mock()
    return CollisionManager(mock_asset_manager)


@pytest.fixture
def player_with_sprite(mock_sprite, mock_bullet_sprite):
    """Create a player instance for collision testing."""
    from voidrunner.entities.player import Player
    return Player(400, 500, mock_sprite, mock_bullet_sprite)


class TestPlayerBulletEnemyCollisions:
    """Test collisions between player bullets and enemies."""

    def test_bullet_hitting_enemy_awards_points(
        self, collision_manager, player_with_sprite, mock_sprite, mock_bullet_sprite
    ):
        """Player bullet hitting enemy should award points."""
        # Create sprite groups
        player_bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        
        # Create enemy
        enemy = BasicEnemy(400, 300, mock_sprite)
        enemies.add(enemy)
        
        # Create bullet at same position
        bullet = Bullet(400, 300, pygame.Vector2(0, -8), "player", mock_bullet_sprite)
        player_bullets.add(bullet)
        
        # Check collision
        points = collision_manager.check_player_bullet_enemy_collisions(
            player_bullets, enemies, player_with_sprite
        )
        
        # Should award points equal to enemy value
        assert points == config.BASIC_ENEMY_POINTS

    def test_bullet_hitting_enemy_destroys_both(
        self, collision_manager, player_with_sprite, mock_sprite, mock_bullet_sprite
    ):
        """Bullet and enemy should both be destroyed on collision."""
        player_bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        
        enemy = BasicEnemy(400, 300, mock_sprite)
        enemies.add(enemy)
        
        bullet = Bullet(400, 300, pygame.Vector2(0, -8), "player", mock_bullet_sprite)
        player_bullets.add(bullet)
        
        collision_manager.check_player_bullet_enemy_collisions(
            player_bullets, enemies, player_with_sprite
        )
        
        # Both should be removed from groups
        assert len(player_bullets) == 0
        assert len(enemies) == 0

    def test_killing_enemy_increments_player_streak(
        self, collision_manager, player_with_sprite, mock_sprite, mock_bullet_sprite
    ):
        """Killing an enemy should increment player kill streak."""
        player_bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        
        enemy = BasicEnemy(400, 300, mock_sprite)
        enemies.add(enemy)
        
        bullet = Bullet(400, 300, pygame.Vector2(0, -8), "player", mock_bullet_sprite)
        player_bullets.add(bullet)
        
        initial_streak = player_with_sprite.kill_streak
        
        collision_manager.check_player_bullet_enemy_collisions(
            player_bullets, enemies, player_with_sprite
        )
        
        assert player_with_sprite.kill_streak == initial_streak + 1

    def test_streak_bonus_applies_at_threshold(
        self, collision_manager, player_with_sprite, mock_sprite, mock_bullet_sprite
    ):
        """Streak bonus should apply when threshold is reached."""
        player_bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        
        # Set player streak above threshold
        player_with_sprite.kill_streak = config.STREAK_BONUS_THRESHOLD
        
        enemy = BasicEnemy(400, 300, mock_sprite)
        enemies.add(enemy)
        
        bullet = Bullet(400, 300, pygame.Vector2(0, -8), "player", mock_bullet_sprite)
        player_bullets.add(bullet)
        
        points = collision_manager.check_player_bullet_enemy_collisions(
            player_bullets, enemies, player_with_sprite
        )
        
        # Should award bonus points
        expected_points = int(
            config.BASIC_ENEMY_POINTS * config.STREAK_BONUS_MULTIPLIER
        )
        assert points == expected_points


class TestEnemyBulletPlayerCollisions:
    """Test collisions between enemy bullets and player."""

    def test_enemy_bullet_hitting_player_damages_player(
        self, collision_manager, player_with_sprite, mock_bullet_sprite
    ):
        """Enemy bullet should damage player on hit."""
        enemy_bullets = pygame.sprite.Group()
        
        # Create bullet at player position
        bullet = Bullet(
            player_with_sprite.rect.centerx,
            player_with_sprite.rect.centery,
            pygame.Vector2(0, 8),
            "enemy",
            mock_bullet_sprite,
        )
        enemy_bullets.add(bullet)
        
        initial_health = player_with_sprite.health
        
        collision_manager.check_enemy_bullet_player_collisions(
            enemy_bullets, player_with_sprite
        )
        
        # Player should take damage (health reduced)
        assert player_with_sprite.health < initial_health

    def test_enemy_bullet_hitting_player_removes_bullet(
        self, collision_manager, player_with_sprite, mock_bullet_sprite
    ):
        """Enemy bullet should be removed on hit."""
        enemy_bullets = pygame.sprite.Group()
        
        bullet = Bullet(
            player_with_sprite.rect.centerx,
            player_with_sprite.rect.centery,
            pygame.Vector2(0, 8),
            "enemy",
            mock_bullet_sprite,
        )
        enemy_bullets.add(bullet)
        
        collision_manager.check_enemy_bullet_player_collisions(
            enemy_bullets, player_with_sprite
        )
        
        # Bullet should be removed
        assert len(enemy_bullets) == 0

    def test_invincible_player_ignores_bullet(
        self, collision_manager, player_with_sprite, mock_bullet_sprite
    ):
        """Invincible player should not take damage from bullets."""
        player_with_sprite.invincible = True
        initial_health = player_with_sprite.health
        
        enemy_bullets = pygame.sprite.Group()
        bullet = Bullet(
            player_with_sprite.rect.centerx,
            player_with_sprite.rect.centery,
            pygame.Vector2(0, 8),
            "enemy",
            mock_bullet_sprite,
        )
        enemy_bullets.add(bullet)
        
        collision_manager.check_enemy_bullet_player_collisions(
            enemy_bullets, player_with_sprite
        )
        
        # Health should not change
        assert player_with_sprite.health == initial_health


class TestEnemyPlayerCollisions:
    """Test collisions between enemies and player (ramming)."""

    def test_enemy_ramming_player_damages_player(
        self, collision_manager, player_with_sprite, mock_sprite
    ):
        """Enemy ramming player should damage player."""
        enemies = pygame.sprite.Group()
        
        # Create enemy at player position
        enemy = BasicEnemy(
            player_with_sprite.rect.centerx,
            player_with_sprite.rect.centery,
            mock_sprite,
        )
        enemies.add(enemy)
        
        initial_health = player_with_sprite.health
        
        collision_manager.check_enemy_player_collisions(enemies, player_with_sprite)
        
        # Player should take damage
        assert player_with_sprite.health < initial_health

    def test_enemy_ramming_player_destroys_enemy(
        self, collision_manager, player_with_sprite, mock_sprite
    ):
        """Enemy should be destroyed when ramming player."""
        enemies = pygame.sprite.Group()
        
        enemy = BasicEnemy(
            player_with_sprite.rect.centerx,
            player_with_sprite.rect.centery,
            mock_sprite,
        )
        enemies.add(enemy)
        
        collision_manager.check_enemy_player_collisions(enemies, player_with_sprite)
        
        # Enemy should be removed
        assert len(enemies) == 0

