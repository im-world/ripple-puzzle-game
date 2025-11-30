#!/usr/bin/env python3
"""
Manual test for Zen Mode - launches the game for visual verification.
Instructions:
1. Click "Start Game" to begin
2. Look for the "Zen Mode" checkbox in the top-right corner
3. Click the checkbox to enable Zen Mode
4. Verify the stone counter shows "∞" symbol
5. Launch stones and verify they are not deducted
6. Complete the level and verify "Peace" rating is shown instead of stars
"""

import pygame
import sys
from main import Game

def main():
    """Launch game for manual Zen Mode testing."""
    print("=" * 60)
    print("ZEN MODE MANUAL TEST")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Click 'Start Game' to begin")
    print("2. Look for 'Zen Mode' checkbox in top-right corner")
    print("3. Click checkbox to enable Zen Mode")
    print("4. Verify stone counter shows '∞' symbol")
    print("5. Launch stones - they should NOT be deducted")
    print("6. Complete level - should show 'Peace' rating")
    print("\nPress ESC to exit the game")
    print("=" * 60)
    
    input("\nPress Enter to start the game...")
    
    game = Game()
    game.run()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
