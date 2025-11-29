# Task Checklist: ohgodpleasehelpme Branch

## Phase 1: The Foundation (The Triad)
- [x] **Bridge Server**: Implement basic TCP server for communication. <!-- id: 0 -->
- [x] **Factory Prototype**: Create Blender script for background rendering. <!-- id: 1 -->
- [x] **Simulation Client**: Write GDScript for Godot TCP connection. <!-- id: 2 -->
- [x] **Integration Test**: Verify Python -> Blender connection via `launcher.py`. <!-- id: 3 -->

## Phase 2: Synthetic Data Generation (The Factory)
- [x] **Use cycles and auto-find the best renderer like cuda or apple metal or optix for intel**: <!-- id: 4 -->
- [x] **Auto-Labeling**: Upgrade Blender script to generate YOLO bounding boxes. <!-- id: 5 -->
- [x] **Domain Randomization**: Add random lighting, textures, and camera angles. <!-- id: 6 -->
- [x] **Batch Processing**: Allow requesting N images in a batch. <!-- id: 7 -->

## Phase 3: The Playground (The Simulation)
- [ ] **Godot Project Setup**: Initialize the Godot project (User Action Required). <!-- id: 8 -->
- [ ] **Object Spawner**: Implement logic to spawn objects via Bridge commands. <!-- id: 9 -->
- [ ] **Camera Streaming**: Stream viewport data back to Python (if possible) or save to disk. <!-- id: 10 -->

## Phase 4: The Interface (The App)
- [ ] **Bridge UI**: Create a control panel in the main app to manage the server. <!-- id: 11 -->
- [x] **Job Manager**: UI to queue rendering tasks for the Factory. <!-- id: 12 -->

## Phase 5: Advanced Features
- [ ] **Physics Sync**: Sync rigid body states between Godot and Python. <!-- id: 13 -->
- [ ] **Asset Pipeline**: Automate loading `.blend` files into Godot. <!-- id: 14 -->
