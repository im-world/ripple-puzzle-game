"""
Level module for Ripple game.
Handles level data structures, loading, and management.
"""

import json
import os
from typing import List, Optional, Dict, Any
from game.physics import Vector2
from game.config import INITIAL_STONES


class Wall:
    """Wall obstacle that reflects ripples and bounces the ball."""
    
    def __init__(self, position: Vector2, length: float, rotation: float):
        """
        Initialize a wall obstacle.
        
        Args:
            position: Center position of the wall
            length: Length of the wall in pixels
            rotation: Rotation angle in radians (0 = horizontal, π/2 = vertical)
        """
        self.position = position.copy()
        self.length = length
        self.rotation = rotation  # Angle in radians
        self.thickness = 10  # Wall thickness for collision detection
        
        # Calculate wall endpoints for collision detection
        import math
        half_length = length / 2
        self.start = Vector2(
            position.x - half_length * math.cos(rotation),
            position.y - half_length * math.sin(rotation)
        )
        self.end = Vector2(
            position.x + half_length * math.cos(rotation),
            position.y + half_length * math.sin(rotation)
        )
        
        # Calculate wall normal vector (perpendicular to wall)
        self.normal = Vector2(-math.sin(rotation), math.cos(rotation))
    
    def get_reflection_vector(self, incident_vector: Vector2) -> Vector2:
        """
        Calculate reflection vector using angle of incidence.
        Formula: R = I - 2(I·N)N where I is incident, N is normal, R is reflection
        
        Args:
            incident_vector: Incoming direction vector (normalized)
        
        Returns:
            Reflected direction vector (normalized)
        """
        # Dot product of incident and normal
        dot = incident_vector.x * self.normal.x + incident_vector.y * self.normal.y
        
        # Reflection formula: R = I - 2(I·N)N
        reflection = Vector2(
            incident_vector.x - 2 * dot * self.normal.x,
            incident_vector.y - 2 * dot * self.normal.y
        )
        
        return reflection.normalize()
    
    def distance_to_point(self, point: Vector2) -> float:
        """
        Calculate shortest distance from a point to the wall line segment.
        
        Args:
            point: Point to check distance from
        
        Returns:
            Distance in pixels
        """
        # Vector from start to end
        wall_vec = self.end - self.start
        wall_length_sq = wall_vec.x * wall_vec.x + wall_vec.y * wall_vec.y
        
        if wall_length_sq == 0:
            # Wall has zero length, return distance to start point
            return (point - self.start).magnitude()
        
        # Vector from start to point
        point_vec = point - self.start
        
        # Project point onto wall line (clamped to segment)
        t = max(0, min(1, (point_vec.x * wall_vec.x + point_vec.y * wall_vec.y) / wall_length_sq))
        
        # Find closest point on wall segment
        closest = Vector2(
            self.start.x + t * wall_vec.x,
            self.start.y + t * wall_vec.y
        )
        
        # Return distance
        return (point - closest).magnitude()
    
    def get_closest_point_on_wall(self, point: Vector2) -> Vector2:
        """
        Get the closest point on the wall to a given point.
        
        Args:
            point: Point to find closest wall point to
        
        Returns:
            Closest point on wall segment
        """
        # Vector from start to end
        wall_vec = self.end - self.start
        wall_length_sq = wall_vec.x * wall_vec.x + wall_vec.y * wall_vec.y
        
        if wall_length_sq == 0:
            return self.start.copy()
        
        # Vector from start to point
        point_vec = point - self.start
        
        # Project point onto wall line (clamped to segment)
        t = max(0, min(1, (point_vec.x * wall_vec.x + point_vec.y * wall_vec.y) / wall_length_sq))
        
        # Return closest point
        return Vector2(
            self.start.x + t * wall_vec.x,
            self.start.y + t * wall_vec.y
        )


