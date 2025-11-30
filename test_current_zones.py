"""
Test script to verify Current Zone implementation.
Tests:
1. CurrentZone class creation
2. Force calculation at different positions
3. Multiple overlapping currents (vectorial addition)
4. Ripple speed modifier based on alignment
"""

from game.physics import Vector2
from game.level import CurrentZone

def test_current_zone_creation():
    """Test CurrentZone creation and basic properties."""
    print("Test 1: CurrentZone creation")
    zone = CurrentZone(
        position=Vector2(500, 400),
        size=[150, 100],
        strength=200,
        direction=Vector2(1, 0)
    )
    
    assert zone.position.x == 500
    assert zone.position.y == 400
    assert zone.size == [150, 100]
    assert zone.strength == 200
    assert abs(zone.direction.magnitude() - 1.0) < 0.001  # Should be normalized
    print("✓ CurrentZone created successfully")
    print(f"  Position: {zone.position}")
    print(f"  Size: {zone.size}")
    print(f"  Strength: {zone.strength}")
    print(f"  Direction: {zone.direction} (magnitude: {zone.direction.magnitude()})")
    print()

def test_point_inside():
    """Test point inside detection."""
    print("Test 2: Point inside detection")
    zone = CurrentZone(
        position=Vector2(500, 400),
        size=[150, 100],
        strength=200,
        direction=Vector2(1, 0)
    )
    
    # Point inside
    inside_point = Vector2(500, 400)
    assert zone.is_point_inside(inside_point) == True
    print(f"✓ Point {inside_point} is inside zone")
    
    # Point at edge (should be inside)
    edge_point = Vector2(575, 400)  # 75 pixels from center (half width)
    assert zone.is_point_inside(edge_point) == True
    print(f"✓ Point {edge_point} is at edge (inside)")
    
    # Point outside
    outside_point = Vector2(700, 400)
    assert zone.is_point_inside(outside_point) == False
    print(f"✓ Point {outside_point} is outside zone")
    print()

def test_force_calculation():
    """Test force calculation."""
    print("Test 3: Force calculation")
    zone = CurrentZone(
        position=Vector2(500, 400),
        size=[150, 100],
        strength=200,
        direction=Vector2(1, 0)
    )
    
    # Force inside zone
    inside_point = Vector2(500, 400)
    force = zone.get_force_at(inside_point)
    print(f"✓ Force at {inside_point}: {force}")
    assert force.x == 200  # Should be strength * direction
    assert force.y == 0
    
    # Force outside zone
    outside_point = Vector2(700, 400)
    force = zone.get_force_at(outside_point)
    print(f"✓ Force at {outside_point}: {force}")
    assert force.x == 0
    assert force.y == 0
    print()

def test_multiple_overlapping_currents():
    """Test multiple overlapping current zones (vectorial addition)."""
    print("Test 4: Multiple overlapping currents")
    
    # Create two zones with perpendicular directions
    zone1 = CurrentZone(
        position=Vector2(500, 400),
        size=[200, 200],
        strength=100,
        direction=Vector2(1, 0)  # Right
    )
    
    zone2 = CurrentZone(
        position=Vector2(500, 400),
        size=[200, 200],
        strength=100,
        direction=Vector2(0, 1)  # Down
    )
    
    # Point inside both zones
    test_point = Vector2(500, 400)
    
    force1 = zone1.get_force_at(test_point)
    force2 = zone2.get_force_at(test_point)
    total_force = force1 + force2
    
    print(f"  Zone 1 force: {force1}")
    print(f"  Zone 2 force: {force2}")
    print(f"  Total force: {total_force}")
    
    # Verify vectorial addition
    assert total_force.x == 100
    assert total_force.y == 100
    print("✓ Forces add vectorially correctly")
    
    # Verify magnitude (should be sqrt(100^2 + 100^2) = 141.42...)
    magnitude = total_force.magnitude()
    expected_magnitude = 141.42
    assert abs(magnitude - expected_magnitude) < 1.0
    print(f"✓ Total force magnitude: {magnitude:.2f} (expected ~{expected_magnitude})")
    print()

def test_ripple_speed_modifier():
    """Test ripple speed modifier based on alignment."""
    print("Test 5: Ripple speed modifier")
    
    zone = CurrentZone(
        position=Vector2(500, 400),
        size=[150, 100],
        strength=200,
        direction=Vector2(1, 0)  # Right
    )
    
    # Ripple moving in same direction (aligned)
    aligned_direction = Vector2(1, 0)
    modifier = zone.get_ripple_speed_modifier(aligned_direction)
    print(f"  Aligned ripple (same direction): {modifier}x speed")
    assert abs(modifier - 1.5) < 0.001  # Should be 1.5x
    
    # Ripple moving in opposite direction
    opposite_direction = Vector2(-1, 0)
    modifier = zone.get_ripple_speed_modifier(opposite_direction)
    print(f"  Opposite ripple: {modifier}x speed")
    assert abs(modifier - 0.5) < 0.001  # Should be 0.5x
    
    # Ripple moving perpendicular
    perpendicular_direction = Vector2(0, 1)
    modifier = zone.get_ripple_speed_modifier(perpendicular_direction)
    print(f"  Perpendicular ripple: {modifier}x speed")
    assert abs(modifier - 1.0) < 0.001  # Should be 1.0x
    
    print("✓ Ripple speed modifiers work correctly")
    print()

def test_from_dict():
    """Test creating CurrentZone from dictionary."""
    print("Test 6: Creating CurrentZone from dictionary")
    
    data = {
        "position": [500, 400],
        "size": [150, 100],
        "strength": 200,
        "direction": [1, 0]
    }
    
    zone = CurrentZone.from_dict(data)
    
    assert zone.position.x == 500
    assert zone.position.y == 400
    assert zone.size == [150, 100]
    assert zone.strength == 200
    assert abs(zone.direction.x - 1.0) < 0.001
    assert abs(zone.direction.y - 0.0) < 0.001
    
    print("✓ CurrentZone created from dictionary successfully")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Current Zone Implementation Tests")
    print("=" * 60)
    print()
    
    try:
        test_current_zone_creation()
        test_point_inside()
        test_force_calculation()
        test_multiple_overlapping_currents()
        test_ripple_speed_modifier()
        test_from_dict()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
