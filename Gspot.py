import re
import os
import shutil
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import numpy as np
from tempfile import mkdtemp

def parse_gcode(gcode_file):
    movements = []
    print("Parsing G-code file...")
    with open(gcode_file, 'r') as file:
        previous_pos = [0, 0, 0]  # Initial position (X, Y, Z)
        extrusion = 0  # Start with no extrusion
        line_count = 0  # Debug: Count lines
        for line in file:
            line_count += 1
            if line.startswith('G1'):
                # Regex to capture G1 commands with X, Y, Z, and E
                x = re.search(r'X(-?\d+\.?\d*)', line)
                y = re.search(r'Y(-?\d+\.?\d*)', line)
                z = re.search(r'Z(-?\d+\.?\d*)', line)
                e = re.search(r'E(-?\d+\.?\d*)', line)
                
                new_pos = previous_pos.copy()
                if x:
                    new_pos[0] = float(x.group(1))
                if y:
                    new_pos[1] = float(y.group(1))
                if z:
                    new_pos[2] = float(z.group(1))
                if e:
                    extrusion = float(e.group(1))
                
                # Only add movements where extrusion occurs or valid positional change
                if extrusion > 0 or (x or y or z):  # Movements with extrusion or any valid position change
                    movements.append((new_pos, extrusion))  # Store position and extrusion
                
                previous_pos = new_pos

        print(f"Parsed {line_count} lines, {len(movements)} movements found.")
    return movements

def save_animation_frames(movements, temp_dir):
    """
    Group points by their Z value and create a frame for each unique Z layer.
    """
    print("Saving animation frames...")
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # Group points by their Z value
    layers = {}
    for position, extrusion in movements:
        z_value = round(position[2], 2)  # Round Z to 2 decimal places for grouping
        if z_value not in layers:
            layers[z_value] = []
        layers[z_value].append(position)

    frame_paths = []
    frame_count = 0

    # Create a frame for each Z layer
    for z_value, points in sorted(layers.items()):
        frame_count += 1
        print(f"Adding frame {frame_count} for Z={z_value}...")

        x_vals = [p[0] for p in points]
        y_vals = [p[1] for p in points]
        z_vals = [p[2] for p in points]

        # Plot only the lines (no markers)
        ax.plot(x_vals, y_vals, z_vals, color='r', linestyle='-', linewidth=2)

        # Save the frame
        frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
        plt.savefig(frame_path)
        frame_paths.append(frame_path)

    plt.close(fig)
    print(f"Saved {len(frame_paths)} frames.")
    return frame_paths

def create_gif_from_frames(frame_paths, gif_file, duration=0.5):
    print(f"Creating GIF from {len(frame_paths)} frames...")
    frames = [imageio.imread(path) for path in frame_paths]
    imageio.mimsave(gif_file, frames, format='GIF', duration=duration)
    print(f"GIF saved to {gif_file}.")

def write_obj(vertices, faces, obj_file):
    """
    Write the mesh (vertices, faces) to an .obj file.
    """
    print(f"Writing .obj file: {obj_file}...")
    with open(obj_file, 'w') as file:
        for vertex in vertices:
            # Swap Y and Z to account for the 90-degree rotation
            file.write(f"v {vertex[0]} {vertex[2]} {vertex[1]}\n")
        for face in faces:
            file.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")  # OBJ faces are 1-indexed
    print(f"OBJ file saved to {obj_file}.")

def generate_mesh(movements):
    vertices = []
    edges = []
    
    # Create vertices based on positions
    for i, (position, extrusion) in enumerate(movements):
        vertices.append(position)
        if i > 0:
            # Create an edge between consecutive positions
            edges.append((i - 1, i))
    
    return vertices, edges

def create_faces(vertices, edges, layer_height):
    faces = []
    
    # Group vertices by layer (based on Z coordinate)
    layers = {}
    for i, vertex in enumerate(vertices):
        z_layer = int(vertex[2] / layer_height)  # Round Z value to layer level
        if z_layer not in layers:
            layers[z_layer] = []
        layers[z_layer].append(i)
    
    # Create faces by connecting vertices in the same layer
    for z_layer in layers:
        layer_vertices = layers[z_layer]
        for i in range(len(layer_vertices) - 1):
            # Create faces between consecutive vertices
            face = (layer_vertices[i], layer_vertices[i + 1], layer_vertices[(i + 1) % len(layer_vertices)])
            faces.append(face)
    
    return faces

def gcode_to_obj_with_animation(gcode_file, obj_file, gif_file, layer_height=0.2):
    print(f"Starting conversion for {gcode_file}...")
    movements = parse_gcode(gcode_file)

    # Generate mesh (vertices, edges)
    vertices, edges = generate_mesh(movements)

    # Generate faces based on mesh and layer height
    faces = create_faces(vertices, edges, layer_height)

    # Write the object file
    write_obj(vertices, faces, obj_file)

    # Temporary directory for saving frames
    temp_dir = mkdtemp()
    try:
        frame_paths = save_animation_frames(movements, temp_dir)
        create_gif_from_frames(frame_paths, gif_file)
    finally:
        shutil.rmtree(temp_dir)  # Clean up temporary files

    print(f"GIF animation saved as {gif_file}")

# Example usage
gcode_to_obj_with_animation('input.gcode', 'output.obj', 'animation.gif')
