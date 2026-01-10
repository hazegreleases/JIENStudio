import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from app.ui.components import RoundedButton
from PIL import Image, ImageTk
import os
import shutil
from app.core.theme_manager import ThemeManager
from datetime import datetime

class OrganizedLabelingTool(ttk.Frame):
    """Tabbed labeling interface with drawing capabilities."""
    
    def __init__(self, parent, project_manager):
        super().__init__(parent)
        self.project_manager = project_manager
        self.theme = ThemeManager()
        
        # Drawing state
        self.current_image_path = None
        self.photo_image = None
        self.img_width = 0
        self.img_height = 0
        self.img_width = 0
        self.img_height = 0
        self.scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.pil_image = None  # Store original PIL image
        self.image_id = None
        
        self.boxes = []  # {'id': rect_id, 'text_id': text_id, 'class': class_name, 'bbox': [x1,y1,x2,y2]}
        self.current_box_start = None
        self.drawing_rect_id = None
        self.selected_class = None
        
        # Crosshair guides
        self.crosshair_x = None
        self.crosshair_y = None
        
        # History
        self.history = []
        self.redo_stack = []
        
        self.redo_stack = []
        
        # Auto-Label state
        self.auto_label_model_path = None
        
        # Track current selection context
        self.selected_image_for_deletion = None
        
        # Auto-Label State
        self.auto_label_model_path = None
        self.confidence_var = tk.DoubleVar(value=0.7)
        
        self.setup_ui()
        self.refresh_all_images()
    
    def setup_ui(self):
        # ... (lines 45-84 remain, we need to locate where to insert the new button or key bind)
        # I'll use multi_replace for safer edits across the file.
        pass # Placeholder, actually using multi_replace_file_content is better here.
        # Main container
        container = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Organized tabs
        left_panel = ttk.Frame(container, width=300)
        container.add(left_panel, minsize=250)
        
        # Import buttons
        import_frame = ttk.Frame(left_panel)
        import_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(import_frame, text="Import Images", command=self.import_images).pack(side=tk.LEFT, padx=2)
        ttk.Button(import_frame, text="Refresh", command=self.refresh_all_images).pack(side=tk.LEFT, padx=2)
        
        # Tab notebook
        self.notebook = ttk.Notebook(left_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs (removed Unclassified, keeping Classes, Negatives, Generated)
        self.classes_tab = self.create_classes_tab()
        self.negatives_tab = self.create_simple_tab("Negatives")
        self.notebook.add(self.classes_tab, text="Classes")
        self.notebook.add(self.negatives_tab, text="Negatives")
        
        # Right panel - Canvas and drawing tools
        right_panel = ttk.Frame(container)
        container.add(right_panel, minsize=500)
        
        # Tools frame
        tools_frame = ttk.Frame(right_panel)
        tools_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(tools_frame, text="Brush:").pack(side=tk.LEFT, padx=5)
        
        # Class selector (brush)
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(tools_frame, textvariable=self.class_var, state="readonly", width=15)
        self.class_combo.pack(side=tk.LEFT, padx=5)
        self.class_combo.bind("<<ComboboxSelected>>", self.on_brush_select)
        self.update_class_combo()
        
        ttk.Button(tools_frame, text="Save (Ctrl+S)", command=self.save_labels).pack(side=tk.LEFT, padx=5)
        ttk.Button(tools_frame, text="Select Model", command=self.select_auto_label_model).pack(side=tk.LEFT, padx=2)
        
        # Confidence Control
        conf_frame = ttk.Frame(tools_frame)
        conf_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(conf_frame, text="Conf:").pack(side=tk.LEFT)
        ttk.Scale(conf_frame, from_=0.1, to=1.0, variable=self.confidence_var, orient=tk.HORIZONTAL, length=80).pack(side=tk.LEFT)
        ttk.Label(conf_frame, textvariable=self.confidence_var).pack(side=tk.LEFT)
        
        ttk.Button(tools_frame, text="Auto-Label (O)", command=self.auto_label).pack(side=tk.LEFT, padx=2)
        ttk.Button(tools_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=2)
        ttk.Button(tools_frame, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=2)
        
        self.info_label = ttk.Label(tools_frame, text="No image loaded")
        self.info_label.pack(side=tk.RIGHT, padx=10)
        
        # Canvas + Inspector layout
        canvas_inspector = tk.PanedWindow(right_panel, orient=tk.HORIZONTAL)
        canvas_inspector.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas
        canvas_frame = ttk.Frame(canvas_inspector)
        canvas_inspector.add(canvas_frame, minsize=400)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#2b2b2b", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind drawing events
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Leave>", self.on_canvas_leave)
        self.bind_all("<Control-s>", lambda e: self.save_labels())
        self.bind_all("<Control-z>", lambda e: self.undo())
        self.bind_all("<Control-y>", lambda e: self.redo())
        self.bind_all("<Delete>", self.handle_delete_key)
        self.bind_all("<Control-Shift-Delete>", lambda e: self.delete_current_image())
        self.bind_all("<Key-r>", self.reset_view)
        # Pan bindings
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan)
        self.canvas.bind("<ButtonPress-3>", self.start_pan) 
        self.canvas.bind("<B3-Motion>", self.pan)
        
        # Zoom/Brush bindings (Canvas only)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)
        
        # Inspector
        inspector_frame = ttk.LabelFrame(canvas_inspector, text="Boxes", width=200)
        canvas_inspector.add(inspector_frame, minsize=150)
        
        self.inspector_listbox = tk.Listbox(inspector_frame, bg="#1e1e1e", fg="white", selectmode='extended')
        self.inspector_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.inspector_listbox.bind("<<ListboxSelect>>", self.on_inspector_select)
        
        ttk.Button(inspector_frame, text="Delete Box(es)", command=self.delete_selected_box).pack(pady=5)
    
    def create_classes_tab(self):
        """Create the Classes tab with collapsible tree."""
        tab = ttk.Frame(self.notebook)
        
        controls = ttk.Frame(tab)
        controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls, text="Add Class", command=self.add_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls, text="Delete Class", command=self.delete_class).pack(side=tk.LEFT, padx=2)
        
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.class_tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.class_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, command=self.class_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.class_tree.config(yscrollcommand=scrollbar.set)
        
        self.class_tree.bind("<<TreeviewSelect>>", self.on_class_tree_select)
        
        return tab
    
    def create_simple_tab(self, name):
        """Create a simple list tab."""
        tab = ttk.Frame(self.notebook)
        
        listbox = tk.Listbox(tab, bg="#1e1e1e", fg="white", selectmode='extended')
        listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        listbox.bind("<<ListboxSelect>>", lambda e: self.on_simple_list_select(e, name))
        
        setattr(self, f"{name.lower()}_listbox", listbox)
        return tab
    
    def update_class_combo(self):
        """Update the brush class selector."""
        classes = self.project_manager.get_classes()
        self.class_combo['values'] = classes
        if classes and not self.selected_class:
            self.class_combo.current(0)
            self.selected_class = classes[0]
    
    def on_brush_select(self, event):
        """Handle brush selection."""
        self.selected_class = self.class_var.get()
    
    def add_class(self):
        """Add a new class."""
        class_name = simpledialog.askstring("Add Class", "Enter class name:")
        if class_name:
            self.project_manager.add_class(class_name)
            self.update_class_combo()
            self.refresh_all_images()
    
    def delete_class(self):
        """Delete a class."""
        selection = self.class_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select a class folder to delete.")
            return
        
        item = selection[0]
        if self.class_tree.parent(item):
            messagebox.showwarning("Invalid", "Select a class folder, not an image.")
            return
        
        class_name = self.class_tree.item(item)["text"].split(" (")[0]
        
        if messagebox.askyesno("Delete Class", f"Delete '{class_name}' and all its images?"):
            self.project_manager.remove_class(class_name)
            self.update_class_combo()
            self.refresh_all_images()
    
    def refresh_all_images(self):
        """Refresh all image lists."""
        if not self.project_manager.current_project_path:
            return
        
        images_dir = os.path.join(self.project_manager.current_project_path, "data", "images")
        labels_dir = os.path.join(self.project_manager.current_project_path, "data", "labels")
        
        if not os.path.exists(images_dir):
            return
        
        # Categorize
        all_images = {"Classes": {}, "Negatives": []}
        
        classes = self.project_manager.get_classes()
        for cls in classes:
            all_images["Classes"][cls] = []
        
        for img_file in os.listdir(images_dir):
            if not img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            
            img_path = os.path.join(images_dir, img_file)
            label_path = os.path.join(labels_dir, os.path.splitext(img_file)[0] + ".txt")
            
            # Generated detection
            if os.path.exists(label_path) and os.path.getsize(label_path) > 0:
                with open(label_path, "r") as f:
                    lines = f.readlines()
                    if lines:
                        class_id = int(lines[0].split()[0])
                        if class_id < len(classes):
                            all_images["Classes"][classes[class_id]].append(img_path)
                    else:
                        all_images["Negatives"].append(img_path)
            else:
                # No label = Negative (was unclassified)
                all_images["Negatives"].append(img_path)
        
        # Update UI
        self.class_tree.delete(*self.class_tree.get_children())
        for cls, images in all_images["Classes"].items():
            parent = self.class_tree.insert("", "end", text=f"{cls} ({len(images)})")
            for img in images:
                self.class_tree.insert(parent, "end", text=os.path.basename(img), values=(img,))
        
        for category in ["Negatives"]:
            listbox = getattr(self, f"{category.lower()}_listbox")
            listbox.delete(0, tk.END)
            for img in all_images[category]:
                listbox.insert(tk.END, os.path.basename(img))
            # Store paths for retrieval
            setattr(self, f"{category.lower()}_paths", all_images[category])
    
    def on_class_tree_select(self, event):
        """Handle class tree selection."""
        selection = self.class_tree.selection()
        if selection and self.class_tree.parent(selection[0]):
            img_path = self.class_tree.item(selection[0])["values"][0]
            self.selected_image_for_deletion = img_path  # Track for deletion
            self.load_image(img_path)
    
    def on_simple_list_select(self, event, category):
        """Handle simple list selection."""
        listbox = getattr(self, f"{category.lower()}_listbox")
        sel = listbox.curselection()
        if sel:
            paths = getattr(self, f"{category.lower()}_paths", [])
            if sel[0] < len(paths):
                img_path = paths[sel[0]]
                self.selected_image_for_deletion = img_path  # Track for deletion
                self.load_image(img_path)
    
    def on_inspector_select(self, event):
        """Highlight selected box."""
        pass  # Could highlight the box on canvas
    
    def load_image(self, img_path):
        """Load image onto canvas."""
        self.current_image_path = img_path
        self.info_label.config(text=os.path.basename(img_path))
        
        try:
            self.pil_image = Image.open(img_path)
            self.img_width, self.img_height = self.pil_image.size

            

            # Reset state
            self.boxes = []
            self.history = []
            self.redo_stack = []

            self.canvas.delete("all")
            
            self.load_existing_labels()
            self.reset_view()
            self.update_inspector()

            # self.load_existing_labels()
            # self.update_inspector()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")
    

    def reset_view(self, event=None):
        """Fit image to canvas center."""
        if not self.pil_image: return
        
        self.img_width, self.img_height = self.pil_image.size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            scale_w = canvas_width / self.img_width
            scale_h = canvas_height / self.img_height
            self.scale = min(scale_w, scale_h, 1.0)
            
            # Center it
            disp_w = self.img_width * self.scale
            disp_h = self.img_height * self.scale
            self.pan_x = (canvas_width - disp_w) / 2
            self.pan_y = (canvas_height - disp_h) / 2
        else:
            self.scale = 1.0
            self.pan_x = 0
            self.pan_y = 0
            
        self.redraw_view()

    def redraw_view(self):
        """Redraw the visible portion of the image at current scale."""
        if not self.pil_image: return
        
        # Canvas dimensions
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        if cw < 2: cw = 800
        if ch < 2: ch = 600

        img_w, img_h = self.pil_image.size
        
        # 1. Calculate Visible Rectangle in Image Coords
        # ix = (cx - pan_x) / scale
        vis_x1 = -self.pan_x / self.scale
        vis_y1 = -self.pan_y / self.scale
        vis_x2 = (cw - self.pan_x) / self.scale
        vis_y2 = (ch - self.pan_y) / self.scale
        
        # Intersect with Image Bounds
        crop_x1 = max(0, int(vis_x1))
        crop_y1 = max(0, int(vis_y1))
        crop_x2 = min(img_w, int(vis_x2) + 1)
        crop_y2 = min(img_h, int(vis_y2) + 1)
        
        # Store current boxes data to re-create
        current_boxes = self.boxes
        self.boxes = [] # Will be repopulated
        
        self.canvas.delete("all")

        # If completely off-screen, just redraw boxes (though likely none visible)
        if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
            pass
        else:
            # 2. Crop
            crop = self.pil_image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            
            # 3. Resize
            target_w = int((crop_x2 - crop_x1) * self.scale)
            target_h = int((crop_y2 - crop_y1) * self.scale)
            
            # Use NEAREST for speed/sharpness when zoomed inside
            resample_method = Image.Resampling.NEAREST if self.scale >= 1.0 else Image.Resampling.BILINEAR
                
            display_img = crop.resize((max(1, target_w), max(1, target_h)), resample_method)
            self.photo_image = ImageTk.PhotoImage(display_img)
            
            # 4. Position on Canvas
            draw_x = self.pan_x + crop_x1 * self.scale
            draw_y = self.pan_y + crop_y1 * self.scale
            
            self.image_id = self.canvas.create_image(draw_x, draw_y, anchor=tk.NW, image=self.photo_image)
        
        # 5. Redraw boxes
        for box_data in current_boxes:
             x1, y1, x2, y2 = box_data['bbox']
             cls = box_data['class']
             self.add_box_to_canvas(x1, y1, x2, y2, cls)

    def zoom(self, delta, mouse_x, mouse_y):
        """Zoom in or out relative to mouse position."""
        if not self.pil_image: return
        
        # Zoom factor
        factor = 1.1 if delta > 0 else 0.9
        new_scale = self.scale * factor
        
        # Clamp
        new_scale = max(0.1, min(new_scale, 20.0))
        
        if new_scale == self.scale: return
        
        # Calculate offset adjustment to keep mouse_x/y over same image pixel
        # Mouse pos relative to image origin (pan)
        rel_x = mouse_x - self.pan_x
        rel_y = mouse_y - self.pan_y
        
        # Apply scaling factor to this relative vector
        # new_rel = rel * (new_scale / old_scale)
        scale_ratio = new_scale / self.scale
        
        new_rel_x = rel_x * scale_ratio
        new_rel_y = rel_y * scale_ratio
        
        # New pan position
        self.pan_x = mouse_x - new_rel_x
        self.pan_y = mouse_y - new_rel_y
        
        self.scale = new_scale
        self.redraw_view()
        
    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)
        self._pan_start_x = event.x
        self._pan_start_y = event.y
        self._pan_orig_x = self.pan_x
        self._pan_orig_y = self.pan_y

    def pan(self, event):
        # Calculate delta
        dx = event.x - self._pan_start_x
        dy = event.y - self._pan_start_y
        
        self.pan_x = self._pan_orig_x + dx
        self.pan_y = self._pan_orig_y + dy
        self.redraw_view()
    
    def load_existing_labels(self):
        """Load existing YOLO labels."""
        filename = os.path.basename(self.current_image_path)
        label_path = os.path.join(self.project_manager.current_project_path, "data", "labels",
                                    os.path.splitext(filename)[0] + ".txt")
        
        classes = self.project_manager.get_classes()
        if not os.path.exists(label_path):
            return
        
        with open(label_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_idx = int(parts[0])
                    cx, cy, w, h = map(float, parts[1:5])
                    
                    if cls_idx < len(classes):
                        x1 = (cx - w/2) * self.img_width
                        y1 = (cy - h/2) * self.img_height
                        x2 = (cx + w/2) * self.img_width
                        y2 = (cy + h/2) * self.img_height
                        
                        self.add_box_visual(x1, y1, x2, y2, classes[cls_idx])
    
    def on_canvas_motion(self, event):
        """Update crosshair position as mouse moves."""
        if not self.current_image_path:
            return
        
        # Remove old crosshairs
        if self.crosshair_x:
            self.canvas.delete(self.crosshair_x)
        if self.crosshair_y:
            self.canvas.delete(self.crosshair_y)
        
        # Draw new crosshairs
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Vertical line (X axis)
        self.crosshair_x = self.canvas.create_line(
            event.x, 0, event.x, canvas_height,
            fill="#00FF00", width=1, dash=(4, 4), tags="crosshair"
        )
        
        # Horizontal line (Y axis)
        self.crosshair_y = self.canvas.create_line(
            0, event.y, canvas_width, event.y,
            fill="#00FF00", width=1, dash=(4, 4), tags="crosshair"
        )
    
    def on_canvas_leave(self, event):
        """Remove crosshairs when mouse leaves canvas."""
        if self.crosshair_x:
            self.canvas.delete(self.crosshair_x)
            self.crosshair_x = None
        if self.crosshair_y:
            self.canvas.delete(self.crosshair_y)
            self.crosshair_y = None
    
    def on_canvas_press(self, event):
        if not self.current_image_path or not self.selected_class:
            return
        self.current_box_start = (event.x, event.y)
        self.drawing_rect_id = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red", width=2)
    
    def on_canvas_drag(self, event):
        if self.current_box_start and self.drawing_rect_id:
            x, y = self.current_box_start
            self.canvas.coords(self.drawing_rect_id, x, y, event.x, event.y)
    
    def on_canvas_release(self, event):
        if self.current_box_start and self.drawing_rect_id:
            x1, y1 = self.current_box_start
            x2, y2 = event.x, event.y
            
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            
            if (x2 - x1) > 5 and (y2 - y1) > 5:
                img_x1, img_y1 = x1 / self.scale, y1 / self.scale
                img_x2, img_y2 = x2 / self.scale, y2 / self.scale
                
                self.canvas.delete(self.drawing_rect_id)
                self.add_box_visual(img_x1, img_y1, img_x2, img_y2, self.selected_class, record_history=True)
            else:
                self.canvas.delete(self.drawing_rect_id)
            
            self.current_box_start = None
            self.drawing_rect_id = None
    
    def add_box_visual(self, x1, y1, x2, y2, cls_name, record_history=False):
        """Add a box to the canvas."""
        sx1, sy1 = x1 * self.scale, y1 * self.scale
        sx2, sy2 = x2 * self.scale, y2 * self.scale
        
        rect_id = self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline="lime", width=2, tags="box")
        text_id = self.canvas.create_text(sx1, sy1-10, text=cls_name, fill="lime", anchor=tk.SW, tags="box")
        
        box = {"id": rect_id, "text_id": text_id, "class": cls_name, "bbox": [x1, y1, x2, y2]}
        self.boxes.append(box)
        self.update_inspector()
        
        if record_history:
            self.history.append(("add", box))
            self.redo_stack.clear()
    
    def update_inspector(self):
        """Update the inspector listbox."""
        self.inspector_listbox.delete(0, tk.END)
        for i, box in enumerate(self.boxes):
            self.inspector_listbox.insert(tk.END, f"{i}: {box['class']}")
    
    def delete_selected_box(self):
        """Delete the selected box(es)."""
        selections = self.inspector_listbox.curselection()
        if not selections:
            return
        
        # Sort in reverse to delete from end to start (preserves indices)
        for idx in sorted(selections, reverse=True):
            if idx < len(self.boxes):
                box = self.boxes.pop(idx)
                self.canvas.delete(box['id'])
                self.canvas.delete(box['text_id'])
                self.history.append(("delete", box, idx))
        
        self.redo_stack.clear()
        self.update_inspector()
    
    def undo(self):
        """Undo last action."""
        if not self.history:
            return
        action = self.history.pop()
        
        if action[0] == 'add':
            box = action[1]
            self.boxes.remove(box)
            self.canvas.delete(box['id'])
            self.canvas.delete(box['text_id'])
            self.redo_stack.append(action)
        elif action[0] == 'delete':
            box, idx = action[1], action[2]
            self.boxes.insert(idx, box)
            sx1, sy1 = box['bbox'][0] * self.scale, box['bbox'][1] * self.scale
            sx2, sy2 = box['bbox'][2] * self.scale, box['bbox'][3] * self.scale
            box['id'] = self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline="lime", width=2, tags="box")
            box['text_id'] = self.canvas.create_text(sx1, sy1-10, text=box['class'], fill="lime", anchor=tk.SW, tags="box")
            self.redo_stack.append(action)
        
        self.update_inspector()
    
    def redo(self):
        """Redo last undone action."""
        if not self.redo_stack:
            return
        action = self.redo_stack.pop()
        
        if action[0] == 'add':
            self.add_box_visual(*action[1]['bbox'], action[1]['class'], record_history=False)
            self.history.append(action)
        elif action[0] == 'delete':
            box = action[1]
            if box in self.boxes:
                self.boxes.remove(box)
                self.canvas.delete(box['id'])
                self.canvas.delete(box['text_id'])
                self.history.append(action)
        
        self.update_inspector()
    
    def save_labels(self):
        """Save labels to YOLO format."""
        if not self.current_image_path:
            return
        
        filename = os.path.basename(self.current_image_path)
        label_path = os.path.join(self.project_manager.current_project_path, "data", "labels",
                                    os.path.splitext(filename)[0] + ".txt")
        
        classes = self.project_manager.get_classes()
        
        with open(label_path, "w") as f:
            for box in self.boxes:
                if box['class'] not in classes:
                    continue
                
                cls_idx = classes.index(box['class'])
                x1, y1, x2, y2 = box['bbox']
                
                cx = ((x1 + x2) / 2) / self.img_width
                cy = ((y1 + y2) / 2) / self.img_height
                w = (x2 - x1) / self.img_width
                h = (y2 - y1) / self.img_height
                
                f.write(f"{cls_idx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
        
        messagebox.showinfo("Saved", f"Labels saved for {filename}")
        self.refresh_all_images()
    
    def import_images(self):
        """Import images."""
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("All", "*.*")]
        )
        
        if files:
            images_dir = os.path.join(self.project_manager.current_project_path, "data", "images")
            for file in files:
                shutil.copy2(file, images_dir)
            messagebox.showinfo("Success", f"Imported {len(files)} images.")
            self.refresh_all_images()
    
    def handle_delete_key(self, event):
        """Handle delete key - delete box or image depending on context."""
        # Priority: Inspector > Tab selections > Current image
        if self.inspector_listbox.curselection():
            self.delete_selected_box()
        elif self.class_tree.selection():
            # Check if it's an image in class tree
            sel = self.class_tree.selection()[0]
            if self.class_tree.parent(sel):  # It's an image
                self.delete_selected_image_from_tab()
        elif self.negatives_listbox.curselection():
            self.delete_selected_image_from_tab()
    
    def delete_selected_image_from_tab(self):
        """Delete image(s) selected in any tab."""
        # Collect all selected images
        images_to_delete = []
        
        # Check class tree
        if self.class_tree.selection():
            for sel in self.class_tree.selection():
                if self.class_tree.parent(sel):  # It's an image
                    img_path = self.class_tree.item(sel)["values"][0]
                    images_to_delete.append(img_path)
        
        # Check negatives listbox
        neg_selections = self.negatives_listbox.curselection()
        if neg_selections:
            for idx in neg_selections:
                if idx < len(self.negatives_paths):
                    images_to_delete.append(self.negatives_paths[idx])
        
        if not images_to_delete:
            return
        
        # Confirm deletion
        count = len(images_to_delete)
        if count == 1:
            filename = os.path.basename(images_to_delete[0])
            if not messagebox.askyesno("Delete", f"Delete {filename}?"):
                return
        else:
            if not messagebox.askyesno("Delete Multiple", f"Delete {count} image(s)?"):
                return
        
        # Delete all selected images
        for img_path in images_to_delete:
            try:
                filename = os.path.basename(img_path)
                # Delete image
                if os.path.exists(img_path):
                    os.remove(img_path)
                
                # Delete label
                label_path = os.path.join(
                    self.project_manager.current_project_path, "data", "labels",
                    os.path.splitext(filename)[0] + ".txt"
                )
                if os.path.exists(label_path):
                    os.remove(label_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {filename}: {e}")
        
        self.selected_image_for_deletion = None
        self.current_image_path = None
        self.refresh_all_images()
        
        if count == 1:
            messagebox.showinfo("Deleted", f"Deleted 1 image")
        else:
            messagebox.showinfo("Deleted", f"Deleted {count} images")
    
    def delete_current_image(self):
        """Delete the currently displayed image."""
        if not self.current_image_path:
            return
        
        filename = os.path.basename(self.current_image_path)
        if messagebox.askyesno("Delete Image", f"Delete {filename}?"):
            try:
                os.remove(self.current_image_path)
                
                # Delete label
                label_path = os.path.join(
                    self.project_manager.current_project_path, "data", "labels",
                    os.path.splitext(filename)[0] + ".txt"
                )
                if os.path.exists(label_path):
                    os.remove(label_path)
                
                self.refresh_all_images()
                messagebox.showinfo("Deleted", f"Deleted {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for Zoom (Ctrl) or Brush Change."""
        
        # Determine direction
        delta = 0
        # print(f"DEBUG: MouseWheel num={event.num} delta={getattr(event, 'delta', 'N/A')} state={event.state}")
        if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            delta = -1 # Down / Out
        elif event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            delta = 1 # Up / In
            
        if delta == 0: return

        # Check for Control key (Zoom)
        if (event.state & 0x0004) or (event.state & 4):
             # event.x/y are relative to canvas because we bound to self.canvas
             self.zoom(delta, event.x, event.y)
             return

        # Otherwise Change Brush
        classes = self.project_manager.get_classes()
        if not classes:
            return
        
        current_idx = 0
        if self.selected_class in classes:
            current_idx = classes.index(self.selected_class)
        
        new_idx = (current_idx + delta) % len(classes)
        self.selected_class = classes[new_idx]
        self.class_var.set(self.selected_class)
        
        # Check if widget still exists before updating
        try:
            self.class_combo.current(new_idx)
        except tk.TclError:
            pass  # Widget was destroyed, ignore

    def select_auto_label_model(self):
        """Select and cache the model for auto-labeling."""
        model_path = filedialog.askopenfilename(
            title="Select YOLO Model",
            filetypes=[("YOLO Model", "*.pt")]
        )
        if model_path:
            self.auto_label_model_path = model_path
            messagebox.showinfo("Model Selected", f"Selected: {os.path.basename(model_path)}")

    def auto_label(self):
        """Run YOLO inference to auto-label the current image."""
        if not self.current_image_path:
            return  # Silent return or maybe flash? No, silent is better if no image.

        # 1. Ensure Model
        if not self.auto_label_model_path:
            self.select_auto_label_model()
            if not self.auto_label_model_path:
                return # User cancelled

        try:
            # 2. Run Inference
            from app.core.yolo_wrapper import YOLOWrapper
            # We can instantiate wrapper lightly or reuse if available in project manager
            wrapper = YOLOWrapper(self.project_manager.current_project_path)
            
            # Run with user specified confidence
            conf = self.confidence_var.get()
            results = wrapper.run_inference(self.auto_label_model_path, self.current_image_path, conf=conf)
            
            # 3. Process Results
            added_count = 0
            
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    class_name = r.names[cls_id]
                    
                    if class_name not in self.project_manager.get_classes():
                         # Automatically add class if possible or skip?
                         # User asked for simplified flow. Let's auto-add if missing or skip silently?
                         # The previous "popup" was annoying.
                         # Let's add it silently if we can, or just log.
                         # Safer: Add it silently.
                         self.project_manager.add_class(class_name)
                         self.update_class_combo()
                            
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    self.add_box_to_canvas(x1, y1, x2, y2, class_name)
                    added_count += 1
            
            if added_count > 0:
                self.save_history() # Save state for undo
                # No popup
            else:
                self.flash_feedback()
                
        except Exception as e:
            # Only show error if it's a real crash, but maybe just log to console to not annoy user
            print(f"Auto-label error: {e}")
            self.flash_feedback() # Flash to indicate failure too?

    def flash_feedback(self):
        """Flash the canvas red with 50% transparency for 0.1s."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Create a red image with alpha
        # PIL Image.new("RGBA", (w, h), (255, 0, 0, 128))
        if w <= 1 or h <= 1: return
            
        try:
            flash = Image.new("RGBA", (w, h), (255, 0, 0, 128))
            self._flash_photo = ImageTk.PhotoImage(flash) # Keep reference
            
            flash_id = self.canvas.create_image(0, 0, image=self._flash_photo, anchor="nw")
            
            self.after(100, lambda: self.canvas.delete(flash_id))
        except Exception as e:
            print(f"Flash error: {e}")

    def get_class_color(self, class_name):
        """Generate a deterministic color for a class."""
        # Simple hash based color
        h = hash(class_name)
        # Ensure positive
        if h < 0: h = -h
        # Hue based on hash
        r = (h % 255)
        g = ((h >> 8) % 255)
        b = ((h >> 16) % 255)
        # Ensure it's not too dark
        if r + g + b < 300:
             r = min(255, r + 100)
             g = min(255, g + 100)
             b = min(255, b + 100)
        return f"#{r:02x}{g:02x}{b:02x}"

    def add_box_to_canvas(self, x1, y1, x2, y2, class_name):
        """Helper to add a box from coordinates."""
        # Convert image coords back to canvas coords if zoomed/scaled
        color = self.get_class_color(class_name)
        
        # Apply scale and pan
        cx1 = x1 * self.scale + self.pan_x
        cy1 = y1 * self.scale + self.pan_y
        cx2 = x2 * self.scale + self.pan_x
        cy2 = y2 * self.scale + self.pan_y
        
        rect_id = self.canvas.create_rectangle(
            cx1, cy1, cx2, cy2, 
            outline=color, width=2
        )
        
        text_id = self.canvas.create_text(
            cx1, cy1 - 10, 
            text=class_name, fill=color, anchor="sw"
        )
        
        self.boxes.append({
            'id': rect_id,
            'text_id': text_id,
            'class': class_name,
            'bbox': [x1, y1, x2, y2] # Store separate from canvas coords
        })
    

