"""
Test script for Level Builder functionality.
"""

import pygame
from game.level_builder import LevelBuilder, BuilderObstacle, ObstacleType
from game.physics import Vector2
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT


def test_level_builder_creation():
    """Test that level builder can be created."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    builder = LevelBuilder(screen)
    
    assert builder is not None
    assert len(builder.obstacles) == 0
    assert builder.show_grid == True
    assert len(builder.palette_buttons) == 4
    
    print("✓ Level builder creation test passed")


def test_obstacle_placement():
    """Test placing obstacles."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    builder = LevelBuilder(screen)
    
    # Select anti-ripple type
    builder.selected_palette_type = ObstacleType.ANTI_RIPPLE
    
    # Place obstacle
    builder.place_obstacle((400, 300))
    
    assert len(builder.obstacles) == 1
    assert builder.obstacles[0].type == ObstacleType.ANTI_RIPPLE
    assert builder.obstacles[0].is_selected == True
    
    print("✓ Obstacle placement test passed")


def test_obstacle_selection():
    """Test selecting obstacles."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    builder = LevelBuilder(screen)
    
    # Create obstacle
    obstacle = BuilderObstacle(ObstacleType.ANTI_RIPPLE, Vector2(400, 300), size=[100, 100])
    builder.obstacles.append(obstacle)
    
    # Test contains_point
    assert obstacle.contains_point((400, 300)) == True
    assert obstacle.contains_point((100, 100)) == False
    
    print("✓ Obstacle selection test passed")


def test_obstacle_types():
    """Test all obstacle types can be created."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    builder = LevelBuilder(screen)
    
    # Test each obstacle type
    types = [
        ObstacleType.ANTI_RIPPLE,
        ObstacleType.WALL,
        ObstacleType.CURRENT_ZONE,
        ObstacleType.WHIRLPOOL
    ]
    
    for obstacle_type in types:
        builder.selected_palette_type = obstacle_type
        builder.place_obstacle((400, 300))
    
    assert len(builder.obstacles) == 4
    assert builder.obstacles[0].type == ObstacleType.ANTI_RIPPLE
    assert builder.obstacles[1].type == ObstacleType.WALL
    assert builder.obstacles[2].type == ObstacleType.CURRENT_ZONE
    assert builder.obstacles[3].type == ObstacleType.WHIRLPOOL
    
    print("✓ All obstacle types test passed")


def test_grid_toggle():
    """Test grid toggle functionality."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    builder = LevelBuilder(screen)
    
    # Initial state
    assert builder.show_grid == True
    
    # Create mock key event
    event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_g})
    builder.handle_key_down(event)
    
    assert builder.show_grid == False
    
    # Toggle again
    builder.handle_key_down(event)
    assert builder.show_grid == True
    
    print("✓ Grid toggle test passed")


def test_obstacle_deletion():
    """Test deleting obstacles."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    builder = LevelBuilder(screen)
    
    # Create and select obstacle
    obstacle = BuilderObstacle(ObstacleType.ANTI_RIPPLE, Vector2(400, 300), size=[100, 100])
    builder.obstacles.append(obstacle)
    builder.selected_obstacle = obstacle
    
    assert len(builder.obstacles) == 1
    
    # Delete with Delete key
    event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DELETE})
    builder.handle_key_down(event)
    
    assert len(builder.obstacles) == 0
    assert builder.selected_obstacle is None
    
    print("✓ Obstacle deletion test passed")


def test_resize_handles():
    """Test resize handle detection."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    builder = LevelBuilder(screen)
    
    # Create rectangular obstacle
    obstacle = BuilderObstacle(ObstacleType.ANTI_RIPPLE, Vector2(400, 300), size=[100, 100])
    
    # Test corner handle detection
    handle = builder.get_resize_handle_at((350, 250), obstacle)  # Top-left corner
    assert handle == 'nw'
    
    handle = builder.get_resize_handle_at((450, 250), obstacle)  # Top-right corner
    assert handle == 'ne'
    
    # Test no handle
    handle = builder.get_resize_handle_at((400, 300), obstacle)  # Center
    assert handle is None
    
    print("✓ Resize handles test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Level Builder tests...\n")
    
    test_level_builder_creation()
    test_obstacle_placement()
    test_obstacle_selection()
    test_obstacle_types()
    test_grid_toggle()
    test_obstacle_deletion()
    test_resize_handles()
    
    print("\n✅ All Level Builder tests passed!")
    pygame.quit()


if __name__ == "__main__":
    run_all_tests()
