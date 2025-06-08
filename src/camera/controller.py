"""
Stereo Camera Controller using Picamera2 API for dual IMX219 cameras.
Handles camera initialization, capture, exposure, and focus control.
"""

import logging
import time
import threading
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
import numpy as np
from PIL import Image

try:
    from picamera2 import Picamera2
    from libcamera import controls
except ImportError:
    # For development on non-Pi systems
    print("Warning: Picamera2 not available. Using mock camera for development.")
    Picamera2 = None
    controls = None


class MockCamera:
    """Mock camera for development on non-Pi systems."""
    
    def __init__(self, camera_id: int):
        self.camera_id = camera_id
        self._running = False
        self._focus_position = 500  # Mock focus position
        
    def configure(self, config: Dict[str, Any]) -> None:
        pass
        
    def start(self) -> None:
        self._running = True
        
    def stop(self) -> None:
        self._running = False
        
    def capture_array(self) -> np.ndarray:
        # Return a mock image array
        return np.random.randint(0, 255, (2464, 3280, 3), dtype=np.uint8)
        
    def capture_file(self, filename: str) -> None:
        # Create a mock image file
        img = Image.fromarray(self.capture_array())
        img.save(filename)
        
    def set_controls(self, controls: Dict[str, Any]) -> None:
        # Mock focus control simulation
        if "LensPosition" in controls:
            self._focus_position = controls["LensPosition"]
            print(f"MockCamera {self.camera_id}: Focus set to {self._focus_position}")


