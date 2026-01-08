"""
Augmentation view with modular pipeline support.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil
import threading
from app.core.augmentation_engine import (
    AugmentationEngine, AugmentationPipeline, EFFECT_REGISTRY, create_effect_from_dict, load_filters
)
from app.ui.components import RoundedButton
import cv2
import numpy as np

class AugmentationView(ttk.Frame):
    """UI for configuring and running modular augmentations."""
    
    def __init__(self, parent, project_manager):
        super().__init__(parent)
        self.project_manager = project_manager
        self.pipeline = AugmentationPipeline()
        self.engine = AugmentationEngine(self.pipeline)
        
        self.preview_original = None
        self.preview_augmented = None
        
        # State
        self.selected_effect_index = None
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """Create the UI layout."""
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel (Pipeline Config)
        left_panel = ttk.Frame(paned, width=400)
        paned.add(left_panel, minsize=350)
        
        # Right Panel (Preview)
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, minsize=400)
        
        self.create_config_panel(left_panel)
        self.create_preview_panel(right_panel)

    def create_config_panel(self, parent):
        # Title & Global Settings
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Pipeline Editor", font=('Arial', 14, 'bold')).pack(anchor=tk.W)
        
        # Enable & Count
        global_frame = ttk.LabelFrame(parent, text="Global Settings", padding=5)
        global_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(global_frame, text="Enable Pipeline", variable=self.enabled_var, 
                        command=self.save_global_settings).pack(anchor=tk.W)
        
        count_frame = ttk.Frame(global_frame)
        count_frame.pack(fill=tk.X, pady=5)
        ttk.Label(count_frame, text="Copies per Image:").pack(side=tk.LEFT)
        self.count_var = tk.IntVar(value=5)
        ttk.Spinbox(count_frame, from_=1, to=50, textvariable=self.count_var, width=5, 
                    command=self.save_global_settings).pack(side=tk.LEFT, padx=5)

        # Effect Actions (Add, Remove, Move)
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add Effect Dropdown
        self.add_effect_var = tk.StringVar()
        effect_names = sorted(list(EFFECT_REGISTRY.keys()))
        self.add_effect_combo = ttk.Combobox(action_frame, textvariable=self.add_effect_var, values=effect_names, state="readonly", width=20)
        self.add_effect_combo.pack(side=tk.LEFT, padx=2)
        if effect_names: self.add_effect_combo.current(0)
        
        ttk.Button(action_frame, text="+ Add", command=self.add_effect, width=6).pack(side=tk.LEFT, padx=2)
        
        # Filter Management
        manage_frame = ttk.Frame(parent)
        manage_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Button(manage_frame, text="Import Filter (.py)", command=self.import_filter).pack(side=tk.LEFT, padx=2)
        ttk.Button(manage_frame, text="Refresh List", command=self.refresh_effect_registry).pack(side=tk.LEFT, padx=2)

        ttk.Button(action_frame, text="Remove", command=self.remove_effect).pack(side=tk.RIGHT, padx=2)
        ttk.Button(action_frame, text="↓", width=3, command=self.move_down).pack(side=tk.RIGHT, padx=2)
        ttk.Button(action_frame, text="↑", width=3, command=self.move_up).pack(side=tk.RIGHT, padx=2)

        # Pipeline List
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.effect_listbox = tk.Listbox(list_frame, height=10, selectmode=tk.SINGLE, bg="#1e1e1e", fg="white")
        self.effect_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.effect_listbox.bind("<<ListboxSelect>>", self.on_effect_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.effect_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.effect_listbox.config(yscrollcommand=scrollbar.set)

        # Effect Settings (Dynamic)
        self.settings_frame = ttk.LabelFrame(parent, text="Effect Settings", padding=10)
        self.settings_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10, ipady=5)
        self.settings_content = ttk.Frame(self.settings_frame)
        self.settings_content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.settings_content, text="Select an effect to edit settings").pack()

        # Footer Actions
        footer = ttk.Frame(parent)
        footer.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(footer, text="Save Pipeline", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(footer, text="Run Augmentation", command=self.run_augmentation).pack(side=tk.RIGHT, padx=5)

    def create_preview_panel(self, parent):
        # Similar to before
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(title_frame, text="Preview", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="Refresh Preview", command=self.generate_preview).pack(side=tk.RIGHT)
        
        # Image selector
        select_frame = ttk.Frame(parent)
        select_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(select_frame, text="Image:").pack(side=tk.LEFT)
        self.image_combo = ttk.Combobox(select_frame, state='readonly')
        self.image_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.refresh_image_list()
        
        # Canvases
        preview_container = ttk.Frame(parent)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.original_canvas = tk.Canvas(preview_container, bg='#2b2b2b', height=300)
        self.original_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        
        self.augmented_canvas = tk.Canvas(preview_container, bg='#2b2b2b', height=300)
        self.augmented_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        
        # Progress
        self.progress_frame = ttk.Frame(parent)
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

    def refresh_listbox(self):
        self.effect_listbox.delete(0, tk.END)
        for i, effect in enumerate(self.pipeline.effects):
            status = "[x]" if effect.enabled else "[ ]"
            self.effect_listbox.insert(tk.END, f"{i+1}. {status} {effect.name}")
        
        if self.selected_effect_index is not None and 0 <= self.selected_effect_index < len(self.pipeline.effects):
            self.effect_listbox.selection_set(self.selected_effect_index)

    def add_effect(self):
        effect_name = self.add_effect_var.get()
        if not effect_name: return
        
        # Create dummy dict to use factory
        effect = create_effect_from_dict({'type': effect_name})
        if effect:
            self.pipeline.add_effect(effect)
            self.refresh_listbox()
            self.selected_effect_index = len(self.pipeline.effects) - 1
            self.refresh_listbox()
            self.show_effect_settings(effect)
            self.save_config()

    def remove_effect(self):
        sel = self.effect_listbox.curselection()
        if not sel: return
        
        index = sel[0]
        self.pipeline.remove_effect(index)
        self.selected_effect_index = None
        self.refresh_listbox()
        self.clear_settings()
        self.save_config()

    def move_up(self):
        sel = self.effect_listbox.curselection()
        if not sel: return
        index = sel[0]
        if index > 0:
            self.pipeline.move_effect(index, index - 1)
            self.selected_effect_index = index - 1
            self.refresh_listbox()
            self.save_config()

    def move_down(self):
        sel = self.effect_listbox.curselection()
        if not sel: return
        index = sel[0]
        if index < len(self.pipeline.effects) - 1:
            self.pipeline.move_effect(index, index + 1)
            self.selected_effect_index = index + 1
            self.refresh_listbox()
            self.save_config()

    def on_effect_select(self, event):
        sel = self.effect_listbox.curselection()
        if not sel: return
        
        index = sel[0]
        self.selected_effect_index = index
        effect = self.pipeline.effects[index]
        self.show_effect_settings(effect)
        self.generate_preview()

    def clear_settings(self):
        for widget in self.settings_content.winfo_children():
            widget.destroy()

    def show_effect_settings(self, effect):
        self.clear_settings()
        
        # Common controls
        common_frame = ttk.Frame(self.settings_content)
        common_frame.pack(fill=tk.X, pady=5)
        
        enabled_var = tk.BooleanVar(value=effect.enabled)
        def toggle_enable():
            effect.enabled = enabled_var.get()
            self.refresh_listbox() # Update [x] status
            self.save_config()
            self.generate_preview()
            
        ttk.Checkbutton(common_frame, text="Enabled", variable=enabled_var, command=toggle_enable).pack(side=tk.LEFT)
        
        prob_frame = ttk.Frame(self.settings_content)
        prob_frame.pack(fill=tk.X, pady=5)
        ttk.Label(prob_frame, text="Probability:").pack(side=tk.LEFT)
        prob_var = tk.DoubleVar(value=effect.probability)
        def update_prob(val):
            effect.probability = float(val)
            self.save_config()
        ttk.Scale(prob_frame, from_=0, to=1, variable=prob_var, command=update_prob).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Dynamic specific controls
        params = effect.get_params()
        for key, value in params.items():
            frame = ttk.Frame(self.settings_content)
            frame.pack(fill=tk.X, pady=2)
            
            clean_name = key.replace('_', ' ').title()
            ttk.Label(frame, text=f"{clean_name}:").pack(side=tk.LEFT)
            
            if isinstance(value, float):
                var = tk.DoubleVar(value=value)
                # Heuristic for range...
                scale_max = 1.0
                if 'limit' in key or 'var' in key: scale_max = 50.0  # broader range for limits
                if 'fraction' in key: scale_max = 1.0
                
                cmd = lambda v, k=key: self.update_param(effect, k, v)
                ttk.Scale(frame, from_=0, to=scale_max, variable=var, command=cmd).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                # Label to show value
                ttk.Label(frame, textvariable=var, width=6).pack(side=tk.LEFT)
                
            elif isinstance(value, int):
                var = tk.IntVar(value=value)
                scale_max = 100
                if 'blur' in key: scale_max = 20
                if 'limit' in key: scale_max = 180
                
                cmd = lambda v, k=key: self.update_param(effect, k, v)
                ttk.Scale(frame, from_=0, to=scale_max, variable=var, command=cmd).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                ttk.Label(frame, textvariable=var, width=6).pack(side=tk.LEFT)

    def update_param(self, effect, key, value):
        effect.set_params({key: float(value)})
        self.generate_preview()
        # Debounce save?
        self.save_config()

    def save_global_settings(self):
        self.pipeline.enabled = self.enabled_var.get()
        self.pipeline.augmentations_per_image = self.count_var.get()
        self.save_config()

    def save_config(self):
        if self.project_manager.current_project_path:
            config_path = os.path.join(self.project_manager.current_project_path, "augmentation_pipeline.json")
            self.pipeline.save(config_path)

    def load_config(self):
        if self.project_manager.current_project_path:
            config_path = os.path.join(self.project_manager.current_project_path, "augmentation_pipeline.json")
            if os.path.exists(config_path):
                self.pipeline.load(config_path)
                self.enabled_var.set(self.pipeline.enabled)
                self.count_var.set(self.pipeline.augmentations_per_image)
                self.refresh_listbox()
    
    # Utility methods for preview and image handling (copied/adapted from previous)
    def refresh_image_list(self):
        if not self.project_manager.current_project_path: return
        images_dir = os.path.join(self.project_manager.current_project_path, "data", "images")
        if not os.path.exists(images_dir): return
        images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        self.image_combo['values'] = images
        if images: self.image_combo.current(0)

    def generate_preview(self):
        selected = self.image_combo.get()
        if not selected: return
        
        images_dir = os.path.join(self.project_manager.current_project_path, "data", "images")
        labels_dir = os.path.join(self.project_manager.current_project_path, "data", "labels")
        img_path = os.path.join(images_dir, selected)
        label_path = os.path.join(labels_dir, os.path.splitext(selected)[0] + '.txt')
        
        # Display Original
        original_img = Image.open(img_path)
        self.display_image(self.original_canvas, original_img)
        
        # Display Augmented
        res = self.engine.preview_augmentation(img_path, label_path)
        if res:
            aug_img, bbox, cls = res
            self.display_image(self.augmented_canvas, Image.fromarray(aug_img))

    def display_image(self, canvas, pil_img):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w < 10: w, h = 300, 300
        
        # Aspect Ratio
        img_w, img_h = pil_img.size
        scale = min(w/img_w, h/img_h, 1.0)
        new_w, new_h = int(img_w*scale), int(img_h*scale)
        
        resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        
        canvas.delete("all")
        canvas.create_image(w//2, h//2, image=photo)
        
        # hold ref
        if canvas == self.original_canvas: self.preview_original = photo
        else: self.preview_augmented = photo

    def run_augmentation(self):
        if not self.project_manager.current_project_path: return
        if not messagebox.askyesno("Run", f"Generate {self.count_var.get()} augmentations per image?"): return
        
        self.progress_frame.pack(fill=tk.X, padx=10, pady=10)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting...")
        
        thread = threading.Thread(target=self._run_thread)
        thread.daemon = True
        thread.start()

    def _run_thread(self):
        try:
            p = self.project_manager.current_project_path
            count = self.engine.augment_dataset(
                os.path.join(p, "data", "images"),
                os.path.join(p, "data", "labels"),
                os.path.join(p, "data", "images"),
                os.path.join(p, "data", "labels"),
                lambda c, t, m: self.after(0, lambda: self._update_progress(c, t, m))
            )
            self.after(0, lambda: self._complete(count))
        except Exception as e:
            print(e)
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def _update_progress(self, current, total, message):
        self.progress_bar['value'] = (current/total)*100
        self.progress_label.config(text=message)

    def _complete(self, count):
        self.progress_frame.pack_forget()
        messagebox.showinfo("Done", f"Created {count} images.")
        self.refresh_image_list()

    def import_filter(self):
        """Import a custom filter file."""
        file_path = filedialog.askopenfilename(
            title="Select Filter Script",
            filetypes=[("Python Files", "*.py")]
        )
        if not file_path: return
        
        try:
            # Determine destination
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dest_dir = os.path.join(base_dir, 'core', 'augmentation', 'filters', 'libraries', 'custom')
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            shutil.copy(file_path, dest_dir)
            messagebox.showinfo("Success", f"Imported {os.path.basename(file_path)} to custom library.")
            self.refresh_effect_registry()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import filter: {e}")

    def refresh_effect_registry(self):
        """Reload filters and update dropdown."""
        global EFFECT_REGISTRY
        EFFECT_REGISTRY = load_filters()
        effect_names = sorted(list(EFFECT_REGISTRY.keys()))
        self.add_effect_combo['values'] = effect_names
        if effect_names:
            self.add_effect_combo.current(0)
