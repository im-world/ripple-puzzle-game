#!/usr/bin/env python3
"""
Demo script to showcase the level selection screen.
Run this to see the level selection UI in action.
"""

import pygame
import sys
from main import Game, GameState

def demo_level_selection():
    """Demo the level selection screen."""
    print("="*60)
    print("Level Selection Screen Demo")
    print("="*60)
    print("\nStarting game in Level Selection mode...")
    print("\nControls:")
    print("  • Click any level card to start that level")
    print("  • Use Arrow Keys to navigate between levels")
    print("  • Press Enter/Space to start selected level")
    print("  • Click 'Back to Menu' to return to main menu")
    print("  • Press ESC to exit")
    print("\nFeatures to observe:")
    print("  ✓ 20 level cards in 5x4 grid")
    print("  ✓ Tutorial badges on levels 1-4 (yellow)")
    print("  ✓ Hover effects on cards")
    print("  ✓ Selection highlight (keyboard navigation)")
    print("  ✓ All levels unlocked from start")
    print("\n" + "="*60)
    
    # Create and run game
    game = Game()
    
    # Jump directly to level selection screen
    game.state = GameState.LEVEL_SELECT
    
    # Run the game
    game.run()

if __name__ == "__main__":
    demo_level_selection()
