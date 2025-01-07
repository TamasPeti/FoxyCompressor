import os
import shutil
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

class FoxoCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FoxyCompressor")
        self.root.geometry("500x550")
        self.style = ttk.Style(theme='darkly')
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "assets", "foxycompressor.ico")
        self.root.iconbitmap(icon_path)

        self.input_folder = ""
        self.output_folder = ""
        self.running = False

        self.create_widgets()


    def create_widgets(self):
        # Load and display the image
        base_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
        logo_path = os.path.join(base_path, "assets", "foxycompressor.png")  # Append the relative path to the image
        self.fox_image = tk.PhotoImage(file=logo_path)

        # Resize the image so it fucking fits
        self.fox_image = self.fox_image.subsample(6)  # Adjust subsample factor to resize (e.g., 2 for half size)

        # Display the image at the top
        image_label = ttk.Label(self.root, image=self.fox_image)
        image_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)  # Span across all columns

        # Input Folder
        ttk.Label(self.root, text="Input Folder:").grid(row=1, column=0, padx=10, pady=10)
        self.input_entry = ttk.Entry(self.root, width=40)
        self.input_entry.grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(self.root, text="Browse", command=self.browse_input).grid(row=1, column=2, padx=10, pady=10)

        # Output Folder
        ttk.Label(self.root, text="Output Folder:").grid(row=2, column=0, padx=10, pady=10)
        self.output_entry = ttk.Entry(self.root, width=40)
        self.output_entry.grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(self.root, text="Browse", command=self.browse_output).grid(row=2, column=2, padx=10, pady=10)

        # Start/Abort Button
        self.start_button = ttk.Button(self.root, text="Start", command=self.start_process)
        self.start_button.grid(row=3, column=1, padx=10, pady=20)

        # Progress Window
        self.progress_window = None

    def browse_input(self):
        self.input_folder = filedialog.askdirectory()
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, self.input_folder)

    def browse_output(self):
        self.output_folder = filedialog.askdirectory()
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, self.output_folder)

    def start_process(self):
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        if self.running:
            self.running = False
            self.start_button.config(text="Start")
            return

        self.running = True
        self.start_button.config(text="Abort")

        # Open progress window
        self.open_progress_window()

        # Run the process in a separate thread
        threading.Thread(target=self.run_process, daemon=True).start()

    def open_progress_window(self):
        if self.progress_window is None or not self.progress_window.winfo_exists():
            self.progress_window = tk.Toplevel(self.root)
            self.progress_window.title("Progress")
            self.progress_window.geometry("400x200")

            self.progress_label = ttk.Label(self.progress_window, text="Starting...")
            self.progress_label.pack(pady=10)

            self.progress_bar = ttk.Progressbar(self.progress_window, orient=HORIZONTAL, length=300, mode='determinate')
            self.progress_bar.pack(pady=10)

            self.log_text = tk.Text(self.progress_window, height=10, width=50)
            self.log_text.pack(pady=10)

    def update_progress(self, message, value=None):
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_label.config(text=message)
            if value is not None:
                self.progress_bar['value'] = value
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.progress_window.update_idletasks()

    def run_process(self):
        try:
            # Step 1: Sort files
            self.update_progress("Sorting files...")
            sorted_files = sort_files(self.input_folder, self.output_folder)
            self.update_progress("Files sorted.")

            # Step 2: Compress images
            self.update_progress("Compressing images...")
            compress_images(self.output_folder, self.update_progress)  # Only 2 arguments now
            self.update_progress("Images compressed.")

            # Step 3: Compress audio
            self.update_progress("Compressing audio...")
            compress_audio(sorted_files['audio'], self.output_folder, self.update_progress)
            self.update_progress("Audio compressed.")

            # Step 4: Compress documents
            self.update_progress("Compressing documents...")
            compress_documents(sorted_files['documents'], self.output_folder, self.update_progress)
            self.update_progress("Documents compressed.")

            # Step 5: Compress videos
            self.update_progress("Compressing videos...")
            compress_videos(sorted_files['videos'], self.output_folder, self.update_progress)
            self.update_progress("Videos compressed.")

            # Step 6: Compress other files
            self.update_progress("Compressing other files...")
            compress_other(sorted_files['other'], self.output_folder, self.update_progress)
            self.update_progress("Other files compressed.")

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
