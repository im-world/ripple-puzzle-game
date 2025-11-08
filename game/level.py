"""
Level module for Ripple game.
Handles level data structures, loading, and management.
"""

import json
import os
from typing import List, Optional, Dict, Any
from game.physics import Vector2
from game.config import INITIAL_STONES


class Obstacle:
    """Obstacle entity (e.g., anti-ripple zone)."""
    
    def __init__(self, obstacle_type: str, position: Vector2, size: Any):
        self.type = obstacle_type  # "anti_ripple_zone"
        self.position = position.copy()
        self.size = size  # Can be Vector2 for rectangle or float for circle
    
    def is_point_inside(self, point: Vector2) -> bool:
        """Check if a point is inside this obstacle."""
        if self.type == "anti_ripple_zone":
            # Assume rectangular obstacle for now
            if isinstance(self.size, (list, tuple)) and len(self.size) == 2:
                # Rectangle: size is [width, height]
                width, height = self.size
                half_w = width / 2
                half_h = height / 2
                return (abs(point.x - self.position.x) <= half_w and
                        abs(point.y - self.position.y) <= half_h)
            elif isinstance(self.size, (int, float)):
                # Circle: size is radius
                distance = (point - self.position).magnitude()
                return distance <= self.size
        return False
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Obstacle':
        """Create Obstacle from dictionary."""
        obstacle_type = data.get("type", "anti_ripple_zone")
        position = Vector2(data["position"][0], data["position"][1])
        size = data["size"]
        return Obstacle(obstacle_type, position, size)


class LevelData:
    """Level data structure."""
    
    def __init__(self, level_id: int, ball_start: Vector2, target_position: Vector2,
                 target_radius: float, obstacles: List[Obstacle] = None,
                 initial_stones: int = INITIAL_STONES):
        self.id = level_id
        self.ball_start = ball_start.copy()
        self.target_position = target_position.copy()
        self.target_radius = target_radius
        self.obstacles = obstacles if obstacles is not None else []
        self.initial_stones = initial_stones
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LevelData':
        """Create LevelData from dictionary."""
        level_id = data["id"]
        ball_start = Vector2(data["ball_start"][0], data["ball_start"][1])
        target_position = Vector2(data["target_position"][0], data["target_position"][1])
        target_radius = data["target_radius"]
        
        obstacles = []
        if "obstacles" in data:
            for obs_data in data["obstacles"]:
                obstacles.append(Obstacle.from_dict(obs_data))
        
        initial_stones = data.get("initial_stones", INITIAL_STONES)
        
        return LevelData(level_id, ball_start, target_position, target_radius,
                        obstacles, initial_stones)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert LevelData to dictionary."""
        return {
            "id": self.id,
            "ball_start": [self.ball_start.x, self.ball_start.y],
            "target_position": [self.target_position.x, self.target_position.y],
            "target_radius": self.target_radius,
            "obstacles": [
                {
                    "type": obs.type,
                    "position": [obs.position.x, obs.position.y],
                    "size": obs.size
                }
                for obs in self.obstacles
            ],
            "initial_stones": self.initial_stones
        }


def load_levels_from_json(filepath: str) -> List[LevelData]:
    """
    Load levels from JSON file.
    Returns list of LevelData objects.
    Raises exception if file not found or invalid format.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Level file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    if "levels" not in data:
        raise ValueError("Invalid level file format: missing 'levels' key")
    
    levels = []
    for level_data in data["levels"]:
        # Validate required fields
        required_fields = ["id", "ball_start", "target_position", "target_radius"]
        for field in required_fields:
            if field not in level_data:
                raise ValueError(f"Level {level_data.get('id', '?')} missing required field: {field}")
        
        levels.append(LevelData.from_dict(level_data))
    
    return levels


def get_default_level() -> LevelData:
    """Return a default level as fallback."""
    return LevelData(
        level_id=1,
        ball_start=Vector2(150, 300),
        target_position=Vector2(800, 300),
        target_radius=40,
        obstacles=[],
        initial_stones=INITIAL_STONES
    )


def load_levels_with_fallback(filepath: str) -> List[LevelData]:
    """
    Load levels from JSON file with error handling and fallback.
    Returns list of LevelData objects. If loading fails, returns default level.
    """
    try:
        return load_levels_from_json(filepath)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Failed to load levels from {filepath}: {e}")
        print("Using default level as fallback.")
        return [get_default_level()]


