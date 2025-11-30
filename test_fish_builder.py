"""
Test script for Fish Builder functionality.
"""

import pygame
from game.fish_builder import FishBuilder, DrawingTool, FishTemplate


def test_fish_builder_initialization():
    """Test that fish builder initializes correctly."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    
    builder = FishBuilder(screen)
    
    # Check initial state
    assert len(builder.templates) == 3, "Should have 3 default templates"
    assert builder.selected_template_index == 0, "Should start with first template selected"
    assert builder.current_tool == DrawingTool.PENCIL, "Should start with pencil tool"
    assert len(builder.color_palette) == 20, "Should have 20 colors in palette"
    assert builder.current_color == (255, 140, 0), "Should start with orange color"
    
    print("✓ Fish builder initialization test passed")


def test_fish_template():
    """Test fish template creation and properties."""
    template = FishTemplate("Test Fish")
    
    assert template.name == "Test Fish"
    assert template.enabled == True
    assert template.min_count == 0
    assert template.max_count == 4
    assert len(template.pixel_data) == 32
    assert len(template.pixel_data[0]) == 32
    assert template.behavior_pattern == "Random"
    assert template.speed == 50.0
    assert template.reaction_intensity == 1.0
    assert template.size == 15.0
    
    print("✓ Fish template test passed")


def test_drawing_tools():
    """Test drawing tool functionality."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    
    builder = FishBuilder(screen)
    template = builder.get_selected_template()
    
    # Test pencil drawing
    builder.current_tool = DrawingTool.PENCIL
    builder.current_color = (255, 0, 0)
    builder.draw_pixel((5, 5))
    assert template.pixel_data[5][5] == (255, 0, 0), "Pencil should draw pixel"
    
    # Test eraser
    builder.current_tool = DrawingTool.ERASER
    builder.draw_pixel((5, 5))
    assert template.pixel_data[5][5] is None, "Eraser should clear pixel"
    
    print("✓ Drawing tools test passed")


def test_undo_redo():
    """Test undo/redo functionality."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    
    builder = FishBuilder(screen)
    template = builder.get_selected_template()
    
    # Save initial state
    builder.save_state_for_undo()
    
    # Make a change
    builder.current_tool = DrawingTool.PENCIL
    builder.current_color = (255, 0, 0)
    builder.draw_pixel((10, 10))
    assert template.pixel_data[10][10] == (255, 0, 0)
    
    # Undo
    builder.undo()
    assert template.pixel_data[10][10] is None, "Undo should restore previous state"
    
    # Redo
    builder.redo()
    assert template.pixel_data[10][10] == (255, 0, 0), "Redo should restore undone state"
    
    print("✓ Undo/redo test passed")


def test_clear_canvas():
    """Test clear canvas functionality."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    
    builder = FishBuilder(screen)
    template = builder.get_selected_template()
    
    # Draw some pixels
    builder.current_tool = DrawingTool.PENCIL
    builder.current_color = (255, 0, 0)
    for i in range(5):
        builder.draw_pixel((i, i))
    
    # Verify pixels are drawn
    assert template.pixel_data[0][0] == (255, 0, 0)
    
    # Clear canvas
    builder.clear_canvas()
    
    # Verify all pixels are cleared
    for y in range(32):
        for x in range(32):
            assert template.pixel_data[y][x] is None, "All pixels should be cleared"
    
    print("✓ Clear canvas test passed")


def test_flood_fill():
    """Test flood fill functionality."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    
    builder = FishBuilder(screen)
    template = builder.get_selected_template()
    
    # Draw a border
    builder.current_tool = DrawingTool.PENCIL
    builder.current_color = (0, 0, 0)
    for i in range(10):
        builder.draw_pixel((i, 0))
        builder.draw_pixel((i, 9))
        builder.draw_pixel((0, i))
        builder.draw_pixel((9, i))
    
    # Fill inside
    builder.current_color = (255, 0, 0)
    builder.flood_fill((5, 5))
    
    # Check that inside is filled
    assert template.pixel_data[5][5] == (255, 0, 0), "Center should be filled"
    assert template.pixel_data[1][1] == (255, 0, 0), "Inside should be filled"
    
    # Check that border is not changed
    assert template.pixel_data[0][0] == (0, 0, 0), "Border should remain black"
    
    print("✓ Flood fill test passed")


def test_pixel_coordinate_conversion():
    """Test mouse position to pixel grid conversion."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    
    builder = FishBuilder(screen)
    
    # Test valid position
    canvas_center_x = builder.canvas_x + builder.canvas_size // 2
    canvas_center_y = builder.canvas_y + builder.canvas_size // 2
    pixel_pos = builder.get_pixel_at_pos((canvas_center_x, canvas_center_y))
    
    assert pixel_pos is not None, "Should return valid pixel position"
    assert pixel_pos[0] == 16, "Should be center X"
    assert pixel_pos[1] == 16, "Should be center Y"
    
    # Test invalid position (outside canvas)
    pixel_pos = builder.get_pixel_at_pos((0, 0))
    assert pixel_pos is None, "Should return None for position outside canvas"
    
    print("✓ Pixel coordinate conversion test passed")


def run_all_tests():
    """Run all fish builder tests."""
    print("\n=== Running Fish Builder Tests ===\n")
    
    test_fish_builder_initialization()
    test_fish_template()
    test_drawing_tools()
    test_undo_redo()
    test_clear_canvas()
    test_flood_fill()
    test_pixel_coordinate_conversion()
    
    print("\n=== All Fish Builder Tests Passed! ===\n")
    
    pygame.quit()


if __name__ == "__main__":
    run_all_tests()
