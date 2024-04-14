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
        # Convert cube coordinates to hex coordinates (col, row)
        col = x + (z - (z & 1)) / 2
        row = z
        return col, row

    # Function to draw hexagons

    def draw_hex(ax, x, y, color):
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

    # Added Grid
    # Function to draw a hexagonal grid
    def draw_hex_grid(ax, map_size, hex_size):
        # Iterate through rows and columns to draw hexagonal grid
        for row in range(-map_size, map_size + 1):
            for col in range(-map_size, map_size + 1):
                # Calculate the center of the hexagon
                x_center = col * hex_size * 1.5
                y_center = row * hex_size * np.sqrt(3)

                # Adjust the y-coordinate for odd columns
                if col % 2 != 0:
                    y_center += hex_size * np.sqrt(3) / 2

                # Draw the hexagon
                draw_hex(ax, x_center, y_center, color='white')

    # Draw the hexagonal grid
    draw_hex_grid(ax, map_size, hex_size)

    # Get 'content' and 'spawn_points' from 'map_data'
    content = map_data.get('content', {})
    spawn_points = map_data.get('spawn_points', [])

    # Draw bases
    for base in content.get('base', []):
        # Convert cube coordinates to hex coordinates
        x, y, z = base['x'], base['y'], base['z']
        col, row = cube_to_hex(x, y, z)
        draw_hex(ax, col, row, color='blue')

    # Draw obstacles
    for obstacle in content.get('obstacle', []):
        # Convert cube coordinates to hex coordinates
        x, y, z = obstacle['x'], obstacle['y'], obstacle['z']
        col, row = cube_to_hex(x, y, z)
        draw_hex(ax, col, row, color='gray') # Draw a gray hexagon for the obstacle

    # Draw spawn points
    for spawn_point in spawn_points:
        for vehicle_type, points in spawn_point.items():
            # Set color based on the vehicle type
            color = 'green' if vehicle_type == 'medium_tank' else 'red'
            for point in points:
                # Convert cube coordinates to hex coordinates
                x, y, z = point['x'], point['y'], point['z']
                col, row = cube_to_hex(x, y, z)
                # Draw the hexagon with the correct color
                draw_hex(ax, col, row, color=color)

    # Set axis limits
    ax.set_xlim(-map_size, map_size)
    ax.set_ylim(-map_size, map_size)

    # Disable axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # #Display the hexagonal map
    # plt.show()

