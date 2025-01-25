import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sort import sort_files
from compress_images import compress_images
from compress_audio import compress_audio
from compress_documents import compress_documents
from compress_videos import compress_videos
from compress_other import compress_other
from PIL import Image, ImageTk

class FoxoCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FoxyCompressor")
        self.root.geometry("500x550")
        self.root.minsize(500, 550)
        self.root.resizable(True, True)
        self.style = ttk.Style(theme='darkly')
        
        # Initialize progress window attribute
        self.progress_window = None

        # Set rounded corners (Windows only)
        try:
            self.root.attributes('-transparentcolor', '#f0f0f0')
            self.root.wm_attributes('-transparentcolor', '#f0f0f0')
        except:
            pass

        # Setup background canvas
        self.bg_canvas = tk.Canvas(root, highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Background image setup
        self.bg_image = None
        self.bg_image_tk = None  # Holds the PhotoImage reference
        self.bg_image_id = None
        self.load_background_image()
        
        # Main container frame
        self.main_frame = ttk.Frame(self.bg_canvas)
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.input_folder = ""
        self.output_folder = ""
        self.running = False

        self.create_widgets()
        self.setup_responsive_grid()

        # Set window icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "assets", "foxycompressor.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

    def load_background_image(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            bg_path = os.path.join(base_path, "assets", "background.png")
            print(f"Loading background from: {bg_path}")  # Debug path
            if not os.path.exists(bg_path):
                raise FileNotFoundError(f"Background image not found at {bg_path}")
            
            self.pil_image = Image.open(bg_path)
            self.bg_image_tk = ImageTk.PhotoImage(self.pil_image)
            self.bg_canvas.bind("<Configure>", self.resize_background)
            self.resize_background(None)  # Initial resize
        except Exception as e:
            print(f"Background image error: {e}")

    def resize_background(self, event):
        if hasattr(self, 'pil_image'):
            try:
                # Get current canvas dimensions
                w = self.root.winfo_width()
                h = self.root.winfo_height()
                
                if w <= 0 or h <= 0:
                    return  # Avoid invalid dimensions

                # Calculate aspect ratio-preserving dimensions
                canvas_ratio = w / h
                img_ratio = self.pil_image.width / self.pil_image.height

                if canvas_ratio > img_ratio:
                    # Canvas is wider than image - fit to width
                    new_width = w
                    new_height = int(new_width / img_ratio)
                else:
                    # Canvas is taller than image - fit to height
                    new_height = h
                    new_width = int(new_height * img_ratio)

                # Resize with high-quality downsampling
                resized_img = self.pil_image.resize(
                    (new_width, new_height),
                    Image.Resampling.LANCZOS
                )
                self.bg_image_tk = ImageTk.PhotoImage(resized_img)

                # Update canvas image
                self.bg_canvas.delete(self.bg_image_id)
                self.bg_image_id = self.bg_canvas.create_image(
                    w//2, h//2,
                    image=self.bg_image_tk,
                    anchor=tk.CENTER
                )
            except Exception as e:
                print(f"Error resizing background: {e}")

    def setup_responsive_grid(self):
        """Configure grid weights for responsive layout"""
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.columnconfigure(2, weight=1)
        for i in range(6):
            self.main_frame.rowconfigure(i, weight=1)

    def create_widgets(self):
        """Create and arrange UI widgets"""
        # Load logo
        base_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_path, "assets", "foxycompressor.png")
        self.fox_image = tk.PhotoImage(file=logo_path).subsample(6)

        # Logo display
        image_label = ttk.Label(self.main_frame, image=self.fox_image)
        image_label.grid(row=0, column=0, columnspan=3, pady=(20, 10))

        # Input Folder Section
        ttk.Label(self.main_frame, text="Input Folder:", 
                font=('Helvetica', 10, 'bold')).grid(
                    row=1, column=0, padx=10, pady=10, sticky=tk.E)
        self.input_entry = ttk.Entry(self.main_frame, width=35)
        self.input_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)
        ttk.Button(self.main_frame, text="Browse", 
                 command=self.browse_input, style='primary.TButton').grid(
                     row=1, column=2, padx=10, pady=10, sticky=tk.W)

        # Output Folder Section
        ttk.Label(self.main_frame, text="Output Folder:", 
                font=('Helvetica', 10, 'bold')).grid(
                    row=2, column=0, padx=10, pady=10, sticky=tk.E)
        self.output_entry = ttk.Entry(self.main_frame, width=35)
        self.output_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)
        ttk.Button(self.main_frame, text="Browse", 
                 command=self.browse_output, style='primary.TButton').grid(
                     row=2, column=2, padx=10, pady=10, sticky=tk.W)

        # Start/Abort Button
        self.start_button = ttk.Button(
            self.main_frame, 
            text="Start", 
            command=self.start_process,
            style='success.TButton',
            width=10
        )
        self.start_button.grid(row=3, column=1, pady=20)

        # Configure grid weights
        self.main_frame.columnconfigure(1, weight=1)

    def browse_input(self):
        """Browse for input folder"""
        self.input_folder = filedialog.askdirectory()
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, self.input_folder)

    def browse_output(self):
        """Browse for output folder"""
        self.output_folder = filedialog.askdirectory()
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, self.output_folder)

    def start_process(self):
        """Start or abort the compression process"""
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        if self.running:
            self.running = False
            self.start_button.config(text="Start")
            return

        self.running = True
        self.start_button.config(text="Abort")
        self.open_progress_window()
        threading.Thread(target=self.run_process, daemon=True).start()

    def open_progress_window(self):
        """Create and configure progress window with safe checks"""
        if not hasattr(self, 'progress_window') or \
           self.progress_window is None or \
           not self.progress_window.winfo_exists():
            
            self.progress_window = tk.Toplevel(self.root)
            self.progress_window.title("Foxy Progress and Logs")
            self.progress_window.geometry("600x400")
            self.progress_window.minsize(400, 300)
            # Set window icon
            base_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_path, "assets", "foxycompressor.ico")
            if os.path.exists(icon_path):
                self.progress_window.iconbitmap(icon_path)
            
            # Configure grid
            self.progress_window.columnconfigure(0, weight=1)
            self.progress_window.rowconfigure(1, weight=1)
            
            # Progress label
            self.progress_label = ttk.Label(
                self.progress_window, 
                text="Starting...",
                font=('Helvetica', 10, 'bold'),
                anchor=tk.CENTER
            )
            self.progress_label.grid(row=0, column=0, pady=10, sticky=tk.EW)
            
            # Progress bar
            self.progress_bar = ttk.Progressbar(
                self.progress_window, 
                orient=HORIZONTAL, 
                mode='determinate',
                style='success.Striped.Horizontal.TProgressbar'
            )
            self.progress_bar.grid(row=1, column=0, padx=20, pady=10, sticky=tk.NSEW)
            
            # Log text area
            self.log_text = tk.Text(
                self.progress_window, 
                height=10,
                bg='#303030',
                fg='white',
                insertbackground='white',
                wrap=tk.WORD
            )
            self.log_text.grid(row=2, column=0, padx=10, pady=10, sticky=tk.NSEW)

    def update_progress(self, message, value=None):
        """Update progress window with new messages"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_label.config(text=message)
            if value is not None:
                self.progress_bar['value'] = value
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.progress_window.update_idletasks()

    def run_process(self):
        """Main processing function"""
        try:
            # Step 1: Sort files
            self.update_progress("Sorting files...")
            sorted_files = sort_files(self.input_folder, self.output_folder)
            self.update_progress("Files sorted.", 10)

            # Step 2: Compress images
            self.update_progress("Compressing images...")
            compress_images(self.output_folder, self.update_progress)
            self.update_progress("Images compressed.", 30)

            # Step 3: Compress audio
            self.update_progress("Compressing audio...")
            compress_audio(sorted_files['audio'], self.output_folder, self.update_progress)
            self.update_progress("Audio compressed.", 50)

            # Step 4: Compress documents
            self.update_progress("Compressing documents...")
            compress_documents(sorted_files['documents'], self.output_folder, self.update_progress)
            self.update_progress("Documents compressed.", 70)

            # Step 5: Compress videos
            self.update_progress("Compressing videos...")
            compress_videos(sorted_files['videos'], self.output_folder, self.update_progress)
            self.update_progress("Videos compressed.", 90)

            # Step 6: Compress other files
            self.update_progress("Compressing other files...")
            compress_other(sorted_files['other'], self.output_folder, self.update_progress)
            self.update_progress("Other files compressed.", 100)

            self.update_progress("Process completed successfully.")
        except Exception as e:
            self.update_progress(f"Error: {str(e)}")
        finally:
            self.running = False
            self.start_button.config(text="Start")

if __name__ == "__main__":
    root = ttk.Window(themename='darkly')
    app = FoxoCompressorApp(root)
    root.mainloop()
