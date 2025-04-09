# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, time
import os
from typing import Optional, Callable

from models import CallSheet, Location, CastMember, CrewMember

class TimeInput(ttk.Frame):
    """Custom widget for time input"""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.hour_var = tk.StringVar()
        self.minute_var = tk.StringVar()
        
        # Create spinboxes for hour and minute
        self.hour_spinbox = ttk.Spinbox(self, from_=0, to=23, width=3, textvariable=self.hour_var)
        self.minute_spinbox = ttk.Spinbox(self, from_=0, to=59, width=3, textvariable=self.minute_var)
        
        # Add a separator
        self.hour_spinbox.pack(side=tk.LEFT, padx=(0, 0))
        ttk.Label(self, text=":").pack(side=tk.LEFT, padx=(0, 0))
        self.minute_spinbox.pack(side=tk.LEFT, padx=(0, 0))
        
        # Set default values
        self.hour_var.set("08")
        self.minute_var.set("00")
    
    def get_time(self) -> time:
        """Get time from spinboxes"""
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        return time(hour=hour, minute=minute)
    
    def set_time(self, t: time) -> None:
        """Set time in spinboxes"""
        self.hour_var.set(f"{t.hour:02d}")
        self.minute_var.set(f"{t.minute:02d}")

class CallSheetApp(tk.Tk):
    """Main application window"""
    def __init__(self):
        super().__init__()
        
        # Set application title and size
        self.title("Call Sheet Generator")
        self.geometry("800x600")
        
        # Initialize call sheet
        self.call_sheet = CallSheet(
            production_name="",
            production_date=datetime.now(),
            general_call_time=time(hour=7, minute=0)
        )
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tab frames
        self.production_frame = ProductionInfoFrame(self.notebook, self.call_sheet)
        self.locations_frame = LocationsFrame(self.notebook, self.call_sheet)
        self.cast_frame = CastFrame(self.notebook, self.call_sheet)
        self.crew_frame = CrewFrame(self.notebook, self.call_sheet)
        
        # Add tabs to notebook
        self.notebook.add(self.production_frame, text="Production Info")
        self.notebook.add(self.locations_frame, text="Locations")
        self.notebook.add(self.cast_frame, text="Cast")
        self.notebook.add(self.crew_frame, text="Crew")
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add buttons
        ttk.Button(self.buttons_frame, text="New Call Sheet", command=self.new_call_sheet).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Save", command=self.save_call_sheet).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Load", command=self.load_call_sheet).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Generate PDF", command=self.generate_pdf).pack(side=tk.RIGHT, padx=5)
    
    def new_call_sheet(self) -> None:
        """Create a new call sheet"""
        # Ask for confirmation if current sheet has data
        if self.call_sheet.cast_members or self.call_sheet.crew_members:
            if not messagebox.askyesno("New Call Sheet", "Are you sure you want to create a new call sheet? Any unsaved changes will be lost."):
                return
        
        # Create new call sheet
        self.call_sheet = CallSheet(
            production_name="",
            production_date=datetime.now(),
            general_call_time=time(hour=7, minute=0)
        )
        
        # Update tabs
        self.production_frame.update_fields()
        self.locations_frame.update_fields()
        self.cast_frame.update_list()
        self.crew_frame.update_list()
        
        messagebox.showinfo("New Call Sheet", "New call sheet created.")
    
    def save_call_sheet(self) -> None:
        """Save call sheet to file"""
        # Update call sheet from frames
        self.production_frame.save_to_call_sheet()
        self.locations_frame.save_to_call_sheet()
        
        # Validate call sheet
        if not self.call_sheet.production_name:
            messagebox.showerror("Save Error", "Production name is required.")
            return
        
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir="data"
        )
        
        if not filename:
            return
        
        # Save call sheet
        from data_manager import save_call_sheet
        if save_call_sheet(self.call_sheet, os.path.basename(filename)):
            messagebox.showinfo("Save Call Sheet", "Call sheet saved successfully.")
        else:
            messagebox.showerror("Save Error", "Failed to save call sheet.")
    
    def load_call_sheet(self) -> None:
        """Load call sheet from file"""
        # Ask for confirmation if current sheet has data
        if self.call_sheet.cast_members or self.call_sheet.crew_members:
            if not messagebox.askyesno("Load Call Sheet", "Are you sure you want to load a call sheet? Any unsaved changes will be lost."):
                return
        
        # Ask for filename
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir="data"
        )
        
        if not filename:
            return
        
        # Load call sheet
        from data_manager import load_call_sheet
        call_sheet = load_call_sheet(os.path.basename(filename))
        
        if call_sheet:
            self.call_sheet = call_sheet
            
            # Update tabs
            self.production_frame.update_fields()
            self.locations_frame.update_fields()
            self.cast_frame.update_list()
            self.crew_frame.update_list()
            
            messagebox.showinfo("Load Call Sheet", "Call sheet loaded successfully.")
        else:
            messagebox.showerror("Load Error", "Failed to load call sheet.")
    
    def generate_pdf(self) -> None:
        """Generate PDF from call sheet"""
        # Update call sheet from frames
        self.production_frame.save_to_call_sheet()
        self.locations_frame.save_to_call_sheet()
        
        # Validate call sheet
        if not self.call_sheet.production_name:
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
        messagebox.showinfo("Generate PDF", "PDF functionality will be implemented next.")

