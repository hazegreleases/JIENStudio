import bpy
import os
import sys
import math
import mathutils
import random
import platform

def clear_scene():
    """Clear all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def get_blender_builtin_hdris():
    """Find built-in HDRI files in Blender installation."""
    import platform
    
    # Try to find Blender's datafiles directory
    blender_version = bpy.app.version_string.split('.')[0] + '.' + bpy.app.version_string.split('.')[1]
    
    possible_paths = []
    
    if platform.system() == 'Windows':
        possible_paths = [
            f"C:\\Program Files\\Blender Foundation\\Blender {blender_version}\\{blender_version}\\datafiles\\studiolights\\world",
            f"C:\\Program Files\\Blender Foundation\\Blender\\{blender_version}\\datafiles\\studiolights\\world",
        ]
    elif platform.system() == 'Darwin':  # macOS
        possible_paths = [
            f"/Applications/Blender.app/Contents/Resources/{blender_version}/datafiles/studiolights/world",
        ]
    else:  # Linux
        possible_paths = [
            f"/usr/share/blender/{blender_version}/datafiles/studiolights/world",
        ]
    
    # Find existing path
    for path in possible_paths:
        if os.path.exists(path):
            hdris = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.exr')]
            if hdris:
                return hdris
    
    return []

def setup_environment():
    """Sets up HDRI environment lighting."""
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    # Clear existing nodes
    nodes.clear()
    
    # Add nodes: Texture Coordinate -> Mapping -> Environment Texture -> Background -> Output
    node_texcoord = nodes.new(type='ShaderNodeTexCoord')
    node_mapping = nodes.new(type='ShaderNodeMapping')
    node_env = nodes.new(type='ShaderNodeTexEnvironment')
    node_background = nodes.new(type='ShaderNodeBackground')
    node_output = nodes.new(type='ShaderNodeOutputWorld')
    
    # Try to use built-in HDRIs
    builtin_hdris = get_blender_builtin_hdris()
    if builtin_hdris:
        selected_hdri = random.choice(builtin_hdris)
        node_env.image = bpy.data.images.load(selected_hdri)
        print(f"Using built-in HDRI: {os.path.basename(selected_hdri)}")
    else:
        print("Warning: No HDRI found, using solid color background")
    
    # Connect nodes
    links.new(node_texcoord.outputs['Generated'], node_mapping.inputs['Vector'])
    links.new(node_mapping.outputs['Vector'], node_env.inputs['Vector'])
    links.new(node_env.outputs['Color'], node_background.inputs['Color'])
    links.new(node_background.outputs['Background'], node_output.inputs['Surface'])
    
    # Randomize rotation (Z-axis rotation in radians)
    node_mapping.inputs['Rotation'].default_value[2] = random.uniform(0, 2 * math.pi)
    
    # Set background strength
    node_background.inputs['Strength'].default_value = 1.0

def setup_eevee_scene():
    """Configure Eevee render engine with transparency."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.film_transparent = True
    
    # Eevee specific settings for better quality
    # scene.eevee.use_gtao = True
    # scene.eevee.use_bloom = True



def import_model(filepath):
    """Import 3D model based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.obj':
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext in ['.gltf', '.glb']:
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif ext == '.dae':
        bpy.ops.wm.collada_import(filepath=filepath)
    elif ext == '.stl':
        bpy.ops.wm.stl_import(filepath=filepath)
    elif ext == '.ply':
        bpy.ops.wm.ply_import(filepath=filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    # Get imported objects
    imported = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    return imported

def setup_lighting():
    """Add basic lighting (in addition to HDRI)."""
    # Key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
    key_light = bpy.context.active_object
    key_light.data.energy = 1.0  # Reduced energy since we have HDRI

def setup_camera(target_objects):
    """Setup camera to frame all imported objects."""
    bpy.ops.object.camera_add(location=(0, 0, 0))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera
    
    # Calculate bounding box of all objects
    if target_objects:
        # Get combined bounds
        min_coords = [float('inf')] * 3
        max_coords = [float('-inf')] * 3
        
        for obj in target_objects:
            for vertex in obj.bound_box:
                # Convert bound_box vertex to Vector
                bbox_vec = mathutils.Vector(vertex)
                world_coord = obj.matrix_world @ bbox_vec
                for i in range(3):
                    min_coords[i] = min(min_coords[i], world_coord[i])
                    max_coords[i] = max(max_coords[i], world_coord[i])
        
        # Calculate center and size
        center = [(min_coords[i] + max_coords[i]) / 2 for i in range(3)]
        size = max([max_coords[i] - min_coords[i] for i in range(3)])
        
        # Position camera
        distance = size * 2.5
        camera.location = (center[0] + distance, center[1] - distance, center[2] + distance * 0.7)
        
        # Point camera at center
        direction = bpy.data.objects.new("CameraTarget", None)
        direction.location = center
        bpy.context.collection.objects.link(direction)
        
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = direction
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
    
    return camera

def render_turntable(output_base, frames=24):
    """Render a turntable animation."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = frames
    
    # Find all root objects (objects without a parent) to rotate
    # We only care about objects that are part of the imported model, 
    # but since we cleared the scene, that's basically everything except the camera/lights we added.
    # However, to be safe, let's just grab all root objects that are MESH or EMPTY (in case the root is an empty).
    
    root_objects = [obj for obj in bpy.context.scene.objects 
                   if obj.parent is None 
                   and obj.type in ['MESH', 'EMPTY', 'ARMATURE']
                   and obj.name not in ['Camera', 'CameraTarget', 'Sun', 'Area', 'Spot']]
    
    if root_objects:
        # Create empty at center to rotate around
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        turntable_empty = bpy.context.active_object
        turntable_empty.name = "Turntable_Center"
        
        # Parent root objects to the turntable empty
        # Use 'KEEP_TRANSFORM' to ensure they stay in place relative to the new parent
        for obj in root_objects:
            obj.parent = turntable_empty
            obj.matrix_parent_inverse = turntable_empty.matrix_world.inverted()
        
        # Animate rotation
        turntable_empty.rotation_euler = (0, 0, 0)
        turntable_empty.keyframe_insert(data_path="rotation_euler", frame=1)
        
        turntable_empty.rotation_euler = (0, 0, 2 * math.pi)
        turntable_empty.keyframe_insert(data_path="rotation_euler", frame=frames + 1) # +1 for seamless loop
    
    # Render frames
    output_dir = os.path.dirname(output_base)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for frame in range(1, frames + 1):
        scene.frame_set(frame)
        output_path = f"{output_base}_{frame:04d}.png"
        scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        print(f"Rendered frame {frame}/{frames}")

if __name__ == "__main__":
    print("--- Blender: Starting Preview Render ---")
    # Parse arguments
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # Get args after "--"
    
    if len(argv) < 2:
        print("Usage: blender --background --python preview.py -- <model_file> <output_base>")
        sys.exit(1)
    
    model_file = argv[0]
    output_base = argv[1].replace('.gif', '')  # Remove .gif extension
    
    print(f"Generating preview for: {model_file}")
    
    try:
        clear_scene()
        setup_eevee_scene()
        
        imported = import_model(model_file)
        print(f"Imported {len(imported)} objects")
        
        setup_environment()
        setup_lighting()
        setup_camera(imported)
        
        render_turntable(output_base, frames=24)
        
        print(f"Preview saved to {output_base}_0001.png")
    except Exception as e:
        print(f"Error generating preview: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