class CurrentZone:
    """Current Zone obstacle that applies constant force to ball and affects ripple propagation."""
    
    def __init__(self, position: Vector2, size: list, strength: float, direction: Vector2):
        """
        Initialize a current zone obstacle.
        
        Args:
            position: Center position of the rectangular zone
            size: [width, height] of the rectangular area
            strength: Force magnitude applied to ball (pixels/second²)
            direction: Direction vector (will be normalized)
        """
        self.position = position.copy()
        self.size = size  # [width, height]
        self.strength = strength
        self.direction = direction.normalize()  # Ensure normalized
        self.type = "current_zone"
    
    def is_point_inside(self, point: Vector2) -> bool:
        """Check if a point is inside this current zone."""
        width, height = self.size
        half_w = width / 2
        half_h = height / 2
        return (abs(point.x - self.position.x) <= half_w and
                abs(point.y - self.position.y) <= half_h)
    
    def get_force_at(self, point: Vector2) -> Vector2:
        """
        Get the force applied by this current zone at a given point.
        Returns zero vector if point is outside the zone.
        
        Args:
            point: Position to check
        
        Returns:
            Force vector
        """
        if self.is_point_inside(point):
            return self.direction * self.strength
        return Vector2(0, 0)
    
    def get_ripple_speed_modifier(self, ripple_direction: Vector2) -> float:
        """
        Calculate ripple speed modifier based on alignment with current direction.
        Ripples move faster when aligned with current, slower when against it.
        
        Args:
            ripple_direction: Direction of ripple propagation (normalized)
        
        Returns:
            Speed multiplier (0.5 to 1.5)
        """
        # Dot product gives alignment: 1 = same direction, -1 = opposite, 0 = perpendicular
        alignment = ripple_direction.x * self.direction.x + ripple_direction.y * self.direction.y
        
        # Map alignment to speed modifier: -1 -> 0.5x, 0 -> 1.0x, 1 -> 1.5x
        return 1.0 + alignment * 0.5
    
    @staticmethod
    def from_dict(data: dict) -> 'CurrentZone':
        """Create CurrentZone from dictionary."""
        position = Vector2(data["position"][0], data["position"][1])
        size = data["size"]
        strength = data["strength"]
        direction = Vector2(data["direction"][0], data["direction"][1])
        return CurrentZone(position, size, strength, direction)


class Whirlpool:
    """Whirlpool obstacle that pulls ball toward center and curves ripple trajectories."""
    
    def __init__(self, position: Vector2, radius: float, pull_strength: float):
        """
        Initialize a whirlpool obstacle.
        
        Args:
            position: Center position of the whirlpool
            radius: Outer radius of the whirlpool effect
            pull_strength: Force magnitude pulling toward center (pixels/second²)
        """
        self.position = position.copy()
        self.radius = radius
        self.pull_strength = pull_strength
        self.center_threshold = radius * 0.15  # Ball is stuck if within 15% of radius
        self.type = "whirlpool"
    
    def get_force_at(self, point: Vector2) -> Vector2:
        """
        Calculate radial force pulling toward whirlpool center.
        Force increases as distance to center decreases.
        
        Args:
            point: Position to check
        
        Returns:
            Force vector pointing toward center
        """
        to_center = self.position - point
        distance = to_center.magnitude()
        
        # No force if outside whirlpool radius
        if distance > self.radius:
            return Vector2(0, 0)
        
        # Avoid division by zero at exact center
        if distance < 0.1:
            return Vector2(0, 0)
        
        # Force increases as we get closer to center (inverse square-like)
        # At edge: minimal force, at center: maximum force
        distance_ratio = 1.0 - (distance / self.radius)  # 0 at edge, 1 at center
        force_magnitude = self.pull_strength * (distance_ratio ** 2)  # Quadratic increase
        
        # Direction toward center
        direction = to_center.normalize()
        
        return direction * force_magnitude
    
    def is_ball_stuck(self, ball_position: Vector2) -> bool:
        """
        Check if ball has reached the center threshold and is stuck orbiting.
        
        Args:
            ball_position: Current ball position
        
        Returns:
            True if ball is stuck (lose condition), False otherwise
        """
        distance = (ball_position - self.position).magnitude()
        return distance <= self.center_threshold
    
    def get_ripple_curve_force(self, ripple_position: Vector2, ripple_direction: Vector2) -> Vector2:
        """
        Calculate force that curves ripple trajectory toward whirlpool center.
        This affects ripple propagation direction.
        
        Args:
            ripple_position: Current position on ripple wavefront
            ripple_direction: Current direction of ripple propagation (normalized)
        
        Returns:
            Force vector to add to ripple direction (will be normalized by caller)
        """
        to_center = self.position - ripple_position
        distance = to_center.magnitude()
        
        # No effect if outside whirlpool radius
        if distance > self.radius:
            return Vector2(0, 0)
        
        # Avoid division by zero
        if distance < 0.1:
            return Vector2(0, 0)
        
        # Curve strength increases closer to center
        distance_ratio = 1.0 - (distance / self.radius)
        curve_strength = distance_ratio * 0.5  # Max 50% influence on direction
        
        # Direction toward center
        direction = to_center.normalize()
        
        return direction * curve_strength
    
    @staticmethod
    def from_dict(data: dict) -> 'Whirlpool':
        """Create Whirlpool from dictionary."""
        position = Vector2(data["position"][0], data["position"][1])
        radius = data["radius"]
        pull_strength = data["pull_strength"]
        return Whirlpool(position, radius, pull_strength)


