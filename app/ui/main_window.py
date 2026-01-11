import tkinter as tk
from app.core.project_manager import ProjectManager
from app.ui.project_view import ProjectView
from app.ui.labeling_tool import LabelingTool
from app.ui.organized_labeling import OrganizedLabelingTool
from app.ui.training_view import TrainingView
from app.ui.inference_view import InferenceView
from app.ui.augmentation_view import AugmentationView
from app.ui.components import RoundedButton
from app.core.theme_manager import ThemeManager

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Trainer/Tester")
        self.root.geometry("1200x800")
        
        self.theme = ThemeManager()
        self.root.configure(bg=self.theme.get("window_bg_color"))

        self.project_manager = ProjectManager()
        
        self.main_container = tk.Frame(self.root, bg=self.theme.get("window_bg_color"))
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.nav_bar = tk.Frame(self.root, bg=self.theme.get("window_bg_color"), height=40)
        # Don't pack nav bar yet, only show after project loaded

        self.views = {}
        self.current_view = None

        self.show_project_view()

    def show_project_view(self):
        self.clear_view()
        self.nav_bar.pack_forget()
        self.views["project"] = ProjectView(self.main_container, self.project_manager, on_project_loaded=self.on_project_loaded)

    def on_project_loaded(self):
        self.setup_nav_bar()
        self.show_view("labeling")

    def setup_nav_bar(self):
        self._setup_menu()
        
        self.nav_bar.pack(side=tk.TOP, fill=tk.X)
        
        # Clear existing buttons if any
        for widget in self.nav_bar.winfo_children():
            widget.destroy()

        buttons = [
            ("Labeling", "labeling"),
            ("Training", "training"),
            ("Inference", "inference"),
            ("Augmentation", "augmentation"),
            ("Project", "project_settings") 
        ]

        for text, view_name in buttons:
            btn = RoundedButton(self.nav_bar, text=text, command=lambda v=view_name: self.show_view(v), 
                                width=100, height=30)
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Add project name label
        tk.Label(self.nav_bar, text=f"Project: {self.project_manager.project_config.get('name')}", 
                 bg=self.theme.get("window_bg_color"), fg=self.theme.get("window_text_color"), 
                 font=(self.theme.get("font_family"), int(self.theme.get("font_size_normal")))).pack(side=tk.RIGHT, padx=10)

    def _setup_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        jiet_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="JIET", menu=jiet_menu)
        jiet_menu.add_command(label="Settings", command=self.show_settings)
        
    def show_settings(self):
        from app.ui.settings_window import SettingsWindow
        SettingsWindow(self.root, self.project_manager)


    def show_view(self, view_name):
        self.clear_view()

        if view_name == "project_settings":
            # For now just go back to project selection, or we could have a settings page
            # Let's go back to project selection for simplicity to switch projects
            self.show_project_view()
            return

        if view_name == "labeling":
            self.views[view_name] = OrganizedLabelingTool(self.main_container, self.project_manager)
        elif view_name == "training":
            self.views[view_name] = TrainingView(self.main_container, self.project_manager)
        elif view_name == "inference":
            self.views[view_name] = InferenceView(self.main_container, self.project_manager)
        elif view_name == "augmentation":
            self.views[view_name] = AugmentationView(self.main_container, self.project_manager)
        if view_name == "project_settings":
            # For now just go back to project selection, or we could have a settings page
            # Let's go back to project selection for simplicity to switch projects
            self.show_project_view()
            return
        
        self.views[view_name].pack(fill=tk.BOTH, expand=True)
        self.current_view = self.views[view_name]

    def clear_view(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
