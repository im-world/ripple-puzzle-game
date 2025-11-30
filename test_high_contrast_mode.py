#!/usr/bin/env python3
"""
Test script for high-contrast mode functionality.
Tests that high-contrast mode can be toggled and affects rendering colors.
"""

import pygame
import sys
from game.renderer import Renderer
from game.config import HIGH_CONTRAST_COLORS, COLOR_BALL, COLOR_TARGET, COLOR_START

def test_high_contrast_mode():
    """Test high-contrast mode toggle and color changes."""
    print("Testing High-Contrast Mode...")
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create renderer
    renderer = Renderer(screen)
    
    # Test 1: Default mode (high-contrast off)
    print("\n1. Testing default mode (high-contrast off)...")
    assert renderer.high_contrast_mode == False, "High-contrast mode should be off by default"
    
    # Test color retrieval in normal mode
    ball_color = renderer.get_color('ball', COLOR_BALL)
    assert ball_color == COLOR_BALL, f"Expected {COLOR_BALL}, got {ball_color}"
    print("   ✓ Default colors work correctly")
    
    # Test 2: Enable high-contrast mode
    print("\n2. Testing high-contrast mode enabled...")
    renderer.set_high_contrast_mode(True)
    assert renderer.high_contrast_mode == True, "High-contrast mode should be enabled"
    
    # Test color retrieval in high-contrast mode
    ball_color_hc = renderer.get_color('ball', COLOR_BALL)
    assert ball_color_hc == HIGH_CONTRAST_COLORS['ball'], \
        f"Expected {HIGH_CONTRAST_COLORS['ball']}, got {ball_color_hc}"
    print("   ✓ High-contrast colors work correctly")
    
    # Test 3: Verify all high-contrast colors are accessible
    print("\n3. Testing all high-contrast color mappings...")
    test_colors = [
        ('ball', COLOR_BALL),
        ('target', COLOR_TARGET),
        ('start', COLOR_START),
        ('water_light', (173, 216, 230)),
        ('water_dark', (135, 206, 235)),
    ]
    
    for color_name, default_color in test_colors:
        hc_color = renderer.get_color(color_name, default_color)
        expected = HIGH_CONTRAST_COLORS.get(color_name, default_color)
        assert hc_color == expected, \
            f"Color '{color_name}': expected {expected}, got {hc_color}"
    print("   ✓ All color mappings work correctly")
    
    # Test 4: Disable high-contrast mode
    print("\n4. Testing high-contrast mode disabled...")
    renderer.set_high_contrast_mode(False)
    assert renderer.high_contrast_mode == False, "High-contrast mode should be disabled"
    
    ball_color_normal = renderer.get_color('ball', COLOR_BALL)
    assert ball_color_normal == COLOR_BALL, \
        f"Expected {COLOR_BALL}, got {ball_color_normal}"
    print("   ✓ Returns to normal colors correctly")
    
    # Test 5: Test with non-existent color key
    print("\n5. Testing fallback for non-existent color...")
    renderer.set_high_contrast_mode(True)
    fallback_color = (255, 0, 255)
    result = renderer.get_color('nonexistent_color', fallback_color)
    assert result == fallback_color, \
        f"Expected fallback {fallback_color}, got {result}"
    print("   ✓ Fallback works correctly")
    
    pygame.quit()
    print("\n✅ All high-contrast mode tests passed!")
    return True

def test_checkbox_integration():
    """Test that checkbox can be created and toggled."""
    print("\nTesting Checkbox Integration...")
    
    # Import after pygame init
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Import the Checkbox class from main
    import main
    
    # Create checkbox
    checkbox = main.Checkbox(100, 100, 20, "High-Contrast Mode", checked=False)
    
    # Test initial state
    assert checkbox.is_checked() == False, "Checkbox should start unchecked"
    print("   ✓ Checkbox created with correct initial state")
    
    # Test toggle
    checkbox.toggle()
    assert checkbox.is_checked() == True, "Checkbox should be checked after toggle"
    print("   ✓ Checkbox toggle works")
    
    # Test set_checked
    checkbox.set_checked(False)
    assert checkbox.is_checked() == False, "Checkbox should be unchecked"
    print("   ✓ Checkbox set_checked works")
    
    pygame.quit()
    print("✅ Checkbox integration tests passed!")
    return True

if __name__ == "__main__":
    try:
        # Run tests
        test_high_contrast_mode()
        test_checkbox_integration()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("="*50)
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