class StereoCamera:
    """
    Stereo camera controller for dual IMX219 cameras.
    Manages both cameras simultaneously for stereo photography.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Camera settings
        self.resolution = tuple(config['camera']['resolution'])
        self.format = config['camera']['format']
        self.framerate = config['camera']['framerate']
        
        # Camera IDs
        self.camera_0_id = config['camera']['camera_0_id']
        self.camera_1_id = config['camera']['camera_1_id']
        
        # Exposure settings
        self.exposure_range = config['camera']['exposure_range']
        self.current_exposure_mode = config['camera']['default_exposure']
        self.manual_exposure_time = 10000  # microseconds
        
        # Focus settings for IMX219 - 8 discrete steps (0-7)
        self.focus_steps = config['camera'].get('focus_steps', 8)  # Total number of discrete focus positions
        default_step = config['camera'].get('default_focus_step', 3)
        self.focus_step_0 = default_step  # Starting focus step for camera 0
        self.focus_step_1 = default_step  # Starting focus step for camera 1
        self.focus_range = config['camera']['focus_range']  # Continuous range for API mapping
        
        # Camera instances
        self.camera_0: Optional[Picamera2] = None
        self.camera_1: Optional[Picamera2] = None
        
        # Thread safety
        self._lock = threading.Lock()
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize both cameras."""
        try:
            with self._lock:
                self.logger.info("Initializing stereo cameras...")
                
                # Initialize camera 0 (left)
                if Picamera2:
                    try:
                        self.logger.info("Creating Picamera2 instances...")
                        self.camera_0 = Picamera2(self.camera_0_id)
                        self.camera_1 = Picamera2(self.camera_1_id)
                        self.logger.info("Picamera2 instances created successfully")
                    except Exception as e:
                        self.logger.error(f"Failed to create Picamera2 instances: {e}")
                        raise
                else:
                    self.camera_0 = MockCamera(self.camera_0_id)
                    self.camera_1 = MockCamera(self.camera_1_id)
                
                # Configure cameras
                try:
                    self.logger.info("Configuring cameras...")
                    self._configure_camera(self.camera_0, "Camera 0")
                    self._configure_camera(self.camera_1, "Camera 1")
                    self.logger.info("Camera configuration completed")
                except Exception as e:
                    self.logger.error(f"Failed to configure cameras: {e}")
                    raise
                
                # Start cameras
                try:
                    self.logger.info("Starting cameras...")
                    self.camera_0.start()
                    self.logger.info("Camera 0 started")
                    self.camera_1.start()
                    self.logger.info("Camera 1 started")
                except Exception as e:
                    self.logger.error(f"Failed to start cameras: {e}")
                    raise
                
                # Wait for cameras to stabilize
                self.logger.info("Waiting for cameras to stabilize...")
                time.sleep(2)
                
                self._initialized = True
                self.logger.info("Stereo cameras initialized successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to initialize cameras: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            self.cleanup()
            return False
    
    def _configure_camera(self, camera: Any, name: str) -> None:
        """Configure a single camera with optimal settings."""
        try:
            # For OV64A40 cameras, use Picamera2's create_still_configuration method
            # This automatically creates the proper structure with 'main' and 'raw' keys
            self.logger.info(f"Creating configuration for {name}")
            
            config = camera.create_still_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            
            self.logger.info(f"Attempting to configure {name} with still config")
            camera.configure(config)
            self.logger.info(f"{name} configured successfully with RGB888 format")
            
        except Exception as e:
            self.logger.error(f"Still configuration failed for {name}: {e}")
            
            # Fallback to preview configuration
            try:
                self.logger.info(f"Trying preview configuration for {name}")
                
                config = camera.create_preview_configuration(
                    main={"size": (640, 480)}
                )
                
                self.logger.info(f"Preview config for {name}: {config}")
                camera.configure(config)
                self.logger.info(f"{name} configured with preview configuration")
                
            except Exception as fallback_error:
                self.logger.error(f"Preview configuration also failed for {name}: {fallback_error}")
                
                # Last resort: try default configuration
                try:
                    self.logger.info(f"Trying default configuration for {name}")
                    config = camera.create_preview_configuration()
                    camera.configure(config)
                    self.logger.info(f"{name} configured with default configuration")
                    
                except Exception as default_error:
                    self.logger.error(f"All configuration methods failed for {name}: {default_error}")
                    raise
    
    def is_initialized(self) -> bool:
        """Check if cameras are initialized."""
        return self._initialized
    
    def capture_stereo_pair(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Capture a stereo pair of images simultaneously.
        Returns: (left_image, right_image) as numpy arrays or (None, None) on failure.
        """
        if not self._initialized:
            self.logger.error("Cameras not initialized")
            return None, None
            
        try:
            with self._lock:
                self.logger.info("Capturing stereo pair...")
                
                # Capture from both cameras simultaneously
                image_0 = self.camera_0.capture_array()
                image_1 = self.camera_1.capture_array()
                
                self.logger.info("Stereo pair captured successfully")
                return image_0, image_1
                
        except Exception as e:
            self.logger.error(f"Failed to capture stereo pair: {e}")
            return None, None
    
    def save_stereo_pair(self, image_0: np.ndarray, image_1: np.ndarray, 
                        base_filename: str) -> Tuple[bool, List[str]]:
        """
        Save stereo pair to files.
        Returns: (success, [filename_0, filename_1])
        """
        try:
            # Generate filenames
            filename_0 = f"{base_filename}-1.jpg"
            filename_1 = f"{base_filename}-2.jpg"
            
            # Ensure directories exist
            Path(filename_0).parent.mkdir(parents=True, exist_ok=True)
            Path(filename_1).parent.mkdir(parents=True, exist_ok=True)
            
            # Save images
            Image.fromarray(image_0).save(filename_0, 'JPEG', 
                                        quality=self.config['storage']['image_quality'])
            Image.fromarray(image_1).save(filename_1, 'JPEG', 
                                        quality=self.config['storage']['image_quality'])
            
            self.logger.info(f"Stereo pair saved: {filename_0}, {filename_1}")
            return True, [filename_0, filename_1]
            
        except Exception as e:
            self.logger.error(f"Failed to save stereo pair: {e}")
            return False, []
    
    def adjust_exposure(self, direction: str) -> bool:
        """
        Adjust exposure for both cameras simultaneously.
        Direction: 'brighter' or 'darker'.
        Returns: success status
        """
        if not self._initialized:
            return False
            
        try:
            with self._lock:
                if direction == 'brighter':
                    self.manual_exposure_time = min(
                        self.manual_exposure_time * 1.5,
                        self.exposure_range[1]
                    )
                elif direction == 'darker':
                    self.manual_exposure_time = max(
                        self.manual_exposure_time / 1.5,
                        self.exposure_range[0]
                    )
                else:
                    return False
                
                # Apply exposure to both cameras
                exposure_controls = {"ExposureTime": int(self.manual_exposure_time)}
                
                if Picamera2 and controls:
                    try:
                        self.camera_0.set_controls(exposure_controls)
                        self.camera_1.set_controls(exposure_controls)
                    except Exception as e:
                        self.logger.warning(f"Exposure control failed: {e}")
                        return False
                
                self.logger.info(f"Exposure adjusted {direction}: {self.manual_exposure_time}μs")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to adjust exposure: {e}")
            return False
    
    def adjust_focus(self, direction: str, camera_index: int = 0) -> bool:
        """
        Adjust focus for specified camera using discrete steps (0-7).
        Args:
            direction: 'increase' or 'decrease'
            camera_index: 0 for camera_0 (left), 1 for camera_1 (right)
        Returns: success status
        """
        try:
            with self._lock:
                # Select the appropriate focus step variable
                current_step = self.focus_step_0 if camera_index == 0 else self.focus_step_1
                
                if direction == 'increase':
                    new_step = min(current_step + 1, self.focus_steps - 1)  # Max step is 7
                elif direction == 'decrease':
                    new_step = max(current_step - 1, 0)  # Min step is 0
                else:
                    return False
                
                # Check if step actually changed (boundary condition)
                if new_step == current_step:
                    self.logger.info(f"Focus at boundary for camera {camera_index}: step {current_step}")
                    return False  # No change made
                
                # Update the appropriate step variable
                if camera_index == 0:
                    self.focus_step_0 = new_step
                else:
                    self.focus_step_1 = new_step
                
                # Convert discrete step to continuous range for camera API
                # Map step 0-7 to the configured focus range
                lens_position = self.focus_range[0] + new_step * (self.focus_range[1] - self.focus_range[0]) / (self.focus_steps - 1)
                focus_controls = {"LensPosition": int(lens_position)}
                
                # Apply focus control if cameras are initialized
                if self._initialized and Picamera2 and controls:
                    try:
                        camera = self.camera_0 if camera_index == 0 else self.camera_1
                        camera.set_controls(focus_controls)
                    except Exception as e:
                        # Focus might not be available on all cameras
                        self.logger.warning(f"Focus control not available on camera {camera_index}: {e}")
                        pass
                
                self.logger.info(f"Focus adjusted {direction} for camera {camera_index}: step {new_step} (lens position: {int(lens_position)})")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to adjust focus for camera {camera_index}: {e}")
            return False
    
    def get_preview_frame(self, camera_index: int = 0) -> Optional[np.ndarray]:
        """
        Get a preview frame from specified camera.
        Args:
            camera_index: 0 for camera_0 (left), 1 for camera_1 (right)
        Returns: preview image as numpy array or None on failure.
        """
        if not self._initialized:
            return None
            
        try:
            # Select camera based on index
            camera = self.camera_0 if camera_index == 0 else self.camera_1
            
            # Get preview from main sensor
            if hasattr(camera, 'capture_array'):
                # Get main sensor preview
                preview = camera.capture_array()
                if preview is not None:
                    # Resize for preview performance
                    from PIL import Image
                    img = Image.fromarray(preview)
                    img.thumbnail((640, 480))
                    preview = np.array(img)
            else:
                # Mock camera
                preview = camera.capture_array()
                if preview is not None:
                    from PIL import Image
                    img = Image.fromarray(preview)
                    img.thumbnail((640, 480))
                    preview = np.array(img)
            
            return preview
            
        except Exception as e:
            self.logger.error(f"Failed to get preview frame from camera {camera_index}: {e}")
            return None
    
    def get_focus_step(self, camera_index: int = 0) -> int:
        """
        Get current focus step for specified camera.
        Args:
            camera_index: 0 for camera_0 (left), 1 for camera_1 (right)
        Returns: current focus step (0-7)
        """
        return self.focus_step_0 if camera_index == 0 else self.focus_step_1
    
    def set_focus_step(self, step: int, camera_index: int = 0) -> bool:
        """
        Set focus step for specified camera.
        Args:
            step: focus step (0-7)
            camera_index: 0 for camera_0 (left), 1 for camera_1 (right)
        Returns: success status
        """
        if not (0 <= step < self.focus_steps):
            self.logger.error(f"Invalid focus step {step}. Must be 0-{self.focus_steps-1}")
            return False
            
        try:
            with self._lock:
                # Update the appropriate step variable
                if camera_index == 0:
                    self.focus_step_0 = step
                else:
                    self.focus_step_1 = step
                
                # Convert discrete step to continuous range for camera API
                lens_position = self.focus_range[0] + step * (self.focus_range[1] - self.focus_range[0]) / (self.focus_steps - 1)
                focus_controls = {"LensPosition": int(lens_position)}
                
                # Apply focus control if cameras are initialized
                if self._initialized and Picamera2 and controls:
                    try:
                        camera = self.camera_0 if camera_index == 0 else self.camera_1
                        camera.set_controls(focus_controls)
                    except Exception as e:
                        self.logger.warning(f"Focus control not available on camera {camera_index}: {e}")
                        pass
                
                self.logger.info(f"Focus set for camera {camera_index}: step {step} (lens position: {int(lens_position)})")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set focus for camera {camera_index}: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up camera resources."""
        try:
            with self._lock:
                if self.camera_0:
                    self.camera_0.stop()
                    self.camera_0 = None
                    
                if self.camera_1:
                    self.camera_1.stop()
                    self.camera_1 = None
                    
                self._initialized = False
                self.logger.info("Camera resources cleaned up")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()

    def get_camera_status(self) -> Dict[str, Any]:
        """
        Get status information for both cameras.
        Returns: Dictionary with camera status information
        """
        status = {
            'initialized': self._initialized,
            'camera_0': {
                'available': self.camera_0 is not None,
                'type': 'Real Camera' if Picamera2 else 'Mock Camera',
                'focus_step': self.focus_step_0
            },
            'camera_1': {
                'available': self.camera_1 is not None,
                'type': 'Real Camera' if Picamera2 else 'Mock Camera',
                'focus_step': self.focus_step_1
            },
            'focus_steps_total': self.focus_steps,
            'current_exposure': self.manual_exposure_time,
            'resolution': self.resolution,
            'framerate': self.framerate
        }
        return status 