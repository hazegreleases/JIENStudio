import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.ui.components import RoundedButton
from PIL import Image, ImageTk
import cv2
import threading
import os

class InferenceView(tk.Frame):
    def __init__(self, parent, project_manager):
        super().__init__(parent)
        self.project_manager = project_manager
        # We instantiate wrapper here too, or pass it in. 
        # Since wrapper takes project path, we can create new one.
        from app.core.yolo_wrapper import YOLOWrapper
        self.yolo_wrapper = YOLOWrapper(project_manager.current_project_path)
        
        self.cap = None
        self.is_running = False
        self.current_image = None
        
        self._create_ui()

    def _create_ui(self):
        # Control Panel
        control_frame = tk.Frame(self, padx=10, pady=10, bg="#ddd")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # Model Selection
        tk.Label(control_frame, text="Model Path:", bg="#ddd").grid(row=0, column=0, sticky=tk.W)
        self.model_path_var = tk.StringVar()
        tk.Entry(control_frame, textvariable=self.model_path_var, width=40).grid(row=0, column=1, padx=5)
        RoundedButton(control_frame, text="Browse", command=self.browse_model, width=80, height=30).grid(row=0, column=2, padx=5)

        # Source Selection
        tk.Label(control_frame, text="Source:", bg="#ddd").grid(row=1, column=0, sticky=tk.W)
        self.source_var = tk.StringVar(value="Image")
        ttk.Combobox(control_frame, textvariable=self.source_var, values=["Image", "Webcam 0", "Webcam 1"]).grid(row=1, column=1, padx=5, sticky=tk.EW)
        
        self.run_btn = RoundedButton(control_frame, text="Run Inference", command=self.start_inference, width=120, height=30)
        self.run_btn.grid(row=1, column=2, padx=5)
        
        self.stop_btn = RoundedButton(control_frame, text="Stop Inference", command=self.stop_inference, width=120, height=30)
        self.stop_btn.grid(row=1, column=3, padx=5)
        self.stop_btn.config(state="disabled")

        # Export
        tk.Label(control_frame, text="Export:", bg="#ddd").grid(row=0, column=3, sticky=tk.W, padx=(20, 5))
        RoundedButton(control_frame, text="Export ONNX", command=lambda: self.export_model("onnx"), width=120, height=30).grid(row=0, column=4, padx=2)
        RoundedButton(control_frame, text="Export TorchScript", command=lambda: self.export_model("torchscript"), width=150, height=30).grid(row=0, column=5, padx=2)

        # Display Area
        self.display_frame = tk.Frame(self, bg="black")
        self.display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.display_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def browse_model(self):
        # Default to runs directory if exists
        initial_dir = os.path.join(self.project_manager.current_project_path, "runs")
        if not os.path.exists(initial_dir):
            initial_dir = self.project_manager.current_project_path
            
        path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Model Files", "*.pt")])
        if path:
            self.model_path_var.set(path)

        if self.is_running:
            self.stop_inference()
        else:
            self.start_inference()
            
    def update_buttons(self, running):
        if running:
            self.run_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        else:
            self.run_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def start_inference(self):
        model_path = self.model_path_var.get()
        if not model_path or not os.path.exists(model_path):
            messagebox.showerror("Error", "Invalid model path")
            return

        source = self.source_var.get()
        
        if source == "Image":
            file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
            if not file_path: return
            
            self.run_image_inference(model_path, file_path)
        
        elif "Webcam" in source:
            cam_idx = int(source.split()[-1])
            self.run_webcam_inference(model_path, cam_idx)
            self.update_buttons(True)

    def run_image_inference(self, model_path, image_path):
        try:
            results = self.yolo_wrapper.run_inference(model_path, image_path)
            # Results is a list
            for r in results:
                im_array = r.plot()  # plot() returns BGR numpy array
                im_rgb = cv2.cvtColor(im_array, cv2.COLOR_BGR2RGB)
                self.display_image(im_rgb)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_webcam_inference(self, model_path, cam_idx):
        self.cap = cv2.VideoCapture(cam_idx)
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Cannot open webcam {cam_idx}")
            return
            
        self.is_running = True
        
        def loop():
            from ultralytics import YOLO
            model = YOLO(model_path)
            
            while self.is_running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret: break
                
                results = model.predict(frame, conf=0.5, verbose=False)
                annotated_frame = results[0].plot()
                
                im_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                
                # Schedule update on main thread
                self.after(10, lambda img=im_rgb: self.display_image(img))
            
            self.cap.release()
            self.canvas.delete("all")
            self.after(0, lambda: self.update_buttons(False))

        threading.Thread(target=loop, daemon=True).start()

    def stop_inference(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.update_buttons(False)

    def display_image(self, img_array):
        # Resize to fit canvas
        h, w, _ = img_array.shape
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        if canvas_w < 1 or canvas_h < 1: return

        scale = min(canvas_w/w, canvas_h/h)
        new_w, new_h = int(w*scale), int(h*scale)
        
        pil_img = Image.fromarray(img_array)
        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        self.current_image = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_w//2, canvas_h//2, anchor=tk.CENTER, image=self.current_image)

    def export_model(self, fmt):
        model_path = self.model_path_var.get()
        if not model_path or not os.path.exists(model_path):
            messagebox.showerror("Error", "Invalid model path")
            return
            
        try:
            export_path = self.yolo_wrapper.export_model(model_path, fmt)
            messagebox.showinfo("Success", f"Model exported to {export_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
