"""
Augmentation view for configuring and running dataset augmentation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import threading
from app.core.augmentation_engine import AugmentationEngine, AugmentationConfig
from app.ui.components import RoundedButton
import cv2
import numpy as np


class AugmentationView(ttk.Frame):
    """UI for configuring and running augmentations."""
    
    def __init__(self, parent, project_manager):
        super().__init__(parent)
        self.project_manager = project_manager
        self.config = AugmentationConfig()
        self.engine = AugmentationEngine(self.config)
        
        self.preview_original = None
        self.preview_augmented = None
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """Create the UI layout."""
        # Main container with paned window
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Configuration
        left_panel = ttk.Frame(paned, width=350)
        paned.add(left_panel, minsize=300)
        
        # Right panel - Preview
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, minsize=400)
        
        self.create_config_panel(left_panel)
        self.create_preview_panel(right_panel)
    
    def create_config_panel(self, parent):
        """Create configuration panel."""
        # Title
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(title_frame, text="Augmentation Settings", font=('Arial', 14, 'bold')).pack()
        
        # Enable/Disable
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Enable Augmentation", variable=self.enabled_var,
                       command=self.on_config_change).pack(anchor=tk.W)
        
        # Augmentations per image
        count_frame = ttk.LabelFrame(parent, text="Augmentations Per Image", padding=10)
        count_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.aug_count_var = tk.IntVar(value=5)
        ttk.Scale(count_frame, from_=1, to=20, variable=self.aug_count_var,
                 orient=tk.HORIZONTAL, command=lambda v: self.on_config_change()).pack(fill=tk.X)
        
        self.count_label = ttk.Label(count_frame, text="5 augmentations")
        self.count_label.pack()
        
        # Filters configuration
        filters_frame = ttk.LabelFrame(parent, text="Augmentation Filters", padding=10)
        filters_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollable frame for filters
        canvas = tk.Canvas(filters_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(filters_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.filter_vars = {}
        self.create_filter_controls(scrollable_frame)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Run Augmentation", command=self.run_augmentation).pack(side=tk.LEFT, padx=5)
    
    def create_filter_controls(self, parent):
        """Create controls for each filter."""
        filters = self.config.filters
        
        for filter_name, settings in filters.items():
            frame = ttk.LabelFrame(parent, text=filter_name.replace('_', ' ').title(), padding=5)
            frame.pack(fill=tk.X, pady=5)
            
            # Enabled checkbox
            enabled_var = tk.BooleanVar(value=settings.get('enabled', False))
            self.filter_vars[f"{filter_name}_enabled"] = enabled_var
            ttk.Checkbutton(frame, text="Enabled", variable=enabled_var,
                           command=self.on_config_change).pack(anchor=tk.W)
            
            # Probability slider
            prob_frame = ttk.Frame(frame)
            prob_frame.pack(fill=tk.X, pady=2)
            ttk.Label(prob_frame, text="Probability:", width=12).pack(side=tk.LEFT)
            
            prob_var = tk.DoubleVar(value=settings.get('probability', 0.5))
            self.filter_vars[f"{filter_name}_probability"] = prob_var
            ttk.Scale(prob_frame, from_=0, to=1, variable=prob_var,
                     orient=tk.HORIZONTAL, command=lambda v: self.on_config_change()).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            prob_label = ttk.Label(prob_frame, text=f"{settings.get('probability', 0.5):.2f}", width=5)
            prob_label.pack(side=tk.LEFT)
            self.filter_vars[f"{filter_name}_prob_label"] = prob_label
            
            # Filter-specific parameters
            if filter_name == 'rotation' and 'limit' in settings:
                limit_frame = ttk.Frame(frame)
                limit_frame.pack(fill=tk.X, pady=2)
                ttk.Label(limit_frame, text="Limit (deg):", width=12).pack(side=tk.LEFT)
                limit_var = tk.IntVar(value=settings['limit'])
                self.filter_vars[f"{filter_name}_limit"] = limit_var
                ttk.Scale(limit_frame, from_=0, to=45, variable=limit_var,
                         orient=tk.HORIZONTAL, command=lambda v: self.on_config_change()).pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Label(limit_frame, textvariable=limit_var, width=5).pack(side=tk.LEFT)
            
            elif filter_name == 'blur' and 'blur_limit' in settings:
                limit_frame = ttk.Frame(frame)
                limit_frame.pack(fill=tk.X, pady=2)
                ttk.Label(limit_frame, text="Blur Limit:", width=12).pack(side=tk.LEFT)
                limit_var = tk.IntVar(value=settings['blur_limit'])
                self.filter_vars[f"{filter_name}_blur_limit"] = limit_var
                ttk.Scale(limit_frame, from_=1, to=15, variable=limit_var,
                         orient=tk.HORIZONTAL, command=lambda v: self.on_config_change()).pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Label(limit_frame, textvariable=limit_var, width=5).pack(side=tk.LEFT)
            
            elif filter_name == 'brightness_contrast':
                for param in ['brightness_limit', 'contrast_limit']:
                    param_frame = ttk.Frame(frame)
                    param_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(param_frame, text=f"{param.split('_')[0].title()}:", width=12).pack(side=tk.LEFT)
                    param_var = tk.DoubleVar(value=settings.get(param, 0.2))
                    self.filter_vars[f"{filter_name}_{param}"] = param_var
                    ttk.Scale(param_frame, from_=0, to=0.5, variable=param_var,
                             orient=tk.HORIZONTAL, command=lambda v: self.on_config_change()).pack(side=tk.LEFT, fill=tk.X, expand=True)
                    param_label = ttk.Label(param_frame, text=f"{settings.get(param, 0.2):.2f}", width=5)
                    param_label.pack(side=tk.LEFT)
                    self.filter_vars[f"{filter_name}_{param}_label"] = param_label
    
    def create_preview_panel(self, parent):
        """Create preview panel."""
        # Title
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(title_frame, text="Preview", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="Generate Preview", command=self.generate_preview).pack(side=tk.RIGHT)
        
        # Image selection
        select_frame = ttk.Frame(parent)
        select_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(select_frame, text="Select Image:").pack(side=tk.LEFT, padx=5)
        
        self.image_combo = ttk.Combobox(select_frame, state='readonly')
        self.image_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.refresh_image_list()
        
        # Preview canvases
        preview_container = ttk.Frame(parent)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Original
        original_frame = ttk.LabelFrame(preview_container, text="Original", padding=5)
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_canvas = tk.Canvas(original_frame, bg='#2b2b2b', width=300, height=300)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Augmented
        augmented_frame = ttk.LabelFrame(preview_container, text="Augmented", padding=5)
        augmented_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.augmented_canvas = tk.Canvas(augmented_frame, bg='#2b2b2b', width=300, height=300)
        self.augmented_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar (hidden by default)
        self.progress_frame = ttk.Frame(parent)
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
    
    def refresh_image_list(self):
        """Refresh the list of available images."""
        if not self.project_manager.current_project_path:
            return
        
        images_dir = os.path.join(self.project_manager.current_project_path, "data", "images")
        if not os.path.exists(images_dir):
            return
        
        images = [f for f in os.listdir(images_dir) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        self.image_combo['values'] = images
        if images:
            self.image_combo.current(0)
    
    def on_config_change(self):
        """Handle configuration changes."""
        # Update count label
        count = int(self.aug_count_var.get())
        self.count_label.config(text=f"{count} augmentations")
        
        # Update probability labels
        for filter_name in self.config.filters.keys():
            prob_var = self.filter_vars.get(f"{filter_name}_probability")
            prob_label = self.filter_vars.get(f"{filter_name}_prob_label")
            if prob_var and prob_label:
                prob_label.config(text=f"{prob_var.get():.2f}")
            
            # Update other parameter labels
            for param in ['brightness_limit', 'contrast_limit']:
                param_var = self.filter_vars.get(f"{filter_name}_{param}")
                param_label = self.filter_vars.get(f"{filter_name}_{param}_label")
                if param_var and param_label:
                    param_label.config(text=f"{param_var.get():.2f}")
    
    def save_config(self):
        """Save current configuration."""
        # Update config from UI
        self.config.enabled = self.enabled_var.get()
        self.config.augmentations_per_image = int(self.aug_count_var.get())
        
        # Update filter settings
        for filter_name in self.config.filters.keys():
            enabled_var = self.filter_vars.get(f"{filter_name}_enabled")
            prob_var = self.filter_vars.get(f"{filter_name}_probability")
            
            if enabled_var:
                self.config.filters[filter_name]['enabled'] = enabled_var.get()
            if prob_var:
                self.config.filters[filter_name]['probability'] = prob_var.get()
            
            # Update filter-specific parameters
            if filter_name == 'rotation':
                limit_var = self.filter_vars.get(f"{filter_name}_limit")
                if limit_var:
                    self.config.filters[filter_name]['limit'] = int(limit_var.get())
            
            elif filter_name == 'blur':
                limit_var = self.filter_vars.get(f"{filter_name}_blur_limit")
                if limit_var:
                    self.config.filters[filter_name]['blur_limit'] = int(limit_var.get())
            
            elif filter_name == 'brightness_contrast':
                for param in ['brightness_limit', 'contrast_limit']:
                    param_var = self.filter_vars.get(f"{filter_name}_{param}")
                    if param_var:
                        self.config.filters[filter_name][param] = param_var.get()
        
        # Save to project config
        if self.project_manager.current_project_path:
            config_path = os.path.join(self.project_manager.current_project_path, "augmentation_config.yaml")
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(self.config.to_dict(), f)
            
            messagebox.showinfo("Saved", "Augmentation configuration saved!")
    
    def load_config(self):
        """Load configuration from project."""
        if not self.project_manager.current_project_path:
            return
        
        config_path = os.path.join(self.project_manager.current_project_path, "augmentation_config.yaml")
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    self.config.from_dict(data)
                    
                    # Update UI
                    self.enabled_var.set(self.config.enabled)
                    self.aug_count_var.set(self.config.augmentations_per_image)
                    
                    # Update filter vars
                    for filter_name, settings in self.config.filters.items():
                        enabled_var = self.filter_vars.get(f"{filter_name}_enabled")
                        prob_var = self.filter_vars.get(f"{filter_name}_probability")
                        
                        if enabled_var:
                            enabled_var.set(settings.get('enabled', False))
                        if prob_var:
                            prob_var.set(settings.get('probability', 0.5))
            except Exception as e:
                # If loading fails (e.g., old format with tuples), delete the file and use defaults
                print(f"Warning: Could not load augmentation config: {e}")
                try:
                    os.remove(config_path)
                    print("Deleted invalid config file, using defaults")
                except:
                    pass
    
    def generate_preview(self):
        """Generate preview of augmentation."""
        selected = self.image_combo.get()
        if not selected:
            messagebox.showwarning("No Image", "Please select an image to preview.")
            return
        
        images_dir = os.path.join(self.project_manager.current_project_path, "data", "images")
        labels_dir = os.path.join(self.project_manager.current_project_path, "data", "labels")
        
        img_path = os.path.join(images_dir, selected)
        label_path = os.path.join(labels_dir, os.path.splitext(selected)[0] + '.txt')
        
        # Update config from UI
        self.save_config()
        
        # Load original image
        original_img = Image.open(img_path)
        self.display_image(self.original_canvas, original_img)
        
        # Generate augmented preview
        result = self.engine.preview_augmentation(img_path, label_path)
        
        if result:
            aug_img_array, bboxes, class_labels = result
            aug_img = Image.fromarray(aug_img_array)
            self.display_image(self.augmented_canvas, aug_img)
        else:
            messagebox.showerror("Error", "Failed to generate preview.")
    
    def display_image(self, canvas, pil_image):
        """Display PIL image on canvas."""
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 300
            canvas_height = 300
        
        # Resize to fit canvas
        img_width, img_height = pil_image.size
        scale_w = canvas_width / img_width
        scale_h = canvas_height / img_height
        scale = min(scale_w, scale_h, 1.0)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        resized = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        
        canvas.delete("all")
        canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo)
        
        # Keep reference
        if canvas == self.original_canvas:
            self.preview_original = photo
        else:
            self.preview_augmented = photo
    
    def run_augmentation(self):
        """Run batch augmentation on dataset."""
        if not self.project_manager.current_project_path:
            messagebox.showwarning("No Project", "Please open a project first.")
            return
        
        # Confirm
        count = int(self.aug_count_var.get())
        if not messagebox.askyesno("Run Augmentation", 
                                   f"This will generate {count} augmented versions of each labeled image.\n\nContinue?"):
            return
        
        # Update config
        self.save_config()
        
        # Show progress
        self.progress_frame.pack(fill=tk.X, padx=10, pady=10)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting augmentation...")
        
        # Run in thread
        thread = threading.Thread(target=self._run_augmentation_thread)
        thread.daemon = True
        thread.start()
    
    def _run_augmentation_thread(self):
        """Thread worker for augmentation."""
        try:
            images_dir = os.path.join(self.project_manager.current_project_path, "data", "images")
            labels_dir = os.path.join(self.project_manager.current_project_path, "data", "labels")
            
            def progress_callback(current, total, message):
                self.after(0, lambda: self.update_progress(current, total, message))
            
            augmented_count = self.engine.augment_dataset(
                images_dir, labels_dir, images_dir, labels_dir, progress_callback
            )
            
            self.after(0, lambda: self.augmentation_complete(augmented_count))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Augmentation failed: {e}"))
            self.after(0, lambda: self.progress_frame.pack_forget())
    
    def update_progress(self, current, total, message):
        """Update progress bar."""
        progress = (current / total) * 100
        self.progress_bar['value'] = progress
        self.progress_label.config(text=message)
    
    def augmentation_complete(self, count):
        """Handle augmentation completion."""
        self.progress_frame.pack_forget()
        messagebox.showinfo("Complete", f"Successfully created {count} augmented images!")
        self.refresh_image_list()
