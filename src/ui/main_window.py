"""
Main Window UI for the Stereo Core Camera System.
Optimized for 5-inch touchscreen operation.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QMessageBox, QDialog, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, pyqtSignal
from PySide6.QtGui import QPixmap, QImage, QFont, QPalette, QColor

from ..camera import StereoCamera
from ..storage import StorageManager
from .preview_dialog import PreviewDialog
from .focus_dialog import FocusDialog


class PreviewUpdateThread(QThread):
    """Thread for updating camera preview without blocking UI."""
    
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self, camera: StereoCamera):
        super().__init__()
        self.camera = camera
        self.running = False
        
    def run(self):
        """Run preview update loop."""
        self.running = True
        while self.running:
            if self.camera.is_initialized():
                frame = self.camera.get_preview_frame()
                if frame is not None:
                    self.frame_ready.emit(frame)
            self.msleep(100)  # 10 FPS preview
            
    def stop(self):
        """Stop the preview thread."""
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    """
    Main application window with touchscreen-optimized interface.
    """
    
    def __init__(self, config: Dict[str, Any], camera: StereoCamera, 
                 storage: StorageManager):
        super().__init__()
        
        self.config = config
        self.camera = camera
        self.storage = storage
        self.logger = logging.getLogger(__name__)
        
        # UI state
        self.current_project = ""
        self.current_borehole = ""
        self.current_depth_from = 0.0
        self.current_depth_to = 0.5
        
        # Preview thread
        self.preview_thread: Optional[PreviewUpdateThread] = None
        
        # Current captured images (for preview/review)
        self.captured_images: Optional[Tuple[np.ndarray, np.ndarray]] = None
        
        self._setup_ui()
        self._setup_styling()
        self._setup_connections()
        self._start_preview()
        
        # Update storage info periodically
        self.storage_timer = QTimer()
        self.storage_timer.timeout.connect(self._update_storage_info)
        self.storage_timer.start(10000)  # Update every 10 seconds
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(self.config['ui']['window_title'])
        
        # Set window size or fullscreen
        if self.config['ui']['fullscreen']:
            self.showFullScreen()
        else:
            size = self.config['ui']['window_size']
            self.resize(size[0], size[1])
        
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
        
        # Borehole name
        borehole_label = QLabel("Borehole Name:")
        borehole_label.setFont(input_font)
        self.borehole_input = QLineEdit()
        self.borehole_input.setFont(input_font)
        self.borehole_input.setMinimumHeight(40)
        
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
        self.preview_label.setStyleSheet(
            "QLabel { background-color: black; border: 2px solid gray; }"
        )
        self.preview_label.setText("Camera Preview\n(Initializing...)")
        self.preview_label.setStyleSheet(
            "QLabel { background-color: black; color: white; border: 2px solid gray; }"
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
        
    def _setup_styling(self):
        """Set up application styling."""
        # Set overall application style
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
        """Set up signal connections."""
        # Main action buttons
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.no_button.clicked.connect(self._on_no_clicked)
        
        # Adjustment buttons
        self.plus_button.clicked.connect(self._on_plus_clicked)
        self.minus_button.clicked.connect(self._on_minus_clicked)
        
        # Exposure buttons
        self.brighter_button.clicked.connect(self._on_brighter_clicked)
        self.darker_button.clicked.connect(self._on_darker_clicked)
        
        # Focus button
        self.focus_button.clicked.connect(self._on_focus_clicked)
        
        # Input field changes
        self.project_input.textChanged.connect(self._on_input_changed)
        self.borehole_input.textChanged.connect(self._on_input_changed)
        self.depth_from_input.textChanged.connect(self._on_input_changed)
        self.depth_to_input.textChanged.connect(self._on_input_changed)
    
    def _start_preview(self):
        """Start camera preview."""
        if self.camera.is_initialized():
            self.preview_thread = PreviewUpdateThread(self.camera)
            self.preview_thread.frame_ready.connect(self._update_preview)
            self.preview_thread.start()
            self._log_status("Camera preview started")
        else:
            self._log_status("ERROR: Camera not initialized")
    
    def _update_preview(self, frame: np.ndarray):
        """Update preview display with new frame."""
        try:
            # Convert numpy array to QImage
            if len(frame.shape) == 3:
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            else:
                # Grayscale
                height, width = frame.shape
                bytes_per_line = width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            
            # Convert to pixmap and scale to fit label
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.preview_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.logger.error(f"Failed to update preview: {e}")
    
    def _on_ok_clicked(self):
        """Handle OK button click."""
        if not self._validate_inputs():
            return
            
        try:
            self._log_status("Capturing stereo pair...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(25)
            
            # Capture images
            left_image, right_image = self.camera.capture_stereo_pair()
            
            if left_image is None or right_image is None:
                self._show_error("Failed to capture images from cameras")
                return
                
            self.progress_bar.setValue(50)
            self.captured_images = (left_image, right_image)
            
            # Show preview dialog for first image
            self._show_image_preview(left_image, "Camera 1")
            
        except Exception as e:
            self._show_error(f"Capture failed: {str(e)}")
            self.logger.error(f"Capture error: {e}")
        finally:
            self.progress_bar.setVisible(False)
    
    def _show_image_preview(self, image: np.ndarray, title: str):
        """Show simple image preview and ask for confirmation."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Preview: {title}")
        dialog.resize(400, 350)
        
        layout = QVBoxLayout(dialog)
        
        # Convert image to QPixmap
        if len(image.shape) == 3:
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        else:
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(q_image)
        
        # Image label
        image_label = QLabel()
        image_label.setPixmap(pixmap.scaled(350, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_label.setAlignment(Qt.AlignCenter)
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
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            if title == "Camera 1":
                # Show second image
                self._show_image_preview(self.captured_images[1], "Camera 2")
            else:
                # Save both images
                self._save_images()
        else:
            self._on_no_clicked()
    
    def _save_images(self):
        """Save the captured stereo pair."""
        if self.captured_images is None:
            return
            
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(75)
            
            # Generate file path
            base_path = self.storage.generate_file_path(
                self.current_project,
                self.current_borehole,
                self.current_depth_from,
                self.current_depth_to
            )
            
            # Save stereo pair
            success, filenames = self.camera.save_stereo_pair(
                self.captured_images[0],
                self.captured_images[1],
                base_path
            )
            
            if success:
                # Backup to USB
                storage_result = self.storage.save_images_to_storage(filenames)
                
                if storage_result['usb_success']:
                    self._log_status(f"Images saved successfully to internal and USB storage")
                else:
                    self._log_status(f"Images saved to internal storage (USB backup failed)")
                
                # Update workflow - advance to next segment
                self._advance_to_next_segment()
                
            else:
                self._show_error("Failed to save images")
                
        except Exception as e:
            self._show_error(f"Save failed: {str(e)}")
            self.logger.error(f"Save error: {e}")
        finally:
            self.progress_bar.setVisible(False)
            self.captured_images = None
    
    def _on_no_clicked(self):
        """Handle NO button click - discard current capture."""
        self.captured_images = None
        self._log_status("Current capture discarded")
    
    def _on_plus_clicked(self):
        """Handle + button click - increase depth_to."""
        try:
            step = self.config['ui']['segment_adjustment_step']
            current_to = float(self.depth_to_input.text())
            new_to = current_to + step
            self.depth_to_input.setText(f"{new_to:.2f}")
            self._log_status(f"Depth To adjusted to {new_to:.2f}m")
        except ValueError:
            self._show_error("Invalid depth value")
    
    def _on_minus_clicked(self):
        """Handle - button click - decrease depth_to."""
        try:
            step = self.config['ui']['segment_adjustment_step']
            current_to = float(self.depth_to_input.text())
            new_to = max(0, current_to - step)
            self.depth_to_input.setText(f"{new_to:.2f}")
            self._log_status(f"Depth To adjusted to {new_to:.2f}m")
        except ValueError:
            self._show_error("Invalid depth value")
    
    def _on_brighter_clicked(self):
        """Handle BRIGHTER button click."""
        if self.camera.adjust_exposure('brighter'):
            self._log_status("Exposure increased (brighter)")
        else:
            self._show_error("Failed to adjust exposure")
    
    def _on_darker_clicked(self):
        """Handle DARKER button click."""
        if self.camera.adjust_exposure('darker'):
            self._log_status("Exposure decreased (darker)")
        else:
            self._show_error("Failed to adjust exposure")
    
    def _on_focus_clicked(self):
        """Handle FOCUS button click - simple focus adjustment."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Focus Adjustment")
        dialog.resize(300, 200)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Use + and - to adjust focus, then OK"))
        
        button_layout = QHBoxLayout()
        plus_btn = QPushButton("+")
        minus_btn = QPushButton("-")
        ok_btn = QPushButton("OK")
        
        button_layout.addWidget(plus_btn)
        button_layout.addWidget(minus_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)
        
        plus_btn.clicked.connect(lambda: self._adjust_focus_step("increase"))
        minus_btn.clicked.connect(lambda: self._adjust_focus_step("decrease"))
        ok_btn.clicked.connect(dialog.accept)
        
        dialog.exec()
    
    def _adjust_focus_step(self, direction: str):
        """Adjust focus in given direction."""
        if self.camera.adjust_focus(direction):
            self._log_status(f"Focus adjusted: {direction}")
    
    def _on_input_changed(self):
        """Handle input field changes."""
        self._update_current_values()
    
    def _validate_inputs(self) -> bool:
        """Validate input fields."""
        try:
            self._update_current_values()
            
            if not self.current_project:
                self._show_error("Project name is required")
                return False
                
            if not self.current_borehole:
                self._show_error("Borehole name is required")
                return False
                
            if self.current_depth_from >= self.current_depth_to:
                self._show_error("Depth From must be less than Depth To")
                return False
                
            return True
            
        except ValueError:
            self._show_error("Invalid depth values")
            return False
    
    def _update_current_values(self):
        """Update current values from input fields."""
        self.current_project = self.project_input.text().strip()
        self.current_borehole = self.borehole_input.text().strip()
        self.current_depth_from = float(self.depth_from_input.text())
        self.current_depth_to = float(self.depth_to_input.text())
    
    def _advance_to_next_segment(self):
        """Advance to next segment after successful capture."""
        # From becomes previous To, To becomes From + default segment length
        new_from = self.current_depth_to
        new_to = new_from + self.config['ui']['default_segment_length']
        
        self.depth_from_input.setText(f"{new_from:.2f}")
        self.depth_to_input.setText(f"{new_to:.2f}")
        
        self._log_status(f"Advanced to next segment: {new_from:.2f}m - {new_to:.2f}m")
    
    def _update_storage_info(self):
        """Update storage information display."""
        try:
            storage_summary = self.storage.get_storage_summary()
            # Add storage info to status without overwhelming the display
            lines = storage_summary.split('\n')
            storage_line = lines[0] if lines else "Storage: Unknown"
            
            # Check for warnings
            if any('warning' in line.lower() for line in lines):
                storage_line += " ⚠️"
                
        except Exception as e:
            self.logger.error(f"Failed to update storage info: {e}")
    
    def _log_status(self, message: str):
        """Log status message to status display."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.status_text.append(formatted_message)
        self.logger.info(message)
        
        # Scroll to bottom
        cursor = self.status_text.textCursor()
        cursor.movePosition(cursor.End)
        self.status_text.setTextCursor(cursor)
    
    def _show_error(self, message: str):
        """Show error message dialog."""
        QMessageBox.critical(self, "Error", message)
        self._log_status(f"ERROR: {message}")
    
    def _show_info(self, message: str):
        """Show information message dialog."""
        QMessageBox.information(self, "Information", message)
        self._log_status(f"INFO: {message}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop preview thread
        if self.preview_thread:
            self.preview_thread.stop()
            
        # Stop timers
        if hasattr(self, 'storage_timer'):
            self.storage_timer.stop()
            
        event.accept() 