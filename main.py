# main.py
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import importlib.util

# List of required packages
REQUIRED_PACKAGES = [
    "reportlab",
    "pillow"
]

def check_dependencies():
    """
    Check if required packages are installed and install them if missing
    """
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        packages_str = ", ".join(missing_packages)
        install_response = messagebox.askyesno(
            "Missing Dependencies",
            f"The following required packages are missing: {packages_str}\n\n"
            f"Would you like to automatically install them now?\n"
            f"(This may take a moment)"
        )
        
        if install_response:
            try:
                import subprocess
                import sys
                
                # Create a simple progress window
                progress_window = tk.Toplevel()
                progress_window.title("Installing Dependencies")
                progress_window.geometry("300x100")
                
                # Add progress message
                tk.Label(progress_window, text=f"Installing: {packages_str}...").pack(pady=10)
                progress = ttk.Progressbar(progress_window, mode="indeterminate")
                progress.pack(fill=tk.X, padx=20, pady=10)
                progress.start()
                progress_window.update()
                
                # Install packages using pip
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
                
                # Close progress window
                progress_window.destroy()
                
                messagebox.showinfo("Installation Complete", "Required packages were successfully installed.")
                return True
            except Exception as e:
                messagebox.showerror(
                    "Installation Failed",
                    f"Failed to install dependencies: {str(e)}\n\n"
                    f"Please install them manually using pip:\n"
                    f"pip install {' '.join(missing_packages)}"
                )
                return False
        else:
            messagebox.showinfo(
                "Installation Required",
                f"Please install the missing packages manually before running the application:\n"
                f"pip install {' '.join(missing_packages)}"
            )
            return False
    
    return True

def main():
    """
    Main entry point for the Call Sheet Generator application
    """
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Create resources directory if it doesn't exist
    os.makedirs("resources", exist_ok=True)
    
    try:
        # Import application components
        from gui import CallSheetApp
        from pdf_generator import generate_call_sheet_pdf, preview_call_sheet
        
        # Create the application
        app = CallSheetApp()
        
        # Connect PDF generation functionality
        def new_generate_pdf():
            # Update call sheet from frames
            app.production_frame.save_to_call_sheet()
            app.locations_frame.save_to_call_sheet()
            
            # Validate call sheet
            if not app.call_sheet.production_name:
                messagebox.showerror("PDF Error", "Production name is required.")
                return
            
            # Ask for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialdir="."
            )
            
            if not filename:
                return
            
            # Generate PDF
            if generate_call_sheet_pdf(app.call_sheet, filename):
                messagebox.showinfo("Generate PDF", "Call sheet PDF generated successfully.")
                
                # Ask if user wants to open the PDF
                if messagebox.askyesno("Open PDF", "Do you want to open the generated PDF?"):
                    import platform
                    import subprocess
                    
                    # Open PDF with default viewer
                    if platform.system() == 'Windows':
                        os.startfile(filename)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', filename])
                    else:  # Linux
                        subprocess.call(['xdg-open', filename])
            else:
                messagebox.showerror("PDF Error", "Failed to generate PDF.")
        
        # Replace the generate_pdf method
        app.generate_pdf = new_generate_pdf
        
        # Add preview functionality
        def preview_pdf():
            # Update call sheet from frames
            app.production_frame.save_to_call_sheet()
            app.locations_frame.save_to_call_sheet()
            
            # Validate call sheet
            if not app.call_sheet.production_name:
                messagebox.showerror("Preview Error", "Production name is required.")
                return
            
            # Preview call sheet
            preview_call_sheet(app.call_sheet)
        
        # Add preview button
        ttk.Button(app.buttons_frame, text="Preview", command=preview_pdf).pack(side=tk.RIGHT, padx=5)
        
        # Run the application
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Application Error", f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
