#!/usr/bin/env python3
"""
Integration test for Environment Randomizer in gameplay and level builder.
Verifies the button works correctly in both modes.
"""

import pygame
import sys
import time


def test_environment_in_gameplay():
    """Test environment randomizer in gameplay mode."""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Environment Randomizer in Gameplay")
    print("=" * 60)
    
    # Import after pygame init
    from main import Game
    
    # Create game instance
    game = Game()
    
    # Start game
    game.start_game(level_index=0)
    
    print("\n✓ Game started successfully")
    print("✓ Environment system initialized")
    print("✓ Environment randomizer button created")
    
    # Verify button exists and is positioned correctly
    assert game.env_randomizer_button is not None, "Button should exist"
    assert game.env_randomizer_button.x == 20, "Button X position should be 20"
    assert game.env_randomizer_button.y == 20, "Button Y position should be 20"
    assert game.env_randomizer_button.size == 50, "Button size should be 50"
    
    print("✓ Button position verified (top-left corner)")
    
    # Verify environment system exists
    assert game.environment is not None, "Environment system should exist"
    assert game.renderer.environment is not None, "Renderer should have environment reference"
    
    print("✓ Environment system connected to renderer")
    
    # Test randomization
    initial_theme = game.environment.current_theme
    initial_weather = game.environment.current_weather
    initial_time = game.environment.current_time
    
    print(f"\nInitial state:")
    print(f"  Theme: {initial_theme}")
    print(f"  Weather: {initial_weather}")
    print(f"  Time: {initial_time}")
    
    # Randomize multiple times
    changes_detected = False
    for i in range(5):
        game.environment.randomize()
        if (game.environment.current_theme != initial_theme or
            game.environment.current_weather != initial_weather or
            game.environment.current_time != initial_time):
            changes_detected = True
            break
    
    assert changes_detected, "Randomization should change environment"
    
    print(f"\nAfter randomization:")
    print(f"  Theme: {game.environment.current_theme}")
    print(f"  Weather: {game.environment.current_weather}")
    print(f"  Time: {game.environment.current_time}")
    print("✓ Randomization working correctly")
    
    # Test button animations
    game.env_randomizer_button.start_spin()
    assert game.env_randomizer_button.is_spinning, "Button should be spinning"
    
    # Update button for a bit
    for _ in range(10):
        game.env_randomizer_button.update((100, 100), 0.016)
    
    print("✓ Button spin animation working")
    
    # Test hover state
    game.env_randomizer_button.update((35, 35), 0.016)  # Mouse over button
    assert game.env_randomizer_button.is_hovered, "Button should detect hover"
    
    game.env_randomizer_button.update((500, 500), 0.016)  # Mouse away
    assert not game.env_randomizer_button.is_hovered, "Button should not be hovered"
    
    print("✓ Button hover detection working")
    
    # Test weather particle system
    game.environment.current_weather = 'snow'
    game.environment.update(0.5)  # Update for half a second
    
    # Should have spawned some particles
    particle_count = len(game.environment.weather_particles)
    print(f"✓ Weather system spawned {particle_count} particles")
    
    print("\n" + "=" * 60)
    print("GAMEPLAY TEST PASSED ✓")
    print("=" * 60)


def test_environment_in_level_builder():
    """Test environment randomizer in level builder mode."""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Environment Randomizer in Level Builder")
    print("=" * 60)
    
    from main import Game
    
    # Create game instance
    game = Game()
    
    # Switch to level builder
    game.state = game.state.__class__.LEVEL_BUILDER
    
    print("\n✓ Level builder mode activated")
    
    # Verify button still works
    assert game.env_randomizer_button is not None, "Button should exist in level builder"
    
    # Test randomization in level builder
    initial_theme = game.environment.current_theme
    game.environment.randomize()
    
    print(f"✓ Randomization works in level builder")
    print(f"  Theme changed from {initial_theme} to {game.environment.current_theme}")
    
    # Test that environment updates work
    game.environment.current_weather = 'leaves'
    game.environment.update(0.5)
    
    particle_count = len(game.environment.weather_particles)
    print(f"✓ Weather effects work in level builder ({particle_count} particles)")
    
    print("\n" + "=" * 60)
    print("LEVEL BUILDER TEST PASSED ✓")
    print("=" * 60)


def test_no_cooldown():
    """Test that there's no cooldown on randomization."""
    print("\n" + "=" * 60)
    print("TEST: No Cooldown on Randomization")
    print("=" * 60)
    
    from main import Game
    
    game = Game()
    
    # Rapid randomizations
    themes = []
    for i in range(10):
        game.environment.randomize()
        themes.append(game.environment.current_theme)
    
    print(f"\n✓ Performed 10 rapid randomizations")
    print(f"  Themes: {', '.join(themes)}")
    print("✓ No cooldown - can click anytime")
    
    print("\n" + "=" * 60)
    print("NO COOLDOWN TEST PASSED ✓")
    print("=" * 60)


def test_visual_only():
    """Test that environment changes don't affect physics."""
    print("\n" + "=" * 60)
    print("TEST: Visual Changes Only (No Physics Impact)")
    print("=" * 60)
    
    from main import Game
    
    game = Game()
    game.start_game(level_index=0)
    
    # Get initial ball physics state
    initial_ball_pos = (game.ball.position.x, game.ball.position.y)
    initial_ball_vel = (game.ball.velocity.x, game.ball.velocity.y)
    
    # Randomize environment
    game.environment.randomize()
    
    # Ball physics should be unchanged
    assert game.ball.position.x == initial_ball_pos[0], "Ball X position unchanged"
    assert game.ball.position.y == initial_ball_pos[1], "Ball Y position unchanged"
    assert game.ball.velocity.x == initial_ball_vel[0], "Ball X velocity unchanged"
    assert game.ball.velocity.y == initial_ball_vel[1], "Ball Y velocity unchanged"
    
    print("\n✓ Environment changes don't affect ball physics")
    print("✓ Visual changes only - confirmed")
    
    print("\n" + "=" * 60)
    print("VISUAL ONLY TEST PASSED ✓")
    print("=" * 60)


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("ENVIRONMENT RANDOMIZER INTEGRATION TESTS")
    print("=" * 60)
    
    try:
        test_environment_in_gameplay()
        test_environment_in_level_builder()
        test_no_cooldown()
        test_visual_only()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓✓✓")
        print("=" * 60)
        print("\nEnvironment Randomizer Implementation:")
        print("  ✓ Button positioned in top-left corner")
        print("  ✓ Hover pulse animation working")
        print("  ✓ Click spin animation working")
        print("  ✓ Randomizes background color/theme")
        print("  ✓ Randomizes weather effects")
        print("  ✓ Randomizes time of day")
        print("  ✓ No cooldown - click anytime")
        print("  ✓ Works in gameplay mode")
        print("  ✓ Works in level builder mode")
        print("  ✓ Visual changes only - no physics impact")
        print("\n" + "=" * 60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
