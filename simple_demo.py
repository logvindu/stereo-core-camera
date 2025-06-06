#!/usr/bin/env python3
"""
Simple standalone UI demo for the Stereo Core Camera System.
This version doesn't depend on the camera/storage modules to avoid import conflicts.
"""

import sys
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
        QMessageBox, QDialog, QFrame
    )
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
    
    
    class SimpleMainWindow(QMainWindow):
        """Simple demo of the main window interface."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Stereo Core Camera System - UI Demo")
            self.resize(800, 600)
            
            # Current values
            self.current_depth_from = 0.0
            self.current_depth_to = 0.5
            
            self._setup_ui()
            self._setup_connections()
            self._log_status("UI Demo started - Mock mode")
            
        def _setup_ui(self):
            """Set up the user interface."""
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(15, 15, 15, 15)
            
            # Header
            self._create_header(main_layout)
            
            # Input section
            self._create_input_section(main_layout)
            
            # Preview section
            self._create_preview_section(main_layout)
            
            # Control buttons
            self._create_control_buttons(main_layout)
            
            # Status section
            self._create_status_section(main_layout)
            
            # Apply styling
            self._apply_styling()
            
        def _create_header(self, parent_layout):
            """Create header section."""
            header_frame = QFrame()
            header_frame.setFrameStyle(QFrame.StyledPanel)
            header_layout = QVBoxLayout(header_frame)
            
            title_label = QLabel("Stereo Core Camera System")
            title_label.setAlignment(Qt.AlignCenter)
            title_font = QFont()
            title_font.setPointSize(18)
            title_font.setBold(True)
            title_label.setFont(title_font)
            
            header_layout.addWidget(title_label)
            parent_layout.addWidget(header_frame)
            
        def _create_input_section(self, parent_layout):
            """Create input fields section."""
            input_frame = QFrame()
            input_frame.setFrameStyle(QFrame.StyledPanel)
            input_layout = QGridLayout(input_frame)
            
            # Font for labels and inputs
            input_font = QFont()
            input_font.setPointSize(12)
            
            # Project name
            project_label = QLabel("Project Name:")
            project_label.setFont(input_font)
            self.project_input = QLineEdit()
            self.project_input.setFont(input_font)
            self.project_input.setMinimumHeight(40)
            self.project_input.setPlaceholderText("Enter project name...")
            
            # Borehole name
            borehole_label = QLabel("Borehole Name:")
            borehole_label.setFont(input_font)
            self.borehole_input = QLineEdit()
            self.borehole_input.setFont(input_font)
            self.borehole_input.setMinimumHeight(40)
            self.borehole_input.setPlaceholderText("Enter borehole name...")
            
            # Depth from
            depth_from_label = QLabel("Depth From (m):")
            depth_from_label.setFont(input_font)
            self.depth_from_input = QLineEdit("0.00")
            self.depth_from_input.setFont(input_font)
            self.depth_from_input.setMinimumHeight(40)
            
            # Depth to
            depth_to_label = QLabel("Depth To (m):")
            depth_to_label.setFont(input_font)
            self.depth_to_input = QLineEdit("0.50")
            self.depth_to_input.setFont(input_font)
            self.depth_to_input.setMinimumHeight(40)
            
            # Layout inputs
            input_layout.addWidget(project_label, 0, 0)
            input_layout.addWidget(self.project_input, 0, 1)
            input_layout.addWidget(borehole_label, 1, 0)
            input_layout.addWidget(self.borehole_input, 1, 1)
            input_layout.addWidget(depth_from_label, 2, 0)
            input_layout.addWidget(self.depth_from_input, 2, 1)
            input_layout.addWidget(depth_to_label, 3, 0)
            input_layout.addWidget(self.depth_to_input, 3, 1)
            
            parent_layout.addWidget(input_frame)
            
        def _create_preview_section(self, parent_layout):
            """Create camera preview section."""
            preview_frame = QFrame()
            preview_frame.setFrameStyle(QFrame.StyledPanel)
            preview_layout = QVBoxLayout(preview_frame)
            
            # Preview label
            preview_title = QLabel("Camera Preview")
            preview_title.setAlignment(Qt.AlignCenter)
            preview_title.setFont(QFont("Arial", 12, QFont.Bold))
            preview_layout.addWidget(preview_title)
            
            # Preview display
            self.preview_label = QLabel()
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.preview_label.setMinimumSize(320, 240)
            self.preview_label.setText("📷 Camera Preview\n(Mock Mode - Demo)\n\nThis would show live camera feed\nfrom dual IMX219 cameras")
            self.preview_label.setStyleSheet(
                "QLabel { background-color: #2a2a2a; color: white; border: 2px solid #666; font-size: 14px; }"
            )
            
            preview_layout.addWidget(self.preview_label)
            parent_layout.addWidget(preview_frame)
        
        def _create_control_buttons(self, parent_layout):
            """Create control buttons section."""
            controls_frame = QFrame()
            controls_frame.setFrameStyle(QFrame.StyledPanel)
            controls_layout = QVBoxLayout(controls_frame)
            
            # Main action buttons
            main_buttons_layout = QHBoxLayout()
            
            self.ok_button = QPushButton("OK")
            self.ok_button.setMinimumSize(100, 60)
            self.ok_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 14px; font-weight: bold; }")
            
            self.no_button = QPushButton("NO")
            self.no_button.setMinimumSize(100, 60)
            self.no_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-size: 14px; font-weight: bold; }")
            
            main_buttons_layout.addWidget(self.ok_button)
            main_buttons_layout.addWidget(self.no_button)
            
            # Adjustment buttons
            adjustment_layout = QHBoxLayout()
            
            self.plus_button = QPushButton("+")
            self.plus_button.setMinimumSize(80, 50)
            self.plus_button.setStyleSheet("QPushButton { font-size: 16px; font-weight: bold; }")
            
            self.minus_button = QPushButton("−")
            self.minus_button.setMinimumSize(80, 50)
            self.minus_button.setStyleSheet("QPushButton { font-size: 16px; font-weight: bold; }")
            
            adjustment_layout.addWidget(self.plus_button)
            adjustment_layout.addWidget(self.minus_button)
            
            # Exposure buttons
            exposure_layout = QHBoxLayout()
            
            self.brighter_button = QPushButton("BRIGHTER")
            self.brighter_button.setMinimumSize(100, 50)
            self.brighter_button.setStyleSheet("QPushButton { font-size: 12px; }")
            
            self.darker_button = QPushButton("DARKER")
            self.darker_button.setMinimumSize(100, 50)
            self.darker_button.setStyleSheet("QPushButton { font-size: 12px; }")
            
            exposure_layout.addWidget(self.brighter_button)
            exposure_layout.addWidget(self.darker_button)
            
            # Focus button
            focus_layout = QHBoxLayout()
            
            self.focus_button = QPushButton("FOCUS")
            self.focus_button.setMinimumSize(120, 50)
            self.focus_button.setStyleSheet("QPushButton { font-size: 12px; background-color: #2196F3; color: white; }")
            
            focus_layout.addWidget(self.focus_button)
            focus_layout.addStretch()
            
            # Add all button layouts
            controls_layout.addLayout(main_buttons_layout)
            controls_layout.addLayout(adjustment_layout)
            controls_layout.addLayout(exposure_layout)
            controls_layout.addLayout(focus_layout)
            
            parent_layout.addWidget(controls_frame)
        
        def _create_status_section(self, parent_layout):
            """Create status information section."""
            status_frame = QFrame()
            status_frame.setFrameStyle(QFrame.StyledPanel)
            status_layout = QVBoxLayout(status_frame)
            
            # Status text
            self.status_text = QTextEdit()
            self.status_text.setMaximumHeight(100)
            self.status_text.setReadOnly(True)
            self.status_text.setFont(QFont("Courier", 9))
            
            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            
            status_layout.addWidget(QLabel("System Status:"))
            status_layout.addWidget(self.status_text)
            status_layout.addWidget(self.progress_bar)
            
            parent_layout.addWidget(status_frame)
        
        def _apply_styling(self):
            """Apply overall styling."""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QFrame {
                    background-color: white;
                    border-radius: 5px;
                    margin: 2px;
                }
                QLineEdit {
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border-color: #4CAF50;
                }
                QPushButton {
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #f9f9f9;
                }
                QPushButton:hover {
                    background-color: #e9e9e9;
                }
                QPushButton:pressed {
                    background-color: #d9d9d9;
                }
            """)
        
        def _setup_connections(self):
            """Set up button connections."""
            self.ok_button.clicked.connect(self._on_ok_clicked)
            self.no_button.clicked.connect(self._on_no_clicked)
            self.plus_button.clicked.connect(self._on_plus_clicked)
            self.minus_button.clicked.connect(self._on_minus_clicked)
            self.brighter_button.clicked.connect(self._on_brighter_clicked)
            self.darker_button.clicked.connect(self._on_darker_clicked)
            self.focus_button.clicked.connect(self._on_focus_clicked)
        
        def _on_ok_clicked(self):
            """Handle OK button click."""
            project = self.project_input.text().strip()
            borehole = self.borehole_input.text().strip()
            
            if not project or not borehole:
                QMessageBox.warning(self, "Validation Error", "Please enter both Project Name and Borehole Name")
                return
                
            self._log_status("📸 Starting capture workflow...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(50)
            
            # Simulate the capture workflow
            QTimer.singleShot(1000, self._show_camera1_preview)
            
        def _show_camera1_preview(self):
            """Show Camera 1 preview dialog."""
            self.progress_bar.setVisible(False)
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Preview: Camera 1")
            dialog.resize(400, 350)
            
            layout = QVBoxLayout(dialog)
            
            # Mock image display
            image_label = QLabel()
            image_label.setText("📷 Camera 1 Image\n(Simulated Capture)\n\nThis would show the actual\nphoto from left camera")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setMinimumSize(350, 250)
            image_label.setStyleSheet("QLabel { background-color: #444; color: white; border: 2px solid #888; font-size: 14px; }")
            layout.addWidget(image_label)
            
            # Buttons
            button_layout = QHBoxLayout()
            ok_btn = QPushButton("OK")
            no_btn = QPushButton("NO")
            
            button_layout.addWidget(ok_btn)
            button_layout.addWidget(no_btn)
            layout.addLayout(button_layout)
            
            # Connect buttons
            ok_btn.clicked.connect(dialog.accept)
            no_btn.clicked.connect(dialog.reject)
            
            # Show dialog
            if dialog.exec_() == QDialog.Accepted:
                self._show_camera2_preview()
            else:
                self._log_status("❌ Camera 1 image rejected")
        
        def _show_camera2_preview(self):
            """Show Camera 2 preview dialog."""
            dialog = QDialog(self)
            dialog.setWindowTitle("Preview: Camera 2")
            dialog.resize(400, 350)
            
            layout = QVBoxLayout(dialog)
            
            # Mock image display
            image_label = QLabel()
            image_label.setText("📷 Camera 2 Image\n(Simulated Capture)\n\nThis would show the actual\nphoto from right camera")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setMinimumSize(350, 250)
            image_label.setStyleSheet("QLabel { background-color: #444; color: white; border: 2px solid #888; font-size: 14px; }")
            layout.addWidget(image_label)
            
            # Buttons
            button_layout = QHBoxLayout()
            ok_btn = QPushButton("OK")
            no_btn = QPushButton("NO")
            
            button_layout.addWidget(ok_btn)
            button_layout.addWidget(no_btn)
            layout.addLayout(button_layout)
            
            # Connect buttons
            ok_btn.clicked.connect(dialog.accept)
            no_btn.clicked.connect(dialog.reject)
            
            # Show dialog
            if dialog.exec_() == QDialog.Accepted:
                self._simulate_save()
            else:
                self._log_status("❌ Camera 2 image rejected")
        
        def _simulate_save(self):
            """Simulate saving images and advancing."""
            project = self.project_input.text().strip()
            borehole = self.borehole_input.text().strip()
            depth_from = self.current_depth_from
            depth_to = self.current_depth_to
            
            filename = f"{project}/{borehole}/{borehole}-{depth_from:.2f}-{depth_to:.2f}"
            self._log_status(f"💾 Saved: {filename}-1.jpg and {filename}-2.jpg")
            self._log_status("✅ Images saved successfully!")
            
            # Auto-advance to next segment
            new_from = depth_to
            new_to = new_from + 0.5
            
            self.depth_from_input.setText(f"{new_from:.2f}")
            self.depth_to_input.setText(f"{new_to:.2f}")
            self.current_depth_from = new_from
            self.current_depth_to = new_to
            
            self._log_status(f"➡️ Advanced to next segment: {new_from:.2f}m - {new_to:.2f}m")
        
        def _on_no_clicked(self):
            """Handle NO button click."""
            self._log_status("❌ Current operation cancelled")
        
        def _on_plus_clicked(self):
            """Handle + button click."""
            try:
                current_to = float(self.depth_to_input.text())
                new_to = current_to + 0.05
                self.depth_to_input.setText(f"{new_to:.2f}")
                self.current_depth_to = new_to
                self._log_status(f"➕ Depth To adjusted to {new_to:.2f}m")
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid depth value")
        
        def _on_minus_clicked(self):
            """Handle - button click."""
            try:
                current_to = float(self.depth_to_input.text())
                new_to = max(0, current_to - 0.05)
                self.depth_to_input.setText(f"{new_to:.2f}")
                self.current_depth_to = new_to
                self._log_status(f"➖ Depth To adjusted to {new_to:.2f}m")
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid depth value")
        
        def _on_brighter_clicked(self):
            """Handle BRIGHTER button click."""
            self._log_status("🔆 Exposure increased (brighter) - Mock Mode")
        
        def _on_darker_clicked(self):
            """Handle DARKER button click."""
            self._log_status("🔅 Exposure decreased (darker) - Mock Mode")
        
        def _on_focus_clicked(self):
            """Handle FOCUS button click."""
            dialog = QDialog(self)
            dialog.setWindowTitle("Focus Adjustment")
            dialog.resize(300, 200)
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("🎯 Use + and - to adjust focus\n(Mock Mode)"))
            
            button_layout = QHBoxLayout()
            plus_btn = QPushButton("+")
            minus_btn = QPushButton("-")
            ok_btn = QPushButton("OK")
            
            button_layout.addWidget(plus_btn)
            button_layout.addWidget(minus_btn)
            button_layout.addWidget(ok_btn)
            layout.addLayout(button_layout)
            
            plus_btn.clicked.connect(lambda: self._log_status("🎯 Focus adjusted: increase"))
            minus_btn.clicked.connect(lambda: self._log_status("🎯 Focus adjusted: decrease"))
            ok_btn.clicked.connect(dialog.accept)
            
            dialog.exec_()
        
        def _log_status(self, message: str):
            """Log status message."""
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            self.status_text.append(formatted_message)
            
            # Scroll to bottom
            cursor = self.status_text.textCursor()
            cursor.movePosition(cursor.End)
            self.status_text.setTextCursor(cursor)


    def main():
        """Run the simple demo."""
        print("🎬 Starting Simple UI Demo...")
        
        app = QApplication(sys.argv)
        app.setApplicationName("Stereo Core Camera - Simple Demo")
        
        window = SimpleMainWindow()
        window.show()
        
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
        
        return app.exec_()


    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Please install PyQt5:")
    print("   pip install PyQt5")
    sys.exit(1) 