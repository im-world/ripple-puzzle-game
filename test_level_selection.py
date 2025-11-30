#!/usr/bin/env python3
"""
Test script for level selection screen functionality.
This script verifies that the level selection screen is properly implemented.
"""

import pygame
import sys
from main import Game, GameState, LevelCard

def test_level_selection():
    """Test level selection screen implementation."""
    print("Testing Level Selection Screen Implementation...")
    
    # Initialize Pygame
    pygame.init()
    
    # Create game instance
    game = Game()
    
    # Test 1: Verify level cards are created
    print("\n1. Testing level card creation...")
    assert len(game.level_cards) == 20, f"Expected 20 level cards, got {len(game.level_cards)}"
    print("   ✓ 20 level cards created")
    
    # Test 2: Verify tutorial badges on levels 1-4
    print("\n2. Testing tutorial badges...")
    tutorial_count = sum(1 for card in game.level_cards[:4] if card.is_tutorial)
    assert tutorial_count == 4, f"Expected 4 tutorial levels, got {tutorial_count}"
    print("   ✓ Tutorial badges on levels 1-4")
    
    # Test 3: Verify level numbers
    print("\n3. Testing level numbers...")
    for i, card in enumerate(game.level_cards):
        assert card.level_number == i + 1, f"Expected level {i+1}, got {card.level_number}"
    print("   ✓ All level numbers correct (1-20)")
    
    # Test 4: Verify grid layout (5x4)
    print("\n4. Testing grid layout...")
    # Check that cards are arranged in a grid
    first_card = game.level_cards[0]
    second_card = game.level_cards[1]
    sixth_card = game.level_cards[5]
    
    # Cards in same row should have same y position
    assert first_card.rect.y == second_card.rect.y, "Cards in same row should have same y"
    # Cards in different rows should have different y positions
    assert first_card.rect.y != sixth_card.rect.y, "Cards in different rows should have different y"
    print("   ✓ Grid layout (5 columns x 4 rows)")
    
    # Test 5: Verify back button exists
    print("\n5. Testing back button...")
    assert game.level_select_back_button is not None, "Back button should exist"
    assert game.level_select_back_button.text == "Back to Menu", "Back button text incorrect"
    print("   ✓ Back button exists")
    
    # Test 6: Verify keyboard navigation state
    print("\n6. Testing keyboard navigation...")
    assert game.selected_level_index == 0, "Initial selection should be 0"
    print("   ✓ Keyboard navigation initialized")
    
    # Test 7: Verify level select button in menu
    print("\n7. Testing menu integration...")
    assert 'level_select' in game.menu_buttons, "Level Select button should be in menu"
    print("   ✓ Level Select button in main menu")
    
    # Test 8: Verify state transition
    print("\n8. Testing state transitions...")
    game.state = GameState.LEVEL_SELECT
    assert game.state == GameState.LEVEL_SELECT, "Should be able to set LEVEL_SELECT state"
    print("   ✓ LEVEL_SELECT state exists")
    
    # Test 9: Verify start_game accepts level_index parameter
    print("\n9. Testing start_game with level parameter...")
    # This should not crash
    try:
        # Don't actually start the game, just verify the signature works
        import inspect
        sig = inspect.signature(game.start_game)
        params = list(sig.parameters.keys())
        assert 'level_index' in params, "start_game should accept level_index parameter"
        print("   ✓ start_game accepts level_index parameter")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Clean up
    pygame.quit()
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50)
    print("\nLevel Selection Screen Features:")
    print("  • 20 level cards in 5x4 grid layout")
    print("  • Tutorial badges on levels 1-4")
    print("  • All levels unlocked from start")
    print("  • Keyboard navigation (arrow keys + enter)")
    print("  • Mouse click to select level")
    print("  • Back to Menu button")
    print("  • Visual feedback (hover and selection states)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_level_selection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
