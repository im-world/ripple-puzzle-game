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
    COLOR_STONE, COLOR_UI_TEXT, COLOR_TRAJECTORY, BALL_RADIUS
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
    
    def render_frame(self):
        """
        Main render method that clears screen and draws all layers.
        Call this once per frame.
        """
        # Clear screen
        self.screen.fill((200, 220, 240))  # Light background
        
        # Render water base layer
        self._render_water_surface()
    
    def _render_water_surface(self):
        """Render water pool with enhanced pastel blue gradient background."""
        x, y, width, height = WATER_POOL_RECT
        
        # Create smooth gradient from light to dark blue (top to bottom)
        for i in range(height):
            # Interpolate between light and dark colors with smooth curve
            ratio = i / height
            # Apply easing for smoother gradient
            smooth_ratio = ratio * ratio * (3 - 2 * ratio)  # Smoothstep
            
            r = int(COLOR_WATER_LIGHT[0] * (1 - smooth_ratio) + COLOR_WATER_DARK[0] * smooth_ratio)
            g = int(COLOR_WATER_LIGHT[1] * (1 - smooth_ratio) + COLOR_WATER_DARK[1] * smooth_ratio)
            b = int(COLOR_WATER_LIGHT[2] * (1 - smooth_ratio) + COLOR_WATER_DARK[2] * smooth_ratio)
            
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
        for i in range(radius, 0, -1):
            # Lighter in center, darker at edges with smoother gradient
            ratio = i / radius
            # Enhanced gradient calculation
            color = tuple(int(c * (ratio * 0.7 + 0.3) + 255 * (1 - ratio) * 0.3) for c in COLOR_BALL)
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
        for i in range(r - 5, 0, -1):
            ratio = i / (r - 5)
            alpha = int(150 * ratio)
            color = (*COLOR_START, alpha)
            pygame.draw.circle(self.screen, color, pos, i)
        
        # Draw outer ring
        pygame.draw.circle(self.screen, COLOR_START, pos, r, 3)
    
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
        for i in range(r_pulsed - 5, 0, -1):
            ratio = i / (r_pulsed - 5)
            alpha = int(150 * ratio)
            color = (*COLOR_TARGET, alpha)
            pygame.draw.circle(self.screen, color, pos, i)
        
        # Draw outer ring with pulsing
        ring_alpha = int(200 + 55 * math.sin(time.time() * 2))
        pygame.draw.circle(self.screen, (*COLOR_TARGET, ring_alpha), pos, r_pulsed, 3)
    
    def render_obstacle(self, obstacle):
        """
        Render obstacle (anti-ripple zone).
        
        Args:
            obstacle: Obstacle object to render
        """
        if obstacle.type == "anti_ripple_zone":
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
                pygame.draw.rect(temp_surface, (100, 100, 100, 100), temp_surface.get_rect())
                pygame.draw.rect(temp_surface, (80, 80, 80), temp_surface.get_rect(), 2)
                self.screen.blit(temp_surface, rect.topleft)
            elif isinstance(obstacle.size, (int, float)):
                # Circle obstacle
                pos = (int(obstacle.position.x), int(obstacle.position.y))
                radius = int(obstacle.size)
                # Create semi-transparent surface
                size = radius * 2
                temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (100, 100, 100, 100), (radius, radius), radius)
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
        
        # Create surface with alpha for transparency
        if alpha < 1.0:
            # Create temporary surface for alpha blending
            temp_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            temp_pos = (radius + 2, radius + 2)
            
            # Draw stone on temp surface
            color_with_alpha = (*COLOR_STONE, int(255 * alpha))
            pygame.draw.circle(temp_surface, color_with_alpha, temp_pos, radius)
            
            # Blit to screen
            self.screen.blit(temp_surface, (pos[0] - radius - 2, pos[1] - radius - 2))
        else:
            # Draw normally without alpha
            pygame.draw.circle(self.screen, COLOR_STONE, pos, radius)
            
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
            
            # Enhanced color: white with blue tint and slight variation
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

    def render_stone_counter(self, stones_remaining: int):
        """
        Render stone counter at top center with enhanced styling.
        
        Args:
            stones_remaining: Number of stones remaining
        """
        # Render text
        text = f"Stones: {stones_remaining}"
        text_surface = self.font_large.render(text, True, COLOR_UI_TEXT)
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
        for i in range(icon_radius, 0, -1):
            ratio = i / icon_radius
            color = tuple(int(c * ratio) for c in COLOR_STONE)
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
