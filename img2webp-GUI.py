import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import sys
import subprocess
from pathlib import Path
import glob
import json


def get_webp_tools_path():
    """Get the path to the webp-tools directory"""
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = os.path.dirname(sys._MEIPASS)
        return os.path.join(bundle_dir, 'webp-tools')
    else:
        # Running in normal Python environment
        return 'webp-tools'


def get_img2webp_path():
    """Get the full path to img2webp executable"""
    tools_path = get_webp_tools_path()
    if sys.platform == 'darwin':  # macOS
        return os.path.join(tools_path, 'img2webp')
    else:  # Linux/Windows
        return 'img2webp'  # Assume it's in PATH


class Img2WebpGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image Sequence to WebP Animation")
        self.geometry("700x1024")

        # Define fonts
        self.header_font = ("Arial", 16, "bold")
        self.normal_font = ("Arial", 14)
        self.monospace_font = ("Courier", 16)

        # Container frame to limit width
        self.container = ctk.CTkFrame(self, width=600)
        self.container.pack(expand=True, fill="both", padx=10, pady=10)
        self.container.pack_propagate(False)  # Prevent frame from shrinking

        # Create main scrollable frame
        # self.main_frame = ctk.CTkScrollableFrame(self.container)
        self.main_frame = ctk.CTkFrame(self.container)
        self.main_frame.pack(fill="both", expand=True)

        # Add buttons for saving and loading config
        self.create_config_buttons()

        # Input/Output Selection
        self.create_io_frame()

        # File Level Options
        self.create_file_options_frame()

        # Frame Options
        self.create_frame_options_frame()

        # Command Display
        self.create_command_frame()

        # Output Log
        self.create_output_frame()

        # Initialize command
        self.update_command()

    def create_config_buttons(self):
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Configuration",
                     font=self.header_font).pack(anchor="w")

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(fill="x", pady=5)

        save_button = ctk.CTkButton(
            button_frame, text="Save Config", font=self.normal_font, command=self.save_config)
        save_button.pack(side="left", padx=5, pady=5)

        load_button = ctk.CTkButton(
            button_frame, text="Load Config", font=self.normal_font, command=self.load_config)
        load_button.pack(side="left", padx=5, pady=5)

    def save_config(self):
        config = {
            "input_dir": self.input_dir.get(),
            "glob_pattern": self.glob_pattern.get(),
            "output_dir": self.output_dir.get(),
            "output_prefix": self.output_prefix.get(),
            "min_size": self.min_size.get(),
            "mixed": self.mixed.get(),
            "sharp_yuv": self.sharp_yuv.get(),
            "kmax": self.kmax.get(),
            "kmin": self.kmin.get(),
            "near_lossless": self.near_lossless.get(),
            "loop": self.loop.get(),
            "lossless": self.lossless.get(),
            "exact": self.exact.get(),
            "duration": self.duration.get(),
            "quality": self.quality.get(),
            "method": self.method.get()
        }

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(config, f, indent=4)

    def load_config(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                config = json.load(f)

            self.input_dir.set(config.get("input_dir", ""))
            self.glob_pattern.set(config.get("glob_pattern", ""))
            self.output_dir.set(config.get("output_dir", ""))
            self.output_prefix.set(config.get("output_prefix", ""))
            self.min_size.set(config.get("min_size", False))
            self.mixed.set(config.get("mixed", False))
            self.sharp_yuv.set(config.get("sharp_yuv", False))
            self.kmax.set(config.get("kmax", 0))
            self.kmin.set(config.get("kmin", 0))
            self.near_lossless.set(config.get("near_lossless", 100))
            self.loop.set(config.get("loop", 0))
            self.lossless.set(config.get("lossless", True))
            self.exact.set(config.get("exact", False))
            self.duration.set(config.get("duration", 100))
            self.quality.set(config.get("quality", 75.0))
            self.method.set(config.get("method", 4))

            self.update_command()

    def create_io_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Input/Output Selection",
                     font=self.header_font).pack(anchor="w")

        # Input directory
        input_dir_frame = ctk.CTkFrame(frame)
        input_dir_frame.pack(fill="x", pady=2)
        self.input_dir = tk.StringVar(value=str(Path.home()))
        ctk.CTkLabel(input_dir_frame, text="Input Directory:",
                     font=self.normal_font).pack(side="left")
        ctk.CTkEntry(input_dir_frame, textvariable=self.input_dir,
                     width=400, font=self.normal_font).pack(side="left", padx=5)
        ctk.CTkButton(input_dir_frame, text="Browse", font=self.normal_font,
                      command=lambda: self.browse_directory(self.input_dir, start_dir=str(Path.home()))).pack(side="left")

        # Glob pattern
        glob_frame = ctk.CTkFrame(frame)
        glob_frame.pack(fill="x", pady=2)
        self.glob_pattern = tk.StringVar(value="*")
        ctk.CTkLabel(glob_frame, text="Glob Pattern:",
                     font=self.normal_font).pack(side="left")
        ctk.CTkEntry(glob_frame, textvariable=self.glob_pattern,
                     font=self.normal_font,
                     width=400).pack(side="left", padx=5)

        # Output directory
        output_dir_frame = ctk.CTkFrame(frame)
        output_dir_frame.pack(fill="x", pady=2)
        self.output_dir = tk.StringVar(value=str(Path.home()))
        ctk.CTkLabel(output_dir_frame,
                     text="Output Directory:",
                     font=self.normal_font).pack(side="left")
        ctk.CTkEntry(output_dir_frame, textvariable=self.output_dir,
                     font=self.normal_font,
                     width=400).pack(side="left", padx=5)
        ctk.CTkButton(output_dir_frame, text="Browse",
                      font=self.normal_font,
                      command=lambda: self.browse_directory(self.output_dir,
                                                            start_dir=self.input_dir.get())).pack(side="left")

        # Output prefix
        prefix_frame = ctk.CTkFrame(frame)
        prefix_frame.pack(fill="x", pady=2)
        self.output_prefix = tk.StringVar(value="output")
        ctk.CTkLabel(prefix_frame, text="Output Prefix:",
                     font=self.normal_font).pack(side="left")
        ctk.CTkEntry(prefix_frame, textvariable=self.output_prefix, font=self.normal_font,
                     width=400).pack(side="left", padx=5)

        # Bind variables to command update
        for var in [self.input_dir, self.glob_pattern, self.output_dir, self.output_prefix]:
            var.trace_add("write", lambda *args: self.update_command())

    def create_file_options_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="File Level Options",
                     font=self.header_font).pack(anchor="w")

        # Checkboxes
        self.min_size = tk.BooleanVar()
        self.mixed = tk.BooleanVar()
        self.sharp_yuv = tk.BooleanVar()

        checkbox_frame = ctk.CTkFrame(frame)
        checkbox_frame.pack(fill="x", pady=2)

        for var, text in [(self.min_size, "Minimize Size"),
                          (self.mixed, "Mixed Mode"),
                          (self.sharp_yuv, "Sharp YUV")]:
            cb = ctk.CTkCheckBox(checkbox_frame, text=text, font=self.normal_font, variable=var,
                                 command=self.update_command)
            cb.pack(side="left", padx=5)
        # Vertical space
        ctk.CTkLabel(checkbox_frame, text="").pack(pady=8)
        # Sliders with entry fields
        self.kmax = tk.IntVar(value=0)
        self.kmin = tk.IntVar(value=0)
        self.near_lossless = tk.IntVar(value=100)
        self.loop = tk.IntVar(value=0)

        for var, text, range_val in [
            (self.kmax, "Max frames between keyframes", (0, 100)),
            (self.kmin, "Min frames between keyframes", (0, 100)),
            (self.near_lossless, "Near Lossless", (0, 100)),
            (self.loop, "Loop Count", (0, 100))
        ]:
            self.create_slider_with_entry(frame, var, text, range_val)

    def create_frame_options_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Frame Options",
                     font=self.header_font).pack(anchor="w")

        # Checkboxes
        self.lossless = tk.BooleanVar(value=True)
        self.exact = tk.BooleanVar(value=False)

        checkbox_frame = ctk.CTkFrame(frame)
        checkbox_frame.pack(fill="x", pady=2)

        for var, text in [(self.lossless, "Lossless"),
                          (self.exact, "Exact")]:
            cb = ctk.CTkCheckBox(checkbox_frame, text=text, font=self.normal_font, variable=var,
                                 command=self.update_command)
            cb.pack(side="left", padx=5)
        # Vertical space
        ctk.CTkLabel(checkbox_frame, text="").pack(pady=8)
        # Sliders with entry fields
        self.duration = tk.IntVar(value=100)
        self.quality = tk.DoubleVar(value=75.0)
        self.method = tk.IntVar(value=4)

        self.create_slider_with_entry(
            frame, self.duration, "Duration (ms)", (0, 1000))
        self.create_slider_with_entry(frame, self.quality, "Quality", (0, 100))
        self.create_slider_with_entry(frame, self.method, "Method", (0, 6))

    def create_command_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Command",
                     font=self.header_font).pack(anchor="w")

        self.command_text = ctk.CTkTextbox(
            frame, height=80, font=self.monospace_font)
        self.command_text.pack(fill="x", pady=5)

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(fill="x", pady=5)

        self.execute_button = ctk.CTkButton(button_frame, text="Execute Command", font=self.normal_font,
                                            command=self.execute_command)
        self.execute_button.pack(side="left", padx=5)

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", font=self.normal_font,
                                           command=self.cancel_execution,
                                           fg_color="red", hover_color="darkred")
        self.cancel_button.pack(side="left", padx=5)
        self.cancel_button.configure(state="disabled")

        # Store process reference
        self.current_process = None

    def create_output_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(frame, text="Output Log",
                     font=self.header_font).pack(anchor="w")

        self.output_text = ctk.CTkTextbox(
            frame, height=180, font=self.monospace_font)
        self.output_text.pack(fill="x", pady=5)

    def create_slider_with_entry(self, parent, variable, text, range_val):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=2)

        ctk.CTkLabel(frame, text=text, font=self.normal_font).pack(
            side="left", padx=5)

        slider = ctk.CTkSlider(frame, from_=range_val[0], to=range_val[1],
                               variable=variable, command=self.update_command)
        slider.pack(side="left", expand=True, padx=5)

        entry = ctk.CTkEntry(
            frame, width=70, textvariable=variable, font=self.normal_font)
        entry.pack(side="left", padx=5)

        # Bind entry to update slider
        def validate_and_update(*args):
            try:
                value = float(variable.get())
                if range_val[0] <= value <= range_val[1]:
                    slider.set(value)
                    self.update_command()
            except ValueError:
                pass

        variable.trace_add("write", validate_and_update)

    def browse_directory(self, variable, start_dir=None):
        if start_dir is None or not os.path.exists(start_dir):
            start_dir = str(Path.home())

        directory = filedialog.askdirectory(initialdir=start_dir)
        if directory:
            variable.set(directory)

    def update_command(self, *args):
        try:
            cmd = [get_img2webp_path(), "-v"]  # Use the full path to img2webp

            # File level options
            if self.min_size.get():
                cmd.append("-min_size")
            if self.kmax.get() > 0:
                cmd.extend(["-kmax", str(self.kmax.get())])
            if self.kmin.get() > 0:
                cmd.extend(["-kmin", str(self.kmin.get())])
            if self.mixed.get():
                cmd.append("-mixed")
            if self.near_lossless.get() < 100:
                cmd.extend(["-near_lossless", str(self.near_lossless.get())])
            if self.sharp_yuv.get():
                cmd.append("-sharp_yuv")
            if self.loop.get() > 0:
                cmd.extend(["-loop", str(self.loop.get())])

            # Frame options
            cmd.extend(["-d", str(self.duration.get())])
            if self.lossless.get():
                cmd.append("-lossless")
            else:
                cmd.append("-lossy")
            cmd.extend(["-q", str(self.quality.get())])
            cmd.extend(["-m", str(self.method.get())])
            if self.exact.get():
                cmd.append("-exact")
            else:
                cmd.append("-noexact")

            # Input files
            input_pattern = os.path.join(
                self.input_dir.get(), self.glob_pattern.get())
            cmd.append(input_pattern)

            # Output file
            suffix_parts = []

            # File level options
            if self.min_size.get():
                suffix_parts.append("minsize")
            if self.kmax.get() > 0:
                suffix_parts.append(f"kmax{self.kmax.get()}")
            if self.kmin.get() > 0:
                suffix_parts.append(f"kmin{self.kmin.get()}")
            if self.mixed.get():
                suffix_parts.append("mixed")
            if self.near_lossless.get() < 100:
                suffix_parts.append(f"nl{self.near_lossless.get()}")
            if self.sharp_yuv.get():
                suffix_parts.append("sharp")
            if self.loop.get() > 0:
                suffix_parts.append(f"loop{self.loop.get()}")

            # Frame options
            suffix_parts.append(f"d{self.duration.get()}")
            suffix_parts.append("loss" if self.lossless.get()
                                else f"q{int(self.quality.get())}")
            suffix_parts.append(f"m{self.method.get()}")
            if self.exact.get():
                suffix_parts.append("exact")

            options_suffix = "_".join(suffix_parts)
            output_file = os.path.join(
                self.output_dir.get(),
                f"{self.output_prefix.get()}_{options_suffix}.webp"
            )
            cmd.extend(["-o", output_file])

            # Update command display
            self.command_text.delete("1.0", tk.END)
            self.command_text.insert("1.0", " ".join(cmd))

        except Exception as e:
            self.command_text.delete("1.0", tk.END)
            self.command_text.insert(
                "1.0", f"Error generating command: {str(e)}")

    def cancel_execution(self):
        if self.current_process:
            self.current_process.terminate()
            self.output_text.insert(
                tk.END, "\nCommand execution cancelled by user")
            self.execute_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            self.current_process = None

    def execute_command(self):
        command = self.command_text.get("1.0", tk.END).strip()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", f"Command to execute: {command}\n\n")

        try:
            # Split the command but keep the parts before the input pattern
            cmd_parts = command.split()
            input_pattern_idx = next(i for i, part in enumerate(cmd_parts)
                                     if '*' in part or '?' in part)

            # Get the base command and the output parts
            # Replace 'img2webp' with full path
            base_cmd = [get_img2webp_path()] + cmd_parts[1:input_pattern_idx]
            output_parts = cmd_parts[input_pattern_idx + 1:]

            # Expand the glob pattern
            input_pattern = cmd_parts[input_pattern_idx]
            input_files = sorted(glob.glob(input_pattern))

            if not input_files:
                self.output_text.insert(
                    tk.END, f"No files found matching pattern: {input_pattern}\n")
                return

            # Construct the final command
            final_cmd = base_cmd + input_files + output_parts

            self.output_text.insert(
                tk.END, f"Expanded command:\n{' '.join(final_cmd)}\n\n")

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_parts[-1])
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            self.current_process = subprocess.Popen(
                final_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            # Update button states
            self.execute_button.configure(state="disabled")
            self.cancel_button.configure(state="normal")

            while True:
                output = self.current_process.stdout.readline()
                if output == '' and self.current_process.poll() is not None:
                    break
                if output:
                    self.output_text.insert(tk.END, output)
                    self.output_text.see(tk.END)
                    self.update()

            return_code = self.current_process.poll()
            self.output_text.insert(
                tk.END, f"\nCommand completed with return code: {return_code}")

        except Exception as e:
            self.output_text.insert(
                tk.END, f"\nError executing command: {str(e)}")
        finally:
            # Reset button states
            self.execute_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            self.current_process = None


if __name__ == "__main__":
    app = Img2WebpGUI()
    app.mainloop()
