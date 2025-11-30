#!/usr/bin/env python3
"""
Test script for tutorial system.
"""

import pygame
from game.tutorial import TutorialManager, Tooltip
from game.physics import Vector2
from game.level import LevelData

def test_tooltip_creation():
    """Test tooltip creation and rendering."""
    print("Testing tooltip creation...")
    
    tooltip = Tooltip(
        "This is a test tooltip with some longer text that should wrap to multiple lines.",
        Vector2(400, 300),
        "down",
        auto_dismiss_time=10.0
    )
    
    assert tooltip.text is not None
    assert tooltip.position.x == 400
    assert tooltip.position.y == 300
    assert tooltip.pointer_direction == "down"
    assert len(tooltip.wrapped_lines) > 0
    
    print("✓ Tooltip creation test passed")

def test_tutorial_manager():
    """Test tutorial manager initialization."""
    print("Testing tutorial manager...")
    
    manager = TutorialManager(1024, 768)
    
    assert manager.screen_width == 1024
    assert manager.screen_height == 768
    assert manager.skip_button is not None
    assert not manager.is_tutorial_active()
    
    print("✓ Tutorial manager test passed")

def test_level_1_tutorial():
    """Test Level 1 tutorial tooltips."""
    print("Testing Level 1 tutorial...")
    
    manager = TutorialManager(1024, 768)
    
    # Create mock level data
    level_data = LevelData(
        level_id=1,
        ball_start=Vector2(150, 300),
        target_position=Vector2(800, 300),
        target_radius=40,
        obstacles=[],
        walls=[],
        current_zones=[],
        whirlpools=[],
        initial_stones=10,
        tutorial=True
    )
    
    manager.start_tutorial(1, level_data)
    
    assert manager.current_level == 1
    assert len(manager.active_tooltips) == 3  # Level 1 has 3 tooltips
    assert manager.is_tutorial_active()
    
    print("✓ Level 1 tutorial test passed")

def test_skip_tutorial():
    """Test skipping tutorial."""
    print("Testing skip tutorial...")
    
    manager = TutorialManager(1024, 768)
    
    # Create mock level data
    level_data = LevelData(
        level_id=1,
        ball_start=Vector2(150, 300),
        target_position=Vector2(800, 300),
        target_radius=40,
        tutorial=True
    )
    
    manager.start_tutorial(1, level_data)
    assert manager.is_tutorial_active()
    
    manager.skip_tutorial()
    assert not manager.is_tutorial_active()
    assert manager.tutorial_skipped
    
    print("✓ Skip tutorial test passed")

def test_dismiss_tooltip():
    """Test dismissing tooltips."""
    print("Testing dismiss tooltip...")
    
    manager = TutorialManager(1024, 768)
    
    # Create mock level data
    level_data = LevelData(
        level_id=1,
        ball_start=Vector2(150, 300),
        target_position=Vector2(800, 300),
        target_radius=40,
        tutorial=True
    )
    
    manager.start_tutorial(1, level_data)
    
    initial_index = manager.current_tooltip_index
    manager.dismiss_current_tooltip()
    
    assert manager.current_tooltip_index == initial_index + 1
    
    print("✓ Dismiss tooltip test passed")

def test_non_tutorial_level():
    """Test that non-tutorial levels don't show tooltips."""
    print("Testing non-tutorial level...")
    
    manager = TutorialManager(1024, 768)
    
    # Create mock level data for level 5 (not a tutorial level)
    level_data = LevelData(
        level_id=5,
        ball_start=Vector2(150, 300),
        target_position=Vector2(800, 300),
        target_radius=40,
        tutorial=False
    )
    
    manager.start_tutorial(5, level_data)
    
    assert not manager.is_tutorial_active()
    assert len(manager.active_tooltips) == 0
    
    print("✓ Non-tutorial level test passed")

def main():
    """Run all tests."""
    print("=" * 50)
    print("Tutorial System Tests")
    print("=" * 50)
    
    # Initialize Pygame (required for font rendering)
    pygame.init()
    
    try:
        test_tooltip_creation()
        test_tutorial_manager()
        test_level_1_tutorial()
        test_skip_tutorial()
        test_dismiss_tooltip()
        test_non_tutorial_level()
        
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1
    finally:
        pygame.quit()
    
    return 0

if __name__ == "__main__":
    exit(main())
