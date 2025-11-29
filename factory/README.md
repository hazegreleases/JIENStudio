# Factory (Blender Backend)

This directory contains the Blender scripts and assets for high-fidelity rendering and synthetic data generation.

## Purpose
- **Data Generation**: Scripts to automate rendering of training datasets with domain randomization.
- **Auto-Labeling**: Logic to generate bounding boxes and segmentation masks for rendered images.
- **Asset Processing**: Tools to process and optimize 3D models for the simulation engine.

## Usage
Scripts in this directory are typically executed via the Blender command line interface:
`blender --background --python factory/script_name.py`
