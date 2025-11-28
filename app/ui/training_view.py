import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.core.yolo_wrapper import YOLOWrapper
from app.ui.components import RoundedButton
import sys
import os

class RedirectText(object):
    def __init__(self, text_widget):
        self.output = text_widget

    def write(self, string):
        try:
            self.output.insert(tk.END, string)
            self.output.see(tk.END)
        except tk.TclError:
            # Widget likely destroyed
            pass

    def flush(self):
        pass

class TrainingView(tk.Frame):
    def __init__(self, parent, project_manager):
        super().__init__(parent)
        self.project_manager = project_manager
        self.yolo_wrapper = YOLOWrapper(project_manager.current_project_path)
        
        # Store original stdout/stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        self._create_ui()
        
        # Redirect stdout/stderr
        sys.stdout = RedirectText(self.console_text)
        sys.stderr = RedirectText(self.console_text)

    def _create_ui(self):
        # Config Panel
        config_frame = tk.Frame(self, padx=10, pady=10)
        config_frame.pack(side=tk.TOP, fill=tk.X)

        # Model Selection
        tk.Label(config_frame, text="Model:").grid(row=0, column=0, sticky=tk.W)
        self.model_var = tk.StringVar(value="yolov8n.pt")
        models = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt",
                  "yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt", "yolo11x.pt"]
        self.model_combo = ttk.Combobox(config_frame, textvariable=self.model_var, values=models)
        self.model_combo.grid(row=0, column=1, padx=5, pady=5)
        
        RoundedButton(config_frame, text="Import Model", command=self.import_model, width=120, height=30).grid(row=0, column=2, padx=5)
        self.pretrained_var = tk.BooleanVar(value=True)
        tk.Checkbutton(config_frame, text="Pretrained", variable=self.pretrained_var).grid(row=0, column=3)

        # Parameters
        tk.Label(config_frame, text="Epochs:").grid(row=1, column=0, sticky=tk.W)
        self.epochs_var = tk.IntVar(value=50)
        tk.Entry(config_frame, textvariable=self.epochs_var, width=10).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(config_frame, text="Batch Size:").grid(row=1, column=2, sticky=tk.W)
        self.batch_var = tk.IntVar(value=16)
        tk.Entry(config_frame, textvariable=self.batch_var, width=10).grid(row=1, column=3, padx=5, pady=5)

        tk.Label(config_frame, text="Image Size:").grid(row=1, column=4, sticky=tk.W)
        self.imgsz_var = tk.IntVar(value=640)
        tk.Entry(config_frame, textvariable=self.imgsz_var, width=10).grid(row=1, column=5, padx=5, pady=5)

        # Validation Split
        tk.Label(config_frame, text="Val Split (%):").grid(row=2, column=0, sticky=tk.W)
        self.val_split_var = tk.IntVar(value=20)
        self.val_slider = tk.Scale(config_frame, from_=0, to=50, orient=tk.HORIZONTAL, variable=self.val_split_var)
        self.val_slider.grid(row=2, column=1, columnspan=2, sticky=tk.EW)

        self.val_slider.grid(row=2, column=1, columnspan=2, sticky=tk.EW)

        # Train Button
        # We need to wrap RoundedButton in a frame or use place if grid is tricky with canvas size, 
        # but grid works fine for canvas.
        self.start_btn = RoundedButton(config_frame, text="START TRAINING", command=self.start_training, 
                                  width=200, height=50)
        self.start_btn.grid(row=3, column=0, columnspan=3, pady=20, sticky=tk.E, padx=5)

        self.stop_btn = RoundedButton(config_frame, text="STOP TRAINING", command=self.stop_training, 
                                  width=200, height=50)
        self.stop_btn.grid(row=3, column=3, columnspan=3, pady=20, sticky=tk.W, padx=5)
        self.stop_btn.config(state="disabled")

        # Console Output
        tk.Label(self, text="Training Log:").pack(anchor=tk.W, padx=10)
        
        # Resource Monitor Bar
        self.resource_frame = tk.Frame(self, bg="#222")
        self.resource_frame.pack(fill=tk.X, padx=10, pady=2)
        
        self.lbl_device = tk.Label(self.resource_frame, text="Device: Detecting...", bg="#222", fg="#aaa", font=("Consolas", 9))
        self.lbl_device.pack(side=tk.LEFT, padx=5)
        
        self.lbl_cpu = tk.Label(self.resource_frame, text="CPU: 0%", bg="#222", fg="#aaa", font=("Consolas", 9))
        self.lbl_cpu.pack(side=tk.RIGHT, padx=5)
        
        self.lbl_ram = tk.Label(self.resource_frame, text="RAM: 0%", bg="#222", fg="#aaa", font=("Consolas", 9))
        self.lbl_ram.pack(side=tk.RIGHT, padx=5)

        self.lbl_gpu = tk.Label(self.resource_frame, text="GPU: N/A", bg="#222", fg="#aaa", font=("Consolas", 9))
        self.lbl_gpu.pack(side=tk.RIGHT, padx=5)

        self.console_text = tk.Text(self, bg="black", fg="white", height=20)
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.monitor = None
        self.start_monitoring()

    def start_monitoring(self):
        from app.core.resource_monitor import ResourceMonitor
        self.monitor = ResourceMonitor(callback=self.update_stats)
        self.monitor.start()
        
        # Update device info
        device_info = self.yolo_wrapper.get_device_info()
        self.lbl_device.config(text=f"Device: {device_info}")

    def update_stats(self, stats):
        if not self.winfo_exists():
            return
            
        # Schedule UI update on main thread
        self.after(0, lambda: self._update_labels(stats))

    def _update_labels(self, stats):
        self.lbl_cpu.config(text=f"CPU: {stats['cpu']}%")
        self.lbl_ram.config(text=f"RAM: {stats['ram']}%")
        self.lbl_gpu.config(text=f"GPU: {stats['gpu']}")

    def import_model(self):
        path = filedialog.askopenfilename(filetypes=[("Model Files", "*.pt *.onnx")])
        if path:
            self.model_var.set(path)

    def start_training(self):
        try:
            epochs = self.epochs_var.get()
            batch = self.batch_var.get()
            imgsz = self.imgsz_var.get()
            val_split = self.val_split_var.get() / 100.0
            model_name = self.model_var.get()
            
            classes = self.project_manager.get_classes()
            if not classes:
                messagebox.showerror("Error", "No classes defined! Please add classes in Labeling tab.")
                return

            self.console_text.insert(tk.END, "Preparing dataset...\n")
            train_txt, val_txt = self.yolo_wrapper.prepare_dataset(val_split)
            
            self.console_text.insert(tk.END, "Generating config...\n")
            data_yaml = self.yolo_wrapper.generate_yaml(classes, train_txt, val_txt)
            
            self.console_text.insert(tk.END, f"Starting training with {model_name}...\n")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.yolo_wrapper.train_model(model_name, data_yaml, epochs, batch, imgsz, callback=self.on_training_complete)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def stop_training(self):
        if messagebox.askyesno("Stop Training", "Are you sure you want to stop training? It will stop after the current epoch."):
            self.yolo_wrapper.stop_training()
            self.console_text.insert(tk.END, "Stopping training... (waiting for epoch end)\n")
            self.stop_btn.config(state="disabled") # Prevent multiple clicks

    def on_training_complete(self, message):
        try:
            self.console_text.insert(tk.END, f"\n{message}\n")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            messagebox.showinfo("Training", "Training process finished.")
        except tk.TclError:
            pass

    def destroy(self):
        if self.monitor:
            self.monitor.stop()
        # Restore original stdout/stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        super().destroy()
