#!/usr/bin/env python3
"""
Main entry point for the Stereo Core Camera System.
"""

import sys
import logging
import signal
from pathlib import Path
from typing import Optional

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from src.config import ConfigManager
from src.camera import StereoCamera
from src.storage import StorageManager
from src.ui import MainWindow
from src.utils import setup_logging, create_directories, get_system_info, validate_camera_hardware


class StereoCoreCameraApp:
    """
    Main application class for the Stereo Core Camera System.
    """
    
    def __init__(self):
        self.config_manager: Optional[ConfigManager] = None
        self.config: Optional[dict] = None
        self.camera: Optional[StereoCamera] = None
        self.storage: Optional[StorageManager] = None
        self.main_window: Optional[MainWindow] = None
        self.app: Optional[QApplication] = None
        self.logger: Optional[logging.Logger] = None
        
    def initialize(self) -> bool:
        """
        Initialize the application components.
        Returns: True if successful, False otherwise
        """
        try:
            # Load configuration
            self.config_manager = ConfigManager("config.yaml")
            self.config = self.config_manager.load_config()
            
            # Set up logging
            setup_logging(self.config)
            self.logger = logging.getLogger(__name__)
            
            self.logger.info("=== Stereo Core Camera System Starting ===")
            
            # Create necessary directories
            create_directories(self.config)
            
            # Log system information
            system_info = get_system_info()
            self.logger.info(f"System Info: {system_info}")
            
            # Validate camera hardware
            camera_validation = validate_camera_hardware()
            self.logger.info(f"Camera Hardware: {camera_validation}")
            
            if camera_validation['errors']:
                for error in camera_validation['errors']:
                    self.logger.warning(f"Camera validation warning: {error}")
            
            # Initialize storage manager
            self.storage = StorageManager(self.config)
            self.logger.info("Storage manager initialized")
            
            # Initialize camera system
            self.camera = StereoCamera(self.config)
            
            if not self.camera.initialize():
                self.logger.error("Failed to initialize camera system")
                return False
                
            self.logger.info("Camera system initialized")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Initialization failed: {e}")
            else:
                print(f"Initialization failed: {e}")
            return False
    
    def create_qt_application(self) -> bool:
        """
        Create and configure the Qt application.
        Returns: True if successful, False otherwise
        """
        try:
            # Create QApplication
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Stereo Core Camera System")
            self.app.setApplicationVersion("1.0.0")
            
            # Set application properties for touchscreen
            self.app.setAttribute(Qt.AA_Use96Dpi)
            
            # Handle system signals for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.logger.info("Qt application created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Qt application: {e}")
            return False
    
    def create_main_window(self) -> bool:
        """
        Create and show the main application window.
        Returns: True if successful, False otherwise
        """
        try:
            # Ensure camera system is initialized before creating UI
            if not self.camera or not self.camera.is_initialized():
                self.logger.error("Camera system must be initialized before creating main window")
                return False
                
            self.main_window = MainWindow(self.config, self.camera, self.storage)
            self.main_window.show()
            
            self.logger.info("Main window created and shown")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create main window: {e}")
            return False
    
    def run(self) -> int:
        """
        Run the application.
        Returns: Exit code
        """
        try:
            if not self.initialize():
                self._show_error("Failed to initialize application")
                return 1
            
            if not self.create_qt_application():
                self._show_error("Failed to create Qt application")
                return 1
                
            if not self.create_main_window():
                self._show_error("Failed to create main window")
                return 1
            
            self.logger.info("Application started successfully")
            
            # Run the Qt event loop
            exit_code = self.app.exec()
            
            self.logger.info(f"Application exiting with code: {exit_code}")
            return exit_code
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            return 0
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            return 1
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up application resources."""
        try:
            self.logger.info("Cleaning up application resources...")
            
            # Clean up camera
            if self.camera:
                self.camera.cleanup()
                self.logger.info("Camera resources cleaned up")
            
            # Close main window
            if self.main_window:
                self.main_window.close()
                self.logger.info("Main window closed")
            
            # Quit Qt application
            if self.app:
                self.app.quit()
                self.logger.info("Qt application quit")
                
            self.logger.info("=== Stereo Core Camera System Shutdown ===")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Cleanup error: {e}")
            else:
                print(f"Cleanup error: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        signal_names = {
            signal.SIGINT: "SIGINT",
            signal.SIGTERM: "SIGTERM"
        }
        signal_name = signal_names.get(signum, f"Signal {signum}")
        
        if self.logger:
            self.logger.info(f"Received {signal_name}, shutting down gracefully...")
        
        if self.app:
            self.app.quit()
    
    def _show_error(self, message: str):
        """Show error message to user."""
        if self.logger:
            self.logger.error(message)
        
        if self.app:
            QMessageBox.critical(None, "Application Error", message)
        else:
            print(f"ERROR: {message}")


def main():
    """Main entry point."""
    app = StereoCoreCameraApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 