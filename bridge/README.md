# Bridge (Communication Layer)

This directory contains the logic for communication between the Python Core, Godot Simulation, and Blender Factory.

## Components
- **Server**: A Python-based server (WebSocket or IPC) that manages state and routes commands.
- **Client (Godot)**: GDScript or C# client to receive simulation commands.
- **Client (Blender)**: Python script to receive rendering tasks.

## Protocol
(To be defined: JSON-based command structure for spawning objects, moving cameras, and retrieving status)
