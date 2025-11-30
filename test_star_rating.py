#!/usr/bin/env python3
"""
Test script for star rating system
"""

from game.level import LevelManager, LevelData
from game.physics import Vector2

# Create a simple test level
test_level = LevelData(
    level_id=1,
    ball_start=Vector2(100, 300),
    target_position=Vector2(700, 300),
    target_radius=40,
    obstacles=[],
    walls=[],
    current_zones=[],
    whirlpools=[],
    initial_stones=10,
    tutorial=False
)

# Create level manager with test level
level_manager = LevelManager([test_level])

# Test star rating calculation
print("Testing Star Rating System")
print("=" * 50)

test_cases = [
    (3, 3, "Perfect! Used 3 stones"),
    (5, 3, "Excellent! Used 5 stones"),
    (6, 2, "Good! Used 6 stones"),
    (8, 2, "Good! Used 8 stones"),
    (9, 1, "Okay. Used 9 stones"),
    (10, 1, "Okay. Used 10 stones"),
    (11, 0, "No stars. Used 11 stones"),
    (15, 0, "No stars. Used 15 stones"),
]

for stones_used, expected_stars, description in test_cases:
    actual_stars = level_manager.calculate_star_rating(stones_used)
    status = "✓" if actual_stars == expected_stars else "✗"
    print(f"{status} {description}: {actual_stars} stars (expected {expected_stars})")

print("=" * 50)
print("Star Rating Formula:")
print("  ≤5 stones = 3 stars ⭐⭐⭐")
print("  ≤8 stones = 2 stars ⭐⭐")
print("  ≤10 stones = 1 star ⭐")
print("  >10 stones = 0 stars")
print("=" * 50)

# Test stones_used_this_level tracking
print("\nTesting stones_used_this_level tracking:")
print("=" * 50)

# Initialize level
from game.physics import Ball
level_manager.initialize_level(Ball, 0)

print(f"Initial stones_used_this_level: {level_manager.stones_used_this_level}")

# Simulate using stones
for i in range(1, 6):
    level_manager.use_stone()
    print(f"After using stone {i}: stones_used_this_level = {level_manager.stones_used_this_level}")

# Calculate star rating
stars = level_manager.calculate_star_rating(level_manager.stones_used_this_level)
print(f"\nFinal star rating: {stars} stars")

print("=" * 50)
print("All tests completed!")
