#!/usr/bin/env python3
"""
VoidRunner - 2D Space Survival Shooter

Main entry point for the game.

Usage:
    python main.py [--debug]
"""

import argparse
import sys
from pathlib import Path

# Add the voidrunner package to path
sys.path.insert(0, str(Path(__file__).parent))

from voidrunner.game import main as game_main
from voidrunner.utils import config


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="VoidRunner - 2D Space Survival Shooter"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (shows FPS, collision boxes, etc.)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    # Set debug mode from command line
    if args.debug:
        config.DEBUG_MODE = True
        config.SHOW_FPS = True
        config.SHOW_COLLISION_BOXES = True
        print("Debug mode enabled")
    
    # Run the game
    game_main()

