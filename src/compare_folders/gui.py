import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

from .core import NOW, compare


class App(tk.Tk):
    def __init__(
        self,
        source: str,
        destination: str,
        output_file: str = f"compare-folders_{NOW}.md",
    ):
        super().__init__()
        self.title("Compare Folders")
        self.geometry("600x400")

        self.source_dir = tk.StringVar(value=source)
        self.dest_dir = tk.StringVar(value=destination)
        self.output_file = tk.StringVar(value=output_file)

        self.create_widgets()

    def create_widgets(self):
        # Frame for directory selection
        dir_frame = tk.Frame(self)
        dir_frame.pack(fill="x", padx=10, pady=5)

        # Source directory
        tk.Label(dir_frame, text="Source Directory:").pack(side="left")
        tk.Entry(dir_frame, textvariable=self.source_dir, width=50).pack(
            side="left", expand=True, fill="x"
        )
        tk.Button(dir_frame, text="Browse...", command=self.browse_source).pack(side="left")

        # Destination directory
        dest_frame = tk.Frame(self)
        dest_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(dest_frame, text="Destination Directory:").pack(side="left")
        tk.Entry(dest_frame, textvariable=self.dest_dir, width=50).pack(
            side="left", expand=True, fill="x"
        )
        tk.Button(dest_frame, text="Browse...", command=self.browse_dest).pack(side="left")

        # Output file
        output_frame = tk.Frame(self)
        output_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(output_frame, text="Output File:").pack(side="left")
        tk.Entry(output_frame, textvariable=self.output_file, width=50).pack(
            side="left", expand=True, fill="x"
        )
        tk.Button(output_frame, text="Generate", command=self.generate_output_filename).pack(
            side="left"
        )

        # Run button
        run_button = tk.Button(self, text="Run Comparison", command=self.run_comparison)
        run_button.pack(pady=10)

        # Open output file button
        self.open_output_button = tk.Button(
            self, text="Open Output File", command=self.open_output_file, state="disabled"
        )
        self.open_output_button.pack(pady=5)

        # Status text
        self.status_text = tk.Text(self, height=10)
        self.status_text.pack(fill="both", expand=True, padx=10, pady=5)

    def browse_source(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.source_dir.set(dirname)

    def browse_dest(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.dest_dir.set(dirname)

    def generate_output_filename(self):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_file.set(f"compare-folders_{now}.md")
        self.open_output_button.config(state="disabled")

    def open_output_file(self):
        output_file_path = self.output_file.get()
        try:
            if sys.platform == "win32":
                os.startfile(output_file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", output_file_path], check=True)
            else:
                subprocess.run(["xdg-open", output_file_path], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def run_comparison(self):
        source = self.source_dir.get()
        dest = self.dest_dir.get()
        output = self.output_file.get()

        if not source or not dest:
            messagebox.showerror("Error", "Source and destination directories are required.")
            return

        from pathlib import Path

        if Path(output).exists():
            messagebox.showerror("Error", f"Output file already exists: {output}")
            return

        source_path = Path(source)
        dest_path = Path(dest)

        if not source_path.exists() or not source_path.is_dir():
            messagebox.showerror("Error", f"Source directory not found: {source}")
            return
        if not dest_path.exists() or not dest_path.is_dir():
            messagebox.showerror("Error", f"Destination directory not found: {dest}")
            return

        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, "Running comparison...\n")
        self.open_output_button.config(state="disabled")
        self.update_idletasks()

        try:
            stats = compare(
                source_path,
                dest_path,
                output,
                False,
                False,
            )
            self.status_text.insert(tk.END, "Comparison finished.\n\n")
            self.status_text.insert(tk.END, "Stats:\n")
            for k, v in stats.items():
                self.status_text.insert(tk.END, f"{k}: {v}\n")
            self.status_text.insert(tk.END, f"\nReport saved to: {output}\n")
            self.open_output_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status_text.insert(tk.END, f"An error occurred: {e}\n")
