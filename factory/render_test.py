import bpy
import os
import json
import sys
import random
import math
import mathutils
from bpy_extras.object_utils import world_to_camera_view

# --- GPU Configuration ---
def configure_gpu():
    # Attempts to configure Blender to use the best available GPU (CUDA, OptiX, Metal).
    print("Configuring GPU...")
    preferences = bpy.context.preferences
    cycles_preferences = preferences.addons['cycles'].preferences
    
    # Refresh devices
    cycles_preferences.refresh_devices()
    
    # Priority order for device types
    device_types = ['OPTIX', 'CUDA', 'METAL', 'HIP', 'ONEAPI']
    
    found_device = False
    for device_type in device_types:
        try:
            cycles_preferences.compute_device_type = device_type
            print(f"Attempting to use {device_type}...")
            
            # Enable all devices of this type
            devices = cycles_preferences.get_devices_for_type(compute_device_type=device_type)
            if devices:
                for device in devices:
                    device.use = True
                    print(f"  - Enabled: {device.name}")
                found_device = True
                break
        except Exception as e:
            print(f"  - Failed to set {device_type}: {e}")
            
    if found_device:
        bpy.context.scene.cycles.device = 'GPU'
        print("GPU Configuration Successful.")
    else:
        bpy.context.scene.cycles.device = 'CPU'
        print("No suitable GPU found. Falling back to CPU.")

# --- HDRI/Environment Setup ---
def get_blender_builtin_hdris():
    # Get list of Blender's built-in HDRI files.
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

def setup_environment(hdri_path=None):
    # Sets up HDRI environment lighting.
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
    
    # Load HDRI
    if hdri_path and os.path.exists(hdri_path):
        node_env.image = bpy.data.images.load(hdri_path)
        print(f"Loaded HDRI: {os.path.basename(hdri_path)}")
    else:
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
    
    # Randomize background strength
    node_background.inputs['Strength'].default_value = random.uniform(0.5, 1.5)

def setup_compositor(blur_amount=0.0, distortion_amount=0.0, noise_amount=0.0, jitter_amount=0.0):
    # Sets up the compositor for realistic camera effects.
    bpy.context.scene.use_nodes = True
    bpy.context.scene.render.use_compositing = True
    tree = bpy.context.scene.node_tree
    nodes = tree.nodes
    links = tree.links
    
    print(f"DEBUG: Setting up compositor. Blur={blur_amount}, Dist={distortion_amount}, Noise={noise_amount}, Jitter={jitter_amount}")
    
    # Clear existing nodes
    nodes.clear()
    
    # Add Render Layers
    node_rl = nodes.new(type='CompositorNodeRLayers')
    node_rl.location = (-800, 0)
    
    # Current connection point
    current_output = node_rl.outputs['Image']
    current_location_x = -600
    
    # 1. Lens Distortion (Chromatic Aberration & Dispersion)
    if distortion_amount > 0:
        node_dist = nodes.new(type='CompositorNodeLensdist')
        node_dist.location = (current_location_x, 0)
        node_dist.inputs['Dispersion'].default_value = distortion_amount
        node_dist.use_fit = True
        
        links.new(current_output, node_dist.inputs['Image'])
        current_output = node_dist.outputs['Image']
        current_location_x += 200
    
    # 2. Color Jitter (Hue/Saturation/Value)
    if jitter_amount > 0:
        node_hsv = nodes.new(type='CompositorNodeHueSat')
        node_hsv.location = (current_location_x, 0)
        
        # Randomize slightly around 0.5 (default)
        hue_shift = 0.5 + random.uniform(-jitter_amount, jitter_amount) * 0.1
        sat_shift = 1.0 + random.uniform(-jitter_amount, jitter_amount)
        val_shift = 1.0 + random.uniform(-jitter_amount, jitter_amount)
        
        node_hsv.inputs['Hue'].default_value = hue_shift
        node_hsv.inputs['Saturation'].default_value = sat_shift
        node_hsv.inputs['Value'].default_value = val_shift
        
        links.new(current_output, node_hsv.inputs['Image'])
        current_output = node_hsv.outputs['Image']
        current_location_x += 200
    
    # 3. Blur (Gaussian) - Scaled up for visibility
    if blur_amount > 0:
        node_blur = nodes.new(type='CompositorNodeBlur')
        node_blur.location = (current_location_x, 0)
        node_blur.filter_type = 'GAUSS'
        # Scale blur: 1.0 in UI = 10 pixels blur
        scaled_blur = int(blur_amount * 10.0)
        node_blur.size_x = scaled_blur
        node_blur.size_y = scaled_blur
        
        links.new(current_output, node_blur.inputs['Image'])
        current_output = node_blur.outputs['Image']
        current_location_x += 200
    
    # 4. Noise (Grain)
    if noise_amount > 0:
        # Noise Texture
        node_noise_tex = nodes.new(type='CompositorNodeTexture')
        node_noise_tex.location = (current_location_x, 200)
        
        # Create a noise texture if it doesn't exist
        if "NoiseTex" not in bpy.data.textures:
            tex = bpy.data.textures.new("NoiseTex", type='NOISE')
        else:
            tex = bpy.data.textures["NoiseTex"]
        node_noise_tex.texture = tex
        
        # Mix Node (Overlay/Add)
        node_mix = nodes.new(type='CompositorNodeMixRGB')
        node_mix.location = (current_location_x, 0)
        node_mix.blend_type = 'OVERLAY' # Stronger than Soft Light
        node_mix.inputs['Fac'].default_value = noise_amount
        
        links.new(current_output, node_mix.inputs[1]) # Image to slot 1
        links.new(node_noise_tex.outputs['Color'], node_mix.inputs[2]) # Noise to slot 2
        
        current_output = node_mix.outputs['Image']
        current_location_x += 200

    # Output to Composite
    node_comp = nodes.new(type='CompositorNodeComposite')
    node_comp.location = (current_location_x + 200, 0)
    links.new(current_output, node_comp.inputs['Image'])

