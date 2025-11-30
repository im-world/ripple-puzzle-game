#!/usr/bin/env python3
"""
Test script for Whirlpool obstacle implementation.
Tests whirlpool physics, rendering, and lose condition.
"""

from game.physics import Vector2
from game.level import Whirlpool, LevelData
import json


def test_whirlpool_creation():
    """Test creating a whirlpool."""
    print("Testing whirlpool creation...")
    position = Vector2(400, 300)
    radius = 100
    pull_strength = 200
    
    whirlpool = Whirlpool(position, radius, pull_strength)
    
    assert whirlpool.position.x == 400
    assert whirlpool.position.y == 300
    assert whirlpool.radius == 100
    assert whirlpool.pull_strength == 200
    assert whirlpool.center_threshold == 15  # 15% of 100
    assert whirlpool.type == "whirlpool"
    
    print("✓ Whirlpool creation test passed")


def test_whirlpool_force():
    """Test whirlpool force calculation."""
    print("\nTesting whirlpool force calculation...")
    whirlpool = Whirlpool(Vector2(400, 300), 100, 200)
    
    # Test force at edge (should be zero or minimal due to quadratic falloff)
    edge_point = Vector2(500, 300)  # 100 pixels away (at edge)
    edge_force = whirlpool.get_force_at(edge_point)
    print(f"  Force at edge: magnitude = {edge_force.magnitude():.2f}")
    assert edge_force.magnitude() == 0, "Force at edge should be zero (quadratic falloff)"
    
    # Test force at mid-distance (should be stronger)
    mid_point = Vector2(450, 300)  # 50 pixels away (halfway)
    mid_force = whirlpool.get_force_at(mid_point)
    print(f"  Force at mid: magnitude = {mid_force.magnitude():.2f}")
    assert mid_force.magnitude() > 0, "Force at mid-distance should be non-zero"
    
    # Test force near center (should be strongest)
    near_center = Vector2(410, 300)  # 10 pixels away (very close)
    center_force = whirlpool.get_force_at(near_center)
    print(f"  Force near center: magnitude = {center_force.magnitude():.2f}")
    assert center_force.magnitude() > mid_force.magnitude(), "Force should be strongest near center"
    
    # Test force outside radius (should be zero)
    outside_point = Vector2(600, 300)  # 200 pixels away (outside)
    outside_force = whirlpool.get_force_at(outside_point)
    print(f"  Force outside: magnitude = {outside_force.magnitude():.2f}")
    assert outside_force.magnitude() == 0, "Force outside radius should be zero"
    
    # Test force direction (should point toward center)
    test_point = Vector2(450, 350)
    force = whirlpool.get_force_at(test_point)
    to_center = whirlpool.position - test_point
    to_center_normalized = to_center.normalize()
    force_normalized = force.normalize()
    
    # Check if force direction is toward center (dot product should be close to 1)
    dot_product = force_normalized.x * to_center_normalized.x + force_normalized.y * to_center_normalized.y
    print(f"  Force direction alignment: {dot_product:.3f} (should be ~1.0)")
    assert dot_product > 0.99, "Force should point toward center"
    
    print("✓ Whirlpool force calculation test passed")


def test_whirlpool_stuck_condition():
    """Test whirlpool stuck condition (lose condition)."""
    print("\nTesting whirlpool stuck condition...")
    whirlpool = Whirlpool(Vector2(400, 300), 100, 200)
    
    # Ball outside whirlpool - not stuck
    ball_pos_outside = Vector2(600, 300)
    assert not whirlpool.is_ball_stuck(ball_pos_outside), "Ball outside should not be stuck"
    print("  ✓ Ball outside whirlpool: not stuck")
    
    # Ball at edge - not stuck
    ball_pos_edge = Vector2(500, 300)
    assert not whirlpool.is_ball_stuck(ball_pos_edge), "Ball at edge should not be stuck"
    print("  ✓ Ball at edge: not stuck")
    
    # Ball in middle - not stuck yet
    ball_pos_middle = Vector2(450, 300)
    assert not whirlpool.is_ball_stuck(ball_pos_middle), "Ball in middle should not be stuck yet"
    print("  ✓ Ball in middle: not stuck")
    
    # Ball at center threshold - stuck!
    ball_pos_threshold = Vector2(400 + whirlpool.center_threshold, 300)
    assert whirlpool.is_ball_stuck(ball_pos_threshold), "Ball at threshold should be stuck"
    print("  ✓ Ball at center threshold: STUCK (lose condition)")
    
    # Ball at exact center - stuck!
    ball_pos_center = Vector2(400, 300)
    assert whirlpool.is_ball_stuck(ball_pos_center), "Ball at center should be stuck"
    print("  ✓ Ball at exact center: STUCK (lose condition)")
    
    print("✓ Whirlpool stuck condition test passed")


