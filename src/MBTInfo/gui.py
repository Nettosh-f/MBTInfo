import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys
import threading
from main import process_files
from personal_report import generate_personal_report


class MBTIGUI:
    def __init__(self, master):
        self.personal_input_file = None
        self.personal_output_dir = None
        self.personal_output_file = None
        self.dual_first_input_file = None
        self.dual_second_input_file = None
        self.dual_output_dir = None
        self.dual_output_file = None
        self.output_file = None
        self.output_dir = None
        self.input_dir = None
        self.master = master
        master.title("MBTI Processor")
        master.geometry("650x300")  # Increased height to accommodate tabs
        master.configure(bg='#f0f0f0')  # Set background color

        # Set the theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # You can try different themes like 'alt', 'default', 'classic'

        # Customize styles
        self.style.configure('TButton', padding=6, relief="flat", background="#ccc")
        self.style.configure('TLabel', padding=6, background="#f0f0f0")
        self.style.configure('TEntry', padding=6)
        self.style.configure('TNotebook', background="#f0f0f0")
        self.style.configure('TNotebook.Tab', padding=[12, 4], background="#e0e0e0")
        self.style.map('TNotebook.Tab', background=[('selected', '#f0f0f0')])

        # Get the project root directory
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        input_dir_var = os.path.join(self.project_root, "input")
        output_dir_var = os.path.join(self.project_root, "output")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.group_tab = ttk.Frame(self.notebook, style='TFrame')
        self.personal_tab = ttk.Frame(self.notebook, style='TFrame')
        self.dual_tab = ttk.Frame(self.notebook, style='TFrame')

        # Add tabs to notebook
        self.notebook.add(self.group_tab, text="Group PDF")
        self.notebook.add(self.personal_tab, text="Personal PDF")
        self.notebook.add(self.dual_tab, text="Couple PDF")

        # Setup Group Report Tab (default)
        self.setup_group_tab(input_dir_var, output_dir_var)

        # Setup Personal Report Tab
        self.setup_personal_tab(input_dir_var, output_dir_var)

        # Setup Dual Report Tab
        self.setup_dual_tab(input_dir_var, output_dir_var)

    def setup_group_tab(self, input_dir_var, output_dir_var):
        # Input Directory
        ttk.Label(self.group_tab, text="Select Input Folder:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.input_dir = tk.StringVar(value=input_dir_var)
        ttk.Entry(self.group_tab, textvariable=self.input_dir, width=50).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self.group_tab, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=10, pady=5)

        # Output Directory
        ttk.Label(self.group_tab, text="Select Output Folder:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.output_dir = tk.StringVar(value=output_dir_var)
        ttk.Entry(self.group_tab, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(self.group_tab, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=10, pady=5)

        # Output File Name
        ttk.Label(self.group_tab, text="Output File Name:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.output_file = tk.StringVar(value="MBTI_Results.xlsx")
        ttk.Entry(self.group_tab, textvariable=self.output_file, width=50).grid(row=2, column=1, padx=10, pady=5)

        # Process Button
        ttk.Button(self.group_tab, text="Process Files", command=self.process).grid(row=3, column=1, pady=20)

    def setup_personal_tab(self, input_dir_var, output_dir_var):
        # Input PDF File
        ttk.Label(self.personal_tab, text="Select Input PDF:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.personal_input_file = tk.StringVar()
        ttk.Entry(self.personal_tab, textvariable=self.personal_input_file, width=50).grid(row=0, column=1, padx=10,
                                                                                           pady=5)
        ttk.Button(self.personal_tab, text="Browse", command=self.browse_personal_input).grid(row=0, column=2, padx=10,
                                                                                              pady=5)

        # Output Directory
        ttk.Label(self.personal_tab, text="Select Output Folder:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.personal_output_dir = tk.StringVar(value=output_dir_var)
        ttk.Entry(self.personal_tab, textvariable=self.personal_output_dir, width=50).grid(row=1, column=1, padx=10,
                                                                                           pady=5)
        ttk.Button(self.personal_tab, text="Browse", command=self.browse_personal_output).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

        # Output File Name
        ttk.Label(self.personal_tab, text="Select Output File Name:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.personal_output_file = tk.StringVar(value="Personal_MBTI_Report.xlsx")
        ttk.Entry(self.personal_tab, textvariable=self.personal_output_file, width=50).grid(row=2, column=1, padx=10,
                                                                                            pady=5)

        # Process Button
        ttk.Button(self.personal_tab, text="Generate Personal Report", command=self.process_personal).grid(row=3,
                                                                                                           column=1,
                                                                                                           pady=20)

    def setup_dual_tab(self, input_dir_var, output_dir_var):
        # First Input PDF File
        ttk.Label(self.dual_tab, text="First PDF File:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.dual_first_input_file = tk.StringVar()
        ttk.Entry(self.dual_tab, textvariable=self.dual_first_input_file, width=50).grid(row=0, column=1, padx=10,
                                                                                         pady=5)
        ttk.Button(self.dual_tab, text="Browse", command=self.browse_dual_first_input).grid(row=0, column=2, padx=10,
                                                                                            pady=5)

        # Second Input PDF File
        ttk.Label(self.dual_tab, text="Second PDF File:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.dual_second_input_file = tk.StringVar()
        ttk.Entry(self.dual_tab, textvariable=self.dual_second_input_file, width=50).grid(row=1, column=1, padx=10,
                                                                                          pady=5)
        ttk.Button(self.dual_tab, text="Browse", command=self.browse_dual_second_input).grid(row=1, column=2, padx=10,
                                                                                             pady=5)

        # Output Directory
        ttk.Label(self.dual_tab, text="Output Directory:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.dual_output_dir = tk.StringVar(value=output_dir_var)
        ttk.Entry(self.dual_tab, textvariable=self.dual_output_dir, width=50).grid(row=2, column=1, padx=10, pady=5)
        ttk.Button(self.dual_tab, text="Browse", command=self.browse_dual_output).grid(row=2, column=2, padx=10, pady=5)

        # Output File Name
        ttk.Label(self.dual_tab, text="Output File Name:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.dual_output_file = tk.StringVar(value="Dual_MBTI_Report.xlsx")
        ttk.Entry(self.dual_tab, textvariable=self.dual_output_file, width=50).grid(row=3, column=1, padx=10, pady=5)

        # Process Button
        ttk.Button(self.dual_tab, text="Generate Dual Report", command=self.process_dual).grid(row=4, column=1, pady=20)

    def browse_input(self):
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir.set(directory)

    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def browse_personal_input(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.personal_input_file.set(file_path)
            # Auto-set output filename based on input filename
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            self.personal_output_file.set(f"{name_without_ext}_Report.xlsx")

    def browse_personal_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.personal_output_dir.set(directory)

    def browse_dual_first_input(self):
        file_path = filedialog.askopenfilename(
            title="Select First PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.dual_first_input_file.set(file_path)
            self.update_dual_output_filename()

    def browse_dual_second_input(self):
        file_path = filedialog.askopenfilename(
            title="Select Second PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.dual_second_input_file.set(file_path)
            self.update_dual_output_filename()

    def update_dual_output_filename(self):
        # Update the output filename based on the two selected files
        first_file = self.dual_first_input_file.get()
        second_file = self.dual_second_input_file.get()

        if first_file and second_file:
            first_name = os.path.splitext(os.path.basename(first_file))[0]
            second_name = os.path.splitext(os.path.basename(second_file))[0]
            self.dual_output_file.set(f"{first_name}_vs_{second_name}_Report.xlsx")

    def browse_dual_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dual_output_dir.set(directory)

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

        # Show loading animation
        loading_window, progress_bar = self.show_loading_animation(
            title="Processing Files",
            message="Processing MBTI files. This may take a few moments..."
        )

        # Define the processing function
        def process_thread():
            try:
                workbook = process_files(input_dir, output_dir, output_filename, textfiles_dir)

                # Ensure proper sheet ordering
                try:
                    from chart_creator import reorder_sheets
                    import openpyxl as xl
                    workbook = xl.load_workbook(output_path)
                    reorder_sheets(workbook)
                    workbook.save(output_path)
                except Exception as sheet_error:
                    # Log the specific error but continue execution
                    print(f"Warning: Could not reorder sheets: {str(sheet_error)}")

                # Close the loading window
                self.master.after(0, loading_window.destroy)

                # Show success message
                self.master.after(100, lambda: messagebox.showinfo("Success",
                                                                   f"Processing complete. Results saved to {output_path}"))

                # Ask if the user wants to open the file
                def ask_open_file():
                    if messagebox.askyesno("Open File", "Would you like to open the file?"):
                        try:
                            os.startfile(output_path)  # For Windows
                        except AttributeError:
                            # For non-Windows systems
                            opener = "open" if sys.platform == "darwin" else "xdg-open"
                            subprocess.call([opener, output_path])

                self.master.after(200, ask_open_file)

            except Exception as e:
                # Close the loading window
                self.master.after(0, loading_window.destroy)

                # Add more detailed error information
                import traceback
                error_details = traceback.format_exc()
                print(f"Error details: {error_details}")

                # Check if the file was created despite the error
                if os.path.exists(output_path):
                    def show_partial_success():
                        if messagebox.askyesno("Partial Success",
                                               f"The file was created but there were some formatting errors.\n\n"
                                               f"Would you like to open the file anyway?"):
                            try:
                                os.startfile(output_path)  # For Windows
                            except AttributeError:
                                # For non-Windows systems
                                opener = "open" if sys.platform == "darwin" else "xdg-open"
                                subprocess.call([opener, output_path])

                    self.master.after(100, show_partial_success)
                else:
                    self.master.after(100, lambda: messagebox.showerror("Error",
                                                                        f"An error occurred: {str(e)}\n\nPlease check the console for more details."))

        # Start the processing thread
        threading.Thread(target=process_thread, daemon=True).start()

    def process_personal(self):
        input_file = self.personal_input_file.get()
        output_dir = self.personal_output_dir.get()
        output_filename = self.personal_output_file.get()

        if not input_file or not output_dir or not output_filename:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist.")
            return

        if not output_filename.endswith('.xlsx'):
            output_filename += '.xlsx'

        output_path = os.path.join(output_dir, output_filename)

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

        # Show loading animation
        loading_window, progress_bar = self.show_loading_animation(
            title="Processing Personal Report",
            message="Generating personal MBTI report. Please wait..."
        )

        def process_thread():
            try:
                # Create textfiles directory if it doesn't exist
                textfiles_dir = os.path.join(self.project_root, 'output', 'textfiles')
                os.makedirs(textfiles_dir, exist_ok=True)

                # Generate the personal report
                final_output_path = generate_personal_report(input_file, output_dir, output_filename)

                # Close the loading window
                self.master.after(0, loading_window.destroy)

                # Show success message
                self.master.after(100, lambda: messagebox.showinfo("Success",
                                                                   f"Personal MBTI report generated successfully!\n\nSaved to: {final_output_path}"))

                # Open the generated file
                def open_file():
                    if os.path.exists(final_output_path):
                        try:
                            os.startfile(final_output_path)  # For Windows
                        except AttributeError:
                            # For non-Windows systems
                            opener = "open" if sys.platform == "darwin" else "xdg-open"
                            subprocess.call([opener, final_output_path])

                self.master.after(200, open_file)

            except Exception as e:
                # Close the loading window
                self.master.after(0, loading_window.destroy)

                # Add more detailed error information
                import traceback
                error_details = traceback.format_exc()
                print(f"Error details: {error_details}")

                self.master.after(100, lambda: messagebox.showerror("Error",
                                                                    f"An error occurred: {str(e)}\n\nPlease check the console for more details."))

        # Start the processing thread
        threading.Thread(target=process_thread, daemon=True).start()

    def process_dual(self):
        first_input_file = self.dual_first_input_file.get()
        second_input_file = self.dual_second_input_file.get()
        output_dir = self.dual_output_dir.get()
        output_filename = self.dual_output_file.get()

        if not first_input_file or not second_input_file or not output_dir or not output_filename:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if not os.path.exists(first_input_file):
            messagebox.showerror("Error", "First input file does not exist.")
            return

        if not os.path.exists(second_input_file):
            messagebox.showerror("Error", "Second input file does not exist.")
            return

        if first_input_file == second_input_file:
            messagebox.showerror("Error", "Please select two different files.")
            return

        if not output_filename.endswith('.xlsx'):
            output_filename += '.xlsx'

        output_path = os.path.join(output_dir, output_filename)

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

        # Show loading animation
        loading_window, progress_bar = self.show_loading_animation(
            title="Processing Dual Report",
            message="Generating dual MBTI comparison report. Please wait..."
        )

        def process_thread():
            try:
                # Create textfiles directory if it doesn't exist
                textfiles_dir = os.path.join(self.project_root, 'output', 'textfiles')
                os.makedirs(textfiles_dir, exist_ok=True)

                # TODO: Implement dual report generation
                # For now, just simulate processing time
                import time
                time.sleep(2)  # Simulate processing time

                # Close the loading window
                self.master.after(0, loading_window.destroy)

                # Show not implemented message
                first_name = os.path.basename(first_input_file)
                second_name = os.path.basename(second_input_file)
                self.master.after(100, lambda: messagebox.showinfo("Not Implemented",
                                                                   f"Dual report generation for {first_name} and {second_name} is not yet implemented."))

            except Exception as e:
                # Close the loading window
                self.master.after(0, loading_window.destroy)

                # Add more detailed error information
                import traceback
                error_details = traceback.format_exc()
                print(f"Error details: {error_details}")

                self.master.after(100, lambda: messagebox.showerror("Error",
                                                                    f"An error occurred: {str(e)}\n\nPlease check the console for more details."))

        # Start the processing thread
        threading.Thread(target=process_thread, daemon=True).start()

    def show_loading_animation(self, title="Processing", message="Please wait..."):
        """
        Shows a loading window with a progress bar
        Returns the loading window and progress bar objects
        """
        # Create a new toplevel window
        loading_window = tk.Toplevel(self.master)
        loading_window.title(title)
        loading_window.geometry("300x180")
        loading_window.resizable(False, False)
        loading_window.grab_set()  # Make it modal

        # Remove window decorations for cleaner look
        loading_window.overrideredirect(True)

        # Center the window
        loading_window.update_idletasks()
        width = loading_window.winfo_width()
        height = loading_window.winfo_height()
        x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
        y = (loading_window.winfo_screenheight() // 2) - (height // 2)
        loading_window.geometry(f'{width}x{height}+{x}+{y}')

        # Add a frame with border
        frame = ttk.Frame(loading_window, padding=10)
        frame.pack(fill='both', expand=True)

        # Add message
        ttk.Label(frame, text=message, wraplength=250).pack(pady=10)

        # Add progress bar
        progress = ttk.Progressbar(frame, mode='indeterminate', length=250)
        progress.pack(pady=10)
        progress.start(10)  # Start the animation

        # Add a cancel button
        cancel_button = ttk.Button(frame, text="Cancel", command=loading_window.destroy)
        cancel_button.pack(pady=5)

        # Force update the window to show immediately
        loading_window.update()

        return loading_window, progress

def run_gui():
    root = tk.Tk()
    gui = MBTIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
