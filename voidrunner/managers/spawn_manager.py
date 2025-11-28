"""
Spawn manager for enemy wave generation.

Handles wave-based enemy spawning with difficulty scaling.
"""

import random

import pygame

from ..entities.enemies.basic_enemy import BasicEnemy
from ..utils import config, helpers


class SpawnManager:
    """
    Manages enemy spawning based on wave progression.

    Increases spawn rate and enemy count as waves progress.
    """

    def __init__(self, asset_manager) -> None:
        """
        Initialize the spawn manager.

        Args:
            asset_manager: Reference to AssetManager for loading sprites
        """
        self.asset_manager = asset_manager
        
        self.current_wave = 1
        self.enemies_spawned_this_wave = 0
        self.max_kills_this_wave = config.ENEMIES_PER_WAVE_BASE
        self.enemies_killed_this_wave = 0
        
        self.spawn_timer = 0.0
        self.spawn_interval = config.ENEMY_SPAWN_RATE_BASE
        
        self.max_alive = config.ENEMIES_ON_SCREEN_MAX
        # self.wave_complete = False

    def update(self, dt: float, enemy_group: pygame.sprite.Group) -> None:
        """
        Update spawn timer and create enemies.

        Args:
            dt: Delta time in seconds
            enemy_group: Sprite group to add new enemies to
        """
        if self.enemies_killed_this_wave >= self.max_kills_this_wave:
            return
        
        # Update spawn timer
        self.spawn_timer += dt

        alive_enemies = len(enemy_group)
        
        can_spawn = (alive_enemies < self.max_alive and self.enemies_killed_this_wave < self.max_kills_this_wave)
        # Check if it's time to spawn
        if not can_spawn:
            return

        if (self.spawn_timer >= self.spawn_interval):
            self.spawn_timer = 0.0
            self._spawn_enemy(enemy_group)
            self.enemies_spawned_this_wave += 1

        # if self.spawn_timer >= self.spawn_interval:
        #     self.spawn_timer = 0.0
            
        #     # Spawn enemy if we haven't reached the wave limit
        #     if self.enemies_spawned_this_wave < self.max_kills_this_wave:
        #         self._spawn_enemy(enemy_group)
        #         self.enemies_spawned_this_wave += 1


        #     # Check if wave is complete
        #     if self.enemies_spawned_this_wave >= self.max_kills_this_wave:
        #         self.wave_complete = True

    def _spawn_enemy(self, enemy_group: pygame.sprite.Group) -> None:
        """
        Spawn a single enemy at the top of the screen.

        Args:
            enemy_group: Sprite group to add the enemy to
        """
        # Random position at top of screen
        x = random.uniform(50, config.SCREEN_WIDTH - 50)
        y = -50
        
        # For now, only spawn basic enemies
        # TODO: Add other enemy types in later phases
        sprite = self.asset_manager.get_sprite("basic_enemy")
        enemy = BasicEnemy(x, y, sprite)
        
        enemy_group.add(enemy)

    def advance_wave(self) -> None:
        """
        Progress to the next wave with increased difficulty.
        """
        self.current_wave += 1
        self.enemies_killed_this_wave = 0
        
        # Increase enemies per wave
        self.max_kills_this_wave = (
            config.ENEMIES_PER_WAVE_BASE
            + (self.current_wave - 1) * config.ENEMIES_PER_WAVE_INCREMENT
        )
        
        # Decrease spawn interval (faster spawning)
        self.spawn_interval = config.ENEMY_SPAWN_RATE_BASE / (
            config.WAVE_DIFFICULTY_MULTIPLIER ** (self.current_wave - 1)
        )
        
        # Ensure minimum spawn rate
        self.spawn_interval = max(0.5, self.spawn_interval)
        
        # Reset wave state
        self.enemies_spawned_this_wave = 0
        # self.wave_complete = False
        self.spawn_timer = 0.0

    def is_wave_complete(self, enemy_group: pygame.sprite.Group) -> bool:
        """
        Check if the current wave is complete.

        A wave is complete when all enemies have been spawned AND
        all spawned enemies have been destroyed.

        Args:
            enemy_group: Sprite group containing active enemies

        Returns:
            True if wave is complete
        """
        return self.enemies_killed_this_wave >= self.max_kills_this_wave 

    def get_wave_number(self) -> int:
        """
        Get the current wave number.

        Returns:
            Current wave number
        """
        return self.current_wave

    def register_enemy_killed(self):
        self.enemies_killed_this_wave += 1