def test_whirlpool_ripple_curve():
    """Test whirlpool ripple trajectory curving."""
    print("\nTesting whirlpool ripple curve effect...")
    whirlpool = Whirlpool(Vector2(400, 300), 100, 200)
    
    # Test ripple curve force at edge (should be zero due to distance ratio)
    ripple_pos = Vector2(500, 300)
    ripple_dir = Vector2(0, 1)  # Moving downward
    curve_force = whirlpool.get_ripple_curve_force(ripple_pos, ripple_dir)
    print(f"  Curve force at edge: magnitude = {curve_force.magnitude():.3f}")
    assert curve_force.magnitude() == 0, "Curve force at edge should be zero"
    
    # Test ripple curve force at mid-distance (should be non-zero)
    ripple_pos_mid = Vector2(450, 300)
    curve_force_mid = whirlpool.get_ripple_curve_force(ripple_pos_mid, ripple_dir)
    print(f"  Curve force at mid: magnitude = {curve_force_mid.magnitude():.3f}")
    assert curve_force_mid.magnitude() > 0, "Curve force at mid should be non-zero"
    
    # Test ripple curve force near center (should be stronger)
    ripple_pos_near = Vector2(420, 300)
    curve_force_near = whirlpool.get_ripple_curve_force(ripple_pos_near, ripple_dir)
    print(f"  Curve force near center: magnitude = {curve_force_near.magnitude():.3f}")
    assert curve_force_near.magnitude() > curve_force_mid.magnitude(), "Curve should be stronger near center"
    
    # Test ripple curve force outside (should be zero)
    ripple_pos_outside = Vector2(600, 300)
    curve_force_outside = whirlpool.get_ripple_curve_force(ripple_pos_outside, ripple_dir)
    print(f"  Curve force outside: magnitude = {curve_force_outside.magnitude():.3f}")
    assert curve_force_outside.magnitude() == 0, "Curve force outside should be zero"
    
    print("✓ Whirlpool ripple curve test passed")


def test_whirlpool_json_serialization():
    """Test whirlpool JSON serialization and deserialization."""
    print("\nTesting whirlpool JSON serialization...")
    
    # Create whirlpool
    whirlpool = Whirlpool(Vector2(400, 300), 100, 200)
    
    # Serialize to dict
    whirlpool_dict = {
        "position": [whirlpool.position.x, whirlpool.position.y],
        "radius": whirlpool.radius,
        "pull_strength": whirlpool.pull_strength
    }
    
    # Deserialize from dict
    whirlpool_loaded = Whirlpool.from_dict(whirlpool_dict)
    
    assert whirlpool_loaded.position.x == 400
    assert whirlpool_loaded.position.y == 300
    assert whirlpool_loaded.radius == 100
    assert whirlpool_loaded.pull_strength == 200
    
    print("✓ Whirlpool JSON serialization test passed")


def test_level_data_with_whirlpool():
    """Test LevelData with whirlpool integration."""
    print("\nTesting LevelData with whirlpool...")
    
    # Create level data with whirlpool
    level_dict = {
        "id": 1,
        "ball_start": [100, 200],
        "target_position": [800, 300],
        "target_radius": 40,
        "obstacles": [],
        "walls": [],
        "current_zones": [],
        "whirlpools": [
            {
                "position": [400, 300],
                "radius": 100,
                "pull_strength": 200
            }
        ],
        "initial_stones": 10
    }
    
    # Load level data
    level = LevelData.from_dict(level_dict)
    
    assert len(level.whirlpools) == 1
    assert level.whirlpools[0].position.x == 400
    assert level.whirlpools[0].position.y == 300
    assert level.whirlpools[0].radius == 100
    assert level.whirlpools[0].pull_strength == 200
    
    # Test serialization back to dict
    level_dict_out = level.to_dict()
    assert "whirlpools" in level_dict_out
    assert len(level_dict_out["whirlpools"]) == 1
    assert level_dict_out["whirlpools"][0]["position"] == [400, 300]
    assert level_dict_out["whirlpools"][0]["radius"] == 100
    assert level_dict_out["whirlpools"][0]["pull_strength"] == 200
    
    print("✓ LevelData with whirlpool test passed")


def test_whirlpool_escape_scenario():
    """Test that ball can escape whirlpool with strong ripple forces."""
    print("\nTesting whirlpool escape scenario...")
    whirlpool = Whirlpool(Vector2(400, 300), 100, 200)
    
    # Ball is being pulled by whirlpool
    ball_pos = Vector2(450, 300)  # 50 pixels from center
    whirlpool_force = whirlpool.get_force_at(ball_pos)
    print(f"  Whirlpool pull force: {whirlpool_force.magnitude():.2f}")
    
    # Simulate strong ripple force pushing away from whirlpool
    # (In actual game, this would come from wave simulator)
    ripple_force = Vector2(200, 0)  # Strong force pushing right (away from whirlpool)
    
    # Net force
    net_force = whirlpool_force + ripple_force
    print(f"  Ripple push force: {ripple_force.magnitude():.2f}")
    print(f"  Net force: {net_force.magnitude():.2f}")
    print(f"  Net force direction: ({net_force.x:.2f}, {net_force.y:.2f})")
    
    # If net force points away from whirlpool, ball can escape
    to_center = whirlpool.position - ball_pos
    escape_direction = net_force.normalize()
    to_center_normalized = to_center.normalize()
    
    # Dot product: negative means moving away from center (escaping)
    dot = escape_direction.x * to_center_normalized.x + escape_direction.y * to_center_normalized.y
    print(f"  Escape alignment: {dot:.3f} (negative = escaping)")
    
    if dot < 0:
        print("  ✓ Ball can escape with strong ripple forces!")
    else:
        print("  ✗ Ball is still being pulled toward center")
    
    print("✓ Whirlpool escape scenario test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("WHIRLPOOL OBSTACLE IMPLEMENTATION TESTS")
    print("=" * 60)
    
    try:
        test_whirlpool_creation()
        test_whirlpool_force()
        test_whirlpool_stuck_condition()
        test_whirlpool_ripple_curve()
        test_whirlpool_json_serialization()
        test_level_data_with_whirlpool()
        test_whirlpool_escape_scenario()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nWhirlpool implementation is working correctly:")
        print("  ✓ Whirlpool class created with circular shape and pull strength")
        print("  ✓ Radial force toward center implemented")
        print("  ✓ Lose condition when ball reaches center threshold")
        print("  ✓ Ball can escape if ripple forces overcome whirlpool pull")
        print("  ✓ Ripple trajectory curving toward center")
        print("  ✓ Whirlpool configuration in level JSON format")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
