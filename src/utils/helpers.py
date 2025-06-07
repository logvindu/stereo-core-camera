"""
Utility helper functions for the Stereo Core Camera System.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Set up logging configuration.
    """
    log_config = config.get('logging', {})
    
    # Get logging parameters
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_file = log_config.get('file', '/tmp/stereo_camera.log')
    max_size_mb = log_config.get('max_size_mb', 10)
    
    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size_mb * 1024 * 1024,
        backupCount=3
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging configured: level={log_level}, file={log_file}")


def create_directories(config: Dict[str, Any]) -> None:
    """
    Create necessary directories for the application.
    """
    # Create internal storage directory
    import os
    default_path = os.path.expanduser('~/core_photos')
    internal_path = config.get('storage', {}).get('internal_path', default_path)
    Path(internal_path).mkdir(parents=True, exist_ok=True)
    
    # Create log directory
    log_file = config.get('logging', {}).get('file', '/tmp/stereo_camera.log')
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Directories created: {internal_path}")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.2 MB")
    """
    if size_bytes == 0:
        return "0 B"
        
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import psutil
    
    try:
        info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': format_file_size(psutil.virtual_memory().total),
            'memory_available': format_file_size(psutil.virtual_memory().available),
        }
        
        # Check if we're on Raspberry Pi
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Raspberry Pi' in cpuinfo:
                    info['is_raspberry_pi'] = True
                    # Extract Pi model
                    for line in cpuinfo.split('\n'):
                        if line.startswith('Model'):
                            info['pi_model'] = line.split(':')[1].strip()
                            break
                else:
                    info['is_raspberry_pi'] = False
        except Exception:
            info['is_raspberry_pi'] = False
            
        return info
        
    except Exception as e:
        logging.error(f"Failed to get system info: {e}")
        return {'error': str(e)}


def validate_camera_hardware() -> Dict[str, Any]:
    """
    Validate camera hardware availability.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'picamera2_available': False,
        'cameras_detected': 0,
        'errors': []
    }
    
    try:
        # Check if picamera2 is available
        from picamera2 import Picamera2
        results['picamera2_available'] = True
        
        # Try to detect cameras
        try:
            # This is a simple check - in practice you'd want more thorough detection
            camera_list = Picamera2.global_camera_info()
            results['cameras_detected'] = len(camera_list)
            results['camera_info'] = camera_list
            
            if results['cameras_detected'] < 2:
                results['errors'].append(f"Only {results['cameras_detected']} camera(s) detected, need 2 for stereo")
                
        except Exception as e:
            results['errors'].append(f"Camera detection failed: {e}")
            
    except ImportError as e:
        results['errors'].append(f"Picamera2 not available: {e}")
        
    return results 