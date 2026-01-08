# Just In Enough Time Studio (JIET Studio)

JIET Studio is a comprehensive GUI application designed to streamline the workflow for YOLO object detection projects. From data annotation to model training and inference, this tool provides a unified interface for managing your computer vision tasks.

## Features

*   **Project Management**: Easily create, load, and manage object detection projects.
*   **Integrated Labeling Tool**: Built-in image annotation tool for creating bounding boxes and managing classes.
*   **Data Augmentation**: Dedicated augmentation tab for applying various transformations (rotation, flip, brightness, contrast, blur, noise, etc.) to expand your dataset with real-time preview capabilities.
*   **YOLO Training**: User-friendly interface to configure and launch YOLO training sessions. Supports customization of epochs, batch size, image size, and model selection.
*   **Inference & Testing**: Test your trained models on images or video feeds directly within the application.
*   **Theme Support**: Customizable user interface with theme management.
*   **Dependency Management**: Automatic check and installation of required Python packages.

## Prerequisites

*   Python 3.8 or higher
*   Windows OS (recommended)

## Installation

1.  Clone this repository or download the source code.
2.  Navigate to the project directory.

## Usage

1.  Run the application:
    ```bash
    python main.py
    ```
2.  On the first run, the application will check for missing dependencies (listed in `requirements.txt`) and prompt you to install them.
3.  **Create a Project**: Start by creating a new project or loading an existing one.
4.  **Label Data**: Use the "Labeling" tab to annotate your images.
5.  **Augment Dataset**: (Optional) Use the "Augmentation" tab to expand your dataset with various transformations and filters.
6.  **Train Model**: Switch to the "Training" tab, configure your parameters, and start training.
7.  **Test**: Use the "Inference" tab to validate your model's performance.

## Shortcuts

*   **Labeling**: When in the labeling tab, you can use the following shortcuts:
    *   `Ctrl + S` - Save and move to next image
    *   `Scroll wheel` - Change the drawing class
    *   `Ctrl + Shift + D` OR `Del` - Delete current image
    *   `Ctrl + Shift + D` OR `Del` - Delete selected label
    
    Also to remove the Classes you can select the class you want to remove and then you can use the `-` GUI button to delete it.

## Dependencies

*   `ultralytics` (YOLO)
*   `opencv-python`
*   `Pillow`
*   `pyyaml`
*   `tk` (usually included with Python)

---

Most of this application is made with AI slop. As soon as possible the project will be made from scratch by me a human. This AI slop version was just a proof of concept and a tool for anybody whos willing to use this to train and test their models.
