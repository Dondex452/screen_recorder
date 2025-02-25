import tkinter as tk
from tkinter import ttk, colorchooser
import threading
from recorder import Recorder
import tkinter.messagebox as messagebox

class RegionSelector:
    def __init__(self, callback):
        """Initialize region selector.
        
        Args:
            callback: Function to call with selected region (left, top, right, bottom)
        """
        self.callback = callback
        self.start_x = None
        self.start_y = None
        
        # Create transparent fullscreen window
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3, '-fullscreen', True)
        self.root.configure(bg='grey')
        
        # Create canvas for drawing selection rectangle
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        
        # Bind escape to cancel
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        self.rect_id = None
        
    def on_press(self, event):
        """Handle mouse press."""
        self.start_x = event.x
        self.start_y = event.y
        
    def on_drag(self, event):
        """Handle mouse drag."""
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            event.x, event.y,
            outline='red',
            width=2
        )
        
    def on_release(self, event):
        """Handle mouse release."""
        if self.start_x is not None and self.start_y is not None:
            left = min(self.start_x, event.x)
            top = min(self.start_y, event.y)
            right = max(self.start_x, event.x)
            bottom = max(self.start_y, event.y)
            
            self.root.destroy()
            self.callback((left, top, right, bottom))

class ScreenRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Screen Recorder")
        self.recorder = Recorder()
        self.recording = False
        self.annotation_position = None
        self.selected_region = None  # Add this to track region
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Style config
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TFrame', padding=5)
        style.configure('TLabelframe', padding=5)

    def on_close(self):
        if self.recording:
            self.stop_recording()
        self.root.destroy()

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

        
    def setup_ui(self):
        """Set up the user interface."""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Capture Settings Frame
        capture_frame = ttk.LabelFrame(main_frame, text="Capture Settings", padding="5")
        capture_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Capture mode selection
        ttk.Label(capture_frame, text="Capture Mode:").grid(row=0, column=0, padx=5, pady=5)
        self.capture_mode = tk.StringVar(value="Full Screen")
        mode_combo = ttk.Combobox(
            capture_frame,
            textvariable=self.capture_mode,
            values=["Full Screen", "Custom Region"],
            state="readonly"
        )
        mode_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        # Region selection button (initially hidden)
        self.region_button = ttk.Button(
            capture_frame,
            text="Select Region",
            command=self.start_region_selection
        )
        self.region_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.region_button.grid_remove()
        
        # Recording Controls Frame
        control_frame = ttk.LabelFrame(main_frame, text="Recording Controls", padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Record button
        self.record_button = ttk.Button(
            control_frame,
            text="Start Recording",
            command=self.toggle_recording,
            style='TButton'
        )
        self.record_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Audio toggle
        self.record_audio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            control_frame,
            text="Record Audio",
            variable=self.record_audio_var
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Annotation Frame
        annotation_frame = ttk.LabelFrame(main_frame, text="Text Annotations", padding="5")
        annotation_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Annotation text
        ttk.Label(annotation_frame, text="Text:").grid(row=0, column=0, padx=5, pady=2)
        self.annotation_text = tk.StringVar()
        ttk.Entry(annotation_frame, textvariable=self.annotation_text).grid(
            row=0, column=1, columnspan=3, padx=5, pady=2, sticky=(tk.W, tk.E)
        )
        
        # Font size
        ttk.Label(annotation_frame, text="Size:").grid(row=1, column=0, padx=5, pady=2)
        self.font_scale = tk.DoubleVar(value=1.0)
        ttk.Spinbox(
            annotation_frame,
            from_=0.5,
            to=3.0,
            increment=0.1,
            textvariable=self.font_scale,
            width=5
        ).grid(row=1, column=1, padx=5, pady=2)
        
        # Color pickers
        self.text_color = (255, 255, 255)  # Default: white
        color_button = ttk.Button(
            annotation_frame,
            text="Text Color",
            command=self.choose_color
        )
        color_button.grid(row=1, column=2, padx=5, pady=2)
        
        self.bg_color = None
        bg_color_button = ttk.Button(
            annotation_frame,
            text="Background",
            command=self.choose_bg_color
        )
        bg_color_button.grid(row=1, column=3, padx=5, pady=2)
        
        # Add/Remove buttons
        ttk.Button(
            annotation_frame,
            text="Add Annotation",
            command=self.add_annotation
        ).grid(row=2, column=0, columnspan=2, padx=5, pady=2)
        
        ttk.Button(
            annotation_frame,
            text="Clear All",
            command=self.clear_annotations
        ).grid(row=2, column=2, columnspan=2, padx=5, pady=2)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        # Click position label
        self.position_label = ttk.Label(status_frame, text="Click position for annotation: None")
        self.position_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Bind click event for annotation position
        self.root.bind('<Button-1>', self.on_click)
        
    def on_mode_change(self, event=None):
        """Handle capture mode change."""
        mode = self.capture_mode.get()
        
        # Hide all optional widgets first
        self.region_button.grid_remove()
        
        if mode == "Custom Region":
            self.region_button.grid()
            
    def start_region_selection(self):
        """Start the region selection process."""
        self.root.withdraw()  # Hide main window
        RegionSelector(self.on_region_selected)
        
    def on_region_selected(self, region):
        """Handle selected region."""
        self.root.deiconify()  # Show main window
        self.selected_region = region
        self.status_label.configure(
            text=f"Selected region: {region}"
        )
        
    def on_click(self, event):
        """Fix annotation positioning relative to screen"""
        # Add check to ignore clicks during recording
        if self.recording:
            return
        
        # Get screen coordinates properly
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        
        self.annotation_position = (x, y)
        self.position_label.configure(
            text=f"Click position for annotation: ({x}, {y})"
        )
            
    def choose_color(self):
        """Open color picker for text color."""
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[0]:  # color is ((R,G,B), #RRGGBB)
            self.text_color = tuple(map(int, color[0]))
            
    def choose_bg_color(self):
        """Open color picker for background color."""
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[0]:  # color is ((R,G,B), #RRGGBB)
            self.bg_color = tuple(map(int, color[0]))
        else:
            self.bg_color = None
            
    def add_annotation(self):
        """Add text annotation at the clicked position."""
        if not self.annotation_position:
            messagebox.showwarning("Warning", "Click somewhere to set annotation position")
            return
            
        text = self.annotation_text.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter annotation text")
            return
            
        self.recorder.add_annotation(
            text=text,
            position=self.annotation_position,
            color=self.text_color,
            font_scale=self.font_scale.get(),
            background_color=self.bg_color
        )
        self.status_label.configure(text=f"Added annotation: {text}")
        
    def clear_annotations(self):
        """Remove all annotations."""
        self.recorder.clear_annotations()
        self.status_label.configure(text="Cleared all annotations")
        
    def get_capture_settings(self):
        """Get current capture settings based on mode."""
        mode = self.capture_mode.get()
        
        if mode == "Custom Region":
            if not hasattr(self, 'selected_region'):
                messagebox.showwarning("Warning", "Please select a region")
                return None
            return {
                'region': self.selected_region
            }
        else:  # Full Screen
            return {
                'region': None
            }
            
    def toggle_recording(self):
        """Toggle recording state."""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start screen recording."""
        settings = self.get_capture_settings()
        if settings is None:
            return

        # Minimize instead of withdraw to keep system tray icon
        self.root.iconify()
        
        try:
            self.recording = True
            self.record_button.configure(text="Stop Recording")
            self.status_label.configure(text="Recording...")
            
            # Start recording in a separate thread
            threading.Thread(
                target=lambda: self.recorder.start_recording(**settings),
                daemon=True
            ).start()
        except Exception as e:
            self.recording = False
            self.root.deiconify()
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")

    def stop_recording(self):
        """Stop screen recording."""
        if not self.recording:
            return

        self.recording = False
        self.status_label.configure(text="Saving recording...")
        
        def save_recording():
            try:
                video_path = self.recorder.stop_recording()
                if video_path:
                    self.status_label.configure(text=f"Saved to: {video_path}")
                else:
                    raise Exception("Failed to save recording")
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}")
            finally:
                self.root.deiconify()
                self.record_button.configure(text="Start Recording")
                
        threading.Thread(target=save_recording, daemon=True).start()

def main():
    """Main entry point for the screen recorder application."""
    root = tk.Tk()
    root.title("PC Screen Recorder")
    app = ScreenRecorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
