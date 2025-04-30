import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys
from main import process_files


class MBTIGUI:
    def __init__(self, master):
        self.master = master
        master.title("MBTI Processor")
        master.geometry("600x220")
        master.configure(bg='#f0f0f0')  # Set background color

        # Set the theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # You can try different themes like 'alt', 'default', 'classic'

        # Customize styles
        self.style.configure('TButton', padding=6, relief="flat", background="#ccc")
        self.style.configure('TLabel', padding=6, background="#f0f0f0")
        self.style.configure('TEntry', padding=6)

        # Get the project root directory
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # Input Directory
        ttk.Label(master, text="Input Directory:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.input_dir = tk.StringVar(value="F:/projects/MBTInfo/input")
        ttk.Entry(master, textvariable=self.input_dir, width=50).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(master, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=10, pady=5)

        # Output Directory
        ttk.Label(master, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.output_dir = tk.StringVar(value="F:/projects/MBTInfo/output")
        ttk.Entry(master, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(master, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=10, pady=5)

        # Output File Name
        ttk.Label(master, text="Output File Name:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.output_file = tk.StringVar(value="MBTI_Results.xlsx")
        ttk.Entry(master, textvariable=self.output_file, width=50).grid(row=2, column=1, padx=10, pady=5)

        # Process Button
        ttk.Button(master, text="Process Files", command=self.process).grid(row=3, column=1, pady=20)

    def browse_input(self):
        directory = filedialog.askdirectory()
        self.input_dir.set(directory)

    def browse_output(self):
        directory = filedialog.askdirectory()
        self.output_dir.set(directory)

    def custom_dialog(self, title, message):
        dialog = tk.Toplevel(self.master)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.grab_set()

        ttk.Label(dialog, text=message, wraplength=250).pack(pady=10)

        result = tk.StringVar()

        ttk.Button(dialog, text="Overwrite", command=lambda: result.set("overwrite")).pack(side=tk.LEFT, padx=10)
        ttk.Button(dialog, text="New Version", command=lambda: result.set("new_version")).pack(side=tk.LEFT, padx=10)
        ttk.Button(dialog, text="Cancel", command=lambda: result.set("cancel")).pack(side=tk.LEFT, padx=10)

        dialog.wait_variable(result)
        dialog.destroy()
        return result.get()

    def process(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        output_filename = self.output_file.get()

        if not input_dir or not output_dir or not output_filename:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if not output_filename.endswith('.xlsx'):
            output_filename += '.xlsx'

        output_path = os.path.join(output_dir, output_filename)
        textfiles_dir = os.path.join(self.project_root, 'output', 'textfiles')

        if os.path.exists(output_path):
            response = self.custom_dialog("File Exists", 
                "The output file already exists. What would you like to do?")
            
            if response == "cancel":
                return
            elif response == "new_version":
                base, ext = os.path.splitext(output_filename)
                counter = 1
                while os.path.exists(output_path):
                    new_filename = f"{base}_{counter}{ext}"
                    output_path = os.path.join(output_dir, new_filename)
                    counter += 1
                output_filename = os.path.basename(output_path)

        try:
            process_files(input_dir, output_dir, output_filename, textfiles_dir)
            messagebox.showinfo("Success", f"Processing complete. Results saved to {output_path}")
            
            # Ask if the user wants to open the file
            if messagebox.askyesno("Open File", "Would you like to open the file?"):
                try:
                    os.startfile(output_path)  # For Windows
                except AttributeError:
                    # For non-Windows systems
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, output_path])
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


def run_gui():
    root = tk.Tk()
    gui = MBTIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()