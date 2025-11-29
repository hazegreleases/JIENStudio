import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading
from PIL import Image, ImageTk

class FactoryView(ttk.Frame):
    def __init__(self, parent, project_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.project_manager = project_manager
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with two columns
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left column - Configuration
        left_column = ttk.Frame(main_container)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Right column - Preview
        right_column = ttk.Frame(main_container)
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Title
        title = ttk.Label(left_column, text="Factory - Synthetic Data", font=("Inter", 16, "bold"))
        title.pack(pady=10)
        
        # Model Selection Frame
        model_frame = ttk.LabelFrame(left_column, text="3D Model", padding=10)
        model_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(model_frame, text="Model File:").grid(row=0, column=0, sticky="w", pady=5)
        self.model_path = tk.StringVar(value="(No model selected)")
        model_entry = ttk.Entry(model_frame, textvariable=self.model_path, width=25, state="readonly")
        model_entry.grid(row=0, column=1, sticky="w", padx=10)
        ttk.Button(model_frame, text="Browse", command=self.browse_model).grid(row=0, column=2, padx=5)
        # Preview button removed - automatic preview on browse
        
        # Class selector
        ttk.Label(model_frame, text="Label As Class:").grid(row=1, column=0, sticky="w", pady=5)
        self.target_class = tk.StringVar()
        self.class_combo = ttk.Combobox(model_frame, textvariable=self.target_class, state="readonly", width=15)
        self.class_combo.grid(row=1, column=1, sticky="w", padx=10)
        self.update_class_list()
        
        # Configuration Frame
        config_frame = ttk.LabelFrame(left_column, text="Batch Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=10)
        
        # Number of samples
        ttk.Label(config_frame, text="Number of Samples:").grid(row=0, column=0, sticky="w", pady=5)
        self.sample_count = tk.IntVar(value=10)
        sample_spinner = ttk.Spinbox(config_frame, from_=1, to=1000, textvariable=self.sample_count, width=10)
        sample_spinner.grid(row=0, column=1, sticky="w", padx=10)
        
        # Render samples
        ttk.Label(config_frame, text="Cycles Samples (Quality):").grid(row=1, column=0, sticky="w", pady=5)
        self.render_samples = tk.IntVar(value=64)
        render_spinner = ttk.Spinbox(config_frame, from_=16, to=512, increment=16, textvariable=self.render_samples, width=10)
        render_spinner.grid(row=1, column=1, sticky="w", padx=10)
        
        # Resolution
        ttk.Label(config_frame, text="Resolution:").grid(row=2, column=0, sticky="w", pady=5)
        self.resolution = tk.StringVar(value="640x640")
        res_combo = ttk.Combobox(config_frame, textvariable=self.resolution, 
                                  values=["512x512", "640x640", "1024x1024", "1280x1280"], 
                                  state="readonly", width=10)
        res_combo.grid(row=2, column=1, sticky="w", padx=10)
        
        # Output Directory
        ttk.Label(config_frame, text="Output Directory:").grid(row=3, column=0, sticky="w", pady=5)
        self.output_dir = tk.StringVar(value="factory_output")
        output_entry = ttk.Entry(config_frame, textvariable=self.output_dir, width=30)
        output_entry.grid(row=3, column=1, sticky="w", padx=10)
        ttk.Button(config_frame, text="Browse", command=self.browse_output).grid(row=3, column=2, padx=5)

        # Realism Settings Frame
        realism_frame = ttk.LabelFrame(left_column, text="Realism Settings", padding=10)
        realism_frame.pack(fill="x", padx=10, pady=10)
        
        # Blur
        ttk.Label(realism_frame, text="Blur Amount:").grid(row=0, column=0, sticky="w", pady=5)
        self.blur_amount = tk.DoubleVar(value=0.0)
        ttk.Scale(realism_frame, from_=0.0, to=5.0, variable=self.blur_amount, orient="horizontal", length=150).grid(row=0, column=1, padx=10)
        self.blur_label = ttk.Label(realism_frame, text="0.0")
        self.blur_label.grid(row=0, column=2, padx=5)
        self.blur_amount.trace_add('write', lambda *args: self.blur_label.config(text=f"{self.blur_amount.get():.2f}"))
        
        # Distortion
        ttk.Label(realism_frame, text="Lens Distortion:").grid(row=1, column=0, sticky="w", pady=5)
        self.distortion_amount = tk.DoubleVar(value=0.0)
        ttk.Scale(realism_frame, from_=0.0, to=5.0, variable=self.distortion_amount, orient="horizontal", length=150).grid(row=1, column=1, padx=10)
        self.distortion_label = ttk.Label(realism_frame, text="0.0")
        self.distortion_label.grid(row=1, column=2, padx=5)
        self.distortion_amount.trace_add('write', lambda *args: self.distortion_label.config(text=f"{self.distortion_amount.get():.2f}"))
        
        # Noise
        ttk.Label(realism_frame, text="Noise Level:").grid(row=2, column=0, sticky="w", pady=5)
        self.noise_amount = tk.DoubleVar(value=0.0)
        ttk.Scale(realism_frame, from_=0.0, to=5.0, variable=self.noise_amount, orient="horizontal", length=150).grid(row=2, column=1, padx=10)
        self.noise_label = ttk.Label(realism_frame, text="0.0")
        self.noise_label.grid(row=2, column=2, padx=5)
        self.noise_amount.trace_add('write', lambda *args: self.noise_label.config(text=f"{self.noise_amount.get():.2f}"))
        
        # Color Jitter
        ttk.Label(realism_frame, text="Color Jitter:").grid(row=3, column=0, sticky="w", pady=5)
        self.jitter_amount = tk.DoubleVar(value=0.0)
        ttk.Scale(realism_frame, from_=0.0, to=5.0, variable=self.jitter_amount, orient="horizontal", length=150).grid(row=3, column=1, padx=10)
        self.jitter_label = ttk.Label(realism_frame, text="0.0")
        self.jitter_label.grid(row=3, column=2, padx=5)
        self.jitter_amount.trace_add('write', lambda *args: self.jitter_label.config(text=f"{self.jitter_amount.get():.2f}"))
        
        # Preview Frame (Right Column)
        preview_frame = ttk.LabelFrame(right_column, text="Model Preview (Eevee)", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.preview_label = ttk.Label(preview_frame, text="No preview available\nSelect a model and click Preview", 
                                        justify="center")
        self.preview_label.pack(expand=True)
        
        self.preview_image = None
        
        # Controls Frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        self.generate_btn = ttk.Button(controls_frame, text="Generate Batch", command=self.start_generation)
        self.generate_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(controls_frame, text="Stop", command=self.stop_generation, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(self, text="Progress", padding=10)
        progress_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready", foreground="green")
        self.status_label.pack(pady=5)
        
        # Log output
        self.log_text = tk.Text(progress_frame, height=10, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.generation_process = None
        
    def update_class_list(self):
        """Update class dropdown from project."""
        if self.project_manager:
            classes = self.project_manager.get_classes()
            self.class_combo['values'] = classes
            if classes:
                self.class_combo.current(0)
                self.target_class.set(classes[0])
    
    def browse_output(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)
    
    def browse_model(self):
        filetypes = [
            ("3D Models", "*.obj *.fbx *.gltf *.glb *.dae *.stl *.ply"),
            ("OBJ Files", "*.obj"),
            ("FBX Files", "*.fbx"),
            ("GLTF Files", "*.gltf *.glb"),
            ("All Files", "*.*")
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.model_path.set(filepath)
            self.log(f"Model selected: {os.path.basename(filepath)}")
            self.generate_preview()
    
    def generate_preview(self):
        model_file = self.model_path.get()
        if not model_file or model_file == "(No model selected)":
            messagebox.showwarning("No Model", "Please select a 3D model first.")
            return
        
        if not os.path.exists(model_file):
            messagebox.showerror("Error", "Selected model file not found.")
            return
        
        self.preview_label.config(text="Generating preview...")
        self.log("\n--- Starting Preview Generation ---")
        self.log(f"Target: {os.path.basename(model_file)}")
        thread = threading.Thread(target=self.run_preview, args=(model_file,), daemon=True)
        thread.start()
    
    def run_preview(self, model_file):
        script_path = os.path.abspath("factory/preview.py")
        preview_output_base = os.path.abspath("factory_output/preview_spin")
        
        # Stop any existing animation
        self.stop_preview_animation()
        
        # Create preview script arguments
        cmd = [
            "blender",
            "--background",
            "--python", script_path,
            "--",
            model_file,
            preview_output_base
        ]
        
        try:
            # Run Blender
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Load all frames
            self.preview_frames = []
            frame_idx = 1
            while True:
                frame_path = f"{preview_output_base}_{frame_idx:04d}.png"
                if not os.path.exists(frame_path):
                    break
                
                try:
                    img = Image.open(frame_path)
                    img.thumbnail((400, 400))
                    self.preview_frames.append(ImageTk.PhotoImage(img))
                    frame_idx += 1
                except Exception as e:
                    print(f"Error loading frame {frame_idx}: {e}")
                    break
            
            if self.preview_frames:
                self.log(f"Preview generated with {len(self.preview_frames)} frames!")
                self.current_frame_idx = 0
                self.animate_preview()
            else:
                self.preview_label.config(text="Preview generation failed\nNo frames found")
                self.log("Error: No preview frames generated")
                
        except subprocess.CalledProcessError as e:
            self.preview_label.config(text="Preview failed")
            self.log(f"Preview error: {e.stderr}")
        except Exception as e:
            self.preview_label.config(text="Preview error")
            self.log(f"Error: {str(e)}")

    def animate_preview(self):
        """Cycle through preview frames."""
        if not hasattr(self, 'preview_frames') or not self.preview_frames:
            return
            
        # Update image
        self.preview_label.config(image=self.preview_frames[self.current_frame_idx], text="")
        
        # Next frame
        self.current_frame_idx = (self.current_frame_idx + 1) % len(self.preview_frames)
        
        # Schedule next update (approx 12 fps)
        self.preview_animation_id = self.after(83, self.animate_preview)

    def stop_preview_animation(self):
        """Stop the running animation."""
        if hasattr(self, 'preview_animation_id') and self.preview_animation_id:
            self.after_cancel(self.preview_animation_id)
            self.preview_animation_id = None
    
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def start_generation(self):
        # Validate Blender installation
        try:
            subprocess.run(["blender", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (FileNotFoundError, subprocess.CalledProcessError):
            messagebox.showerror("Error", "Blender not found. Please ensure Blender is installed and added to PATH.")
            return
        
        # Update UI
        self.generate_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress_bar.start()
        self.status_label.config(text="Generating...", foreground="orange")
        self.log("Starting batch generation...")
        
        # Run in thread
        thread = threading.Thread(target=self.run_generation, daemon=True)
        thread.start()
    
    def run_generation(self):
        script_path = os.path.abspath("factory/render_test.py")
        output_dir = os.path.abspath(self.output_dir.get())
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Prepare command with model path if provided
        cmd = ["blender", "--background", "--python", script_path]
        
        self.log("\n--- Starting Synthetic Data Generation ---")
        
        # Add model path argument if a model is selected
        model_file = self.model_path.get()
        if model_file and model_file != "(No model selected)" and os.path.exists(model_file):
            # Get class index
            class_idx = 0
            if self.project_manager:
                classes = self.project_manager.get_classes()
                target_class = self.target_class.get()
                if target_class in classes:
                    class_idx = classes.index(target_class)
            
            # Get batch size
            try:
                batch_size = int(self.sample_count.get())
            except ValueError:
                batch_size = 10
            
            cmd.extend(["--", model_file, str(class_idx), str(batch_size)])
            
            # Add realism arguments
            cmd.extend([
                str(self.blur_amount.get()),
                str(self.distortion_amount.get()),
                str(self.noise_amount.get()),
                str(self.jitter_amount.get())
            ])
            
            self.log(f"Using model: {os.path.basename(model_file)}, class: {self.target_class.get()}, count: {batch_size}")
            self.log(f"Effects: Blur={self.blur_amount.get():.2f}, Dist={self.distortion_amount.get():.2f}, Noise={self.noise_amount.get():.2f}, Jitter={self.jitter_amount.get():.2f}")
        else:
            self.log("No model selected, using default cube")
        
        try:
            self.generation_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output
            for line in self.generation_process.stdout:
                self.log(line.strip())
            
            self.generation_process.wait()
            
            if self.generation_process.returncode == 0:
                self.status_label.config(text="Generation Complete!", foreground="green")
                self.log("Batch generation completed successfully!")
            else:
                self.status_label.config(text="Generation Failed", foreground="red")
                self.log(f"Process exited with code {self.generation_process.returncode}")
                
        except Exception as e:
            self.status_label.config(text="Error", foreground="red")
            self.log(f"Error: {str(e)}")
        finally:
            self.generate_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.progress_bar.stop()
    
    def stop_generation(self):
        if self.generation_process:
            self.generation_process.terminate()
            self.log("Generation stopped by user.")
            self.status_label.config(text="Stopped", foreground="red")