class ProductionInfoFrame(ttk.Frame):
    """Frame for production information"""
    def __init__(self, parent, call_sheet: CallSheet):
        super().__init__(parent)
        self.call_sheet = call_sheet
        
        # Create and place widgets
        ttk.Label(self, text="Production Information", font=("TkDefaultFont", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")
        
        # Production name
        ttk.Label(self, text="Production Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.production_name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.production_name_var, width=40).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Production date
        ttk.Label(self, text="Production Date:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_frame = ttk.Frame(self)
        self.date_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Month, day, year dropdowns
        self.month_var = tk.StringVar()
        self.day_var = tk.StringVar()
        self.year_var = tk.StringVar()
        
        ttk.Combobox(self.date_frame, textvariable=self.month_var, values=list(range(1, 13)), width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(self.date_frame, text="/").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(self.date_frame, textvariable=self.day_var, values=list(range(1, 32)), width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(self.date_frame, text="/").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(self.date_frame, textvariable=self.year_var, values=list(range(2023, 2031)), width=5).pack(side=tk.LEFT)
        
        # General call time
        ttk.Label(self, text="General Call Time:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.call_time_input = TimeInput(self)
        self.call_time_input.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Logo
        ttk.Label(self, text="Production Logo:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.logo_frame = ttk.Frame(self)
        self.logo_frame.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        self.logo_path_var = tk.StringVar()
        ttk.Entry(self.logo_frame, textvariable=self.logo_path_var, width=30).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.logo_frame, text="Browse...", command=self.browse_logo).pack(side=tk.LEFT)
        
        # Notes
        ttk.Label(self, text="Production Notes:").grid(row=5, column=0, padx=5, pady=5, sticky="nw")
        self.notes_text = tk.Text(self, width=40, height=5)
        self.notes_text.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        
        # Update fields with call sheet data
        self.update_fields()
    
    def update_fields(self) -> None:
        """Update fields with call sheet data"""
        self.production_name_var.set(self.call_sheet.production_name)
        
        # Set date values
        self.month_var.set(self.call_sheet.production_date.month)
        self.day_var.set(self.call_sheet.production_date.day)
        self.year_var.set(self.call_sheet.production_date.year)
        
        # Set call time
        self.call_time_input.set_time(self.call_sheet.general_call_time)
        
        # Set logo path
        self.logo_path_var.set(self.call_sheet.logo_path or "")
        
        # Set notes
        self.notes_text.delete("1.0", tk.END)
        if self.call_sheet.notes:
            self.notes_text.insert("1.0", self.call_sheet.notes)
    
    def save_to_call_sheet(self) -> None:
        """Save field values to call sheet"""
        self.call_sheet.production_name = self.production_name_var.get()
        
        # Get date from fields
        try:
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            year = int(self.year_var.get())
            self.call_sheet.production_date = datetime(year, month, day)
        except (ValueError, TypeError):
            messagebox.showerror("Date Error", "Invalid date.")
        
        # Get call time
        self.call_sheet.general_call_time = self.call_time_input.get_time()
        
        # Get logo path
        logo_path = self.logo_path_var.get()
        self.call_sheet.logo_path = logo_path if logo_path else None
        
        # Get notes
        notes = self.notes_text.get("1.0", tk.END).strip()
        self.call_sheet.notes = notes if notes else None
    
    def browse_logo(self) -> None:
        """Browse for logo file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")],
            initialdir="."
        )
        
        if filename:
            self.logo_path_var.set(filename)

class LocationsFrame(ttk.Frame):
    """Frame for locations information"""
    def __init__(self, parent, call_sheet: CallSheet):
        super().__init__(parent)
        self.call_sheet = call_sheet
        
        # Create and place widgets
        ttk.Label(self, text="Filming Locations", font=("TkDefaultFont", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")
        
        # Home base
        ttk.Label(self, text="Home Base", font=("TkDefaultFont", 12, "bold")).grid(row=1, column=0, columnspan=2, pady=(10, 5), sticky="w")
        
        # Home base name
        ttk.Label(self, text="Name:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.home_base_name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.home_base_name_var, width=40).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Home base address
        ttk.Label(self, text="Address:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.home_base_address_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.home_base_address_var, width=40).grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Home base notes
        ttk.Label(self, text="Notes:").grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        self.home_base_notes_text = tk.Text(self, width=40, height=3)
        self.home_base_notes_text.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Filming locations
        ttk.Label(self, text="Filming Locations (max. 3)", font=("TkDefaultFont", 12, "bold")).grid(row=5, column=0, columnspan=2, pady=(20, 5), sticky="w")
        
        # Filming locations notebook
        self.locations_notebook = ttk.Notebook(self)
        self.locations_notebook.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Create location frames
        self.location_frames = []
        for i in range(3):
            frame = ttk.Frame(self.locations_notebook)
            self.locations_notebook.add(frame, text=f"Location {i+1}")
            
            # Name
            ttk.Label(frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            name_var = tk.StringVar()
            ttk.Entry(frame, textvariable=name_var, width=40).grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            # Address
            ttk.Label(frame, text="Address:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            address_var = tk.StringVar()
            ttk.Entry(frame, textvariable=address_var, width=40).grid(row=1, column=1, padx=5, pady=5, sticky="w")
            
            # Notes
            ttk.Label(frame, text="Notes:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
            notes_text = tk.Text(frame, width=40, height=3)
            notes_text.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            
            self.location_frames.append({
                "frame": frame,
                "name_var": name_var,
                "address_var": address_var,
                "notes_text": notes_text
            })
        
        # Update fields with call sheet data
        self.update_fields()
    
    def update_fields(self) -> None:
        """Update fields with call sheet data"""
        # Set home base values
        if self.call_sheet.home_base:
            self.home_base_name_var.set(self.call_sheet.home_base.name)
            self.home_base_address_var.set(self.call_sheet.home_base.address)
            self.home_base_notes_text.delete("1.0", tk.END)
            if self.call_sheet.home_base.notes:
                self.home_base_notes_text.insert("1.0", self.call_sheet.home_base.notes)
        else:
            self.home_base_name_var.set("")
            self.home_base_address_var.set("")
            self.home_base_notes_text.delete("1.0", tk.END)
        
        # Set filming location values
        for i, location_frame in enumerate(self.location_frames):
            if i < len(self.call_sheet.filming_locations):
                location = self.call_sheet.filming_locations[i]
                location_frame["name_var"].set(location.name)
                location_frame["address_var"].set(location.address)
                location_frame["notes_text"].delete("1.0", tk.END)
                if location.notes:
                    location_frame["notes_text"].insert("1.0", location.notes)
            else:
                location_frame["name_var"].set("")
                location_frame["address_var"].set("")
                location_frame["notes_text"].delete("1.0", tk.END)
    
    def save_to_call_sheet(self) -> None:
        """Save field values to call sheet"""
        # Save home base
        home_base_name = self.home_base_name_var.get()
        home_base_address = self.home_base_address_var.get()
        
        if home_base_name and home_base_address:
            home_base_notes = self.home_base_notes_text.get("1.0", tk.END).strip()
            self.call_sheet.home_base = Location(
                name=home_base_name,
                address=home_base_address,
                notes=home_base_notes if home_base_notes else None
            )
        else:
            self.call_sheet.home_base = None
        
        # Save filming locations
        self.call_sheet.filming_locations = []
        
        for location_frame in self.location_frames:
            name = location_frame["name_var"].get()
            address = location_frame["address_var"].get()
            
            if name and address:
                notes = location_frame["notes_text"].get("1.0", tk.END).strip()
                self.call_sheet.add_filming_location(Location(
                    name=name,
                    address=address,
                    notes=notes if notes else None
                ))

class CastFrame(ttk.Frame):
    """Frame for cast information"""
    def __init__(self, parent, call_sheet: CallSheet):
        super().__init__(parent)
        self.call_sheet = call_sheet
        
        # Create and place widgets
        ttk.Label(self, text="Cast Members", font=("TkDefaultFont", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")
        
        # Cast list
        ttk.Label(self, text="Cast List:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        
        # Create treeview and scrollbar
        self.cast_tree_frame = ttk.Frame(self)
        self.cast_tree_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        self.cast_tree = ttk.Treeview(self.cast_tree_frame, columns=("name", "role", "call_time"), show="headings")
        self.cast_tree.heading("name", text="Name")
        self.cast_tree.heading("role", text="Role")
        self.cast_tree.heading("call_time", text="Call Time")
        
        self.cast_tree.column("name", width=150)
        self.cast_tree.column("role", width=150)
        self.cast_tree.column("call_time", width=80)
        
        self.cast_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.cast_tree_frame, orient=tk.VERTICAL, command=self.cast_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cast_tree.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        self.cast_button_frame = ttk.Frame(self)
        self.cast_button_frame.grid(row=2, column=1, padx=5, pady=5, sticky="e")
        
        ttk.Button(self.cast_button_frame, text="Add", command=self.add_cast_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.cast_button_frame, text="Edit", command=self.edit_cast_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.cast_button_frame, text="Remove", command=self.remove_cast_member).pack(side=tk.LEFT, padx=5)
        
        # Update cast list
        self.update_list()
    
    def update_list(self) -> None:
        """Update cast list with call sheet data"""
        # Clear treeview
        for item in self.cast_tree.get_children():
            self.cast_tree.delete(item)
        
        # Add cast members
        for cast_member in self.call_sheet.cast_members:
            self.cast_tree.insert("", tk.END, values=(
                cast_member.name,
                cast_member.role,
                cast_member.call_time.strftime("%H:%M")
            ))
    
    def add_cast_member(self) -> None:
        """Add a new cast member"""
        dialog = CastMemberDialog(self, "Add Cast Member")
        if dialog.result:
            self.call_sheet.add_cast_member(dialog.result)
            self.update_list()
    
    def edit_cast_member(self) -> None:
        """Edit selected cast member"""
        selected_item = self.cast_tree.selection()
        if not selected_item:
            messagebox.showerror("Edit Error", "No cast member selected.")
            return
        
        selected_index = self.cast_tree.index(selected_item[0])
        if selected_index >= 0 and selected_index < len(self.call_sheet.cast_members):
            cast_member = self.call_sheet.cast_members[selected_index]
            dialog = CastMemberDialog(self, "Edit Cast Member", cast_member)
            if dialog.result:
                self.call_sheet.cast_members[selected_index] = dialog.result
                self.update_list()
    
    def remove_cast_member(self) -> None:
        """Remove selected cast member"""
        selected_item = self.cast_tree.selection()
        if not selected_item:
            messagebox.showerror("Remove Error", "No cast member selected.")
            return
        
        selected_index = self.cast_tree.index(selected_item[0])
        if selected_index >= 0 and selected_index < len(self.call_sheet.cast_members):
            if messagebox.askyesno("Remove Cast Member", "Are you sure you want to remove this cast member?"):
                self.call_sheet.cast_members.pop(selected_index)
                self.update_list()

class CastMemberDialog(tk.Toplevel):
    """Dialog for adding/editing cast members"""
    def __init__(self, parent, title, cast_member: Optional[CastMember] = None):
        super().__init__(parent)
        
        self.result = None
        
        # Set dialog properties
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Create and place widgets
        ttk.Label(self, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self, text="Role:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.role_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.role_var, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self, text="Call Time:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.call_time_input = TimeInput(self)
        self.call_time_input.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self, text="Notes:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        self.notes_text = tk.Text(self, width=30, height=3)
        self.notes_text.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="OK", command=self.save).pack(side=tk.LEFT, padx=5)
        
        # Set initial values if editing
        if cast_member:
            self.name_var.set(cast_member.name)
            self.role_var.set(cast_member.role)
            self.call_time_input.set_time(cast_member.call_time)
            if cast_member.notes:
                self.notes_text.insert("1.0", cast_member.notes)
        
        # Center dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make dialog modal
        self.wait_window(self)
    
    def save(self) -> None:
        """Save dialog values and close"""
        name = self.name_var.get()
        role = self.role_var.get()
        
        if not name:
            messagebox.showerror("Input Error", "Name is required.")
            return
        
        if not role:
            messagebox.showerror("Input Error", "Role is required.")
            return
        
        call_time = self.call_time_input.get_time()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        self.result = CastMember(
            name=name,
            role=role,
            call_time=call_time,
            notes=notes if notes else None
        )
        
        self.destroy()

class CrewFrame(ttk.Frame):
    """Frame for crew information"""
    def __init__(self, parent, call_sheet: CallSheet):
        super().__init__(parent)
        self.call_sheet = call_sheet
        
        # Create and place widgets
        ttk.Label(self, text="Crew Members", font=("TkDefaultFont", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")
        
        # Department selection
        ttk.Label(self, text="Department:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.department_frame = ttk.Frame(self)
        self.department_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.department_var = tk.StringVar()
        self.department_combobox = ttk.Combobox(self.department_frame, textvariable=self.department_var, width=20)
        self.department_combobox.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(self.department_frame, text="New Department", command=self.add_department).pack(side=tk.LEFT)
        
        # Crew list
        ttk.Label(self, text="Crew List:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        
        # Create treeview and scrollbar
        self.crew_tree_frame = ttk.Frame(self)
        self.crew_tree_frame.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        
        self.crew_tree = ttk.Treeview(self.crew_tree_frame, columns=("name", "position", "department", "call_time"), show="headings")
        self.crew_tree.heading("name", text="Name")
        self.crew_tree.heading("position", text="Position")
        self.crew_tree.heading("department", text="Department")
        self.crew_tree.heading("call_time", text="Call Time")
        
        self.crew_tree.column("name", width=150)
        self.crew_tree.column("position", width=150)
        self.crew_tree.column("department", width=100)
        self.crew_tree.column("call_time", width=80)
        
        self.crew_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.crew_tree_frame, orient=tk.VERTICAL, command=self.crew_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.crew_tree.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        self.crew_button_frame = ttk.Frame(self)
        self.crew_button_frame.grid(row=3, column=1, padx=5, pady=5, sticky="e")
        
        ttk.Button(self.crew_button_frame, text="Add", command=self.add_crew_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.crew_button_frame, text="Edit", command=self.edit_crew_member).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.crew_button_frame, text="Remove", command=self.remove_crew_member).pack(side=tk.LEFT, padx=5)
        
        # Update crew list and departments
        self.update_departments()
        self.update_list()
        
        # Bind event for department change
        self.department_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_by_department())
    
    def update_departments(self) -> None:
        """Update department list"""
        departments = self.call_sheet.get_departments()
        self.department_combobox["values"] = ["All Departments"] + departments
        
        # Set to "All Departments" if not already set
        if not self.department_var.get() or self.department_var.get() not in departments:
            self.department_var.set("All Departments")
    
    def update_list(self) -> None:
        """Update crew list with call sheet data"""
        # Clear treeview
        for item in self.crew_tree.get_children():
            self.crew_tree.delete(item)
        
        # Filter by department
        department = self.department_var.get()
        crew_members = self.call_sheet.crew_members
        
        if department != "All Departments":
            crew_members = [crew for crew in crew_members if crew.department == department]
        
        # Add crew members
        for crew_member in crew_members:
            self.crew_tree.insert("", tk.END, values=(
                crew_member.name,
                crew_member.position,
                crew_member.department,
                crew_member.call_time.strftime("%H:%M")
            ))
    
    def filter_by_department(self) -> None:
        """Filter crew list by selected department"""
        self.update_list()
    
    def add_department(self) -> None:
        """Add a new department"""
        dialog = DepartmentDialog(self, "Add Department")
        if dialog.result:
            # Update department list
            departments = self.call_sheet.get_departments()
            if dialog.result not in departments:
                self.department_combobox["values"] = self.department_combobox["values"] + (dialog.result,)
            
            # Select new department
            self.department_var.set(dialog.result)
            self.filter_by_department()
    
    def add_crew_member(self) -> None:
        """Add a new crew member"""
        # Get current department selection
        department = self.department_var.get()
        if department == "All Departments":
            department = None
        
        dialog = CrewMemberDialog(self, "Add Crew Member", department=department)
        if dialog.result:
            self.call_sheet.add_crew_member(dialog.result)
            self.update_departments()
            self.update_list()
    
    def edit_crew_member(self) -> None:
        """Edit selected crew member"""
        selected_item = self.crew_tree.selection()
        if not selected_item:
            messagebox.showerror("Edit Error", "No crew member selected.")
            return
        
        # Find selected crew member
        selected_values = self.crew_tree.item(selected_item[0], "values")
        selected_name = selected_values[0]
        selected_department = selected_values[2]
        
        # Find crew member in call sheet
        for i, crew_member in enumerate(self.call_sheet.crew_members):
            if crew_member.name == selected_name and crew_member.department == selected_department:
                dialog = CrewMemberDialog(self, "Edit Crew Member", crew_member=crew_member)
                if dialog.result:
                    self.call_sheet.crew_members[i] = dialog.result
                    self.update_departments()
                    self.update_list()
                break
    
    def remove_crew_member(self) -> None:
        """Remove selected crew member"""
        selected_item = self.crew_tree.selection()
        if not selected_item:
            messagebox.showerror("Remove Error", "No crew member selected.")
            return
        
        # Find selected crew member
        selected_values = self.crew_tree.item(selected_item[0], "values")
        selected_name = selected_values[0]
        selected_department = selected_values[2]
        
        # Find crew member in call sheet
        for i, crew_member in enumerate(self.call_sheet.crew_members):
            if crew_member.name == selected_name and crew_member.department == selected_department:
                if messagebox.askyesno("Remove Crew Member", "Are you sure you want to remove this crew member?"):
                    self.call_sheet.crew_members.pop(i)
                    self.update_departments()
                    self.update_list()
                break

class DepartmentDialog(tk.Toplevel):
    """Dialog for adding departments"""
    def __init__(self, parent, title):
        super().__init__(parent)
        
        self.result = None
        
        # Set dialog properties
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Create and place widgets
        ttk.Label(self, text="Department Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.department_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.department_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="OK", command=self.save).pack(side=tk.LEFT, padx=5)
        
        # Center dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make dialog modal
        self.wait_window(self)
    
    def save(self) -> None:
        """Save dialog values and close"""
        department = self.department_var.get()
        
        if not department:
            messagebox.showerror("Input Error", "Department name is required.")
            return
        
        self.result = department
        self.destroy()

class CrewMemberDialog(tk.Toplevel):
    """Dialog for adding/editing crew members"""
    def __init__(self, parent, title, crew_member: Optional[CrewMember] = None, department: Optional[str] = None):
        super().__init__(parent)
        
        self.result = None
        
        # Set dialog properties
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Create and place widgets
        ttk.Label(self, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self, text="Position:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.position_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.position_var, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self, text="Department:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.department_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.department_var, width=30).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self, text="Call Time:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.call_time_input = TimeInput(self)
        self.call_time_input.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self, text="Notes:").grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        self.notes_text = tk.Text(self, width=30, height=3)
        self.notes_text.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="OK", command=self.save).pack(side=tk.LEFT, padx=5)
        
        # Set initial values if editing
        if crew_member:
            self.name_var.set(crew_member.name)
            self.position_var.set(crew_member.position)
            self.department_var.set(crew_member.department)
            self.call_time_input.set_time(crew_member.call_time)
            if crew_member.notes:
                self.notes_text.insert("1.0", crew_member.notes)
        elif department:
            self.department_var.set(department)
        
        # Center dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make dialog modal
        self.wait_window(self)
    
    def save(self) -> None:
        """Save dialog values and close"""
        name = self.name_var.get()
        position = self.position_var.get()
        department = self.department_var.get()
        
        if not name:
            messagebox.showerror("Input Error", "Name is required.")
            return
        
        if not position:
            messagebox.showerror("Input Error", "Position is required.")
            return
        
        if not department:
            messagebox.showerror("Input Error", "Department is required.")
            return
        
        call_time = self.call_time_input.get_time()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        self.result = CrewMember(
            name=name,
            position=position,
            department=department,
            call_time=call_time,
            notes=notes if notes else None
        )
        
        self.destroy()
