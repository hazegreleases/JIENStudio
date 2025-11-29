# Roadmap: Just In Enough Time Studio (JIET Studio)

## Vision
To build the ultimate, all-in-one open-source AI training and simulation platform. A single program where users can model, simulate, render, and train vision models in a "close to real life" environment.

## 1. Core Simulation & Physics (The Engine: Godot)
- **Godot Integration**: 
    - Utilize Godot's high-performance physics engine for rigid body dynamics and collisions.
    - Embed Godot's Scene View directly into the application for the "Real-ish Playground".
    - **Industrial Mechanisms**: Leverage Godot's joint and physics system for elevators, escalators, and conveyors.
- **Real-Time Inference**: 
    - Stream rendered frames from Godot's virtual cameras directly to the Python YOLO model for instant feedback.

## 2. Advanced Rendering & Data Gen (The Factory: Blender)
- **Blender Backend**:
    - Use Blender's `bpy` for photorealistic synthetic data generation (Cycles/Eevee).
    - **Native Editors**: Instead of building custom tools, integrate/launch Blender's native **Object Viewport**, **Shading Tab**, and **Texture Paint** tabs for asset creation.
- **Auto-Labeling**: 
    - Blender scripts to automatically generate bounding boxes and segmentation masks during the render process.

## 3. The "Glue" (Custom Inspector)
- **Unified Control Panel**:
    - A Python-based Inspector that acts as the bridge.
    - **Object Spawner**: Select an object in the Python UI -> Spawns in Godot/Blender.
    - **Camera Controller**: Configure camera parameters (VRAM dependent) in Python -> Updates Godot simulation.
- **Workflow**: 
    - **Edit Mode**: Opens asset in Blender for modeling/texturing.
    - **Sim Mode**: Loads asset into Godot for physics and inference testing.

## 4. Ecosystem & Monetization
- **Open Source Core**: The entire software platform (simulation, training, modeling tools) remains free and open source.
- **Asset Marketplace (Patreon Model)**:    
    - **Premium Tier **: Exclusive access to high-fidelity, "most real looking" 3D models and scanned assets.
    - *Note: Functionality is never locked, only cosmetic high-end asset files.*

## 5. Future "Never Seen" Features
- **Inference Helpers**: Real-time visualization of model attention maps and confidence scores within the 3D view.
- **Modular Plugin System**: Allow community contributions for new physics constraints, sensors (LiDAR, Depth), and rendering techniques.

---
*This roadmap is a living document. The "OhGodPleaseHelpMe" branch marks the start of our ambitious integration of Godot and Blender.*
