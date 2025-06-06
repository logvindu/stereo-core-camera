"""
Configuration Manager for loading and managing YAML configuration files.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Manages application configuration from YAML files.
    Handles loading, validation, and default values.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self._config: Optional[Dict[str, Any]] = None
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        Returns: Configuration dictionary
        """
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Config file not found: {self.config_path}")
                return self._get_default_config()
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            if not config:
                self.logger.warning("Empty config file, using defaults")
                return self._get_default_config()
                
            # Validate and merge with defaults
            self._config = self._validate_and_merge_config(config)
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
            return self._config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to YAML file.
        Returns: Success status
        """
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
                
            self._config = config
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration. Load if not already loaded.
        Returns: Configuration dictionary
        """
        if self._config is None:
            return self.load_config()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update specific configuration values.
        Returns: Success status
        """
        try:
            current_config = self.get_config()
            
            # Deep merge updates
            self._deep_merge(current_config, updates)
            
            return self.save_config(current_config)
            
        except Exception as e:
            self.logger.error(f"Failed to update config: {e}")
            return False
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """
        Deep merge updates into base dictionary.
        """
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _validate_and_merge_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration and merge with defaults.
        Returns: Validated configuration
        """
        default_config = self._get_default_config()
        
        # Start with defaults
        validated_config = default_config.copy()
        
        # Deep merge user config
        self._deep_merge(validated_config, config)
        
        # Validate specific sections
        self._validate_camera_config(validated_config.get('camera', {}))
        self._validate_ui_config(validated_config.get('ui', {}))
        self._validate_storage_config(validated_config.get('storage', {}))
        
        return validated_config
    
    def _validate_camera_config(self, camera_config: Dict[str, Any]) -> None:
        """Validate camera configuration section."""
        # Validate resolution
        resolution = camera_config.get('resolution', [3280, 2464])
        if not isinstance(resolution, list) or len(resolution) != 2:
            self.logger.warning("Invalid camera resolution, using default")
            camera_config['resolution'] = [3280, 2464]
        
        # Validate exposure range
        exposure_range = camera_config.get('exposure_range', [100, 800000])
        if not isinstance(exposure_range, list) or len(exposure_range) != 2:
            self.logger.warning("Invalid exposure range, using default")
            camera_config['exposure_range'] = [100, 800000]
        
        # Validate camera IDs
        for cam_id in ['camera_0_id', 'camera_1_id']:
            if not isinstance(camera_config.get(cam_id), int):
                self.logger.warning(f"Invalid {cam_id}, using default")
                camera_config[cam_id] = 0 if cam_id == 'camera_0_id' else 1
    
    def _validate_ui_config(self, ui_config: Dict[str, Any]) -> None:
        """Validate UI configuration section."""
        # Validate window size
        window_size = ui_config.get('window_size', [800, 600])
        if not isinstance(window_size, list) or len(window_size) != 2:
            self.logger.warning("Invalid window size, using default")
            ui_config['window_size'] = [800, 600]
        
        # Validate numeric values
        for key, default_value in [
            ('default_segment_length', 0.5),
            ('segment_adjustment_step', 0.05),
            ('preview_timeout', 30)
        ]:
            if not isinstance(ui_config.get(key), (int, float)):
                self.logger.warning(f"Invalid {key}, using default")
                ui_config[key] = default_value
    
    def _validate_storage_config(self, storage_config: Dict[str, Any]) -> None:
        """Validate storage configuration section."""
        # Validate paths
        if not storage_config.get('internal_path'):
            storage_config['internal_path'] = "/home/pi/core_photos"
        
        if not isinstance(storage_config.get('usb_mount_paths'), list):
            storage_config['usb_mount_paths'] = ["/media/pi", "/mnt/usb"]
        
        # Validate warning thresholds
        for key, default_value in [
            ('low_space_warning', 1000),
            ('critical_space_warning', 500),
            ('image_quality', 95)
        ]:
            if not isinstance(storage_config.get(key), (int, float)):
                self.logger.warning(f"Invalid {key}, using default")
                storage_config[key] = default_value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values.
        Returns: Default configuration dictionary
        """
        return {
            'camera': {
                'resolution': [3280, 2464],
                'format': "RGB888",
                'framerate': 15,
                'camera_0_id': 0,
                'camera_1_id': 1,
                'exposure_modes': ["auto", "manual"],
                'default_exposure': "auto",
                'exposure_range': [100, 800000],
                'autofocus_enabled': False,
                'focus_range': [0, 1023]
            },
            'ui': {
                'window_title': "Stereo Core Camera System",
                'window_size': [800, 600],
                'fullscreen': True,
                'default_segment_length': 0.5,
                'segment_adjustment_step': 0.05,
                'preview_size': [640, 480],
                'preview_timeout': 30
            },
            'storage': {
                'internal_path': "/home/pi/core_photos",
                'usb_mount_paths': ["/media/pi", "/mnt/usb"],
                'low_space_warning': 1000,
                'critical_space_warning': 500,
                'image_format': "JPEG",
                'image_quality': 95
            },
            'logging': {
                'level': "INFO",
                'file': "/home/pi/stereo_camera.log",
                'max_size_mb': 10
            }
        } 