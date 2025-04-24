import tkinter as tk
from tkinter import filedialog, messagebox
import os
from main import process_files


class MBTIGUI:
    def __init__(self, master):
        self.master = master
        master.title("MBTI Processor")
        master.geometry("500x300")

        # Input Directory
        tk.Label(master, text="Input Directory:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.input_dir = tk.StringVar()
        tk.Entry(master, textvariable=self.input_dir, width=50).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(master, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=10, pady=5)

        # Output Directory
        tk.Label(master, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.output_dir = tk.StringVar()
        tk.Entry(master, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(master, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=10, pady=5)

        # Output File Name
        tk.Label(master, text="Output File Name:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.output_file = tk.StringVar(value="MBTI_Results.xlsx")
        tk.Entry(master, textvariable=self.output_file, width=50).grid(row=2, column=1, padx=10, pady=5)

        # Process Button
        tk.Button(master, text="Process Files", command=self.process).grid(row=3, column=1, pady=20)

    def browse_input(self):
        directory = filedialog.askdirectory()
        self.input_dir.set(directory)

    def browse_output(self):
        directory = filedialog.askdirectory()
        self.output_dir.set(directory)

    def process(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        output_file = self.output_file.get()

        if not input_dir or not output_dir or not output_file:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if not output_file.endswith('.xlsx'):
            output_file += '.xlsx'

        try:
            process_files(input_dir, output_dir, output_file)
            messagebox.showinfo("Success", f"Processing complete. Results saved to {os.path.join(output_dir, output_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


def run_gui():
    root = tk.Tk()
    gui = MBTIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()