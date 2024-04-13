import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon


def plot_hexagonal_map(map_data):
    # Settings for hexagon size and map size
    hex_size = 1  # Hexagon size
    map_size = map_data['size']

    # Prepare the figure and axes
    fig, ax = plt.subplots(figsize=(8, 8))

    # Function to convert cube coordinates to hex coordinates
    def cube_to_hex(x, y, z):
        col = x + (z - (z & 1)) / 2
        row = z
        return col, row

    # Function to draw hexagons

    def draw_hex(ax, x, y, color, **kwargs):
        # Create RegularPolygon with correct arguments
        hexagon = RegularPolygon(
            (x, y),  # Center of the hexagon
            numVertices=6,  # Number of hexagon sides
            radius=hex_size,  # Radius of the hexagon
            orientation=np.radians(30),  # Optional argument, rotation
            edgecolor='black',  # Edge color
            facecolor=color  # Fill color
            # Remaining optional arguments are forwarded
        )

        ax.add_patch(hexagon)

    # Get 'content' and 'spawn_points' from 'map_data'
    content = map_data.get('content', {})
    spawn_points = map_data.get('spawn_points', [])

    # Draw bases
    for base in content.get('base', []):
        x, y, z = base['x'], base['y'], base['z']
        col, row = cube_to_hex(x, y, z)
        draw_hex(ax, col, row, color='blue')

    # Draw obstacles
    for obstacle in content.get('obstacle', []):
        x, y, z = obstacle['x'], obstacle['y'], obstacle['z']
        col, row = cube_to_hex(x, y, z)
        draw_hex(ax, col, row, color='gray')

    # Draw spawn points
    for spawn_point in spawn_points:
        for vehicle_type, points in spawn_point.items():
            color = 'green' if vehicle_type == 'medium_tank' else 'red'
            for point in points:
                x, y, z = point['x'], point['y'], point['z']
                col, row = cube_to_hex(x, y, z)
                draw_hex(ax, col, row, color=color)

    # Set axis limits
    ax.set_xlim(-map_size, map_size)
    ax.set_ylim(-map_size, map_size)

    # Disable axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Display the hexagonal map
    plt.show()

