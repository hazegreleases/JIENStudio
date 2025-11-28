# Roadmap: Just In Enough Time Studio (JIET Studio)

## Vision
To build the ultimate, all-in-one open-source AI training and simulation platform. A single program where users can model, simulate, render, and train vision models in a "close to real life" environment.

## 1. Core Simulation & Physics
- **Rigid Body Physics Engine**: Implementation of a robust physics engine supporting rigid body dynamics, realistic collisions, and gravity.
- **Dynamic Industrial Mechanisms**: Native support for complex moving parts like escalators, elevators, conveyor belts, and robotic arms that interact physically with objects.
- **"Real-ish" Playground**: A sandbox environment where physics and visuals mimic real-world conditions for reliable model inference testing.

## 2. Advanced Rendering & Vision
- **High-Fidelity Rasterized Lighting**:
    - PBR (Physically Based Rendering) support.
    - Multi-color light sources and dynamic shadows.
    - Optimized for realism to narrow the sim-to-real gap.
- **Scalable Multi-Camera System**:
    - Dynamic camera allocation based on hardware capabilities (Target: VRAM / 4 concurrent cameras).
    - Real-time feed from simulated cameras to the AI model for immediate inference testing.

## 3. Synthetic Data Generation
- **Auto-Labeling Pipeline**: Automatic generation of bounding boxes, segmentation masks, and class labels for rendered scenes.
- **Procedural Scenario Generation**: "Custom 3D Training Ground" where users define conditions (weather, lighting, object density) and the system generates wanted amount of variations.
- **Texture & Material Randomization**: Automated domain randomization to improve model robustness.

## 4. Integrated Content Creation Tools
- **Built-in 3D Modeler**:
    - A modular, basic quad-based 3D modeling tool.
    - Designed for quick creation of training objects without leaving the app.
- **Material Editor**:
    - User-friendly editor for creating and modifying PBR materials.
    - Drag-and-drop workflow for applying textures to simulation objects.
    - Access to medium/low-quality assets and basic primitives.
- **Community made assets**
    - By using python and the app API, users can create and share their own assets containing models, materials, textures, hdri enviromants and python based tools.

## 5. Ecosystem & Monetization
- **Open Source Core**: The entire software platform (simulation, training, modeling tools) remains free and open source.
- **Asset Marketplace (Patreon Model)**:    
    - **Premium Tier **: Exclusive access to high-fidelity, "most real looking" 3D models and scanned assets.
    - *Note: Functionality is never locked, only cosmetic high-end asset files.*

## 6. Future "Never Seen" Features
- **Inference Helpers**: Real-time visualization of model attention maps and confidence scores within the 3D view.
- **Modular Plugin System**: Allow community contributions for new physics constraints, sensors (LiDAR, Depth), and rendering techniques.

---
*This roadmap is a living document and will evolve as we push the boundaries of AI simulation. This is a long term project and we are not sure if we will be able to achieve all of this. We are open to suggestions and contributions. As this system would take years to develop(if possible at all), the project will continue to be open-source and community driven. Only the pre-made high-end assets will be paid for, the rest will be free and open source. As im still in school and this project probably going from python to c++ in the future, the project will evolve very slowly. So please understand that this project could take more than 5 years to complete. And were open to any community made contributions to the main fork of the project. If you want to contribute, please open an issue or a pull request.*