# --- Bounding Box Logic ---
def get_bounding_box(scene, camera, obj):
    # Returns camera space bounding box based on ALL mesh objects in the scene.
    # This ensures we label the entire model, not just one part.
    
    # Get all mesh objects in the scene
    all_mesh_objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    
    if not all_mesh_objects:
        return None
    
    min_x, min_y = 1.0, 1.0
    max_x, max_y = 0.0, 0.0
    
    found_visible = False
    
    # Process all mesh objects
    for mesh_obj in all_mesh_objects:
        matrix_world = mesh_obj.matrix_world
        mesh = mesh_obj.data
        
        # Get all vertices in world space
        vertices_world = [matrix_world @ v.co for v in mesh.vertices]
        
        for v_world in vertices_world:
            # Project to camera space
            co_2d = world_to_camera_view(scene, camera, v_world)
            
            # Skip if behind camera
            if co_2d.z < 0:
                continue
            
            found_visible = True
            
            # Track min/max
            min_x = min(min_x, co_2d.x)
            max_x = max(max_x, co_2d.x)
            min_y = min(min_y, co_2d.y)
            max_y = max(max_y, co_2d.y)
    
    if not found_visible:
        return None
    
    # Clamp to image bounds
    min_x = max(0.0, min(1.0, min_x))
    max_x = max(0.0, min(1.0, max_x))
    min_y = max(0.0, min(1.0, min_y))
    max_y = max(0.0, min(1.0, max_y))
    
    # Calculate YOLO format (center, width, height)
    width = max_x - min_x
    height = max_y - min_y
    
    center_x = min_x + width / 2
    center_y = min_y + height / 2
    
    # Flip Y (Blender is bottom-up, YOLO is top-down)
    center_y = 1.0 - center_y
    
    # Only return if box is reasonable size
    if width > 0.01 and height > 0.01:
        return (center_x, center_y, width, height)
    
    return None

# --- Randomization ---
def randomize_object_material(obj):
    # Apply random PBR material to object.
    # Create or get material
    if obj.data.materials:
        mat = obj.data.materials[0]
    else:
        mat = bpy.data.materials.new(name="RandomMat")
        obj.data.materials.append(mat)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add Principled BSDF + Output
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Randomize PBR properties
    node_bsdf.inputs['Base Color'].default_value = (
        random.uniform(0.1, 1.0),
        random.uniform(0.1, 1.0),
        random.uniform(0.1, 1.0),
        1.0
    )
    node_bsdf.inputs['Metallic'].default_value = random.uniform(0.0, 1.0)
    node_bsdf.inputs['Roughness'].default_value = random.uniform(0.1, 0.9)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    print(f"Randomized material: Color={node_bsdf.inputs['Base Color'].default_value[:3]}")

def randomize_camera(camera, target_location=(0, 0, 0), target_obj=None):
    # Randomize camera position while ensuring object is well-framed.
    # Get all mesh objects in the scene (excluding camera/lights)
    all_mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    
    if all_mesh_objects:
        # Calculate combined bounding box for all mesh objects
        min_coords = [float('inf')] * 3
        max_coords = [float('-inf')] * 3
        
        for obj in all_mesh_objects:
            for vertex in obj.bound_box:
                world_coord = obj.matrix_world @ mathutils.Vector(vertex)
                for i in range(3):
                    min_coords[i] = min(min_coords[i], world_coord[i])
                    max_coords[i] = max(max_coords[i], world_coord[i])
        
        bbox_min = mathutils.Vector(min_coords)
        bbox_max = mathutils.Vector(max_coords)
        
        # Calculate object size and center
        object_size = (bbox_max - bbox_min).length
        object_center = (bbox_min + bbox_max) / 2
        
        # Adjust target location to object center
        target_location = object_center
        
        # Distance based on object size (ensure it fits in frame with some margin)
        distance = random.uniform(object_size * 2.0, object_size * 3.5)
    else:
        distance = random.uniform(4, 8)
    
    # Random spherical coordinates
    theta = random.uniform(0, 2 * math.pi)
    phi = random.uniform(0.3, 1.2)  # Avoid too low or high angles
    
    x = distance * math.sin(phi) * math.cos(theta)
    y = distance * math.sin(phi) * math.sin(theta)
    z = distance * math.cos(phi)
    
    camera.location = (
        target_location[0] + x,
        target_location[1] + y,
        target_location[2] + z
    )
    
    # Point camera at target
    direction = mathutils.Vector(target_location) - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    print(f"Camera placed at {camera.location}, targeting {target_location}")

