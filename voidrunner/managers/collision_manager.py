"""
Collision detection manager.

Handles all collision detection between game entities.
"""

import pygame

from ..utils import config


class CollisionManager:
    """
    Manages collision detection between sprite groups.

    Uses pygame's optimized group collision methods for performance.
    """

    def __init__(self, asset_manager) -> None:
        """
        Initialize the collision manager.

        Args:
            asset_manager: Reference to AssetManager for sound effects
        """
        self.asset_manager = asset_manager
        self.score = 0

    def check_player_bullet_enemy_collisions(
        self,
        player_bullets: pygame.sprite.Group,
        enemies: pygame.sprite.Group,
        player,
    ) -> int:
        """
        Check collisions between player bullets and enemies.

        Args:
            player_bullets: Group of player bullet sprites
            enemies: Group of enemy sprites
            player: Player object (for streak tracking)

        Returns:
            Points earned from destroyed enemies
        """
        points_earned = 0
        
        # Check collisions (remove both bullet and enemy on hit)
        hits = pygame.sprite.groupcollide(
            player_bullets, enemies, True, False
        )
        
        for bullet, hit_enemies in hits.items():
            for enemy in hit_enemies:
                # Apply damage
                if enemy.take_damage(bullet.damage):
                    # Enemy died
                    enemy.kill()
                    
                    # Award points
                    base_points = enemy.score_value
                    
                    # Apply streak bonus
                    if player.kill_streak >= config.STREAK_BONUS_THRESHOLD:
                        points_earned += int(base_points * config.STREAK_BONUS_MULTIPLIER)
                    else:
                        points_earned += base_points
                    
                    # Update player streak
                    player.add_kill_to_streak()
                    
                    # Play sound effect
                    self.asset_manager.play_sound("explosion")
        
        return points_earned

    def check_enemy_bullet_player_collisions(
        self,
        enemy_bullets: pygame.sprite.Group,
        player,
    ) -> bool:
        """
        Check collisions between enemy bullets and player.

        Args:
            enemy_bullets: Group of enemy bullet sprites
            player: Player sprite

        Returns:
            True if player was hit and died
        """
        # Check collisions (remove bullet on hit)
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        
        if hits and not player.invincible:
            # Player was hit - deal proper enemy bullet damage
            player_died = player.take_damage(config.ENEMY_BULLET_DAMAGE)
            self.asset_manager.play_sound("player_hit")
            return player_died
        
        return False

    def check_enemy_player_collisions(
        self,
        enemies: pygame.sprite.Group,
        player,
    ) -> bool:
        """
        Check collisions between enemies and player (ramming).

        Args:
            enemies: Group of enemy sprites
            player: Player sprite

        Returns:
            True if player was hit and died
        """
        # Check collisions (remove enemy on collision)
        hits = pygame.sprite.spritecollide(player, enemies, True)
        
        if hits and not player.invincible:
            # Player was hit by enemy - ramming does more damage
            player_died = player.take_damage(config.ENEMY_BULLET_DAMAGE * 1.5)
            self.asset_manager.play_sound("player_hit")
            self.asset_manager.play_sound("explosion")
            return player_died
        
        return False

    def check_all_collisions(
        self,
        player,
        player_bullets: pygame.sprite.Group,
        enemies: pygame.sprite.Group,
        enemy_bullets: pygame.sprite.Group,
    ) -> tuple[int, bool]:
        """
        Check all collision types in one call.

        Args:
            player: Player sprite
            player_bullets: Group of player bullet sprites
            enemies: Group of enemy sprites
            enemy_bullets: Group of enemy bullet sprites

        Returns:
            Tuple of (points_earned, player_died)
        """
        points = self.check_player_bullet_enemy_collisions(player_bullets, enemies, player)
        
        died1 = self.check_enemy_bullet_player_collisions(enemy_bullets, player)
        died2 = self.check_enemy_player_collisions(enemies, player)
        
        player_died = died1 or died2
        
        return points, player_died

