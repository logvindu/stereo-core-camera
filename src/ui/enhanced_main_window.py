"""
Enhanced Main Window UI for the Stereo Core Camera System.
Implements the complete operator workflow with proper image review and file management.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QMessageBox, QDialog, QFrame, QSizePolicy, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, pyqtSignal
from PySide6.QtGui import QPixmap, QImage, QFont, QPalette, QColor

from ..camera import StereoCamera
from ..storage import StorageManager
from .preview_dialog import PreviewDialog
from .focus_dialog import FocusDialog


class WorkflowState:
    """Tracks the current workflow state."""
    MAIN_INPUT = "main_input"
    POSITIONING = "positioning"
    CAPTURING = "capturing"
    REVIEWING_CAM1 = "reviewing_cam1"
    REVIEWING_CAM2 = "reviewing_cam2"
    SAVING = "saving"
    FOCUS_MODE = "focus_mode"


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


class EnhancedMainWindow(QMainWindow):
    """
    Enhanced main application window implementing the complete stereo core camera workflow.
    """
    
    def __init__(self, config: Dict[str, Any], camera: StereoCamera, 
                 storage: StorageManager):
        super().__init__()
        
        self.config = config
        self.camera = camera
        self.storage = storage
        self.logger = logging.getLogger(__name__)
        
        # Workflow state
        self.workflow_state = WorkflowState.MAIN_INPUT
        
        # Project data
        self.current_project = ""
        self.current_borehole = ""
        self.current_depth_from = 0.0
        self.current_depth_to = 0.5
        
        # Image data
        self.captured_images: Optional[Tuple[np.ndarray, np.ndarray]] = None
        
        # UI components
        self.preview_thread: Optional[PreviewUpdateThread] = None
        self.preview_dialog: Optional[PreviewDialog] = None
        self.focus_dialog: Optional[FocusDialog] = None
        
        self._setup_ui()
        self._setup_styling()
        self._setup_connections()
        self._start_preview()
        self._update_workflow_state()
        
        # Storage monitoring timer
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
        
        # Project information section
        self._create_project_section(main_layout)
        
        # Depth input section
        self._create_depth_section(main_layout)
        
        # Live preview section
        self._create_preview_section(main_layout)
        
        # Control buttons
        self._create_control_buttons(main_layout)
        
        # Status and storage section
        self._create_status_section(main_layout)
        
    def _create_header(self, parent_layout):
        """Create header section."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        # Main title
        title_label = QLabel("Stereo Core Camera System")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Workflow status
        self.workflow_status_label = QLabel("Ready for operation")
        self.workflow_status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(12)
        self.workflow_status_label.setFont(status_font)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(self.workflow_status_label)
        parent_layout.addWidget(header_frame)
        
    def _create_project_section(self, parent_layout):
        """Create project information input section."""
        project_frame = QFrame()
        project_frame.setFrameStyle(QFrame.StyledPanel)
        project_layout = QGridLayout(project_frame)
        
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
        
        # Layout
        project_layout.addWidget(project_label, 0, 0)
        project_layout.addWidget(self.project_input, 0, 1)
        project_layout.addWidget(borehole_label, 1, 0)
        project_layout.addWidget(self.borehole_input, 1, 1)
        
        parent_layout.addWidget(project_frame)
        
    def _create_depth_section(self, parent_layout):
        """Create depth range input section."""
        depth_frame = QFrame()
        depth_frame.setFrameStyle(QFrame.StyledPanel)
        depth_layout = QGridLayout(depth_frame)
        
        input_font = QFont()
        input_font.setPointSize(12)
        
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
        
        # Adjustment buttons for depth_to
        self.plus_button = QPushButton("+")
        self.plus_button.setMinimumSize(50, 40)
        self.plus_button.setToolTip("Increase depth by 0.05m")
        
        self.minus_button = QPushButton("−")
        self.minus_button.setMinimumSize(50, 40)
        self.minus_button.setToolTip("Decrease depth by 0.05m")
        
        # Layout
        depth_layout.addWidget(depth_from_label, 0, 0)
        depth_layout.addWidget(self.depth_from_input, 0, 1)
        depth_layout.addWidget(depth_to_label, 1, 0)
        depth_layout.addWidget(self.depth_to_input, 1, 1)
        depth_layout.addWidget(self.minus_button, 1, 2)
        depth_layout.addWidget(self.plus_button, 1, 3)
        
        parent_layout.addWidget(depth_frame)
        
    def _create_preview_section(self, parent_layout):
        """Create live camera preview section."""
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.StyledPanel)
        preview_layout = QVBoxLayout(preview_frame)
        
        # Preview title
        preview_title = QLabel("Live Camera Preview")
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setFont(QFont("Arial", 12, QFont.Bold))
        preview_layout.addWidget(preview_title)
        
        # Preview display
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #333;
                border: 2px solid #666;
                border-radius: 5px;
                color: white;
                font-size: 14px;
            }
        """)
        self.preview_label.setText("Positioning cameras...\nLive preview will appear here")
        preview_layout.addWidget(self.preview_label)
        
        parent_layout.addWidget(preview_frame)
        
    def _create_control_buttons(self, parent_layout):
        """Create control buttons section."""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Main action buttons row
        main_buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setMinimumSize(120, 60)
        
        self.no_button = QPushButton("NO")
        self.no_button.setMinimumSize(120, 60)
        
        main_buttons_layout.addWidget(self.ok_button)
        main_buttons_layout.addWidget(self.no_button)
        
        # Camera control buttons row
        camera_buttons_layout = QHBoxLayout()
        
        self.brighter_button = QPushButton("BRIGHTER")
        self.brighter_button.setMinimumSize(100, 50)
        
        self.darker_button = QPushButton("DARKER")
        self.darker_button.setMinimumSize(100, 50)
        
        self.focus_button = QPushButton("FOCUS")
        self.focus_button.setMinimumSize(120, 50)
        
        camera_buttons_layout.addWidget(self.brighter_button)
        camera_buttons_layout.addWidget(self.darker_button)
        camera_buttons_layout.addWidget(self.focus_button)
        camera_buttons_layout.addStretch()
        
        # Add layouts to main controls
        controls_layout.addLayout(main_buttons_layout)
        controls_layout.addLayout(camera_buttons_layout)
        
        parent_layout.addWidget(controls_frame)
        
    def _create_status_section(self, parent_layout):
        """Create status and storage information section."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QVBoxLayout(status_frame)
        
        # Status text area
        status_header = QHBoxLayout()
        status_label = QLabel("System Status:")
        status_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        # Storage indicator
        self.storage_indicator = QLabel("Storage: OK")
        self.storage_indicator.setAlignment(Qt.AlignRight)
        
        status_header.addWidget(status_label)
        status_header.addWidget(self.storage_indicator)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont("Courier", 9))
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addLayout(status_header)
        status_layout.addWidget(self.status_text)
        status_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(status_frame)
        
    def _setup_styling(self):
        """Set up application styling."""
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
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                background-color: #f9f9f9;
            }
            QPushButton:hover {
                background-color: #e9e9e9;
            }
            QPushButton:pressed {
                background-color: #d9d9d9;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton#ok_button {
                background-color: #4CAF50;
                color: white;
                border-color: #45a049;
            }
            QPushButton#no_button {
                background-color: #f44336;
                color: white;
                border-color: #da190b;
            }
            QPushButton#focus_button {
                background-color: #2196F3;
                color: white;
                border-color: #1976D2;
            }
        """)
        
        # Set object names for styling
        self.ok_button.setObjectName("ok_button")
        self.no_button.setObjectName("no_button")
        self.focus_button.setObjectName("focus_button")
        
    def _setup_connections(self):
        """Set up signal connections."""
        # Main action buttons
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.no_button.clicked.connect(self._on_no_clicked)
        
        # Depth adjustment buttons
        self.plus_button.clicked.connect(self._on_plus_clicked)
        self.minus_button.clicked.connect(self._on_minus_clicked)
        
        # Camera control buttons
        self.brighter_button.clicked.connect(self._on_brighter_clicked)
        self.darker_button.clicked.connect(self._on_darker_clicked)
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
            self._log_status("Live camera preview started")
        else:
            self._log_status("WARNING: Camera not initialized - running in development mode")
    
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
    
    def _update_workflow_state(self):
        """Update UI based on current workflow state."""
        if self.workflow_state == WorkflowState.MAIN_INPUT:
            self.workflow_status_label.setText("Enter project and borehole information")
            self.ok_button.setText("OK")
            self.ok_button.setEnabled(True)
            self.no_button.setEnabled(False)
            
        elif self.workflow_state == WorkflowState.POSITIONING:
            self.workflow_status_label.setText("Position cameras and set depth range - Press OK to capture")
            self.ok_button.setText("CAPTURE")
            self.ok_button.setEnabled(True)
            self.no_button.setEnabled(True)
            
        elif self.workflow_state == WorkflowState.CAPTURING:
            self.workflow_status_label.setText("Capturing stereo pair...")
            self.ok_button.setEnabled(False)
            self.no_button.setEnabled(False)
            
        elif self.workflow_state == WorkflowState.REVIEWING_CAM1:
            self.workflow_status_label.setText("Review Camera 1 image quality")
            
        elif self.workflow_state == WorkflowState.REVIEWING_CAM2:
            self.workflow_status_label.setText("Review Camera 2 image quality")
            
        elif self.workflow_state == WorkflowState.SAVING:
            self.workflow_status_label.setText("Saving images...")
            
        elif self.workflow_state == WorkflowState.FOCUS_MODE:
            self.workflow_status_label.setText("Focus adjustment mode")
    
    def _on_ok_clicked(self):
        """Handle OK button click - main workflow action."""
        if not self._validate_inputs():
            return
        
        try:
            if self.workflow_state == WorkflowState.MAIN_INPUT:
                # Move to positioning mode
                self._update_current_values()
                self.workflow_state = WorkflowState.POSITIONING
                self._update_workflow_state()
                self._log_status(f"Project: {self.current_project}, Borehole: {self.current_borehole}")
                
            elif self.workflow_state == WorkflowState.POSITIONING:
                # Capture stereo pair
                self._capture_stereo_pair()
                
        except Exception as e:
            self._show_error(f"Error: {str(e)}")
            self.logger.error(f"OK button error: {e}")
    
    def _capture_stereo_pair(self):
        """Capture stereo pair and start review process."""
        try:
            self.workflow_state = WorkflowState.CAPTURING
            self._update_workflow_state()
            
            self._log_status("Capturing stereo pair...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(25)
            
            # Capture images
            left_image, right_image = self.camera.capture_stereo_pair()
            
            if left_image is None or right_image is None:
                self._show_error("Failed to capture images from cameras")
                self._return_to_positioning()
                return
                
            self.progress_bar.setValue(50)
            self.captured_images = (left_image, right_image)
            
            # Start image review process
            self._start_image_review()
            
        except Exception as e:
            self._show_error(f"Capture failed: {str(e)}")
            self.logger.error(f"Capture error: {e}")
            self._return_to_positioning()
        finally:
            self.progress_bar.setVisible(False)
    
    def _start_image_review(self):
        """Start the image review process with Camera 1."""
        try:
            self.workflow_state = WorkflowState.REVIEWING_CAM1
            self._update_workflow_state()
            
            # Create preview dialog if it doesn't exist
            if not self.preview_dialog:
                self.preview_dialog = PreviewDialog(self)
            
            # Show Camera 1 image
            camera1_accepted = self.preview_dialog.show_image(
                self.captured_images[0],
                "Camera 1 Preview",
                "Check image quality and clarity. Press OK to continue or NO to retake."
            )
            
            if camera1_accepted:
                self._review_camera2()
            else:
                self._discard_images()
                
        except Exception as e:
            self._show_error(f"Image review failed: {str(e)}")
            self._return_to_positioning()
    
    def _review_camera2(self):
        """Review Camera 2 image."""
        try:
            self.workflow_state = WorkflowState.REVIEWING_CAM2
            self._update_workflow_state()
            
            # Show Camera 2 image
            camera2_accepted = self.preview_dialog.show_image(
                self.captured_images[1],
                "Camera 2 Preview", 
                "Check image quality and clarity. Press OK to save or NO to retake."
            )
            
            if camera2_accepted:
                self._save_images()
            else:
                self._discard_images()
                
        except Exception as e:
            self._show_error(f"Camera 2 review failed: {str(e)}")
            self._return_to_positioning()
    
    def _save_images(self):
        """Save the captured stereo pair."""
        if self.captured_images is None:
            return
            
        try:
            self.workflow_state = WorkflowState.SAVING
            self._update_workflow_state()
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(75)
            
            # Generate file path according to specification
            # Format: ProjectName/BoreholeName/BoreholeName-From-To-C.jpg
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
                # Backup to USB if available
                storage_result = self.storage.save_images_to_storage(filenames)
                
                if storage_result['usb_success']:
                    self._log_status(f"✓ Images saved to internal storage and USB drive")
                else:
                    self._log_status(f"✓ Images saved to internal storage (USB backup failed)")
                
                # Advance to next segment
                self._advance_to_next_segment()
                
            else:
                self._show_error("Failed to save images")
                self._return_to_positioning()
                
        except Exception as e:
            self._show_error(f"Save failed: {str(e)}")
            self.logger.error(f"Save error: {e}")
            self._return_to_positioning()
        finally:
            self.progress_bar.setVisible(False)
            self.captured_images = None
    
    def _discard_images(self):
        """Discard current captured images and return to positioning."""
        self.captured_images = None
        self._log_status("Images discarded - returning to positioning mode")
        self._return_to_positioning()
    
    def _return_to_positioning(self):
        """Return to positioning mode."""
        self.workflow_state = WorkflowState.POSITIONING
        self._update_workflow_state()
    
    def _advance_to_next_segment(self):
        """Advance to next segment after successful capture."""
        # From becomes previous To, To becomes From + default segment length
        new_from = self.current_depth_to
        new_to = new_from + self.config['ui']['default_segment_length']
        
        self.depth_from_input.setText(f"{new_from:.2f}")
        self.depth_to_input.setText(f"{new_to:.2f}")
        
        self._log_status(f"✓ Advanced to next segment: {new_from:.2f}m - {new_to:.2f}m")
        
        # Return to positioning mode for next capture
        self.workflow_state = WorkflowState.POSITIONING
        self._update_workflow_state()
    
    def _on_no_clicked(self):
        """Handle NO button click - cancel current operation."""
        if self.workflow_state == WorkflowState.POSITIONING:
            # Reset to main input
            self.workflow_state = WorkflowState.MAIN_INPUT
            self._update_workflow_state()
            self._log_status("Operation cancelled - ready for new project")
        else:
            self._discard_images()
    
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
            self._log_status("Failed to adjust exposure")
    
    def _on_darker_clicked(self):
        """Handle DARKER button click."""
        if self.camera.adjust_exposure('darker'):
            self._log_status("Exposure decreased (darker)")
        else:
            self._log_status("Failed to adjust exposure")
    
    def _on_focus_clicked(self):
        """Handle FOCUS button click - open focus adjustment dialog."""
        try:
            # Create focus dialog if it doesn't exist
            if not self.focus_dialog:
                self.focus_dialog = FocusDialog(self, self.camera)
            
            # Show focus dialog
            self.workflow_state = WorkflowState.FOCUS_MODE
            self._update_workflow_state()
            
            result = self.focus_dialog.exec()
            
            # Return to previous state
            self.workflow_state = WorkflowState.POSITIONING
            self._update_workflow_state()
            
            if result == QDialog.Accepted:
                self._log_status("Focus adjustment completed")
            else:
                self._log_status("Focus adjustment cancelled")
                
        except Exception as e:
            self.logger.error(f"Focus dialog error: {e}")
            self._return_to_positioning()
    
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
        try:
            self.current_depth_from = float(self.depth_from_input.text())
            self.current_depth_to = float(self.depth_to_input.text())
        except ValueError:
            # Keep previous values if parsing fails
            pass
    
    def _update_storage_info(self):
        """Update storage information display."""
        try:
            storage_info = self.storage.check_storage_space()
            
            # Update storage indicator
            internal = storage_info['internal']
            warning_level = internal['warning_level']
            
            if warning_level == 'critical':
                self.storage_indicator.setText("⚠️ Storage Critical")
                self.storage_indicator.setStyleSheet("color: red; font-weight: bold;")
            elif warning_level == 'low':
                self.storage_indicator.setText("⚠️ Storage Low")
                self.storage_indicator.setStyleSheet("color: orange; font-weight: bold;")
            else:
                usb_count = len(storage_info['usb_drives'])
                if usb_count > 0:
                    self.storage_indicator.setText("✓ Storage OK (USB)")
                    self.storage_indicator.setStyleSheet("color: green;")
                else:
                    self.storage_indicator.setText("✓ Storage OK")
                    self.storage_indicator.setStyleSheet("color: green;")
                    
        except Exception as e:
            self.logger.error(f"Failed to update storage info: {e}")
            self.storage_indicator.setText("Storage: Unknown")
            self.storage_indicator.setStyleSheet("color: gray;")
    
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
            
        # Close dialogs
        if self.preview_dialog:
            self.preview_dialog.close()
        if self.focus_dialog:
            self.focus_dialog.close()
            
        event.accept() 