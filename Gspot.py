import re

def parse_gcode(gcode_file):
    movements = []
    with open(gcode_file, 'r') as file:
        previous_pos = [0, 0, 0]  # Initial position (X, Y, Z)
        extrusion = 0  # Start with no extrusion
        for line in file:
            if line.startswith('G1'):
                # Regex to capture G1 commands with X, Y, Z, and E
                x = re.search(r'X(-?\d+\.?\d*)', line)
                y = re.search(r'Y(-?\d+\.?\d*)', line)
                z = re.search(r'Z(-?\d+\.?\d*)', line)
                e = re.search(r'E(-?\d+\.?\d*)', line)
                
                # Update positions and extrusion values if they exist
                new_pos = previous_pos.copy()
                if x:
                    new_pos[0] = float(x.group(1))
                if y:
                    new_pos[1] = float(y.group(1))
                if z:
                    new_pos[2] = float(z.group(1))
                if e:
                    extrusion = float(e.group(1))
                
                movements.append((new_pos, extrusion))  # Store position and extrusion
                previous_pos = new_pos
    return movements

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
            faces.append((layer_vertices[i], layer_vertices[i+1], layer_vertices[(i+2)%len(layer_vertices)]))
    
    return faces

def write_obj(vertices, faces, obj_file):
    with open(obj_file, 'w') as file:
        for vertex in vertices:
            file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
        for face in faces:
            file.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")  # OBJ faces are 1-indexed

def gcode_to_obj(gcode_file, obj_file, layer_height=0.2):
    movements = parse_gcode(gcode_file)
    vertices, edges = generate_mesh(movements)
    faces = create_faces(vertices, edges, layer_height)
    write_obj(vertices, faces, obj_file)

# Example usage
gcode_to_obj('input.gcode', 'output.obj')
