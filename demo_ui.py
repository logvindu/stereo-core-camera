#!/usr/bin/env python3
"""
Demo launcher for UI preview - uses PyQt5 and mock components for compatibility.
"""

import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    
    from src.config import ConfigManager
    from src.camera import StereoCamera
    from src.storage import StorageManager
    from src.ui.main_window_qt5 import MainWindow
    from src.utils import setup_logging, create_directories
    
    def main():
        """Demo main function."""
        print("🎬 Starting Stereo Core Camera UI Demo...")
        
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        
        # Disable fullscreen for demo
        config['ui']['fullscreen'] = False
        
        # Set up logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        logger.info("=== UI Demo Mode ===")
        
        # Create demo directories
        create_directories(config)
        
        # Initialize components (will use mock camera automatically)
        storage = StorageManager(config)
        camera = StereoCamera(config)
        
        # Initialize camera (will use mock since Picamera2 unavailable)
        camera.initialize()
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Stereo Core Camera Demo")
        
        # Create main window
        main_window = MainWindow(config, camera, storage)
        main_window.show()
        
        print("✅ UI Demo launched successfully!")
        print("📋 Demo Features:")
        print("   • Full UI layout preview")
        print("   • Interactive buttons and controls")
        print("   • Mock capture workflow")
        print("   • Status logging")
        print("   • Input validation")
        print("")
        print("🔧 Try the following:")
        print("   1. Enter project and borehole names")
        print("   2. Click OK to simulate capture")
        print("   3. Test +/- buttons for depth adjustment")
        print("   4. Try BRIGHTER/DARKER exposure controls")
        print("   5. Test FOCUS adjustment dialog")
        print("")
        
        # Run the application
        return app.exec_()

    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Error: Missing dependencies - {e}")
    print("\n🔧 To install dependencies, run:")
    print("   pip install PyQt5 PyYAML numpy Pillow psutil")
    print("\nOr use the requirements file:")
    print("   pip install -r requirements_dev.txt")
    sys.exit(1) 