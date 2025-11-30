"""
Renderer module for Ripple game.
Handles all visual rendering including water, entities, UI, and effects.
"""

import pygame
import math
from typing import List, Optional, Tuple
from game.physics import Vector2, Ball, Ripple
from game.catapult import Stone, Catapult
from game.fish import Fish
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WATER_POOL_RECT,
    COLOR_WATER_LIGHT, COLOR_WATER_DARK, COLOR_BALL, COLOR_TARGET, COLOR_START,
    COLOR_STONE, COLOR_UI_TEXT, COLOR_TRAJECTORY, BALL_RADIUS, HIGH_CONTRAST_COLORS
)


class Renderer:
    """Main renderer class for the game."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize renderer with screen surface reference.
        
        Args:
            screen: Pygame surface to render to
        """
        self.screen = screen
        
        # Initialize font for UI text
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_large = pygame.font.SysFont('Arial', 32)
        
        # Environment system reference (set externally)
        self.environment = None
        
        # High-contrast mode flag
        self.high_contrast_mode = False
    
    def set_high_contrast_mode(self, enabled: bool):
        """
        Enable or disable high-contrast mode for accessibility.
        
        Args:
            enabled: True to enable high-contrast mode, False to disable
        """
        self.high_contrast_mode = enabled
    
    def get_color(self, color_name: str, default_color: tuple) -> tuple:
        """
        Get color based on high-contrast mode setting.
        
        Args:
            color_name: Name of the color in HIGH_CONTRAST_COLORS
            default_color: Default color to use when high-contrast mode is off
        
        Returns:
            Color tuple (R, G, B) or (R, G, B, A)
        """
        if self.high_contrast_mode and color_name in HIGH_CONTRAST_COLORS:
            return HIGH_CONTRAST_COLORS[color_name]
        return default_color
    
    def render_frame(self):
        """
        Main render method that clears screen and draws all layers.
        Call this once per frame.
        """
        # Clear screen with environment background color or high-contrast background
        if self.high_contrast_mode:
            self.screen.fill(self.get_color('background', (200, 220, 240)))
        elif self.environment:
            self.screen.fill(self.environment.get_background_color())
        else:
            self.screen.fill((200, 220, 240))  # Light background (default)
        
        # Render water base layer
        self._render_water_surface()
    
    def _render_water_surface(self):
        """Render water pool with enhanced pastel blue gradient background."""
        x, y, width, height = WATER_POOL_RECT
        
        # Get water colors from environment system or high-contrast mode
        if self.high_contrast_mode:
            water_light = self.get_color('water_light', COLOR_WATER_LIGHT)
            water_dark = self.get_color('water_dark', COLOR_WATER_DARK)
        elif self.environment:
            water_light, water_dark = self.environment.get_water_colors()
        else:
            water_light = COLOR_WATER_LIGHT
            water_dark = COLOR_WATER_DARK
        
        # Create smooth gradient from light to dark (top to bottom)
        for i in range(height):
            # Interpolate between light and dark colors with smooth curve
            ratio = i / height
            # Apply easing for smoother gradient
            smooth_ratio = ratio * ratio * (3 - 2 * ratio)  # Smoothstep
            
            r = int(water_light[0] * (1 - smooth_ratio) + water_dark[0] * smooth_ratio)
            g = int(water_light[1] * (1 - smooth_ratio) + water_dark[1] * smooth_ratio)
            b = int(water_light[2] * (1 - smooth_ratio) + water_dark[2] * smooth_ratio)
            
            pygame.draw.line(self.screen, (r, g, b), (x, y + i), (x + width, y + i))
        
        # Add subtle border for depth
        border_color = (120, 180, 200)
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 3)

    def render_ball(self, ball: Ball, time_offset: float = 0):
        """
        Render ball as circle with gradient shading and subtle bobbing animation.
        
        Args:
            ball: Ball object to render
            time_offset: Time offset for animation
        """
        # Add subtle bobbing animation
        import time
        bob_offset = math.sin(time.time() * 2 + time_offset) * 2
        
        pos = (int(ball.position.x), int(ball.position.y + bob_offset))
        radius = int(ball.radius)
        
        # Draw enhanced shadow underneath for depth
        shadow_offset = 4
        shadow_radius = radius + 2
        shadow_pos = (pos[0] + shadow_offset, pos[1] + shadow_offset)
        
        # Create shadow surface with alpha
        shadow_size = shadow_radius * 2 + 10
        shadow_surface = pygame.Surface((shadow_size, shadow_size), pygame.SRCALPHA)
        shadow_center = (shadow_size // 2, shadow_size // 2)
        
        # Draw soft shadow with gradient
        for i in range(shadow_radius, 0, -1):
            alpha = int(30 * (i / shadow_radius))
            pygame.draw.circle(shadow_surface, (50, 50, 50, alpha), shadow_center, i)
        
        self.screen.blit(shadow_surface, (shadow_pos[0] - shadow_size // 2, 
                                          shadow_pos[1] - shadow_size // 2))
        
        # Draw main ball with enhanced gradient effect
        ball_color = self.get_color('ball', COLOR_BALL)
        for i in range(radius, 0, -1):
            # Lighter in center, darker at edges with smoother gradient
            ratio = i / radius
            # Enhanced gradient calculation
            color = tuple(int(c * (ratio * 0.7 + 0.3) + 255 * (1 - ratio) * 0.3) for c in ball_color)
            pygame.draw.circle(self.screen, color, pos, i)
        
        # Add highlight for 3D effect
        highlight_offset = radius // 3
        highlight_pos = (pos[0] - highlight_offset, pos[1] - highlight_offset)
        highlight_radius = radius // 3
        pygame.draw.circle(self.screen, (255, 255, 255, 180), highlight_pos, highlight_radius)
    
    def render_starting_spot(self, position: Vector2, radius: float = 30):
        """
        Render starting spot as red circle with gradient and shadow.
        
        Args:
            position: Center position of the spot
            radius: Radius of the spot
        """
        pos = (int(position.x), int(position.y))
        r = int(radius)
        
        # Draw shadow for depth
        shadow_surface = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        shadow_center = (r + 5, r + 5)
        for i in range(r, 0, -1):
            alpha = int(20 * (i / r))
            pygame.draw.circle(shadow_surface, (50, 50, 50, alpha), shadow_center, i)
        self.screen.blit(shadow_surface, (pos[0] - r - 5, pos[1] - r - 5))
        
        # Draw gradient filled circle
        start_color = self.get_color('start', COLOR_START)
        for i in range(r - 5, 0, -1):
            ratio = i / (r - 5)
            alpha = int(150 * ratio)
            color = (*start_color, alpha)
            pygame.draw.circle(self.screen, color, pos, i)
        
        # Draw outer ring
        pygame.draw.circle(self.screen, start_color, pos, r, 3)
    
    def render_target_spot(self, position: Vector2, radius: float = 40):
        """
        Render target spot as green circle with gradient, shadow, and pulsing animation.
        
        Args:
            position: Center position of the spot
            radius: Radius of the spot
        """
        pos = (int(position.x), int(position.y))
        r = int(radius)
        
        # Add subtle pulsing animation
        import time
        pulse = math.sin(time.time() * 2) * 0.1 + 1.0
        r_pulsed = int(r * pulse)
        
        # Draw shadow for depth
        shadow_surface = pygame.Surface((r_pulsed * 2 + 10, r_pulsed * 2 + 10), pygame.SRCALPHA)
        shadow_center = (r_pulsed + 5, r_pulsed + 5)
        for i in range(r_pulsed, 0, -1):
            alpha = int(20 * (i / r_pulsed))
            pygame.draw.circle(shadow_surface, (50, 50, 50, alpha), shadow_center, i)
        self.screen.blit(shadow_surface, (pos[0] - r_pulsed - 5, pos[1] - r_pulsed - 5))
        
        # Draw gradient filled circle
        target_color = self.get_color('target', COLOR_TARGET)
        for i in range(r_pulsed - 5, 0, -1):
            ratio = i / (r_pulsed - 5)
            alpha = int(150 * ratio)
            color = (*target_color, alpha)
            pygame.draw.circle(self.screen, color, pos, i)
        
        # Draw outer ring with pulsing
        ring_alpha = int(200 + 55 * math.sin(time.time() * 2))
        pygame.draw.circle(self.screen, (*target_color, ring_alpha), pos, r_pulsed, 3)
    
    def render_wall(self, wall):
        """
        Render wall with stone/wood texture (zen aesthetic).
        
        Args:
            wall: Wall object to render
        """
        import math
        
        # Calculate wall endpoints
        start_pos = (int(wall.start.x), int(wall.start.y))
        end_pos = (int(wall.end.x), int(wall.end.y))
        
        # Wall colors - stone/wood zen aesthetic or high-contrast
        if self.high_contrast_mode:
            wall_color = self.get_color('wall', (139, 119, 101))
            highlight_color = tuple(min(255, c + 30) for c in wall_color)
            shadow_color = tuple(max(0, c - 30) for c in wall_color)
        else:
            wall_color = (139, 119, 101)  # Warm stone/wood color
            highlight_color = (169, 149, 131)  # Lighter shade
            shadow_color = (109, 89, 71)  # Darker shade
        
        # Draw wall with thickness
        thickness = int(wall.thickness)
        
        # Calculate perpendicular offset for thickness
        perp_x = -math.sin(wall.rotation) * thickness / 2
        perp_y = math.cos(wall.rotation) * thickness / 2
        
        # Create polygon points for wall rectangle
        points = [
            (start_pos[0] + perp_x, start_pos[1] + perp_y),
            (end_pos[0] + perp_x, end_pos[1] + perp_y),
            (end_pos[0] - perp_x, end_pos[1] - perp_y),
            (start_pos[0] - perp_x, start_pos[1] - perp_y)
        ]
        
        # Draw shadow for depth
        shadow_points = [(p[0] + 2, p[1] + 2) for p in points]
        shadow_surface = pygame.Surface((int(wall.length + 20), thickness + 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.screen, (*shadow_color, 100), shadow_points)
        
        # Draw main wall body
        pygame.draw.polygon(self.screen, wall_color, points)
        
        # Draw highlight edge (top/left side)
        pygame.draw.line(self.screen, highlight_color, points[0], points[1], 2)
        
        # Draw shadow edge (bottom/right side)
        pygame.draw.line(self.screen, shadow_color, points[2], points[3], 2)
        
        # Draw texture lines for stone/wood effect
        num_segments = int(wall.length / 30)  # Segment every 30 pixels
        for i in range(1, num_segments):
            t = i / num_segments
            # Calculate position along wall
            seg_x = wall.start.x + (wall.end.x - wall.start.x) * t
            seg_y = wall.start.y + (wall.end.y - wall.start.y) * t
            
            # Draw subtle texture line
            line_start = (int(seg_x + perp_x * 0.8), int(seg_y + perp_y * 0.8))
            line_end = (int(seg_x - perp_x * 0.8), int(seg_y - perp_y * 0.8))
            pygame.draw.line(self.screen, shadow_color, line_start, line_end, 1)
        
        # Draw border outline
        pygame.draw.polygon(self.screen, (80, 60, 40), points, 2)
    
    def render_current_zone(self, current_zone, time_offset: float = 0):
        """
        Render current zone with animated arrows showing current direction.
        
        Args:
            current_zone: CurrentZone object to render
            time_offset: Time offset for animation
        """
        import time
        
        width, height = current_zone.size
        rect = pygame.Rect(
            int(current_zone.position.x - width / 2),
            int(current_zone.position.y - height / 2),
            int(width),
            int(height)
        )
        
        # Create semi-transparent surface for zone background
        temp_surface = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
        
        # Color based on strength (light blue for water current) or high-contrast
        current_zone_color = self.get_color('current_zone', (100, 150, 200))
        alpha = min(120, int(50 + current_zone.strength * 0.5))
        pygame.draw.rect(temp_surface, (*current_zone_color, alpha), temp_surface.get_rect())
        border_color = tuple(max(0, c - 20) for c in current_zone_color)
        pygame.draw.rect(temp_surface, border_color, temp_surface.get_rect(), 2)
        
        self.screen.blit(temp_surface, rect.topleft)
        
        # Draw animated arrows showing current direction
        arrow_spacing = 40  # Space between arrows
        arrow_size = 20
        
        # Calculate number of arrows to fit in the zone
        num_arrows_x = max(1, int(width / arrow_spacing))
        num_arrows_y = max(1, int(height / arrow_spacing))
        
        # Animation offset (arrows move in current direction)
        anim_time = time.time() + time_offset
        anim_offset = (anim_time * 30) % arrow_spacing  # Move 30 pixels per second
        
        # Calculate arrow direction angle
        angle = math.atan2(current_zone.direction.y, current_zone.direction.x)
        
        # Draw arrows in a grid pattern
        for i in range(num_arrows_x + 1):
            for j in range(num_arrows_y + 1):
                # Calculate arrow position with animation offset
                base_x = rect.left + (i * arrow_spacing) + (width % arrow_spacing) / 2
                base_y = rect.top + (j * arrow_spacing) + (height % arrow_spacing) / 2
                
                # Apply animation offset in current direction
                arrow_x = base_x + current_zone.direction.x * anim_offset
                arrow_y = base_y + current_zone.direction.y * anim_offset
                
                # Wrap around to create continuous flow
                while arrow_x < rect.left:
                    arrow_x += width
                while arrow_x > rect.right:
                    arrow_x -= width
                while arrow_y < rect.top:
                    arrow_y += height
                while arrow_y > rect.bottom:
                    arrow_y -= height
                
                # Only draw if inside zone
                if rect.collidepoint(int(arrow_x), int(arrow_y)):
                    self._draw_arrow(int(arrow_x), int(arrow_y), angle, arrow_size)
    
    def _draw_arrow(self, x: int, y: int, angle: float, size: int):
        """
        Draw an arrow at the specified position and angle.
        
        Args:
            x, y: Arrow position
            angle: Arrow direction in radians
            size: Arrow size in pixels
        """
        # Calculate arrow points
        # Arrow head
        head_x = x + size * math.cos(angle)
        head_y = y + size * math.sin(angle)
        
        # Arrow tail
        tail_x = x - size * 0.3 * math.cos(angle)
        tail_y = y - size * 0.3 * math.sin(angle)
        
        # Arrow wings
        wing_angle = 2.5  # Radians
        wing_length = size * 0.6
        
        left_wing_x = head_x - wing_length * math.cos(angle + wing_angle)
        left_wing_y = head_y - wing_length * math.sin(angle + wing_angle)
        
        right_wing_x = head_x - wing_length * math.cos(angle - wing_angle)
        right_wing_y = head_y - wing_length * math.sin(angle - wing_angle)
        
        # Draw arrow shaft
        pygame.draw.line(self.screen, (255, 255, 255), (int(tail_x), int(tail_y)), 
                        (int(head_x), int(head_y)), 3)
        
        # Draw arrow head
        arrow_points = [
            (int(head_x), int(head_y)),
            (int(left_wing_x), int(left_wing_y)),
            (int(right_wing_x), int(right_wing_y))
        ]
        pygame.draw.polygon(self.screen, (255, 255, 255), arrow_points)
    
    def render_obstacle(self, obstacle):
        """
        Render obstacle (anti-ripple zone).
        
        Args:
            obstacle: Obstacle object to render
        """
        if obstacle.type == "anti_ripple_zone":
            # Get obstacle color
            obstacle_color = self.get_color('obstacle', (100, 100, 100))
            
            # Render as semi-transparent gray rectangle or circle
            if isinstance(obstacle.size, (list, tuple)) and len(obstacle.size) == 2:
                # Rectangle obstacle
                width, height = obstacle.size
                rect = pygame.Rect(
                    int(obstacle.position.x - width / 2),
                    int(obstacle.position.y - height / 2),
                    int(width),
                    int(height)
                )
                # Create semi-transparent surface
                temp_surface = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
                pygame.draw.rect(temp_surface, (*obstacle_color, 100), temp_surface.get_rect())
                pygame.draw.rect(temp_surface, (80, 80, 80), temp_surface.get_rect(), 2)
                self.screen.blit(temp_surface, rect.topleft)
            elif isinstance(obstacle.size, (int, float)):
                # Circle obstacle
                pos = (int(obstacle.position.x), int(obstacle.position.y))
                radius = int(obstacle.size)
                # Create semi-transparent surface
                size = radius * 2
                temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (*obstacle_color, 100), (radius, radius), radius)
                pygame.draw.circle(temp_surface, (80, 80, 80), (radius, radius), radius, 2)
                self.screen.blit(temp_surface, (pos[0] - radius, pos[1] - radius))
    
    def render_stone(self, stone: Stone):
        """
        Render stone as circle at 75% of ball size.
        Handles both flight and sinking animation.
        
        Args:
            stone: Stone object to render
        """
        pos = (int(stone.position.x), int(stone.position.y))
        
        # Apply scale for sinking animation
        scale = stone.get_scale()
        radius = int(stone.radius * scale)
        
        if radius < 1:
            return  # Don't render if too small
        
        # Get alpha for fade out
        alpha = stone.get_alpha()
        
        # Get stone color
        stone_color = self.get_color('stone', COLOR_STONE)
        
        # Create surface with alpha for transparency
        if alpha < 1.0:
            # Create temporary surface for alpha blending
            temp_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            temp_pos = (radius + 2, radius + 2)
            
            # Draw stone on temp surface
            color_with_alpha = (*stone_color, int(255 * alpha))
            pygame.draw.circle(temp_surface, color_with_alpha, temp_pos, radius)
            
            # Blit to screen
            self.screen.blit(temp_surface, (pos[0] - radius - 2, pos[1] - radius - 2))
        else:
            # Draw normally without alpha
            pygame.draw.circle(self.screen, stone_color, pos, radius)
            
            # Add highlight for 3D effect
            highlight_pos = (pos[0] - radius // 3, pos[1] - radius // 3)
            highlight_radius = radius // 3
            pygame.draw.circle(self.screen, (200, 200, 200), highlight_pos, highlight_radius)

    def render_ripple(self, ripple: Ripple, obstacles: List = None):
        """
        Render ripple as circular gradient with transparency and shimmer effect.
        Scale based on current radius, alpha based on current amplitude.
        Uses masking to avoid drawing within obstacle boundaries.
        
        Args:
            ripple: Ripple object to render
            obstacles: List of obstacles to check for clipping (optional)
        """
        pos = (int(ripple.position.x), int(ripple.position.y))
        
        # Get current radius and amplitude
        current_radius = ripple.get_current_radius()
        current_amplitude = ripple.get_current_amplitude()
        
        # Calculate alpha based on amplitude (normalized to 0-1 range)
        max_amplitude = ripple.max_amplitude
        alpha = current_amplitude / max_amplitude if max_amplitude > 0 else 0
        alpha = max(0, min(1, alpha))  # Clamp to [0, 1]
        
        # Don't render if too faint or too small
        if alpha < 0.05 or current_radius < 1:
            return
        
        # Add subtle shimmer effect
        import time
        shimmer = math.sin(time.time() * 3 + ripple.creation_time * 10) * 0.15 + 0.85
        alpha *= shimmer
        
        # Create temporary surface for alpha blending
        size = int(current_radius * 2 + 10)
        temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)
        
        # Draw multiple concentric circles for enhanced gradient effect
        num_rings = 8
        for i in range(num_rings):
            ring_ratio = (i + 1) / num_rings
            ring_radius = int(current_radius * ring_ratio)
            
            if ring_radius < 1:
                continue
            
            # Alpha decreases towards outer rings with smoother falloff
            ring_alpha = int(alpha * 255 * (1 - ring_ratio * 0.8) * (1 - ring_ratio * 0.2))
            
            # Enhanced color: white with blue tint and slight variation or high-contrast
            if self.high_contrast_mode:
                ripple_color = self.get_color('ripple', (0, 100, 200))
                color = (*ripple_color, ring_alpha)
            else:
                blue_tint = int(200 + 30 * (1 - ring_ratio))
                color = (blue_tint, blue_tint + 20, 255, ring_alpha)
            
            # Draw ring with varying thickness
            thickness = max(1, int(ring_radius * 0.15))
            pygame.draw.circle(temp_surface, color, center, ring_radius, thickness)
        
        # If obstacles exist, mask out obstacle areas from the ripple surface
        if obstacles:
            # Create an erase mask surface
            erase_mask = pygame.Surface((size, size), pygame.SRCALPHA)
            erase_mask.fill((255, 255, 255, 255))  # Start fully opaque (visible)
            
            for obstacle in obstacles:
                # Check if obstacle blocks ripple rendering
                if not getattr(obstacle, 'blocks_ripple_rendering', True):
                    continue  # Skip if obstacle doesn't block rendering
                
                # Calculate obstacle position relative to temp_surface
                rel_x = obstacle.position.x - ripple.position.x + center[0]
                rel_y = obstacle.position.y - ripple.position.y + center[1]
                
                # Draw obstacle as transparent (alpha 0) on the mask
                if isinstance(obstacle.size, (list, tuple)) and len(obstacle.size) == 2:
                    # Rectangle obstacle
                    width, height = obstacle.size
                    rect = pygame.Rect(
                        int(rel_x - width / 2),
                        int(rel_y - height / 2),
                        int(width),
                        int(height)
                    )
                    pygame.draw.rect(erase_mask, (0, 0, 0, 0), rect)
                elif isinstance(obstacle.size, (int, float)):
                    # Circle obstacle
                    pygame.draw.circle(erase_mask, (0, 0, 0, 0), 
                                     (int(rel_x), int(rel_y)), int(obstacle.size))
            
            # Apply the mask using BLEND_RGBA_MULT (multiplies alpha values)
            temp_surface.blit(erase_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Blit to screen
        self.screen.blit(temp_surface, (pos[0] - size // 2, pos[1] - size // 2))
    
    def render_ripples(self, ripples: List[Ripple], obstacles: List = None):
        """
        Render all active ripples in order, clipping around obstacles.
        
        Args:
            ripples: List of Ripple objects to render
            obstacles: List of obstacles to check for clipping (optional)
        """
        for ripple in ripples:
            self.render_ripple(ripple, obstacles)

    def render_stone_counter(self, stones_remaining: int, zen_mode: bool = False):
        """
        Render stone counter at top center with enhanced styling.
        Display infinity symbol (∞) when in Zen mode.
        
        Args:
            stones_remaining: Number of stones remaining
            zen_mode: Whether Zen mode is enabled
        """
        # Render text with infinity symbol in Zen mode
        if zen_mode:
            text = "Stones: ∞"
        else:
            text = f"Stones: {stones_remaining}"
        ui_text_color = self.get_color('ui_text', COLOR_UI_TEXT)
        text_surface = self.font_large.render(text, True, ui_text_color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        
        # Draw enhanced background with gradient and shadow
        bg_rect = text_rect.inflate(30, 15)
        
        # Shadow
        shadow_rect = bg_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (50, 50, 50, 80), shadow_surface.get_rect(), border_radius=8)
        self.screen.blit(shadow_surface, shadow_rect.topleft)
        
        # Background with gradient effect
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        for i in range(bg_rect.height):
            ratio = i / bg_rect.height
            alpha = int(220 - ratio * 20)
            pygame.draw.line(bg_surface, (255, 255, 255, alpha), (0, i), (bg_rect.width, i))
        self.screen.blit(bg_surface, bg_rect.topleft)
        
        # Border
        pygame.draw.rect(self.screen, (150, 180, 200), bg_rect, 2, border_radius=8)
        
        # Draw text
        self.screen.blit(text_surface, text_rect)
        
        # Draw enhanced stone icon with shadow
        icon_x = text_rect.right + 18
        icon_y = text_rect.centery
        icon_radius = 9
        
        # Icon shadow
        pygame.draw.circle(self.screen, (100, 100, 100, 100), (icon_x + 1, icon_y + 1), icon_radius)
        
        # Icon with gradient
        stone_color = self.get_color('stone', COLOR_STONE)
        for i in range(icon_radius, 0, -1):
            ratio = i / icon_radius
            color = tuple(int(c * ratio) for c in stone_color)
            pygame.draw.circle(self.screen, color, (icon_x, icon_y), i)
        
        # Highlight
        pygame.draw.circle(self.screen, (220, 220, 220), (icon_x - 3, icon_y - 3), 3)
    
    def render_power_meter(self, catapult: Catapult):
        """
        Render enhanced power meter near catapult with smooth gradient and shadow.
        Only visible while aiming with gradient fill (green to red).
        
        Args:
            catapult: Catapult object with aiming state
        """
        if not catapult.is_aiming:
            return
        
        # Position near catapult
        meter_x = int(catapult.position.x + 60)
        meter_y = int(catapult.position.y - 100)
        meter_width = 24
        meter_height = 100
        
        # Draw shadow
        shadow_rect = pygame.Rect(meter_x + 2, meter_y + 2, meter_width, meter_height)
        shadow_surface = pygame.Surface((meter_width, meter_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (50, 50, 50, 100), shadow_surface.get_rect(), border_radius=5)
        self.screen.blit(shadow_surface, shadow_rect.topleft)
        
        # Draw background with gradient
        bg_rect = pygame.Rect(meter_x, meter_y, meter_width, meter_height)
        bg_surface = pygame.Surface((meter_width, meter_height), pygame.SRCALPHA)
        for i in range(meter_height):
            alpha = 180 + int(40 * (i / meter_height))
            pygame.draw.line(bg_surface, (40, 40, 40, alpha), (0, i), (meter_width, i))
        self.screen.blit(bg_surface, bg_rect.topleft)
        
        # Border
        pygame.draw.rect(self.screen, (180, 180, 180), bg_rect, 2, border_radius=5)
        
        # Draw filled portion based on power with smooth gradient
        fill_height = int(meter_height * catapult.aim_power)
        if fill_height > 0:
            # Gradient from green (low) to yellow to red (high)
            for i in range(fill_height):
                ratio = i / meter_height
                
                # Smooth color transition: green -> yellow -> red
                if ratio < 0.5:
                    # Green to yellow
                    local_ratio = ratio * 2
                    r = int(100 * local_ratio)
                    g = 255
                    b = 0
                else:
                    # Yellow to red
                    local_ratio = (ratio - 0.5) * 2
                    r = 255
                    g = int(255 * (1 - local_ratio))
                    b = 0
                
                line_y = meter_y + meter_height - i - 3
                pygame.draw.line(self.screen, (r, g, b), 
                               (meter_x + 3, line_y), 
                               (meter_x + meter_width - 3, line_y))
        
        # Draw power percentage text with background
        power_text = f"{int(catapult.aim_power * 100)}%"
        power_surface = self.font.render(power_text, True, (255, 255, 255))
        power_rect = power_surface.get_rect(center=(meter_x + meter_width // 2, meter_y - 20))
        
        # Text background
        text_bg = power_rect.inflate(10, 5)
        pygame.draw.rect(self.screen, (70, 70, 70, 200), text_bg, border_radius=3)
        
        self.screen.blit(power_surface, power_rect)
    
    def render_trajectory_preview(self, catapult: Catapult):
        """
        Render trajectory preview as dotted line through trajectory points.
        Render landing marker circle at trajectory end point.
        Only visible while aiming.
        
        Args:
            catapult: Catapult object with trajectory data
        """
        if not catapult.is_aiming:
            return
        
        trajectory_points = catapult.get_trajectory_points()
        landing_position = catapult.get_landing_position()
        
        # Draw trajectory as continuous line with dots for better visibility
        if len(trajectory_points) > 1:
            # Draw black outline for contrast
            points_list = [(int(p.x), int(p.y)) for p in trajectory_points]
            pygame.draw.lines(self.screen, (0, 0, 0), False, points_list, 6)
            
            # Draw bright white line on top
            pygame.draw.lines(self.screen, (255, 255, 255), False, points_list, 4)
            
            # Draw bright dots along trajectory for emphasis
            for i, point in enumerate(trajectory_points):
                if i % 2 == 0:  # Every 2nd point
                    pos = (int(point.x), int(point.y))
                    pygame.draw.circle(self.screen, (255, 255, 0), pos, 5)  # Bright yellow
                    pygame.draw.circle(self.screen, (255, 255, 255), pos, 3)  # White center
        
        # Draw landing marker
        if landing_position:
            pos = (int(landing_position.x), int(landing_position.y))
            
            # Draw pulsing circle
            import time
            pulse = abs(math.sin(time.time() * 4))  # Pulse effect
            radius = int(20 + pulse * 8)
            
            # Outer circle (bright yellow)
            pygame.draw.circle(self.screen, (255, 255, 0), pos, radius, 3)
            # Middle circle (white)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, radius - 5, 2)
            # Inner filled circle (semi-transparent yellow)
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 0, 80), (radius, radius), radius - 8)
            self.screen.blit(s, (pos[0] - radius, pos[1] - radius))

    def render_catapult(self, catapult: Catapult):
        """
        Render catapult with base, arm, rubber band, and stone.
        Arm rotates based on aim angle.
        
        Args:
            catapult: Catapult object to render
        """
        pos = (int(catapult.position.x), int(catapult.position.y))
        
        # Catapult dimensions
        base_width = 60
        base_height = 30
        arm_length = 50
        
        # Draw base (wooden platform)
        base_rect = pygame.Rect(pos[0] - base_width // 2, pos[1] - base_height // 2,
                                base_width, base_height)
        pygame.draw.rect(self.screen, (139, 90, 43), base_rect, border_radius=5)  # Brown
        pygame.draw.rect(self.screen, (101, 67, 33), base_rect, 2, border_radius=5)  # Dark brown outline
        
        # Rubber band anchor points on base
        left_anchor = (pos[0] - base_width // 3, pos[1])
        right_anchor = (pos[0] + base_width // 3, pos[1])
        
        # Calculate arm tip position based on aim angle
        if catapult.is_aiming:
            # Use pull_angle for visual feedback (shows where player is pulling)
            angle = catapult.pull_angle
            # Pull back based on power
            pull_back = catapult.aim_power * 30
            arm_tip_x = pos[0] + (arm_length + pull_back) * math.cos(angle)
            arm_tip_y = pos[1] + (arm_length + pull_back) * math.sin(angle)
        else:
            # Rest position (pointing up and slightly forward)
            rest_angle = -math.pi / 3  # 60 degrees up
            arm_tip_x = pos[0] + arm_length * math.cos(rest_angle)
            arm_tip_y = pos[1] + arm_length * math.sin(rest_angle)
        
        arm_tip = (int(arm_tip_x), int(arm_tip_y))
        
        # Draw rubber bands (two lines from arm tip to base anchors)
        if catapult.is_aiming:
            # Stretched rubber bands
            pygame.draw.line(self.screen, (80, 60, 40), left_anchor, arm_tip, 3)
            pygame.draw.line(self.screen, (80, 60, 40), right_anchor, arm_tip, 3)
        
        # Draw arm
        pygame.draw.line(self.screen, (101, 67, 33), pos, arm_tip, 6)
        
        # Draw pivot point
        pygame.draw.circle(self.screen, (60, 40, 20), pos, 8)
        pygame.draw.circle(self.screen, (40, 25, 10), pos, 8, 2)
        
        # Draw stone at arm tip while aiming
        if catapult.is_aiming:
            stone_radius = int(BALL_RADIUS * 0.75)
            pygame.draw.circle(self.screen, COLOR_STONE, arm_tip, stone_radius)
            # Highlight
            highlight_pos = (arm_tip[0] - stone_radius // 3, arm_tip[1] - stone_radius // 3)
            pygame.draw.circle(self.screen, (200, 200, 200), highlight_pos, stone_radius // 3)
    
    def render_fish(self, fish: Fish):
        """
        Render fish with simple sprite representation.
        Flips sprite based on swim direction.
        
        Args:
            fish: Fish object to render
        """
        pos = (int(fish.position.x), int(fish.position.y))
        size = int(fish.size)
        
        # Fish colors (orange/goldfish)
        body_color = (255, 165, 80)  # Orange
        fin_color = (255, 140, 60)  # Darker orange
        
        # Draw fish body (ellipse)
        body_width = size
        body_height = int(size * 0.6)
        
        # Create temporary surface for fish
        fish_surface = pygame.Surface((body_width * 2, body_height * 2), pygame.SRCALPHA)
        
        # Draw on temporary surface (centered)
        center_x = body_width
        center_y = body_height
        
        # Draw tail fin
        if fish.facing_right:
            tail_points = [
                (center_x - body_width // 2, center_y),
                (center_x - body_width, center_y - body_height // 2),
                (center_x - body_width, center_y + body_height // 2)
            ]
        else:
            tail_points = [
                (center_x + body_width // 2, center_y),
                (center_x + body_width, center_y - body_height // 2),
                (center_x + body_width, center_y + body_height // 2)
            ]
        pygame.draw.polygon(fish_surface, fin_color, tail_points)
        
        # Draw body
        body_rect = pygame.Rect(center_x - body_width // 2, center_y - body_height // 2,
                                body_width, body_height)
        pygame.draw.ellipse(fish_surface, body_color, body_rect)
        
        # Draw eye
        eye_size = max(2, size // 6)
        if fish.facing_right:
            eye_pos = (center_x + body_width // 4, center_y - body_height // 4)
        else:
            eye_pos = (center_x - body_width // 4, center_y - body_height // 4)
        pygame.draw.circle(fish_surface, (50, 50, 50), eye_pos, eye_size)
        
        # Draw top fin
        if fish.facing_right:
            fin_points = [
                (center_x, center_y - body_height // 2),
                (center_x + body_width // 4, center_y - body_height),
                (center_x + body_width // 2, center_y - body_height // 2)
            ]
        else:
            fin_points = [
                (center_x, center_y - body_height // 2),
                (center_x - body_width // 4, center_y - body_height),
                (center_x - body_width // 2, center_y - body_height // 2)
            ]
        pygame.draw.polygon(fish_surface, fin_color, fin_points)
        
        # Blit fish to screen
        self.screen.blit(fish_surface, (pos[0] - body_width, pos[1] - body_height))
    
    def render_fish_list(self, fish_list: List[Fish]):
        """
        Render all fish in the list.
        
        Args:
            fish_list: List of Fish objects to render
        """
        for fish in fish_list:
            self.render_fish(fish)
    
    def render_whirlpool(self, whirlpool, time_offset: float = 0):
        """
        Render whirlpool with swirling water animation and rotating effect.
        
        Args:
            whirlpool: Whirlpool object to render
            time_offset: Time offset for animation
        """
        import time
        
        pos = (int(whirlpool.position.x), int(whirlpool.position.y))
        radius = int(whirlpool.radius)
        center_threshold = int(whirlpool.center_threshold)
        
        # Animation time for rotation
        anim_time = time.time() + time_offset
        rotation_speed = 2.0  # Radians per second
        rotation_angle = (anim_time * rotation_speed) % (2 * math.pi)
        
        # Create surface for whirlpool with alpha
        size = radius * 2 + 10
        temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)
        
        # Draw base whirlpool gradient (darker in center)
        num_rings = 20
        for i in range(num_rings):
            ring_ratio = (i + 1) / num_rings
            ring_radius = int(radius * ring_ratio)
            
            if ring_radius < 1:
                continue
            
            # Color: darker blue in center, lighter at edges or high-contrast
            # Alpha increases toward center
            darkness = 1.0 - ring_ratio * 0.7  # 0.3 to 1.0
            alpha = int(120 * (1.0 - ring_ratio * 0.5))  # More opaque in center
            
            if self.high_contrast_mode:
                whirlpool_color = self.get_color('whirlpool', (0, 0, 150))
                color = (
                    int(whirlpool_color[0] * darkness),
                    int(whirlpool_color[1] * darkness),
                    int(whirlpool_color[2] * darkness),
                    alpha
                )
            else:
                color = (
                    int(80 * darkness),
                    int(120 * darkness),
                    int(180 * darkness),
                    alpha
                )
            
            pygame.draw.circle(temp_surface, color, center, ring_radius)
        
        # Draw rotating spiral lines for swirling effect
        num_spirals = 6
        spiral_segments = 30
        
        for spiral_idx in range(num_spirals):
            spiral_angle_offset = (spiral_idx * 2 * math.pi / num_spirals) + rotation_angle
            
            points = []
            for seg in range(spiral_segments):
                # Spiral from edge to center
                t = seg / spiral_segments  # 0 at edge, 1 at center
                
                # Radius decreases as we spiral inward
                seg_radius = radius * (1.0 - t)
                
                # Angle increases as we spiral inward (creates spiral)
                seg_angle = spiral_angle_offset + t * 4 * math.pi
                
                # Calculate position
                seg_x = center[0] + seg_radius * math.cos(seg_angle)
                seg_y = center[1] + seg_radius * math.sin(seg_angle)
                
                points.append((int(seg_x), int(seg_y)))
            
            # Draw spiral line with varying alpha
            if len(points) > 1:
                for i in range(len(points) - 1):
                    t = i / len(points)
                    alpha = int(150 * (1.0 - t * 0.5))  # Fade toward center
                    
                    # Create small surface for line segment with alpha
                    p1, p2 = points[i], points[i + 1]
                    pygame.draw.line(temp_surface, (200, 220, 255, alpha), p1, p2, 2)
        
        # Draw danger zone in center (red tint)
        danger_rings = 8
        for i in range(danger_rings):
            ring_ratio = (i + 1) / danger_rings
            ring_radius = int(center_threshold * ring_ratio)
            
            if ring_radius < 1:
                continue
            
            # Red warning color with pulsing alpha
            pulse = abs(math.sin(anim_time * 3))
            alpha = int((100 + pulse * 50) * (1.0 - ring_ratio * 0.5))
            
            color = (200, 50, 50, alpha)
            pygame.draw.circle(temp_surface, color, center, ring_radius)
        
        # Draw center point (dark)
        pygame.draw.circle(temp_surface, (30, 30, 60, 200), center, max(3, center_threshold // 3))
        
        # Blit to screen
        self.screen.blit(temp_surface, (pos[0] - size // 2, pos[1] - size // 2))
        
        # Draw outer ring border
        pygame.draw.circle(self.screen, (60, 100, 150), pos, radius, 2)
        
        # Draw rotating particles around the edge for extra effect
        num_particles = 12
        for i in range(num_particles):
            particle_angle = (i * 2 * math.pi / num_particles) + rotation_angle * 1.5
            particle_radius = radius - 5
            
            particle_x = pos[0] + particle_radius * math.cos(particle_angle)
            particle_y = pos[1] + particle_radius * math.sin(particle_angle)
            
            # Small white particle
            pygame.draw.circle(self.screen, (200, 220, 255), 
                             (int(particle_x), int(particle_y)), 3)

    def render_star(self, x: int, y: int, size: int, filled: bool = True, fill_progress: float = 1.0):
        """
        Render a star shape at the specified position.
        
        Args:
            x, y: Center position of the star
            size: Size of the star (radius)
            filled: Whether to fill the star or just draw outline
            fill_progress: Progress of fill animation (0.0 to 1.0)
        """
        # Calculate star points (5-pointed star)
        points = []
        num_points = 5
        
        for i in range(num_points * 2):
            angle = (i * math.pi / num_points) - math.pi / 2  # Start from top
            
            # Alternate between outer and inner points
            if i % 2 == 0:
                # Outer point
                radius = size
            else:
                # Inner point (smaller radius)
                radius = size * 0.4
            
            point_x = x + radius * math.cos(angle)
            point_y = y + radius * math.sin(angle)
            points.append((int(point_x), int(point_y)))
        
        if filled:
            # Draw filled star with animation
            if fill_progress < 1.0:
                # Create clipping mask for partial fill
                # Draw from bottom up based on progress
                clip_height = int(size * 2 * (1.0 - fill_progress))
                
                # Create temporary surface for star
                temp_surface = pygame.Surface((size * 2 + 10, size * 2 + 10), pygame.SRCALPHA)
                temp_center = (size + 5, size + 5)
                
                # Adjust points for temp surface
                temp_points = [(int(p[0] - x + temp_center[0]), int(p[1] - y + temp_center[1])) for p in points]
                
                # Draw filled star
                pygame.draw.polygon(temp_surface, (255, 215, 0), temp_points)  # Gold color
                
                # Draw outline
                pygame.draw.polygon(temp_surface, (200, 170, 0), temp_points, 2)
                
                # Create clip rect (reveal from bottom to top)
                clip_rect = pygame.Rect(0, clip_height, size * 2 + 10, size * 2 + 10 - clip_height)
                temp_surface.set_clip(clip_rect)
                
                # Blit to screen
                self.screen.blit(temp_surface, (x - size - 5, y - size - 5))
            else:
                # Draw fully filled star
                pygame.draw.polygon(self.screen, (255, 215, 0), points)  # Gold color
                pygame.draw.polygon(self.screen, (200, 170, 0), points, 2)  # Darker outline
                
                # Add highlight for shine effect
                highlight_size = int(size * 0.3)
                highlight_pos = (x - size // 3, y - size // 3)
                pygame.draw.circle(self.screen, (255, 255, 200, 150), highlight_pos, highlight_size)
        else:
            # Draw outline only (empty star)
            pygame.draw.polygon(self.screen, (180, 180, 180), points, 3)  # Gray outline
    
    def render_star_rating(self, x: int, y: int, stars: int, animation_progress: float = 1.0):
        """
        Render star rating display with animation.
        
        Args:
            x, y: Center position for the star rating display
            stars: Number of stars to display (0-3)
            animation_progress: Animation progress (0.0 to 1.0)
        """
        star_size = 40
        star_spacing = 80
        
        # Calculate starting x position to center the stars
        total_width = star_spacing * 2  # 3 stars with 2 gaps
        start_x = x - total_width // 2
        
        # Render 3 stars
        for i in range(3):
            star_x = start_x + i * star_spacing
            star_y = y
            
            # Determine if this star should be filled
            filled = i < stars
            
            # Calculate fill progress for this star based on animation
            # Stars fill in sequence
            if animation_progress >= 1.0:
                fill_progress = 1.0
            else:
                # Each star gets 1/3 of the animation time
                star_start = i / 3.0
                star_end = (i + 1) / 3.0
                
                if animation_progress < star_start:
                    fill_progress = 0.0
                elif animation_progress > star_end:
                    fill_progress = 1.0
                else:
                    # Interpolate within this star's time window
                    fill_progress = (animation_progress - star_start) / (star_end - star_start)
            
            # Add bounce effect during animation
            if fill_progress < 1.0 and filled:
                bounce = abs(math.sin(fill_progress * math.pi)) * 10
                star_y -= int(bounce)
            
            # Render the star
            self.render_star(star_x, star_y, star_size, filled, fill_progress if filled else 1.0)
    
    def render_peace_rating(self, x: int, y: int):
        """
        Render "Peace" rating for Zen mode instead of stars.
        
        Args:
            x, y: Center position for the peace rating display
        """
        # Render "Peace" text with zen aesthetic
        peace_font = pygame.font.SysFont('Arial', 48, bold=True)
        peace_surface = peace_font.render("Peace", True, (100, 180, 150))  # Calm green color
        peace_rect = peace_surface.get_rect(center=(x, y))
        
        # Add subtle glow effect
        glow_surface = pygame.Surface((peace_rect.width + 20, peace_rect.height + 20), pygame.SRCALPHA)
        glow_rect = glow_surface.get_rect(center=(x, y))
        
        # Draw multiple layers for glow
        for i in range(5, 0, -1):
            alpha = int(30 * (i / 5))
            glow_color = (100, 180, 150, alpha)
            glow_text = peace_font.render("Peace", True, glow_color)
            glow_text_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
            glow_surface.blit(glow_text, glow_text_rect)
        
        self.screen.blit(glow_surface, glow_rect.topleft)
        self.screen.blit(peace_surface, peace_rect)