class Obstacle:
    """Obstacle entity (e.g., anti-ripple zone)."""
    
    def __init__(self, obstacle_type: str, position: Vector2, size: Any, blocks_ripple_rendering: bool = True):
        self.type = obstacle_type  # "anti_ripple_zone", "wall", "whirlpool", etc.
        self.position = position.copy()
        self.size = size  # Can be Vector2 for rectangle or float for circle
        self.blocks_ripple_rendering = blocks_ripple_rendering  # Whether ripples are visually blocked
    
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
        blocks_ripple_rendering = data.get("blocks_ripple_rendering", True)
        return Obstacle(obstacle_type, position, size, blocks_ripple_rendering)


class LevelData:
    """Level data structure."""
    
    def __init__(self, level_id: int, ball_start: Vector2, target_position: Vector2,
                 target_radius: float, obstacles: List[Obstacle] = None,
                 walls: List[Wall] = None,
                 current_zones: List[CurrentZone] = None,
                 whirlpools: List[Whirlpool] = None,
                 initial_stones: int = INITIAL_STONES,
                 tutorial: bool = False):
        self.id = level_id
        self.ball_start = ball_start.copy()
        self.target_position = target_position.copy()
        self.target_radius = target_radius
        self.obstacles = obstacles if obstacles is not None else []
        self.walls = walls if walls is not None else []
        self.current_zones = current_zones if current_zones is not None else []
        self.whirlpools = whirlpools if whirlpools is not None else []
        self.initial_stones = initial_stones
        self.tutorial = tutorial
    
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
        
        walls = []
        if "walls" in data:
            for wall_data in data["walls"]:
                position = Vector2(wall_data["position"][0], wall_data["position"][1])
                length = wall_data["length"]
                rotation = wall_data["rotation"]
                walls.append(Wall(position, length, rotation))
        
        current_zones = []
        if "current_zones" in data:
            for zone_data in data["current_zones"]:
                current_zones.append(CurrentZone.from_dict(zone_data))
        
        whirlpools = []
        if "whirlpools" in data:
            for whirlpool_data in data["whirlpools"]:
                whirlpools.append(Whirlpool.from_dict(whirlpool_data))
        
        initial_stones = data.get("initial_stones", INITIAL_STONES)
        tutorial = data.get("tutorial", False)
        
        return LevelData(level_id, ball_start, target_position, target_radius,
                        obstacles, walls, current_zones, whirlpools, initial_stones, tutorial)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert LevelData to dictionary."""
        result = {
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
            "walls": [
                {
                    "position": [wall.position.x, wall.position.y],
                    "length": wall.length,
                    "rotation": wall.rotation
                }
                for wall in self.walls
            ],
            "current_zones": [
                {
                    "position": [zone.position.x, zone.position.y],
                    "size": zone.size,
                    "strength": zone.strength,
                    "direction": [zone.direction.x, zone.direction.y]
                }
                for zone in self.current_zones
            ],
            "whirlpools": [
                {
                    "position": [whirlpool.position.x, whirlpool.position.y],
                    "radius": whirlpool.radius,
                    "pull_strength": whirlpool.pull_strength
                }
                for whirlpool in self.whirlpools
            ],
            "initial_stones": self.initial_stones
        }
        if self.tutorial:
            result["tutorial"] = True
        return result


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
        walls=[],
        current_zones=[],
        whirlpools=[],
        initial_stones=INITIAL_STONES,
        tutorial=False
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
        self.stones_used_this_level = 0  # Track stones used in current level for star rating
    
    def get_current_level(self) -> Optional[LevelData]:
        """Get the current level data."""
        return self.current_level
    
    def get_current_level_number(self) -> int:
        """Get the current level number (1-indexed)."""
        return self.current_level_index + 1
    
    def has_next_level(self) -> bool:
        """Check if there is a next level available."""
        return self.current_level_index + 1 < len(self.levels)
    
    def initialize_level(self, ball_class, level_index: Optional[int] = None, is_random_level: bool = False):
        """
        Initialize a level by loading data, spawning ball, and setting target.
        If level_index is provided, jump to that level. Otherwise, use current_level_index.
        If is_random_level is True, reset stones to 10 (player starting a random level).
        """
        if level_index is not None:
            if 0 <= level_index < len(self.levels):
                self.current_level_index = level_index
                # If jumping to a random level (not sequential progression), give 10 stones
                if is_random_level:
                    self.stones_remaining = INITIAL_STONES
            else:
                raise ValueError(f"Invalid level index: {level_index}")
        
        # Load level data
        self.current_level = self.levels[self.current_level_index]
        
        # Spawn ball at starting position
        self.ball = ball_class(self.current_level.ball_start)
        
        # Reset level completion flag
        self.is_level_complete = False
        
        # Reset stones used counter for this level
        self.stones_used_this_level = 0
    
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
        Implements stone allocation formula: stones_at_level_start = remaining_stones_from_previous + 10
        This applies to all 20 levels when progressing sequentially.
        Note: Zen mode does NOT affect this calculation (handled separately when implemented).
        Returns True if transition successful, False if no more levels.
        """
        if not self.has_next_level():
            return False
        
        # Add 10 stones when transitioning to next level
        # Formula: stones_at_level_start = remaining_stones_from_previous + 10
        self.stones_remaining += 10
        
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
            self.stones_used_this_level += 1
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
        """
        Reset stone counter to initial value for a new game or retry.
        This gives the player 10 stones (INITIAL_STONES).
        Used when:
        - Starting a new game from level 1
        - Retrying a level after game over
        Note: Zen mode does NOT affect this calculation (handled separately when implemented).
        """
        self.stones_remaining = INITIAL_STONES
        self.total_stones_used = 0
    
    def calculate_star_rating(self, stones_used_this_level: int) -> int:
        """
        Calculate star rating based on stones used in the current level.
        
        Star rating formula:
        - ≤5 stones = 3 stars
        - ≤8 stones = 2 stars
        - ≤10 stones = 1 star
        - >10 stones = 0 stars
        
        Args:
            stones_used_this_level: Number of stones used to complete this level
        
        Returns:
            Star rating (0-3)
        """
        if stones_used_this_level <= 5:
            return 3
        elif stones_used_this_level <= 8:
            return 2
        elif stones_used_this_level <= 10:
            return 1
        else:
            return 0


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
    def check_ball_wall_collision(ball_pos: Vector2, ball_radius: float, wall) -> bool:
        """
        Check if ball collides with a wall.
        Returns True if collision detected, False otherwise.
        
        Args:
            ball_pos: Ball position
            ball_radius: Ball radius
            wall: Wall object
        
        Returns:
            True if collision, False otherwise
        """
        distance = wall.distance_to_point(ball_pos)
        return distance <= (ball_radius + wall.thickness / 2)
    
    @staticmethod
    def handle_ball_wall_bounce(ball, wall):
        """
        Handle elastic collision between ball and wall.
        Updates ball position and velocity.
        
        Args:
            ball: Ball object
            wall: Wall object
        """
        # Get closest point on wall
        closest_point = wall.get_closest_point_on_wall(ball.position)
        
        # Calculate penetration
        to_ball = ball.position - closest_point
        distance = to_ball.magnitude()
        
        if distance == 0:
            return
        
        # Push ball out of wall
        penetration = ball.radius + wall.thickness / 2 - distance
        if penetration > 0:
            push_direction = to_ball.normalize()
            ball.position = ball.position + push_direction * penetration
        
        # Reflect velocity using wall normal
        # Get velocity component along normal
        velocity_dot_normal = ball.velocity.x * wall.normal.x + ball.velocity.y * wall.normal.y
        
        # Only reflect if moving toward wall
        if velocity_dot_normal < 0:
            # Elastic collision: reflect velocity
            ball.velocity = Vector2(
                ball.velocity.x - 2 * velocity_dot_normal * wall.normal.x,
                ball.velocity.y - 2 * velocity_dot_normal * wall.normal.y
            )
    
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

