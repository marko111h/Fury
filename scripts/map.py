import pygame
import math
import socket
import json

# Initializing pygame
pygame.init()

# Window dimensions
width, height = 800, 800

# Creating a window
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Hexagonal Map")

# Hexagonal size
hex_size = 30  # we can change the size of the hexagon
hex_width = hex_size * 3 / 2
hex_height = hex_size * math.sqrt(3)


# Function for drawing hexagons
def draw_hexagon(screen, x, y, size, color):
    # Coordinates of the hexagon vertices
    points = []
    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = math.radians(angle_deg)
        point_x = x + size * math.cos(angle_rad)
        point_y = y + size * math.sin(angle_rad)
        points.append((point_x, point_y))
    pygame.draw.polygon(screen, color, points)


# function to draw a hexagonal grid
def draw_hex_grid(screen, map_data):
    map_size = map_data.get('size', 11)

    # Iterate through all the hexagons on the map
    for q in range(-map_size, map_size + 1):
        for r in range(-map_size, map_size + 1):
            # Move the hexagon for positioning
            x = q * hex_width
            y = r * hex_height + (q % 2) * (hex_height / 2)

            # Move the coordinates to the center of the screen
            screen_x = width // 2 + x
            screen_y = height // 2 + y

            # Color for regular hexagons
            hex_color = (255, 255, 255)

            # Check for special hexagon types
            # Drawing bases
            for base in map_data['content'].get('base', []):
                if q == base['x'] and r == base['y']:
                    hex_color = (0, 0, 255)  # Blue color for bases
                    break

            # Drawing spawn points
            for spawn_point in map_data['spawn_points']:
                for vehicle_type, points in spawn_point.items():
                    for point in points:
                        if q == point['x'] and r == point['y']:
                            hex_color = (0, 255, 0)  # Green color for spawn points
                            break

            # Drawing hexagons
            draw_hexagon(screen, screen_x, screen_y, hex_size, hex_color)