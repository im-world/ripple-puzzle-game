#!/usr/bin/env python3
"""
Test script for Zen Mode functionality.
Verifies that Zen Mode checkbox works correctly.
"""

import pygame
import sys
from main import Game, Checkbox

def test_checkbox_creation():
    """Test that Checkbox can be created."""
    pygame.init()
    checkbox = Checkbox(100, 100, 20, "Test Checkbox", checked=False)
    assert checkbox.x == 100
    assert checkbox.y == 100
    assert checkbox.size == 20
    assert checkbox.label == "Test Checkbox"
    assert checkbox.checked == False
    print("✓ Checkbox creation test passed")

def test_checkbox_toggle():
    """Test that Checkbox can be toggled."""
    pygame.init()
    checkbox = Checkbox(100, 100, 20, "Test Checkbox", checked=False)
    
    # Test toggle
    checkbox.toggle()
    assert checkbox.checked == True
    
    checkbox.toggle()
    assert checkbox.checked == False
    
    print("✓ Checkbox toggle test passed")

def test_checkbox_set_checked():
    """Test that Checkbox state can be set."""
    pygame.init()
    checkbox = Checkbox(100, 100, 20, "Test Checkbox", checked=False)
    
    checkbox.set_checked(True)
    assert checkbox.is_checked() == True
    
    checkbox.set_checked(False)
    assert checkbox.is_checked() == False
    
    print("✓ Checkbox set_checked test passed")

def test_zen_mode_initialization():
    """Test that Game initializes with Zen Mode checkbox."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    game = Game()
    
    # Check that zen_mode_checkbox exists
    assert hasattr(game, 'zen_mode_checkbox')
    assert isinstance(game.zen_mode_checkbox, Checkbox)
    assert game.zen_mode_checkbox.label == "Zen Mode"
    assert game.zen_mode == False
    
    print("✓ Zen Mode initialization test passed")
    
    pygame.quit()

def test_zen_mode_toggle():
    """Test that Zen Mode can be toggled."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    game = Game()
    
    # Toggle zen mode
    game.zen_mode_checkbox.toggle()
    game.zen_mode = game.zen_mode_checkbox.is_checked()
    
    assert game.zen_mode == True
    assert game.zen_mode_checkbox.is_checked() == True
    
    # Toggle back
    game.zen_mode_checkbox.toggle()
    game.zen_mode = game.zen_mode_checkbox.is_checked()
    
    assert game.zen_mode == False
    assert game.zen_mode_checkbox.is_checked() == False
    
    print("✓ Zen Mode toggle test passed")
    
    pygame.quit()

def main():
    """Run all tests."""
    print("Running Zen Mode tests...\n")
    
    try:
        test_checkbox_creation()
        test_checkbox_toggle()
        test_checkbox_set_checked()
        test_zen_mode_initialization()
        test_zen_mode_toggle()
        
        print("\n✓ All Zen Mode tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
