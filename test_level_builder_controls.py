"""
Test script for level builder controls.
Tests undo/redo, templates, and JSON import/export functionality.
"""

import pygame
import sys
from game.level_builder import LevelBuilder, ObstacleType
from game.physics import Vector2
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT


def test_undo_redo():
    """Test undo/redo functionality."""
    print("Testing undo/redo...")
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    builder = LevelBuilder(screen)
    
    # Place some obstacles
    builder.selected_palette_type = ObstacleType.ANTI_RIPPLE
    builder.place_obstacle((300, 300))
    assert len(builder.obstacles) == 1, "Should have 1 obstacle"
    assert len(builder.undo_stack) == 1, "Should have 1 undo state"
    
    builder.place_obstacle((400, 400))
    assert len(builder.obstacles) == 2, "Should have 2 obstacles"
    assert len(builder.undo_stack) == 2, "Should have 2 undo states"
    
    # Test undo
    builder.undo()
    assert len(builder.obstacles) == 1, "Should have 1 obstacle after undo"
    assert len(builder.redo_stack) == 1, "Should have 1 redo state"
    
    builder.undo()
    assert len(builder.obstacles) == 0, "Should have 0 obstacles after second undo"
    assert len(builder.redo_stack) == 2, "Should have 2 redo states"
    
    # Test redo
    builder.redo()
    assert len(builder.obstacles) == 1, "Should have 1 obstacle after redo"
    
    builder.redo()
    assert len(builder.obstacles) == 2, "Should have 2 obstacles after second redo"
    
    # Test max undo stack size (4)
    for i in range(5):
        builder.place_obstacle((500 + i * 10, 300))
    
    assert len(builder.undo_stack) <= 4, "Undo stack should not exceed 4"
    
    pygame.quit()
    print("✓ Undo/redo tests passed")


def test_templates():
    """Test template functionality."""
    print("Testing templates...")
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    builder = LevelBuilder(screen)
    
    # Test Blank template
    builder.template_dropdown.selected_index = 0  # Blank
    builder.apply_template()
    assert len(builder.obstacles) == 0, "Blank template should have no obstacles"
    
    # Test Maze template
    builder.template_dropdown.selected_index = 1  # Maze
    builder.apply_template()
    assert len(builder.obstacles) > 0, "Maze template should have obstacles"
    maze_count = len(builder.obstacles)
    
    # Test Islands template
    builder.template_dropdown.selected_index = 2  # Islands
    builder.apply_template()
    assert len(builder.obstacles) > 0, "Islands template should have obstacles"
    
    # Test Channels template
    builder.template_dropdown.selected_index = 3  # Channels
    builder.apply_template()
    assert len(builder.obstacles) > 0, "Channels template should have obstacles"
    
    pygame.quit()
    print("✓ Template tests passed")


def test_json_export_import():
    """Test JSON export and import."""
    print("Testing JSON export/import...")
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    builder = LevelBuilder(screen)
    
    # Set up a level
    builder.level_name = "Test Level"
    builder.ball_start = Vector2(100, 200)
    builder.target_position = Vector2(700, 400)
    builder.target_radius = 50
    
    # Add some obstacles
    builder.selected_palette_type = ObstacleType.ANTI_RIPPLE
    builder.place_obstacle((300, 300))
    
    builder.selected_palette_type = ObstacleType.WALL
    builder.place_obstacle((500, 300))
    
    builder.selected_palette_type = ObstacleType.WHIRLPOOL
    builder.place_obstacle((600, 400))
    
    original_count = len(builder.obstacles)
    
    # Export to JSON
    json_str = builder.export_to_json()
    assert json_str, "JSON export should return a string"
    assert "Test Level" in json_str, "JSON should contain level name"
    assert "anti_ripple_zone" in json_str, "JSON should contain obstacle types"
    
    # Clear and import
    builder.obstacles.clear()
    builder.level_name = "Empty"
    
    success = builder.import_from_json(json_str)
    assert success, "Import should succeed"
    assert builder.level_name == "Test Level", "Level name should be restored"
    assert len(builder.obstacles) == original_count, "Obstacle count should match"
    assert builder.ball_start.x == 100, "Ball start should be restored"
    assert builder.target_position.x == 700, "Target position should be restored"
    
    pygame.quit()
    print("✓ JSON export/import tests passed")


def test_level_data_creation():
    """Test creating LevelData from builder state."""
    print("Testing LevelData creation...")
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    builder = LevelBuilder(screen)
    
    # Add obstacles
    builder.selected_palette_type = ObstacleType.ANTI_RIPPLE
    builder.place_obstacle((300, 300))
    
    builder.selected_palette_type = ObstacleType.CURRENT_ZONE
    builder.place_obstacle((500, 300))
    
    # Create level data
    level_data = builder.create_level_data()
    
    assert level_data is not None, "Should create level data"
    assert level_data.id == 999, "Test level should have ID 999"
    # Obstacles are separated by type now
    total_obstacles = (len(level_data.obstacles) + len(level_data.walls) + 
                      len(level_data.current_zones) + len(level_data.whirlpools))
    assert total_obstacles == 2, f"Should have 2 obstacles total, got {total_obstacles}"
    assert len(level_data.obstacles) == 1, "Should have 1 anti-ripple obstacle"
    assert len(level_data.current_zones) == 1, "Should have 1 current zone"
    assert level_data.ball_start.x == builder.ball_start.x, "Ball start should match"
    assert level_data.target_position.x == builder.target_position.x, "Target should match"
    
    pygame.quit()
    print("✓ LevelData creation tests passed")


def interactive_test():
    """Interactive test to manually verify controls."""
    print("\n=== Interactive Level Builder Test ===")
    print("Controls:")
    print("- Click obstacle buttons to select type")
    print("- Click in canvas to place obstacles")
    print("- Click and drag to move obstacles")
    print("- Delete key to remove selected obstacle")
    print("- Undo/Redo buttons or Ctrl+Z/Ctrl+Y")
    print("- Grid toggle button or G key")
    print("- Use Template button to apply templates")
    print("- Export/Import buttons to save/load")
    print("- Exit button to quit")
    print("=====================================\n")
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Level Builder Controls Test")
    clock = pygame.time.Clock()
    
    builder = LevelBuilder(screen)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    builder.handle_mouse_down(event.pos)
                    
                    # Check if exit button was clicked
                    if builder.exit_button.is_clicked(event.pos):
                        running = False
                    
                    # Check if test play button was clicked
                    if builder.test_play_button.is_clicked(event.pos):
                        print("Test Play clicked - would launch test level")
                        level_data = builder.start_test_play()
                        print(f"Created test level with {len(level_data.obstacles)} obstacles")
                        builder.exit_test_play()
                        print("Returned from test play")
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    builder.handle_mouse_up(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                builder.handle_mouse_motion(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                builder.handle_key_down(event)
        
        builder.update(dt)
        builder.draw()
        pygame.display.flip()
    
    pygame.quit()
    print("\nInteractive test completed")


if __name__ == "__main__":
    try:
        # Run automated tests
        test_undo_redo()
        test_templates()
        test_json_export_import()
        test_level_data_creation()
        
        print("\n✓ All automated tests passed!\n")
        
        # Ask if user wants to run interactive test
        response = input("Run interactive test? (y/n): ")
        if response.lower() == 'y':
            interactive_test()
        
        print("\n✓ All tests completed successfully!")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
