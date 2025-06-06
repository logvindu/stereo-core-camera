#!/usr/bin/env python3
"""
Tkinter UI demo for the Stereo Core Camera System.
This version uses built-in tkinter and works on all Python installations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class StereoCoreCameraDemo:
    """Demo of the stereo core camera interface using tkinter."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stereo Core Camera System - UI Demo")
        self.root.geometry("900x800")
        self.root.configure(bg='#f0f0f0')
        self.root.minsize(800, 700)
        
        # Current values
        self.current_depth_from = 0.0
        self.current_depth_to = 0.5
        
        self.setup_ui()
        # Don't log immediately - wait for UI to be ready
        self.root.after(100, lambda: self.log_status("UI Demo started - Mock mode"))
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main container with scrollable canvas
        canvas = tk.Canvas(self.root, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main content frame
        main_frame = tk.Frame(scrollable_frame, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Input section
        self.create_input_section(main_frame)
        
        # Preview section
        self.create_preview_section(main_frame)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
        # Status section
        self.create_status_section(main_frame)
        
    def create_header(self, parent):
        """Create header section."""
        header_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            header_frame, 
            text="Stereo Core Camera System",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#333',
            pady=15
        )
        title_label.pack()
        
    def create_input_section(self, parent):
        """Create input fields section."""
        input_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        title_label = tk.Label(input_frame, text="Project Information", font=('Arial', 14, 'bold'), bg='white', fg='#333')
        title_label.pack(pady=(15, 10))
        
        # Input container
        container = tk.Frame(input_frame, bg='white')
        container.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Project name
        proj_frame = tk.Frame(container, bg='white')
        proj_frame.pack(fill=tk.X, pady=5)
        tk.Label(proj_frame, text="Project Name:", font=('Arial', 12), bg='white', fg='#555').pack(anchor='w')
        self.project_var = tk.StringVar()
        self.project_entry = tk.Entry(proj_frame, textvariable=self.project_var, font=('Arial', 12), width=40, relief=tk.SOLID, bd=1)
        self.project_entry.pack(fill=tk.X, pady=(2, 0))
        self.project_entry.insert(0, "TestProject")
        
        # Borehole name
        bore_frame = tk.Frame(container, bg='white')
        bore_frame.pack(fill=tk.X, pady=5)
        tk.Label(bore_frame, text="Borehole Name:", font=('Arial', 12), bg='white', fg='#555').pack(anchor='w')
        self.borehole_var = tk.StringVar()
        self.borehole_entry = tk.Entry(bore_frame, textvariable=self.borehole_var, font=('Arial', 12), width=40, relief=tk.SOLID, bd=1)
        self.borehole_entry.pack(fill=tk.X, pady=(2, 0))
        self.borehole_entry.insert(0, "BH-001")
        
        # Depth fields in horizontal layout
        depth_frame = tk.Frame(container, bg='white')
        depth_frame.pack(fill=tk.X, pady=5)
        
        # Left side - Depth From
        left_frame = tk.Frame(depth_frame, bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(left_frame, text="Depth From (m):", font=('Arial', 12), bg='white', fg='#555').pack(anchor='w')
        self.depth_from_var = tk.StringVar(value="0.00")
        self.depth_from_entry = tk.Entry(left_frame, textvariable=self.depth_from_var, font=('Arial', 12), relief=tk.SOLID, bd=1)
        self.depth_from_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Right side - Depth To
        right_frame = tk.Frame(depth_frame, bg='white')
        right_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(right_frame, text="Depth To (m):", font=('Arial', 12), bg='white', fg='#555').pack(anchor='w')
        self.depth_to_var = tk.StringVar(value="0.50")
        self.depth_to_entry = tk.Entry(right_frame, textvariable=self.depth_to_var, font=('Arial', 12), relief=tk.SOLID, bd=1)
        self.depth_to_entry.pack(fill=tk.X, pady=(2, 0))
        
    def create_preview_section(self, parent):
        """Create camera preview section."""
        preview_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        preview_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        title_label = tk.Label(preview_frame, text="Camera Preview", font=('Arial', 14, 'bold'), bg='white', fg='#333')
        title_label.pack(pady=(15, 10))
        
        # Preview area
        self.preview_label = tk.Label(
            preview_frame,
            text="📷 Camera Preview\n(Mock Mode - Demo)\n\nThis would show live camera feed\nfrom dual IMX219 cameras\n\nResolution: 3280x2464\nStereo Pair Setup",
            font=('Arial', 11),
            bg='#2a2a2a',
            fg='white',
            width=60,
            height=10,
            relief=tk.SUNKEN,
            bd=2,
            justify=tk.CENTER
        )
        self.preview_label.pack(pady=(0, 15))
        
    def create_control_buttons(self, parent):
        """Create control buttons section."""
        controls_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        title_label = tk.Label(controls_frame, text="Controls", font=('Arial', 14, 'bold'), bg='white', fg='#333')
        title_label.pack(pady=(15, 10))
        
        # Main action buttons
        main_btn_frame = tk.Frame(controls_frame, bg='white')
        main_btn_frame.pack(pady=10)
        
        self.ok_button = tk.Button(
            main_btn_frame,
            text="OK",
            font=('Arial', 16, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=3,
            activebackground='#45a049',
            activeforeground='white',
            command=self.on_ok_clicked
        )
        self.ok_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.no_button = tk.Button(
            main_btn_frame,
            text="NO",
            font=('Arial', 16, 'bold'),
            bg='#f44336',
            fg='white',
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=3,
            activebackground='#da190b',
            activeforeground='white',
            command=self.on_no_clicked
        )
        self.no_button.pack(side=tk.LEFT)
        
        # Adjustment buttons
        adj_btn_frame = tk.Frame(controls_frame, bg='white')
        adj_btn_frame.pack(pady=8)
        
        self.plus_button = tk.Button(
            adj_btn_frame,
            text="+",
            font=('Arial', 18, 'bold'),
            bg='#2196F3',
            fg='white',
            width=8,
            height=1,
            relief=tk.RAISED,
            bd=3,
            activebackground='#1976D2',
            activeforeground='white',
            command=self.on_plus_clicked
        )
        self.plus_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.minus_button = tk.Button(
            adj_btn_frame,
            text="−",
            font=('Arial', 18, 'bold'),
            bg='#2196F3',
            fg='white',
            width=8,
            height=1,
            relief=tk.RAISED,
            bd=3,
            activebackground='#1976D2',
            activeforeground='white',
            command=self.on_minus_clicked
        )
        self.minus_button.pack(side=tk.LEFT)
        
        # Exposure buttons
        exp_btn_frame = tk.Frame(controls_frame, bg='white')
        exp_btn_frame.pack(pady=8)
        
        self.brighter_button = tk.Button(
            exp_btn_frame,
            text="BRIGHTER",
            font=('Arial', 12, 'bold'),
            bg='#FF9800',
            fg='white',
            width=14,
            height=1,
            relief=tk.RAISED,
            bd=3,
            activebackground='#F57C00',
            activeforeground='white',
            command=self.on_brighter_clicked
        )
        self.brighter_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.darker_button = tk.Button(
            exp_btn_frame,
            text="DARKER",
            font=('Arial', 12, 'bold'),
            bg='#795548',
            fg='white',
            width=14,
            height=1,
            relief=tk.RAISED,
            bd=3,
            activebackground='#5D4037',
            activeforeground='white',
            command=self.on_darker_clicked
        )
        self.darker_button.pack(side=tk.LEFT)
        
        # Focus button
        focus_btn_frame = tk.Frame(controls_frame, bg='white')
        focus_btn_frame.pack(pady=(8, 15))
        
        self.focus_button = tk.Button(
            focus_btn_frame,
            text="FOCUS",
            font=('Arial', 14, 'bold'),
            bg='#9C27B0',
            fg='white',
            width=18,
            height=1,
            relief=tk.RAISED,
            bd=3,
            activebackground='#7B1FA2',
            activeforeground='white',
            command=self.on_focus_clicked
        )
        self.focus_button.pack()
        
    def create_status_section(self, parent):
        """Create status section."""
        status_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(status_frame, text="System Status", font=('Arial', 12, 'bold'), bg='white').pack(pady=(10, 5))
        
        # Status text area
        text_frame = tk.Frame(status_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.status_text = tk.Text(
            text_frame,
            height=6,
            font=('Courier', 9),
            bg='#f8f8f8',
            wrap=tk.WORD
        )
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress bar
        self.progress_frame = tk.Frame(status_frame, bg='white')
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        
    def show_progress(self, value):
        """Show progress bar with value."""
        self.progress_frame.pack(pady=5)
        self.progress_bar.pack()
        self.progress_var.set(value)
        self.root.update()
        
    def hide_progress(self):
        """Hide progress bar."""
        self.progress_frame.pack_forget()
        
    def on_ok_clicked(self):
        """Handle OK button click."""
        project = self.project_var.get().strip()
        borehole = self.borehole_var.get().strip()
        
        if not project or project == "Enter project name...":
            messagebox.showwarning("Validation Error", "Please enter a Project Name")
            return
            
        if not borehole or borehole == "Enter borehole name...":
            messagebox.showwarning("Validation Error", "Please enter a Borehole Name")
            return
            
        self.log_status("📸 Starting capture workflow...")
        self.show_progress(50)
        
        # Schedule the camera preview
        self.root.after(1000, self.show_camera1_preview)
        
    def show_camera1_preview(self):
        """Show Camera 1 preview dialog."""
        self.hide_progress()
        
        result = messagebox.askyesno(
            "Preview: Camera 1",
            "📷 Camera 1 Image\n(Simulated Capture)\n\nThis would show the actual photo from left camera.\n\nAccept this image?",
            icon='question'
        )
        
        if result:
            self.show_camera2_preview()
        else:
            self.log_status("❌ Camera 1 image rejected")
            
    def show_camera2_preview(self):
        """Show Camera 2 preview dialog."""
        result = messagebox.askyesno(
            "Preview: Camera 2", 
            "📷 Camera 2 Image\n(Simulated Capture)\n\nThis would show the actual photo from right camera.\n\nAccept this image?",
            icon='question'
        )
        
        if result:
            self.simulate_save()
        else:
            self.log_status("❌ Camera 2 image rejected")
            
    def simulate_save(self):
        """Simulate saving images and advancing."""
        project = self.project_var.get().strip()
        borehole = self.borehole_var.get().strip()
        depth_from = self.current_depth_from
        depth_to = self.current_depth_to
        
        filename = f"{project}/{borehole}/{borehole}-{depth_from:.2f}-{depth_to:.2f}"
        self.log_status(f"💾 Saved: {filename}-1.jpg and {filename}-2.jpg")
        self.log_status("✅ Images saved successfully!")
        
        # Auto-advance to next segment
        new_from = depth_to
        new_to = new_from + 0.5
        
        self.depth_from_var.set(f"{new_from:.2f}")
        self.depth_to_var.set(f"{new_to:.2f}")
        self.current_depth_from = new_from
        self.current_depth_to = new_to
        
        self.log_status(f"➡️ Advanced to next segment: {new_from:.2f}m - {new_to:.2f}m")
        
    def on_no_clicked(self):
        """Handle NO button click."""
        self.log_status("❌ Current operation cancelled")
        
    def on_plus_clicked(self):
        """Handle + button click."""
        try:
            current_to = float(self.depth_to_var.get())
            new_to = current_to + 0.05
            self.depth_to_var.set(f"{new_to:.2f}")
            self.current_depth_to = new_to
            self.log_status(f"➕ Depth To adjusted to {new_to:.2f}m")
        except ValueError:
            messagebox.showerror("Error", "Invalid depth value")
            
    def on_minus_clicked(self):
        """Handle - button click."""
        try:
            current_to = float(self.depth_to_var.get())
            new_to = max(0, current_to - 0.05)
            self.depth_to_var.set(f"{new_to:.2f}")
            self.current_depth_to = new_to
            self.log_status(f"➖ Depth To adjusted to {new_to:.2f}m")
        except ValueError:
            messagebox.showerror("Error", "Invalid depth value")
            
    def on_brighter_clicked(self):
        """Handle BRIGHTER button click."""
        self.log_status("🔆 Exposure increased (brighter) - Mock Mode")
        
    def on_darker_clicked(self):
        """Handle DARKER button click."""
        self.log_status("🔅 Exposure decreased (darker) - Mock Mode")
        
    def on_focus_clicked(self):
        """Handle FOCUS button click."""
        # Create focus dialog
        focus_window = tk.Toplevel(self.root)
        focus_window.title("Focus Adjustment")
        focus_window.geometry("300x200")
        focus_window.configure(bg='white')
        focus_window.grab_set()  # Make it modal
        
        # Center the window
        focus_window.transient(self.root)
        
        tk.Label(focus_window, text="🎯 Focus Adjustment", font=('Arial', 12, 'bold'), bg='white').pack(pady=20)
        tk.Label(focus_window, text="Use + and - to adjust focus\n(Mock Mode)", bg='white').pack()
        
        btn_frame = tk.Frame(focus_window, bg='white')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="+", font=('Arial', 14), width=5, 
                 command=lambda: self.log_status("🎯 Focus adjusted: increase")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="−", font=('Arial', 14), width=5,
                 command=lambda: self.log_status("🎯 Focus adjusted: decrease")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="OK", font=('Arial', 12), width=8, bg='#4CAF50', fg='white',
                 command=focus_window.destroy).pack(side=tk.LEFT, padx=10)
        
    def log_status(self, message):
        """Log status message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.root.update()
        
    def run(self):
        """Run the demo."""
        print("🎬 Starting Tkinter UI Demo...")
        print("✅ UI Demo launched!")
        print("\n🎯 Demo Features:")
        print("   📝 Input validation")
        print("   📷 Mock capture workflow") 
        print("   🎮 All button interactions")
        print("   📊 Status logging")
        print("   ➕➖ Depth adjustments")
        print("   🔆🔅 Exposure controls")
        print("   🎯 Focus dialog")
        print("\n🔧 Try this workflow:")
        print("   1. Enter 'TestProject' and 'BH-001'")
        print("   2. Click OK → Accept both camera previews")
        print("   3. Watch automatic depth advancement")
        print("   4. Try +/- buttons and other controls")
        print("\n👀 The UI window should now be visible!")
        
        self.root.mainloop()


if __name__ == "__main__":
    demo = StereoCoreCameraDemo()
    demo.run() 