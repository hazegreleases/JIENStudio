import tkinter as tk
from tkinter import ttk, filedialog
from app.ui.components import RoundedButton
from app.core.theme_manager import ThemeManager

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, project_manager):
        super().__init__(parent)
        self.project_manager = project_manager
        self.theme = ThemeManager()
        
        self.title("Settings")
        self.geometry("500x300")
        self.configure(bg=self.theme.get("window_bg_color"))
        
        # Modal behavior
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        main_frame = tk.Frame(self, bg=self.theme.get("window_bg_color"), padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Auto-Label Model
        model_frame = tk.LabelFrame(main_frame, text="Auto-Labeling", 
                                    bg=self.theme.get("window_bg_color"),
                                    fg=self.theme.get("window_text_color"),
                                    font=(self.theme.get("font_family"), 12, "bold"))
        model_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(model_frame, text="YOLO Model Path:", 
                 bg=self.theme.get("window_bg_color"),
                 fg=self.theme.get("window_text_color")).pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        input_frame = tk.Frame(model_frame, bg=self.theme.get("window_bg_color"))
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.model_path_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=self.model_path_var, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        RoundedButton(input_frame, text="Browse", command=self.browse_model, width=80, height=25).pack(side=tk.RIGHT)
        
        # Confidence
        tk.Label(model_frame, text="Confidence Threshold:", 
                 bg=self.theme.get("window_bg_color"),
                 fg=self.theme.get("window_text_color")).pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        conf_frame = tk.Frame(model_frame, bg=self.theme.get("window_bg_color"))
        conf_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.conf_var = tk.DoubleVar(value=0.5)
        
        scale = ttk.Scale(conf_frame, from_=0.1, to=1.0, variable=self.conf_var, orient=tk.HORIZONTAL)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.conf_label = tk.Label(conf_frame, text="0.50", width=5,
                                   bg=self.theme.get("window_bg_color"),
                                   fg=self.theme.get("window_text_color"))
        self.conf_label.pack(side=tk.RIGHT, padx=5)
        
        # Trace var to update label
        self.conf_var.trace_add("write", self._update_conf_label)
        
        # Save/Close Buttons
        btn_frame = tk.Frame(main_frame, bg=self.theme.get("window_bg_color"))
        btn_frame.pack(fill=tk.X, pady=20)
        
        # Push to right
        tk.Frame(btn_frame, bg=self.theme.get("window_bg_color")).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        RoundedButton(btn_frame, text="Save", command=self.save_settings, width=80, height=30).pack(side=tk.LEFT, padx=5)
        RoundedButton(btn_frame, text="Cancel", command=self.destroy, width=80, height=30).pack(side=tk.LEFT, padx=5)

    def _update_conf_label(self, *args):
        self.conf_label.config(text=f"{self.conf_var.get():.2f}")

    def _load_values(self):
        # Load from project manager
        model = self.project_manager.get_setting("auto_label_model", "")
        conf = self.project_manager.get_setting("auto_label_confidence", 0.5)
        
        self.model_path_var.set(model)
        self.conf_var.set(float(conf))
        self._update_conf_label()

    def browse_model(self):
        path = filedialog.askopenfilename(filetypes=[("YOLO Model", "*.pt")])
        if path:
            self.model_path_var.set(path)

    def save_settings(self):
        self.project_manager.set_setting("auto_label_model", self.model_path_var.get())
        self.project_manager.set_setting("auto_label_confidence", self.conf_var.get())
        self.destroy()
