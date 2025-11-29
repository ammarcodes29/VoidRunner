"""
Tests for Boss Enemy mechanics.

Tests boss spawning, health scaling, penta-shot, and reward system.
"""

import pygame
import pytest

from voidrunner.entities.enemies.boss_enemy import BossEnemy
from voidrunner.managers.spawn_manager import SpawnManager
from voidrunner.utils import config


class TestBossEnemy:
    """Test suite for boss enemy functionality."""

    @pytest.fixture
    def boss_sprite(self):
        """Create a test sprite for boss."""
        pygame.init()
        return pygame.Surface((64, 64))

    def test_boss_initialization(self, boss_sprite):
        """Test boss enemy initializes with correct attributes."""
        boss = BossEnemy(400, 100, boss_sprite, boss_level=1)
        
        assert boss.health == config.BOSS_BASE_HEALTH
        assert boss.boss_level == 1
        assert boss.can_shoot is True
        assert boss.score_value == config.BOSS_POINTS
        
        # Boss should be larger than normal enemy
        assert boss.image.get_width() > boss_sprite.get_width()
        assert boss.image.get_height() > boss_sprite.get_height()

    def test_boss_health_scaling(self, boss_sprite):
        """Test boss health increases with each level."""
        boss1 = BossEnemy(400, 100, boss_sprite, boss_level=1)
        boss2 = BossEnemy(400, 100, boss_sprite, boss_level=2)
        boss3 = BossEnemy(400, 100, boss_sprite, boss_level=3)
        
        assert boss2.health > boss1.health
        assert boss3.health > boss2.health
        
        # Verify the multiplier is applied correctly
        expected_health_2 = int(config.BOSS_BASE_HEALTH * config.BOSS_HEALTH_MULTIPLIER)
        assert boss2.health == expected_health_2

    def test_boss_fire_rate_scaling(self, boss_sprite):
        """Test boss fire rate increases (shoots faster) with each level."""
        boss1 = BossEnemy(400, 100, boss_sprite, boss_level=1)
        boss2 = BossEnemy(400, 100, boss_sprite, boss_level=2)
        
        # Lower fire rate = faster shooting
        assert boss2.fire_rate < boss1.fire_rate

    def test_boss_penta_shot(self, boss_sprite):
        """Test boss creates 5 bullets in fan pattern."""
        boss = BossEnemy(400, 100, boss_sprite, boss_level=1)
        bullet_sprite = pygame.Surface((8, 8))
        
        bullets = boss.create_penta_shot(bullet_sprite)
        
        assert len(bullets) == config.BOSS_BULLET_COUNT
        
        # Verify bullets have different angles
        velocities = [bullet.velocity for bullet in bullets]
        assert len(set((v.x, v.y) for v in velocities)) == len(bullets)

    def test_boss_bullet_speed_scaling(self, boss_sprite):
        """Test boss bullet speed increases with level."""
        boss1 = BossEnemy(400, 100, boss_sprite, boss_level=1)
        boss2 = BossEnemy(400, 100, boss_sprite, boss_level=2)
        
        assert boss2.bullet_speed_multiplier > boss1.bullet_speed_multiplier

    def test_boss_stays_at_top(self, boss_sprite):
        """Test boss locks to top of screen."""
        boss = BossEnemy(400, 50, boss_sprite, boss_level=1)
        player_pos = pygame.Vector2(200, 500)
        
        # Update boss behavior multiple times
        for _ in range(10):
            boss.update_behavior(0.016, player_pos)  # ~60 FPS
            boss.position += boss.velocity * 0.016 * 60
        
        # Boss should be near the top (around y=100)
        assert boss.position.y < 150

    def test_boss_follows_player_horizontally(self, boss_sprite):
        """Test boss tracks player's x position."""
        boss = BossEnemy(400, 100, boss_sprite, boss_level=1)
        player_pos = pygame.Vector2(200, 500)
        
        initial_x = boss.position.x
        
        # Update boss behavior
        for _ in range(30):
            boss.update_behavior(0.016, player_pos)
            boss.position += boss.velocity * 0.016 * 60
        
        # Boss should move toward player (x=200)
        assert boss.position.x < initial_x


class TestBossSpawning:
    """Test suite for boss spawning mechanics."""

    @pytest.fixture
    def mock_asset_manager(self):
        """Create mock asset manager."""
        class MockAssetManager:
            def get_sprite(self, name):
                pygame.init()
                return pygame.Surface((64, 64))
        
        return MockAssetManager()

    def test_boss_spawns_every_5_waves(self, mock_asset_manager):
        """Test boss spawns on waves 5, 10, 15, etc."""
        spawn_manager = SpawnManager(mock_asset_manager)
        
        # Wave 5 should be boss wave
        spawn_manager.current_wave = 5
        assert spawn_manager.is_boss_wave() is True
        
        # Wave 10 should be boss wave
        spawn_manager.current_wave = 10
        assert spawn_manager.is_boss_wave() is True
        
        # Wave 6 should NOT be boss wave
        spawn_manager.current_wave = 6
        assert spawn_manager.is_boss_wave() is False

    def test_boss_level_increments(self, mock_asset_manager):
        """Test boss level increases with each boss wave."""
        spawn_manager = SpawnManager(mock_asset_manager)
        enemy_group = pygame.sprite.Group()
        
        assert spawn_manager.boss_level == 0
        
        # Simulate boss wave
        spawn_manager.current_wave = 5
        spawn_manager._spawn_boss(enemy_group)
        assert spawn_manager.boss_level == 1
        
        # Simulate next boss wave
        spawn_manager.current_wave = 10
        spawn_manager._spawn_boss(enemy_group)
        assert spawn_manager.boss_level == 2

    def test_boss_only_spawns_once_per_wave(self, mock_asset_manager):
        """Test boss doesn't spawn multiple times in same wave."""
        spawn_manager = SpawnManager(mock_asset_manager)
        enemy_group = pygame.sprite.Group()
        
        spawn_manager.current_wave = 5
        
        # First update should spawn boss
        spawn_manager.update(0.016, enemy_group)
        initial_count = len(enemy_group)
        
        # Subsequent updates should not spawn more bosses
        spawn_manager.update(0.016, enemy_group)
        spawn_manager.update(0.016, enemy_group)
        
        assert len(enemy_group) == initial_count

