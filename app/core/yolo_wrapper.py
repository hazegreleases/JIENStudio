import os
import yaml
import random
import threading
from ultralytics import YOLO
import shutil
from datetime import datetime
import gc
import torch

class YOLOWrapper:
    def __init__(self, project_path):
        self.project_path = project_path
        # Global models directory
        self.models_dir = os.path.join(os.path.expanduser("~"), ".jiet_yolo_models")
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            
        self.data_dir = os.path.join(project_path, "data")
        self.images_dir = os.path.join(self.data_dir, "images")
        self.labels_dir = os.path.join(self.data_dir, "labels")

    def prepare_dataset(self, validation_split=0.2):
        """Generates train.txt and val.txt with random split."""
        images = [os.path.join(self.images_dir, f) for f in os.listdir(self.images_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        # Filter images that have corresponding labels? 
        # YOLO can handle background images (no labels), so we include all.
        
        random.shuffle(images)
        split_idx = int(len(images) * (1 - validation_split))
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]

        train_txt = os.path.join(self.data_dir, "train.txt")
        val_txt = os.path.join(self.data_dir, "val.txt")

        with open(train_txt, "w") as f:
            f.write("\n".join(train_imgs))
        
        with open(val_txt, "w") as f:
            f.write("\n".join(val_imgs))

        return train_txt, val_txt

    def generate_yaml(self, classes, train_txt, val_txt):
        """Generates a data.yaml file for training."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        yaml_path = os.path.join(self.data_dir, f"config_{timestamp}.yaml")
        
        data = {
            'path': self.data_dir,
            'train': train_txt,
            'val': val_txt,
            'names': {i: name for i, name in enumerate(classes)}
        }
        
        with open(yaml_path, "w") as f:
            yaml.dump(data, f)
        
        return yaml_path

        self.stop_training_flag = False

    def stop_training(self):
        self.stop_training_flag = True
    
    def cleanup_memory(self):
        """Aggressive memory cleanup to free VRAM and RAM after training."""
        print("[Memory Cleanup] Clearing VRAM and RAM...")
        
        # Force garbage collection
        gc.collect()
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            print(f"[Memory Cleanup] Freed CUDA cache")
        
        # Additional garbage collection
        gc.collect()
        
        print("[Memory Cleanup] Memory cleanup complete")

    def train_model(self, model_name, data_yaml, epochs, batch_size, imgsz, callback=None):
        """Runs training in a separate thread."""
        self.stop_training_flag = False
        
        def on_train_epoch_end(trainer):
            if self.stop_training_flag:
                print("Training stopped by user.")
                trainer.stop = True
                raise InterruptedError("Training stopped by user.")

        def run():
            try:
                # Check if model exists in global dir, else let YOLO download it there?
                # YOLO downloads to current dir by default.
                # We can specify the model path if it exists.
                
                model_path = os.path.join(self.models_dir, model_name)
                if not os.path.exists(model_path) and not model_name.endswith('.pt'):
                     # If it's a base name like yolov8n.pt, YOLO will try to download.
                     # We can try to download it to our global dir first or just let YOLO handle it but move it?
                     # Simpler: Just let YOLO load it. If it's a path, it uses it.
                     pass
                
                # If the user selected a standard model name, we want to ensure it's cached in our global dir
                # But YOLO class handles download automatically. 
                # To force download to specific dir is tricky without manual download.
                # However, we can just pass the name.
                
                model = YOLO(model_name) 
                model.add_callback("on_train_epoch_end", on_train_epoch_end)
                
                project_runs = os.path.join(self.project_path, "runs")
                name = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                results = model.train(
                    data=data_yaml,
                    epochs=epochs,
                    batch=batch_size,
                    imgsz=imgsz,
                    project=project_runs,
                    name=name,
                    exist_ok=True
                )
                
                # Clean up model reference and memory
                del model
                self.cleanup_memory()
                
                if callback:
                    callback(f"Training completed. Results saved to {project_runs}/{name}")
            except InterruptedError:
                # Clean up on manual stop
                try:
                    del model
                except:
                    pass
                self.cleanup_memory()
                
                if callback:
                    callback("Training stopped by user.")
            except Exception as e:
                # Clean up on error
                try:
                    del model
                except:
                    pass
                self.cleanup_memory()
                
                if callback:
                    callback(f"Error during training: {str(e)}")

        thread = threading.Thread(target=run)
        thread.start()

    def run_inference(self, model_path, source, conf=0.25):
        """Runs inference on a source."""
        model = YOLO(model_path)
        # return results object
        # For webcam, source is int. For image, str.
        results = model.predict(source=source, conf=conf, save=False)
        return results

    def export_model(self, model_path, format="onnx"):
        """Exports the model to the specified format."""
        model = YOLO(model_path)
        export_path = model.export(format=format)
        return export_path

    def get_device_info(self):
        """Returns information about the device used for training/inference."""
        import torch
        if torch.cuda.is_available():
            return f"CUDA ({torch.cuda.get_device_name(0)})"
        elif torch.backends.mps.is_available():
            return "MPS (Apple Metal)"
        else:
            return "CPU"
