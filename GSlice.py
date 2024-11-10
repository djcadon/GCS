import re
import os
import io
import matplotlib as mpl
import matplotlib.pyplot as plt
import imageio.v2 as imageio
from tempfile import mkdtemp

mpl.use('Agg')

def parse_gcode(gcode_file):
    movements = []  # Initialize array for movements
    with open(gcode_file, 'r') as file:
        previous_pos = [0, 0, 0]  # Initial position (X, Y, Z)
        
        for line in file:
            if line.startswith('G1'):  # G1 commands are where print head moves
                # Initialize extrusion to 0 at the beginning of each line
                extrusion = 0

                # Regex to capture G1 commands with X, Y, Z, and E
                x = re.search(r'X(-?\d+\.?\d*)', line)
                y = re.search(r'Y(-?\d+\.?\d*)', line)
                z = re.search(r'Z(-?\d+\.?\d*)', line)
                e = re.search(r'E(-?\d+\.?\d*)', line)

                # Copying array for new movements
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
                if extrusion > 0 or (x or y or z):
                    movements.append(new_pos)  # Store position
                previous_pos = new_pos  # Update previous position

    return movements


def save_animation_frames(movements, temp_dir):
    fig = plt.figure() # Figure to hold frames for GIF
    ax = fig.add_subplot(111, projection='3d') # Defining the frames as XYZ plot
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    tolerance = 0.01  # Tolerance for more points
    layers = {} # Saving frames by layers with tolerance
    for position in movements:
        z_value = round(position[2] / tolerance) * tolerance  # Group by tolerance
        if z_value not in layers: # Checking if Z tolerance exists
            layers[z_value] = [] # Create array with Z value position
        layers[z_value].append(position) # Otherwise append position
    # Collect all coordinates for setting the axis limits
    all_x = [position[0] for position in movements]
    all_y = [position[1] for position in movements]
    all_z = [position[2] for position in movements]
    # Set axis limits based on the min and max values of the coordinates
    min_val = min(min(all_x), min(all_y), min(all_z))
    max_val = max(max(all_x), max(all_y), max(all_z))
    # These limits help the GIF's aspect ratio
    ax.set_xlim([min_val, max_val])
    ax.set_ylim([min_val, max_val])
    ax.set_zlim([min_val, max_val])
    # Create a frame for each Z layer
    frame_paths = []
    frame_count = 0
    # Use a color map to generate a gradient for each frame
    color_map = plt.cm.viridis  # Decided on viridis gradient
    total_frames = len(layers)  # Count of frames for coloring
    # Looping through layers to create frames
    for z_value, points in sorted(layers.items()):
        #print(f"Adding frame {frame_count} for Z={z_value}...") #DEBUG info
        x_vals = [point[0] for point in points]
        y_vals = [point[1] for point in points]
        z_vals = [point[2] for point in points]
        # Map the frame count to a color in the colormap
        color = color_map(frame_count / total_frames)  # Normalize frame count to [0, 1] range
        # Plotting the lines and applying the gradient color
        ax.plot(x_vals, y_vals, z_vals, color=color, linestyle='-', linewidth=2)
        # Save the frame in temporary directory
        frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
        frame_count += 1 #DEBUG info
        plt.savefig(frame_path) # Save the current frame
        frame_paths.append(frame_path) # Add frame to array of frames
        # Setting labels for loops
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_xlim([min_val, max_val])
        ax.set_ylim([min_val, max_val])
        ax.set_zlim([min_val, max_val])
    plt.close(fig) # Close figure for freeing up space
    print(f"Saved {len(frame_paths)} frames.") #DEBUG info
    return frame_paths

def write_obj(vertices, faces, edges, obj_file):
    """
    Write the mesh (vertices, faces) and edges (lines) to an .obj file.
    """
    print(f"Writing .obj file: {obj_file}...")
    
    with open(obj_file, 'w') as file:
        # Write the vertices (v)
        for vertex in vertices:
            # Swap Y and Z to account for the 90-degree rotation
            file.write(f"v {vertex[0]} {vertex[2]} {vertex[1]}\n")
        
        # Write the faces (f)
        for face in faces:
            file.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")  # OBJ faces are 1-indexed
        
        # Write the edges (l)
        for edge in edges:
            # OBJ lines are 1-indexed, so add 1 to each index
            file.write(f"l {edge[0] + 1} {edge[1] + 1}\n")
    
    print(f"OBJ file saved to {obj_file}.")

def generate_mesh(movements):
    vertices = [] # Initializing vertices for return
    edges = [] # Initializing edges for return
    # Create vertices based on positions
    for i, (position) in enumerate(movements):
        vertices.append(position)
        if i > 0:
            # Create an edge between consecutive positions
            edges.append((i - 1, i))
    return vertices, edges

def create_faces(vertices, edges, layer_height):
    faces = [] # Initialized faces for return
    # Group vertices by layer (based on Z coordinate)
    layers = {} # Initializing dictionary for grouping Z values 
    for i, vertex in enumerate(vertices):
        z_layer = int(vertex[2] / layer_height)  # Round Z value to layer level
        if z_layer not in layers: # If Z value not in dict
            layers[z_layer] = [] # Create new layer
        layers[z_layer].append(i) # Otherwise append value
    # Create faces by connecting vertices in the same layer
    for z_layer in layers:
        layer_vertices = layers[z_layer]
        for i in range(len(layer_vertices) - 1):
                # Create faces between consecutive vertices
                face = (layer_vertices[i], layer_vertices[i + 1], layer_vertices[(i + 1) % len(layer_vertices)])
                faces.append(face)
    return faces

def create_obj(gcode_file):
    movements = parse_gcode(gcode_file) # Get movements to create 3-D mesh
    vertices, edges = generate_mesh(movements) # Gather vertices and edges from movements
    faces = create_faces(vertices, edges, layer_height=0.2) # Generating faces 
    obj_buffer = io.StringIO() # Creating a buffer to return obj file
    # Write the vertices (v)
    for vertex in vertices:
        # Swap Y and Z to account for the 90-degree rotation from .gcode to .obj
        obj_buffer.write(f"v {vertex[0]} {vertex[2]} {vertex[1]}\n")
    # Write the faces (f)
    for face in faces:
        obj_buffer.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")  # OBJ faces are 1-indexed
    # Write the edges (l)
    for edge in edges:
        # OBJ lines are 1-indexed, so add 1 to each index
        obj_buffer.write(f"l {edge[0] + 1} {edge[1] + 1}\n")
    obj_content = obj_buffer.getvalue() # Retrieving buffer as string
    obj_buffer.close()
    
    return obj_content

def create_gif(gcode_file):
    movements = parse_gcode(gcode_file) # Get movments for making frames
    print("Done Gcode")
    temp_dir = mkdtemp()  # Temporary directory for saving frames
    print(temp_dir)
    gif_buffer = io.BytesIO() # Byte buffer for returning GIF file
    frame_paths = save_animation_frames(movements, temp_dir) # Creating frames for every group of Z values
    frame_images = []
    for filename in frame_paths:
        frame_images.append(imageio.imread(filename))
    imageio.mimsave(gif_buffer, frame_images, format='GIF', duration=0.5) # Creating Gif
    gif_buffer.seek(0)     # Reset buffer position to the start for return
    return gif_buffer