class LevelManager:
    """Manages level state and progression."""
    
    def __init__(self, levels: List[LevelData]):
        self.levels = levels
        self.current_level_index = 0
        self.current_level: Optional[LevelData] = None
        self.ball = None
        self.is_level_complete = False
        
        # Stone inventory management
        self.stones_remaining = INITIAL_STONES
        self.total_stones_used = 0
    
    def get_current_level(self) -> Optional[LevelData]:
        """Get the current level data."""
        return self.current_level
    
    def get_current_level_number(self) -> int:
        """Get the current level number (1-indexed)."""
        return self.current_level_index + 1
    
    def has_next_level(self) -> bool:
        """Check if there is a next level available."""
        return self.current_level_index + 1 < len(self.levels)
    
    def initialize_level(self, ball_class, level_index: Optional[int] = None):
        """
        Initialize a level by loading data, spawning ball, and setting target.
        If level_index is provided, jump to that level. Otherwise, use current_level_index.
        """
        if level_index is not None:
            if 0 <= level_index < len(self.levels):
                self.current_level_index = level_index
            else:
                raise ValueError(f"Invalid level index: {level_index}")
        
        # Load level data
        self.current_level = self.levels[self.current_level_index]
        
        # Spawn ball at starting position
        self.ball = ball_class(self.current_level.ball_start)
        
        # Reset level completion flag
        self.is_level_complete = False
    
    def check_level_completion(self, ball_position: Vector2) -> bool:
        """
        Check if the ball has reached the target (level completion).
        Returns True if level is complete, False otherwise.
        """
        if self.current_level is None:
            return False
        
        # Calculate distance from ball to target
        distance = (ball_position - self.current_level.target_position).magnitude()
        
        # Check if ball is within target radius
        if distance <= self.current_level.target_radius:
            self.is_level_complete = True
            return True
        
        return False
    
    def transition_to_next_level(self, ball_class) -> bool:
        """
        Transition to the next level.
        Returns True if transition successful, False if no more levels.
        """
        if not self.has_next_level():
            return False
        
        self.current_level_index += 1
        self.initialize_level(ball_class)
        return True
    
    def reset_current_level(self, ball_class):
        """Reset the current level (restart)."""
        self.initialize_level(ball_class, self.current_level_index)
    
    def get_stones_remaining(self) -> int:
        """Get the number of stones remaining."""
        return self.stones_remaining
    
    def get_total_stones_used(self) -> int:
        """Get the total number of stones used across all levels."""
        return self.total_stones_used
    
    def use_stone(self) -> bool:
        """
        Decrement stone counter when a stone is launched.
        Returns True if stone was used, False if no stones remaining.
        """
        if self.stones_remaining > 0:
            self.stones_remaining -= 1
            self.total_stones_used += 1
            return True
        return False
    
    def has_stones(self) -> bool:
        """Check if player has stones remaining."""
        return self.stones_remaining > 0
    
    def check_game_over(self) -> bool:
        """
        Check if game over condition is met (stones depleted and ball not at target).
        Returns True if game over, False otherwise.
        """
        return self.stones_remaining == 0 and not self.is_level_complete
    
    def reset_stones_for_new_game(self):
        """Reset stone counter to initial value for a new game."""
        self.stones_remaining = INITIAL_STONES
        self.total_stones_used = 0


class CollisionDetector:
    """Handles collision detection for game entities."""
    
    @staticmethod
    def circle_circle_collision(pos1: Vector2, radius1: float, pos2: Vector2, radius2: float) -> bool:
        """
        Check collision between two circles.
        Returns True if circles overlap, False otherwise.
        """
        distance = (pos1 - pos2).magnitude()
        return distance <= (radius1 + radius2)
    
    @staticmethod
    def point_in_aabb(point: Vector2, aabb_center: Vector2, aabb_size: List[float]) -> bool:
        """
        Check if a point is inside an axis-aligned bounding box (AABB).
        aabb_size is [width, height].
        Returns True if point is inside, False otherwise.
        """
        width, height = aabb_size
        half_w = width / 2
        half_h = height / 2
        
        return (abs(point.x - aabb_center.x) <= half_w and
                abs(point.y - aabb_center.y) <= half_h)
    
    @staticmethod
    def circle_aabb_collision(circle_pos: Vector2, circle_radius: float,
                             aabb_center: Vector2, aabb_size: List[float]) -> bool:
        """
        Check collision between a circle and an AABB.
        Returns True if they overlap, False otherwise.
        """
        width, height = aabb_size
        half_w = width / 2
        half_h = height / 2
        
        # Find the closest point on the AABB to the circle center
        closest_x = max(aabb_center.x - half_w, min(circle_pos.x, aabb_center.x + half_w))
        closest_y = max(aabb_center.y - half_h, min(circle_pos.y, aabb_center.y + half_h))
        
        # Calculate distance from circle center to closest point
        closest_point = Vector2(closest_x, closest_y)
        distance = (circle_pos - closest_point).magnitude()
        
        return distance <= circle_radius
    
    @staticmethod
    def check_ball_target_collision(ball_pos: Vector2, ball_radius: float,
                                    target_pos: Vector2, target_radius: float) -> bool:
        """
        Check if ball has reached the target spot.
        Returns True if ball is within target, False otherwise.
        """
        return CollisionDetector.circle_circle_collision(ball_pos, ball_radius, target_pos, target_radius)
    
    @staticmethod
    def check_ball_obstacle_collision(ball_pos: Vector2, ball_radius: float,
                                     obstacle: Obstacle) -> bool:
        """
        Check if ball collides with an obstacle.
        Returns True if collision detected, False otherwise.
        """
        if obstacle.type == "anti_ripple_zone":
            if isinstance(obstacle.size, (list, tuple)) and len(obstacle.size) == 2:
                # Rectangle obstacle
                return CollisionDetector.circle_aabb_collision(ball_pos, ball_radius,
                                                              obstacle.position, obstacle.size)
            elif isinstance(obstacle.size, (int, float)):
                # Circle obstacle
                return CollisionDetector.circle_circle_collision(ball_pos, ball_radius,
                                                                obstacle.position, obstacle.size)
        return False
    
    @staticmethod
    def is_ripple_blocked_by_obstacle(ripple_pos: Vector2, target_pos: Vector2,
                                     obstacle: Obstacle) -> bool:
        """
        Check if a ripple's propagation to a target position is blocked by an obstacle.
        This checks if the line segment from ripple to target intersects the obstacle.
        Returns True if blocked, False otherwise.
        """
        if obstacle.type == "anti_ripple_zone":
            # Simple approach: check if target position is inside the obstacle
            # More sophisticated approach would check line-segment intersection
            return obstacle.is_point_inside(target_pos)
        return False

