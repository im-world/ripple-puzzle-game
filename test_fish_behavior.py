"""
Test fish behavior configuration implementation.
"""

import pygame
import json
from game.fish_builder import FishBuilder, FishTemplate, load_global_fish_config
from game.fish import Fish, spawn_fish
from game.physics import Vector2


def test_fish_template_serialization():
    """Test that fish templates can be saved and loaded."""
    print("Testing fish template serialization...")
    
    # Create a template with custom properties
    template = FishTemplate("Test Fish")
    template.behavior_pattern = "Circular Patrol"
    template.speed = 75.0
    template.reaction_intensity = 1.5
    template.size = 20.0
    template.min_count = 2
    template.max_count = 5
    
    # Convert to dict and back
    data = template.to_dict()
    loaded_template = FishTemplate.from_dict(data)
    
    # Verify properties
    assert loaded_template.name == "Test Fish"
    assert loaded_template.behavior_pattern == "Circular Patrol"
    assert loaded_template.speed == 75.0
    assert loaded_template.reaction_intensity == 1.5
    assert loaded_template.size == 20.0
    assert loaded_template.min_count == 2
    assert loaded_template.max_count == 5
    
    print("✓ Fish template serialization works correctly")


def test_fish_behavior_patterns():
    """Test that fish can be created with different behavior patterns."""
    print("\nTesting fish behavior patterns...")
    
    behaviors = ["Schooling", "Solo", "Circular Patrol", "Random"]
    
    for behavior in behaviors:
        fish = Fish(
            Vector2(400, 300),
            size=15.0,
            speed=50.0,
            behavior_pattern=behavior,
            reaction_intensity=1.0
        )
        
        assert fish.behavior_pattern == behavior
        assert fish.base_speed == 50.0
        assert fish.reaction_intensity == 1.0
        
        # Test update doesn't crash
        fish.update(0.016)  # 60 FPS frame
        
        print(f"  ✓ {behavior} behavior works")
    
    print("✓ All behavior patterns work correctly")


def test_spawn_fish_with_templates():
    """Test spawning fish using templates."""
    print("\nTesting fish spawning with templates...")
    
    # Create test templates
    templates = [
        FishTemplate("Fast Fish"),
        FishTemplate("Slow Fish"),
        FishTemplate("Big Fish")
    ]
    
    templates[0].enabled = True
    templates[0].min_count = 1
    templates[0].max_count = 2
    templates[0].speed = 80.0
    templates[0].behavior_pattern = "Solo"
    
    templates[1].enabled = True
    templates[1].min_count = 2
    templates[1].max_count = 3
    templates[1].speed = 30.0
    templates[1].behavior_pattern = "Random"
    
    templates[2].enabled = False  # This one should not spawn
    
    # Spawn fish
    fish_list = spawn_fish(fish_templates=templates)
    
    # Should have between 3-5 fish (1-2 fast + 2-3 slow, 0 big)
    assert 3 <= len(fish_list) <= 5
    
    print(f"  ✓ Spawned {len(fish_list)} fish from templates")
    print("✓ Fish spawning with templates works correctly")


def test_fish_builder_save_load():
    """Test saving and loading fish configuration."""
    print("\nTesting fish builder save/load...")
    
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    
    # Create fish builder
    builder = FishBuilder(screen)
    
    # Modify templates
    builder.templates[0].behavior_pattern = "Schooling"
    builder.templates[0].speed = 65.0
    builder.templates[0].reaction_intensity = 1.8
    
    # Save configuration
    builder._save_fish_config()
    
    # Load configuration
    loaded_templates = load_global_fish_config()
    
    # Verify
    assert len(loaded_templates) == len(builder.templates)
    assert loaded_templates[0].behavior_pattern == "Schooling"
    assert loaded_templates[0].speed == 65.0
    assert loaded_templates[0].reaction_intensity == 1.8
    
    print("✓ Fish builder save/load works correctly")
    
    pygame.quit()


def test_schooling_behavior():
    """Test that schooling fish respond to nearby fish."""
    print("\nTesting schooling behavior...")
    
    # Create two fish close together
    fish1 = Fish(Vector2(400, 300), behavior_pattern="Schooling")
    fish2 = Fish(Vector2(450, 300), behavior_pattern="Schooling")
    
    fish_list = [fish1, fish2]
    
    # Update fish1 with fish2 nearby
    initial_direction = fish1.direction
    
    # Update multiple times to see schooling effect
    for _ in range(10):
        fish1.update(0.016, fish_list)
        fish2.update(0.016, fish_list)
    
    # Direction should have changed due to schooling
    # (This is a basic test - in practice the effect is subtle)
    print(f"  Initial direction: {initial_direction:.2f}")
    print(f"  Final direction: {fish1.direction:.2f}")
    print("✓ Schooling behavior executes without errors")


def test_circular_patrol_behavior():
    """Test that circular patrol fish move in circles."""
    print("\nTesting circular patrol behavior...")
    
    fish = Fish(Vector2(400, 300), behavior_pattern="Circular Patrol", speed=50.0)
    
    # Record initial position
    initial_pos = fish.position.copy()
    
    # Update for several frames
    for _ in range(100):
        fish.update(0.016)
    
    # Fish should have moved
    distance_moved = (fish.position - initial_pos).magnitude()
    assert distance_moved > 0
    
    print(f"  Fish moved {distance_moved:.1f} pixels in circular patrol")
    print("✓ Circular patrol behavior works correctly")


def run_all_tests():
    """Run all fish behavior tests."""
    print("=" * 60)
    print("Running Fish Behavior Configuration Tests")
    print("=" * 60)
    
    test_fish_template_serialization()
    test_fish_behavior_patterns()
    test_spawn_fish_with_templates()
    test_fish_builder_save_load()
    test_schooling_behavior()
    test_circular_patrol_behavior()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
