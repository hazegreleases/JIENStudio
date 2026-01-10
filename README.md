### Train YOLOv11 Locally. No Cloud. No Limits.
**The all-in-one GUI for Labeling, Augmentation, and Training on your own GPU.**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![YOLOv11](https://img.shields.io/badge/YOLO-v11%2Fv8-magenta) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Active-success)

---

## 🚀 Why JIETStudio?

Most YOLO tools force you to upload gigabytes of data to the cloud, wait for processing, and pay for training credits. **JIETStudio runs 100% offline on your hardware.**

It is designed for **Flow State**: no popups, no "Are you sure?" dialogs, just speed.

| Feature | Cloud Tools (Roboflow/CVAT) | JIETStudio |
| :--- | :--- | :--- |
| **Privacy** | Data uploaded to public servers | **100% Local & Private** |
| **Labeling** | Slow dropdown menus | **Scroll-Wheel Class Switching And Auto-Labeling** |
| **Saving** | Latency + Spinners | **Instant "Green Flash" Save** |
| **Training** | Limited Credits / Queues | **Unlimited Local GPU Training** |
| **Cost** | $$$ Monthly Subscriptions | **Free & Open Source** |

---

## ⚡ Key Features

### 1. The "Flow State" Labeler
Designed for speed. Switch classes with your mouse wheel. Zoom with `Ctrl+Scroll` for pixel-perfect accuracy. Save instantly with `Ctrl+S`. No lag, no waiting.

### 2. Industrial-Grade Augmentation (Plugin System)
Don't just use standard blurs. JIETStudio features a **modular plugin system**.
* **Built-in:** Rotate, Flip, Noise, Brightness.
* **Custom Scripting:** Write your own Python filters and use them. The UI automatically generates sliders for your custom parameters.

### 3. One-Click Training
Forget messing with `data.yaml` files or complex terminal commands.
* Select your Model (YOLOv8 / YOLO11 / etc.)
* Select Image Size & Epochs.
* Click **Train**.
* *The app handles the entire folder structure and formatting for you.*

### 4. Integrated Inference
Test your model immediately after training. Pick images, run a video file, or open your webcam to see real-time detections with your new model.

---

## 🛠️ Installation

**Prerequisites:**
* Python 3.8+
* Windows OS (Recommended for GUI support)
* A GPU (NVIDIA RTX recommended for training)

**Setup:**
1.  Clone the repository:
    ```bash
    git clone [https://github.com/hazegreleases/JIETStudio.git](https://github.com/hazegreleases/JIETStudio.git)
    cd JIETStudio
    ```
2.  Run the app (Dependencies auto-install on first run):
    ```bash
    python main.py
    ```

---

## 🎮 Workflow Shortcuts

Master these to label 10x faster:

| Action | Shortcut |
| :--- | :--- |
| **Save & Next Image** | `Ctrl + S` (The "Green Flash") |
| **Switch Class** | `Mouse Scroll Wheel` |
| **Zoom In/Out** | `Ctrl + Mouse Scroll` |
| **Delete Box** | `Del` |
| **Delete Image** | `Ctrl + Shift + D` |

---

## 🤝 Contributing

This project is actively maintained. We welcome pull requests!
* **Found a bug?** Open an issue.
* **Created a cool Augmentation Filter?** Submit it to the `filters/community` folder!

**Current Status:** *Rapidly Evolving.* Originally a proof-of-concept, now growing into a robust local tool.

---

## 🏷️ Topics
`yolov11`, `yolov8`, `object-detection`, `computer-vision`, `labeling-tool`, `image-annotation`, `training-gui`, `ultralytics`, `offline`, `data-augmentation`, `python-gui`, `auto-labeling`, `local-training`, `industrial-ai`
