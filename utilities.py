import math
import pygame

def get_direction_vector(start_x, start_y, target_x, target_y):
    """Returns normalized direction vector between two points"""
    dx = target_x - start_x
    dy = target_y - start_y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return (0, 0)
    return (dx/dist, dy/dist)

def calculate_movement_towards(source_rect, target_rect, speed, world_bounds):
    """Calculate movement towards target with boundary constraints"""
    dx = target_rect.centerx - source_rect.centerx
    dy = target_rect.centery - source_rect.centery
    dist = math.hypot(dx, dy)
    
    if dist == 0:
        return (0, 0)
        
    move_x = dx/dist * speed
    move_y = dy/dist * speed
    
    new_x = source_rect.x + move_x
    new_y = source_rect.y + move_y
    
    # Apply world boundaries
    new_x = max(0, min(world_bounds[0] - source_rect.width, new_x))
    new_y = max(0, min(world_bounds[1] - source_rect.height, new_y))
    
    return (new_x - source_rect.x, new_y - source_rect.y)