# --- Model Import ---
def import_model(filepath):
    # Import 3D model based on file extension
    print(f"--- Blender: Importing Model {os.path.basename(filepath)} ---")
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
        print(f"Warning: Unsupported format {ext}, creating cube as fallback")
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        return [bpy.context.active_object]
    
    # Get imported mesh objects
    imported = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if not imported:
        print("Warning: No mesh objects imported, creating cube as fallback")
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        imported = [bpy.context.active_object]
    
    return imported

# --- Scene Setup ---
def create_scene(model_path=None):
    # Create base scene with Cycles + HDRI.
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Set Render Engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    
    # Setup HDRI Environment
    setup_environment()

    # Load model or create cube
    if model_path and os.path.exists(model_path):
        print(f"Loading model: {os.path.basename(model_path)}")
        objects = import_model(model_path)
        target_obj = objects[0]  # Use first object as target
        target_obj.name = "TargetObject"
    else:
        # Fallback: Add a Cube (The Target)
        print("No model provided, using default cube")
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        target_obj = bpy.context.active_object
        target_obj.name = "TargetObject"
    
    # Add a Camera
    bpy.ops.object.camera_add(location=(5, -5, 5))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera
    
    return target_obj, camera

def render_and_label(output_dir, filename_base, target_obj, camera, class_idx=0):
    # Render image and generate YOLO label.
    scene = bpy.context.scene
    
    # 1. Render Image
    image_path = os.path.join(output_dir, f"{filename_base}.png")
    scene.render.filepath = image_path
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    bpy.ops.render.render(write_still=True)
    print(f"Render saved to {image_path}")
    
    # 2. Generate Label
    bbox = get_bounding_box(scene, camera, target_obj)
    
    if bbox:
        label_path = os.path.join(output_dir, f"{filename_base}.txt")
        cx, cy, w, h = bbox
        
        with open(label_path, "w") as f:
            f.write(f"{class_idx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
        print(f"Label saved to {label_path} (class {class_idx})")
    else:
        print("Object not visible, no label generated.")

# --- Batch Processing ---
def generate_batch(output_dir, num_samples=100, model_path=None, class_idx=0, 
                  blur=0.0, distortion=0.0, noise=0.0, jitter=0.0):
    # Generate batch of training samples with randomization.
    target_obj, camera = create_scene(model_path)
    
    for i in range(num_samples):
        print(f"\n=== Generating Sample {i+1}/{num_samples} ===")
        
        # Randomize camera and lighting (preserve original materials)
        randomize_camera(camera, target_location=target_obj.location, target_obj=target_obj)
        setup_environment()  # Re-randomize lighting
        
        # Update compositor for random jitter per frame
        setup_compositor(blur, distortion, noise, jitter)
        
        # Render
        filename = f"train_sample_{i+1:04d}"
        render_and_label(output_dir, filename, target_obj, camera, class_idx)

if __name__ == "__main__":
    print("--- Blender: Starting Batch Generation ---")
    
    try:
        # Parse command line arguments
        model_path = None
        class_idx = 0
        num_samples = 10
        blur = 0.0
        distortion = 0.0
        noise = 0.0
        jitter = 0.0
        
        print(f"DEBUG: sys.argv = {sys.argv}")
        if "--" in sys.argv:
            args = sys.argv[sys.argv.index("--") + 1:]
            print(f"DEBUG: args = {args}")
            print(f"DEBUG: len(args) = {len(args)}")
            if len(args) > 0:
                model_path = args[0]
                print(f"Model argument: {model_path}")
            if len(args) > 1:
                class_idx = int(args[1])
                print(f"Class index: {class_idx}")
            if len(args) > 2:
                num_samples = int(args[2])
                print(f"Batch size: {num_samples}")
            if len(args) > 3:
                blur = float(args[3])
            if len(args) > 4:
                distortion = float(args[4])
            if len(args) > 5:
                noise = float(args[5])
            if len(args) > 6:
                jitter = float(args[6])
        
        configure_gpu()
        
        output_dir = os.path.join(os.getcwd(), "factory_output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate samples
        generate_batch(output_dir, num_samples=num_samples, model_path=model_path, class_idx=class_idx,
                      blur=blur, distortion=distortion, noise=noise, jitter=jitter)
        
        print("\n--- Factory Task Complete ---")
    except Exception as e:
        print(f"\n!!! ERROR: {str(e)} !!!")
        import traceback
        traceback.print_exc()
        sys.exit(1)
