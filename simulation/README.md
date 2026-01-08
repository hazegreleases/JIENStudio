# Simulation (Godot Engine)

This directory contains the Godot project that serves as the "Real-ish Playground" and physics simulation engine.

## Structure
- `project.godot`: The main Godot project file.
- `scenes/`: Godot scenes (.tscn) for the playground, objects, and simulation environments.
- `scripts/`: GDScript files for simulation logic and communication with the Python bridge.
- `assets/`: 3D models and textures optimized for real-time simulation.

## Integration
This project is designed to be run in a viewport embedded within the main Python application or as a separate window controlled via WebSockets/Shared Memory.
