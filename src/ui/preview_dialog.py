"""
Preview Dialog for reviewing captured images in the Stereo Core Camera System.
"""

import logging
import numpy as np
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QFont


class PreviewDialog(QDialog):
    """
    Dialog for previewing captured images with OK/NO options.
    Displays a captured image for operator review.
    """
    
    def __init__(self, parent=None, title: str = "Image Preview"):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle(title)
        self.setModal(True)
        
        # Make dialog larger for better image viewing
        self.resize(600, 500)
        
        self._setup_ui()
        self._setup_styling()
        
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Image display frame
        image_frame = QFrame()
        image_frame.setFrameStyle(QFrame.StyledPanel)
        image_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_layout = QVBoxLayout(image_frame)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 5px;
            }
        """)
        self.image_label.setScaledContents(False)
        image_layout.addWidget(self.image_label)
        
        layout.addWidget(image_frame)
        
        # Quality check message
        self.message_label = QLabel("Check image quality and clarity")
        self.message_label.setAlignment(Qt.AlignCenter)
        message_font = QFont()
        message_font.setPointSize(12)
        self.message_label.setFont(message_font)
        layout.addWidget(self.message_label)
        
        # Buttons
        self._create_buttons(layout)
        
    def _create_buttons(self, parent_layout):
        """Create OK/NO buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # NO button (reject)
        self.no_button = QPushButton("NO")
        self.no_button.setMinimumSize(120, 50)
        self.no_button.clicked.connect(self.reject)
        
        # OK button (accept)
        self.ok_button = QPushButton("OK")
        self.ok_button.setMinimumSize(120, 50)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.no_button)
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
            QFrame {
                background-color: white;
                border-radius: 5px;
            }
        """)
        
        # Set object names for styling
        self.ok_button.setObjectName("ok_button")
        self.no_button.setObjectName("no_button")
        
    def show_image(self, image: np.ndarray, title: str = "Image Preview", 
                   message: str = "Check image quality and clarity") -> bool:
        """
        Show an image in the preview dialog.
        
        Args:
            image: NumPy array containing the image
            title: Title for the dialog
            message: Message to display below image
            
        Returns:
            True if user clicked OK, False if NO
        """
        try:
            # Update title and message
            self.title_label.setText(title)
            self.message_label.setText(message)
            
            # Convert numpy array to QImage
            if len(image.shape) == 3:
                # Color image
                height, width, channel = image.shape
                if channel == 3:
                    # RGB
                    bytes_per_line = 3 * width
                    q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                elif channel == 4:
                    # RGBA
                    bytes_per_line = 4 * width
                    q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
                else:
                    raise ValueError(f"Unsupported number of channels: {channel}")
            else:
                # Grayscale
                height, width = image.shape
                bytes_per_line = width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            
            # Convert to pixmap and scale to fit
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale pixmap to fit label while maintaining aspect ratio
            label_size = self.image_label.size()
            scaled_pixmap = pixmap.scaled(
                label_size.width() - 10,  # Leave some padding
                label_size.height() - 10,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            
            # Show dialog and return result
            result = self.exec()
            return result == QDialog.Accepted
            
        except Exception as e:
            self.logger.error(f"Failed to show image in preview dialog: {e}")
            self.image_label.setText(f"Error displaying image:\n{str(e)}")
            return False
    
    def resizeEvent(self, event):
        """Handle resize events to scale image appropriately."""
        super().resizeEvent(event)
        
        # If we have a pixmap, rescale it
        if hasattr(self, 'image_label') and self.image_label.pixmap():
            pixmap = self.image_label.pixmap()
            label_size = self.image_label.size()
            scaled_pixmap = pixmap.scaled(
                label_size.width() - 10,
                label_size.height() - 10,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap) 