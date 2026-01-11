# JIET Studio
### The Offline, Unlimited YOLO Training Suite
**Label → Augment → Train → Test. All in one app. Zero cloud dependency.**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![YOLOv11](https://img.shields.io/badge/YOLO-v8%20%7C%20v11-magenta) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Active-success)

---

## 🎯 The Problem

Training object detection models shouldn't require:
- ❌ Uploading your proprietary data to third-party servers
- ❌ Paying $50/month for "credits" to train on your own data
- ❌ Waiting in cloud queues while GPUs sit idle on your desk
- ❌ Complex terminal commands and YAML file editing
- ❌ Switching between 5 different tools for one workflow

---

## 💡 The Solution: JIET Studio

**One desktop app. Complete YOLO workflow. 100% local.**

```
Your Images → Auto-Label (SAM2) → Augment (25+ Filters) → Train (YOLO) → Test → Production Model
                              ↑_____________________|
                                  (All Offline)
```

---

## 🚀 Why JIET Studio Beats The Competition

| Feature | Roboflow | CVAT | Label Studio | JIETStudio |
|---------|----------|------|--------------|-------------|
| **Privacy** | ☁️ Cloud Upload Required | ⚙️ Complex Self-Host | ⚙️ Complex Self-Host | ✅ **100% Local** |
| **Cost** | 💰 $50-$250/mo | Free (setup hell) | Free (setup hell) | ✅ **Free Forever** |
| **Training** | Limited credits | Not included | Not included | ✅ **Unlimited** |
| **Augmentation** | 15 basic filters | 5 basic filters | External tools | ✅ **25+ Filters + Custom** |
| **Auto-Labeling** | Paid feature | Manual only | External | ✅ **Built-in SAM2** |
| **Setup Time** | 10 mins (+ upload time) | 2-4 hours | 2-4 hours | ✅ **30 seconds** |
| **Labeling Speed** | Click dropdowns | Click dropdowns | Click dropdowns | ✅ **Scroll-Wheel Switching** |
| **Training Control** | Basic params only | N/A | N/A | ✅ **Full YOLO Control** |
| **Inference Testing** | Separate tool | Separate tool | Not included | ✅ **Built-in** |

### Detailed Comparison

#### vs **Roboflow** (Cloud, $$$)
**Roboflow Pros**: Polished UI, good documentation, team features
**Roboflow Cons**: Data leaves your network, expensive at scale, training limited by credits

**JIET Studio Advantage**:
- **Privacy**: Medical/military/proprietary data stays local
- **Cost**: Train 1000 epochs/month or 10/month - same price: $0
- **Speed**: No upload/download bottleneck (100GB dataset? No problem.)

#### vs **CVAT** (Open Source Enterprise)
**CVAT Pros**: Feature-rich, supports video, team collaboration
**CVAT Cons**: Docker + Postgres + Redis setup, no trainingintegration, overkill for solo developers

**JIET Studio Advantage**:
- **Setup**: `python main.py` vs 2 hours of Docker configuration
- **Workflow**: Label → Train in one app vs Label (CVAT) → Export → Train (Terminal)  
- **Simplicity**: Designed for solo devs/small teams, not Fortune 500

#### vs **Label Studio** (Self-Hosted)
**Label Studio Pros**: Supports many annotation types (NLP, audio, etc.)
**Label Studio Cons**: Web-based = setup overhead, no training included, slow for pure object detection

**JIET Studio Advantage**:
- **Focus**: Built ONLY for object detection = streamlined UX
- **Integration**: One-click training from labeled data
- **Performance**: Desktop app = faster canvas rendering for large images

#### vs **Labelme / Make Sense** (Simple Tools)
**Their Pros**: Very simple, quick start
**Their Cons**: Just annotation, no augmentation, no training, no testing

**JIET Studio Advantage**:
- **Complete Workflow**: Annotation is 25% of the job - we handle the other 75%
- **Auto-Labeling**: SAM2 Magic Wand speeds up labeling 5-10x
- **Augmentation**: Don't train on 100 raw images - multiply to 2000+ variants

---

## ✨ Features That Make You Faster

### 1. ⚡ **Flow-State Labeling**
Designed for speed, not clicks.

- **Scroll-Wheel Class Switching**: Rotate through classes without moving your hands
- **Magic Wand (SAM2)**: Click object → Auto-labeled bounding box in 0.5s
- **Zoom to Mouse**: `Ctrl+Scroll` exactly where you need it
- **Instant Save**: `Ctrl+S` → Green flash → Next image (zero latency)
- **Organized View**: Auto-groups Labeled/Unlabeled/Negatives/Per-Class

**Result**: Label 100 images in 15 minutes (with Magic Wand) vs 2+ hours manually.

### 2. 🎨 **Industrial Augmentation Engine**
Not just "flip and rotate" - production-grade data augmentation.

**25+ Filters Organized by Category**:
- **Color**: Brightness, Contrast, Exposure, CLAHE, HSV, RGBShift
- **Blur**: Gaussian, Motion, Sharpen, Unsharp Mask
- **Geometric**: Rotate, Flips (H/V), Safe 90° rotations
- **Spatial**: RandomCrop, CenterCrop, Bbox-safe resize
- **Noise**: Gaussian, ISO Camera Noise
- **Advanced**: Perspective, Elastic Transform, Grid Distortion, Optical Distortion

**Smart Features**:
- ✅ **Bbox Safety Indicators**: Know which filters preserve bounding boxes
- ✅ **Live Preview**: See augmentations before running
- ✅ **Parameter Validation**: Auto-clamping to safe ranges
- ✅ **Plugin System**: Write custom filters in Python, UI auto-generates controls
- ✅ **Presets**: Light/Medium/Heavy augmentation templates

**Example**:
100 labeled images → 5x augmentation → 500 training images → Better model accuracy

### 3. 🏋️ **One-Click YOLO Training**
Forget `data.yaml` files and terminal commands.

```
1. Click "Training" tab
2. Select model (YOLOv8/v11, nano to x10)
3. Set epochs, batch size, image size
4. Click "START TRAINING"
5. Watch live progress with GPU monitoring
```

**Behind the scenes**:
- Auto-generates proper folder structure
- Creates data.yaml configuration
- Splits train/val sets automatically
- **Unloads inference models** to free 500MB+ GPU RAM
- Real-time CPU/GPU/RAM monitoring
- **Clears VRAM/RAM after completion** (even if stopped manually)
- **Reloads Magic Wand after training** for seamless workflow

**Result**: 50-epoch training starts in 5 seconds, not 30 minutes of setup.

### 4. 🔍 **Built-In Inference Testing**
Train → Test → Iterate without leaving the app.

- **Image mode**: Batch test on folders
- **Video mode**: Upload MP4/AVI and see detections
- **Webcam mode**: Real-time testing
- **Model switching**: Compare v8 vs v11, nano vs large instantly
- **Confidence tuning**: Live slider to find optimal threshold

**Result**: Catch bad models before deploying to production.

---

## 📦 Installation

### Prerequisites
- **Python 3.8+** (3.10 recommended)
- **Windows** (macOS/Linux support planned)
- **GPU** (NVIDIA RTX recommended, CPU works but slower)

### Quick Start
```bash
# Clone
git clone https://github.com/hazegreleases/JIETStudio.git
cd JIETStudio

# Run (dependencies auto-install on first launch)
python main.py
```

**First Run**:
1. Dependencies install automatically (~2 minutes)
2. App opens → Create or load project
3. Import images → Start labeling

**That's it.** No Docker, no databases, no config files.

---

## 🎮 Workflow Example

### Scenario: Training a Product Defect Detector

```
Day 1: Data Collection & Labeling
├─ Take 200 photos of products (good + defective)
├─ Create project in JIET Studio
├─ Import 200 images
├─ Define classes: "scratch", "dent", "crack"
├─ Use Magic Wand (SAM2) to auto-label obvious defects
├─ Manually adjust and label edge cases
└─ **Time**: 1.5 hours total

Day 1: Augmentation
├─ Open "Augmentation" tab
├─ Add filters: Rotate(±15°), Brightness(0.2), Noise, Perspective
├─ Set "5 augmentations per image"
├─ Click "Run" → 1000 training images generated
└─ **Time**: 5 minutes

Day 1: Training
├─ Open "Training" tab
├─ Select YOLOv8s, 50 epochs, 640px, batch 16
├─ Click "START TRAINING"
├─ Grab coffee while GPU works
└─ **Time**: ~20 minutes (RTX 3060)

Day 1: Testing
├─ Open "Inference" tab
├─ Load trained model from runs/detect/train/weights/best.pt
├─ Test on validation images
├─ Adjust confidence threshold to reduce false positives
├─ Test on webcam with real products
└─ **Time**: 10 minutes

Result: Production-ready model in <2 hours total work
```

---

## ⌨️ Power User Shortcuts

Master these to achieve **Flow State**:

| Action | Shortcut | Pro Tip |
|--------|----------|---------|
| **Save & Next** | `Ctrl + S` | Instant save |
| **Switch Class** | `Scroll Wheel` | Keep hand on mouse |
| **Zoom** | `Ctrl + Scroll` | Zooms to mouse position |
| **Delete Box** | `Del` | Select box first |
| **Delete Image** | `Ctrl + Shift + D` | Removes bad images instantly |
| **Magic Wand** | Click Star icon → Click object | Faster than manual boxing |
| **Undo** | `Ctrl + Z` | Works everywhere |
| **Redo** | `Ctrl + Y` | Works everywhere |

**Flow State Goal**: Never lift hands from keyboard+mouse. No clicking dropdowns or menus.

---


## 🔌 Plugin System: Custom Augmentation Filters

### Example: Sepia Filter
```python
# my_sepia_filter.py
from app.core.augmentation.base import AugmentationEffect, ParamSpec, FilterCategory
import albumentations as A

class SepiaEffect(AugmentationEffect):
    \"\"\"Applies vintage sepia tone.\"\"\"
    
    category = FilterCategory.COLOR
    bbox_safe = True
    
    def __init__(self, intensity=0.5, probability=0.5, enabled=True):
        super().__init__(probability, enabled)
        self.intensity = intensity
    
    def get_transform(self):
        # Use albumentations ToSepia
        return A.ToSepia(p=self.probability)
    
    def get_param_specs(self):
        return {
            'intensity': ParamSpec(
                value=self.intensity,
                min_val=0.0,
                max_val=1.0,
                param_type='float',
                description='Sepia intensity'
            )
        }
    
    def set_params(self, params):
        if 'intensity' in params:
            self.intensity = float(params['intensity'])
```

**Usage**:
1. Save as `my_sepia_filter.py`
2. In Augmentation tab → Click "Import Filter"
3. Select file → Filter appears in dropdown **with auto-generated UI slider**

See [FILTER_GUIDE.md](docs/custom_filters.md) for full documentation.

---

## 🤝 Contributing

We welcome contributions! This project is actively maintained.

**How to contribute**:
- 🐛 **Found a bug?** Open an issue with reproduction steps
- 💡 **Feature idea?** Discuss in Issues before implementing
- 🎨 **Created a cool filter?** Submit PR to `app/core/augmentation/filters/community/`
- 📖 **Improved docs?** PRs always welcome

**Development Setup**:
```bash
git clone https://github.com/hazegreleases/JIETStudio.git
cd JIETStudio
pip install -r requirements.txt
python main.py
```

**Code Style**: Follow existing patterns, add docstrings, keep it simple.

---

## 🛣️ Roadmap

**Current Version**: v0.8 (Active Development)

**Planned Features**:
- [ ] macOS/Linux support
- [ ] Multi-GPU training
- [ ] Instance segmentation (polygons)
- [ ] Export to ONNX/TFLite
- [ ] Dataset versioning (git-like diffs)
- [ ] Batch auto-labeling with confidence filtering
- [ ] Training templates (presets for common scenarios)
- [ ] Model comparison dashboard

**Recently Added** ✅:
- [x] SAM2 Magic Wand auto-labeling
- [x] 25+ augmentation filters
- [x] Memory management during training
- [x] Organized labeling view
- [x] Plugin system for custom filters

---

## 📊 Performance Notes

**Hardware Recommendations**:
- **CPU**: 4+ cores (Intel i5/AMD Ryzen 5 or better)
- **RAM**: 8GB minimum, 16GB+ recommended
- **GPU**: RTX 2060 or better (6GB+ VRAM)
- **Storage**: SSD for faster image loading

**Benchmarks** (RTX 3060, 100 images, 50 epochs):
- **YOLOv8n**: ~5 minutes
- **YOLOv8s**: ~10 minutes
- **YOLOv8m**: ~20 minutes
- **YOLO11x**: ~45 minutes

**Memory Management**:
- SAM2 model consumes ~450MB VRAM
- Training automatically unloads SAM to free memory
- Post-training, SAM reloads automatically for continued labeling

---

## 🔒 Privacy & Data Security

**100% Offline Operation**:
- ✅ No telemetry, no analytics, no "phone home"
- ✅ All data stays on your machine
- ✅ No account creation required
- ✅ Works without internet connection (after initial setup)

**Perfect for**:
- Medical imaging (HIPAA compliance)
- Military/defense applications
- Proprietary industrial inspection
- Privacy-sensitive research

---

## ❓ FAQ

**Q: Does it work without GPU?**  
A: Yes, but training is 10-50x slower. Labeling and augmentation are CPU-friendly.

**Q: Can I use my own YOLO model?**  
A: Yes, click "Import Model" in Training tab and select your `.pt` file.

**Q: What image formats are supported?**  
A: JPG, PNG, BMP, TIFF. Labels are YOLO format `.txt` files.

**Q: Can I export to other formats (COCO, Pascal VOC)?**  
A: Not yet - on roadmap. Currently YOLO format only.

**Q: How do I deploy the trained model?**  
A: Use `runs/detect/train/weights/best.pt` with Ultralytics library or export to ONNX.

**Q: Is multi-class detection supported?**  
A: Yes, unlimited classes. Define in project setup.

**Q: Linearity?**  
A: MIT License - free for commercial use.

---

## 🏷️ Keywords

`yolo`, `yolov8`, `yolov11`, `object-detection`, `computer-vision`, `labeling-tool`, `image-annotation`, `data-augmentation`, `training-gui`, `ultralytics`, `offline-ml`, `auto-labeling`, `sam2`, `local-training`, `desktop-app`, `python-gui`, `ml-workflow`, `deep-learning`, `pytorch`

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

**TLDR**: Use it, modify it, sell products built with it. Just don't sue us.

---

<div align="center">

**Built by developers who got tired of cloud lock-in.**

[⭐ Star this repo](https://github.com/hazegreleases/JIETStudio) | [🐛 Report Bug](https://github.com/hazegreleases/JIETStudio/issues) | [💡 Request Feature](https://github.com/hazegreleases/JIETStudio/issues)

</div>
