"""
Focus Dialog for adjusting camera focus in the Stereo Core Camera System.
"""

import logging
import numpy as np
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSizePolicy, QButtonGroup
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage, QFont


class FocusDialog(QDialog):
    """
    Dialog for adjusting camera focus with live preview.
    Shows live feed from cameras and allows focus adjustment.
    """
    
    def __init__(self, parent=None, camera=None):
        super().__init__(parent)
        self.camera = camera
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Focus Adjustment")
        self.setModal(True)
        self.resize(700, 600)
        
        # Current focus mode (0 = camera 1, 1 = camera 2)
        self.current_camera = 0
        
        # Live preview timer
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self._update_preview)
        
        self._setup_ui()
        self._setup_styling()
        self._start_preview()
        
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Focus Adjustment")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Camera selection
        self._create_camera_selection(layout)
        
        # Live preview area
        self._create_preview_area(layout)
        
        # Focus controls
        self._create_focus_controls(layout)
        
        # Action buttons
        self._create_action_buttons(layout)
        
    def _create_camera_selection(self, parent_layout):
        """Create camera selection buttons."""
        selection_frame = QFrame()
        selection_frame.setFrameStyle(QFrame.StyledPanel)
        selection_layout = QHBoxLayout(selection_frame)
        
        selection_label = QLabel("Select Camera:")
        selection_label.setFont(QFont("Arial", 12, QFont.Bold))
        selection_layout.addWidget(selection_label)
        
        # Camera selection buttons
        self.camera_button_group = QButtonGroup()
        
        self.camera1_button = QPushButton("Camera 1")
        self.camera1_button.setCheckable(True)
        self.camera1_button.setChecked(True)
        self.camera1_button.setMinimumSize(100, 40)
        self.camera_button_group.addButton(self.camera1_button, 0)
        
        self.camera2_button = QPushButton("Camera 2")
        self.camera2_button.setCheckable(True)
        self.camera2_button.setMinimumSize(100, 40)
        self.camera_button_group.addButton(self.camera2_button, 1)
        
        self.camera_button_group.buttonClicked.connect(self._on_camera_changed)
        
        selection_layout.addWidget(self.camera1_button)
        selection_layout.addWidget(self.camera2_button)
        selection_layout.addStretch()
        
        parent_layout.addWidget(selection_frame)
        
    def _create_preview_area(self, parent_layout):
        """Create live preview area."""
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.StyledPanel)
        preview_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout = QVBoxLayout(preview_frame)
        
        # Preview title
        self.preview_title = QLabel("Live Preview - Camera 1")
        self.preview_title.setAlignment(Qt.AlignCenter)
        self.preview_title.setFont(QFont("Arial", 12, QFont.Bold))
        preview_layout.addWidget(self.preview_title)
        
        # Preview display
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(500, 350)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #333;
                border: 2px solid #666;
                border-radius: 5px;
                color: white;
            }
        """)
        self.preview_label.setText("Starting live preview...")
        preview_layout.addWidget(self.preview_label)
        
        parent_layout.addWidget(preview_frame)
        
    def _create_focus_controls(self, parent_layout):
        """Create focus adjustment controls."""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Instructions
        instructions = QLabel("Use + and - buttons to adjust focus for the selected camera")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Arial", 11))
        controls_layout.addWidget(instructions)
        
        # Focus buttons
        focus_button_layout = QHBoxLayout()
        
        self.focus_minus_button = QPushButton("-")
        self.focus_minus_button.setMinimumSize(80, 60)
        self.focus_minus_button.clicked.connect(self._on_focus_decrease)
        
        self.focus_plus_button = QPushButton("+")
        self.focus_plus_button.setMinimumSize(80, 60)
        self.focus_plus_button.clicked.connect(self._on_focus_increase)
        
        # Focus status
        self.focus_status_label = QLabel("Focus: 500")
        self.focus_status_label.setAlignment(Qt.AlignCenter)
        self.focus_status_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        focus_button_layout.addWidget(self.focus_minus_button)
        focus_button_layout.addWidget(self.focus_status_label)
        focus_button_layout.addWidget(self.focus_plus_button)
        
        controls_layout.addLayout(focus_button_layout)
        parent_layout.addWidget(controls_frame)
        
    def _create_action_buttons(self, parent_layout):
        """Create OK/Cancel buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumSize(120, 50)
        self.cancel_button.clicked.connect(self.reject)
        
        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.setMinimumSize(120, 50)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        parent_layout.addLayout(button_layout)
        
    def _setup_styling(self):
        """Set up dialog styling."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f8f8;
            }
            QPushButton {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                background-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
                border-color: #1976D2;
            }
            QPushButton#ok_button {
                background-color: #4CAF50;
                color: white;
                border-color: #45a049;
            }
            QPushButton#cancel_button {
                background-color: #f44336;
                color: white;
                border-color: #da190b;
            }
            QFrame {
                background-color: white;
                border-radius: 5px;
            }
        """)
        
        # Set object names for styling
        self.ok_button.setObjectName("ok_button")
        self.cancel_button.setObjectName("cancel_button")
        
    def _start_preview(self):
        """Start live preview update."""
        if self.camera and self.camera.is_initialized():
            self.preview_timer.start(100)  # 10 FPS
        else:
            self.preview_label.setText("Camera not available\n(Running in development mode)")
            
    def _stop_preview(self):
        """Stop live preview update."""
        if self.preview_timer.isActive():
            self.preview_timer.stop()
            
    def _update_preview(self):
        """Update live preview display."""
        if not self.camera or not self.camera.is_initialized():
            return
            
        try:
            # Get preview frame from selected camera
            frame = self.camera.get_preview_frame(self.current_camera)
            
            if frame is not None:
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
                
                # Convert to pixmap and scale
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.preview_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.logger.error(f"Failed to update focus preview: {e}")
            
    def _on_camera_changed(self, button):
        """Handle camera selection change."""
        self.current_camera = self.camera_button_group.id(button)
        camera_name = "Camera 1" if self.current_camera == 0 else "Camera 2"
        self.preview_title.setText(f"Live Preview - {camera_name}")
        self.logger.info(f"Focus mode switched to {camera_name}")
        
    def _on_focus_increase(self):
        """Handle focus increase button."""
        if self.camera:
            success = self.camera.adjust_focus("increase", self.current_camera)
            if success:
                # Update focus status
                focus_value = getattr(self.camera, 'current_focus', 500)
                self.focus_status_label.setText(f"Focus: {focus_value}")
                self.logger.info(f"Focus increased for Camera {self.current_camera + 1}")
            
    def _on_focus_decrease(self):
        """Handle focus decrease button."""
        if self.camera:
            success = self.camera.adjust_focus("decrease", self.current_camera)
            if success:
                # Update focus status
                focus_value = getattr(self.camera, 'current_focus', 500)
                self.focus_status_label.setText(f"Focus: {focus_value}")
                self.logger.info(f"Focus decreased for Camera {self.current_camera + 1}")
                
    def exec(self):
        """Execute the dialog."""
        try:
            result = super().exec()
            return result
        finally:
            self._stop_preview()
            
    def closeEvent(self, event):
        """Handle dialog close."""
        self._stop_preview()
        super().closeEvent(event) 