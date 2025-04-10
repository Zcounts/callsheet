# main.py
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import importlib.util

# Add the directory containing this script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# List of required packages
REQUIRED_PACKAGES = [
    "reportlab",
    "pillow"
]

# Replace the check_dependencies function in main.py with this:
def check_dependencies():
    """
    Check if required packages are installed and warn if missing
    """
    try:
        # Try to import the packages directly, which is more reliable
        import reportlab
        import PIL  # Pillow will be available as PIL
        return True
    except ImportError as e:
        missing_package = str(e).split("'")[-2]
        messagebox.showerror(
            "Missing Dependencies",
            f"The required package '{missing_package}' is missing.\n\n"
            f"Please install it manually using pip:\n"
            f"pip install {missing_package}"
        )
        return False

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
