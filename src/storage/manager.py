"""
Storage Manager for handling file operations, USB detection, and disk space monitoring.
"""

import os
import shutil
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any


class StorageManager:
    """
    Manages file storage operations including:
    - Internal storage management
    - USB drive detection and mounting
    - Disk space monitoring and warnings
    - File operations (save, copy, delete)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Storage paths
        self.internal_path = Path(config['storage']['internal_path'])
        self.usb_mount_paths = config['storage']['usb_mount_paths']
        
        # Space thresholds (convert to bytes)
        self.low_space_warning = config['storage']['low_space_warning'] * 1024 * 1024
        self.critical_space_warning = config['storage']['critical_space_warning'] * 1024 * 1024
        
        # Create internal storage directory
        self.internal_path.mkdir(parents=True, exist_ok=True)
        
    def get_available_usb_drives(self) -> List[str]:
        """
        Detect available USB drives.
        Returns: List of USB mount paths
        """
        usb_drives = []
        
        try:
            # Get all mounted partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                # Check if partition is in USB mount paths
                for usb_path in self.usb_mount_paths:
                    if partition.mountpoint.startswith(usb_path):
                        # Verify it's accessible and writable
                        if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.W_OK):
                            usb_drives.append(partition.mountpoint)
                            
        except Exception as e:
            self.logger.error(f"Error detecting USB drives: {e}")
            
        self.logger.info(f"Found USB drives: {usb_drives}")
        return usb_drives
    
    def get_disk_space(self, path: str) -> Tuple[int, int, int]:
        """
        Get disk space information for a path.
        Returns: (total_bytes, used_bytes, free_bytes)
        """
        try:
            usage = shutil.disk_usage(path)
            return usage.total, usage.used, usage.free
        except Exception as e:
            self.logger.error(f"Error getting disk space for {path}: {e}")
            return 0, 0, 0
    
    def check_storage_space(self) -> Dict[str, Dict[str, Any]]:
        """
        Check storage space for internal and USB drives.
        Returns: Dictionary with space information and warnings
        """
        storage_info = {}
        
        # Check internal storage
        total, used, free = self.get_disk_space(str(self.internal_path))
        storage_info['internal'] = {
            'path': str(self.internal_path),
            'total_mb': total // (1024 * 1024),
            'used_mb': used // (1024 * 1024),
            'free_mb': free // (1024 * 1024),
            'warning_level': self._get_warning_level(free),
            'accessible': True
        }
        
        # Check USB drives
        usb_drives = self.get_available_usb_drives()
        storage_info['usb_drives'] = []
        
        for usb_path in usb_drives:
            total, used, free = self.get_disk_space(usb_path)
            storage_info['usb_drives'].append({
                'path': usb_path,
                'total_mb': total // (1024 * 1024),
                'used_mb': used // (1024 * 1024),
                'free_mb': free // (1024 * 1024),
                'warning_level': self._get_warning_level(free),
                'accessible': True
            })
        
        return storage_info
    
    def _get_warning_level(self, free_bytes: int) -> str:
        """
        Determine warning level based on free space.
        Returns: 'critical', 'low', or 'ok'
        """
        if free_bytes < self.critical_space_warning:
            return 'critical'
        elif free_bytes < self.low_space_warning:
            return 'low'
        else:
            return 'ok'
    
    def generate_file_path(self, project_name: str, borehole_name: str, 
                          depth_from: float, depth_to: float) -> str:
        """
        Generate file path based on project metadata.
        Format: ProjectName/BoreholeName/BoreholeName-From-To
        The camera controller will append -1.jpg and -2.jpg for the two cameras.
        """
        # Sanitize names for filesystem
        project_clean = self._sanitize_filename(project_name)
        borehole_clean = self._sanitize_filename(borehole_name)
        
        # Format depth values (replace decimal point with underscore for filename)
        from_str = f"{depth_from:.2f}".replace('.', '_')
        to_str = f"{depth_to:.2f}".replace('.', '_')
        
        # Build path according to specification: ProjectName/BoreholeName/BoreholeName-From-To
        folder_path = self.internal_path / project_clean / borehole_clean
        base_filename = f"{borehole_clean}-{from_str}-{to_str}"
        
        return str(folder_path / base_filename)
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing/replacing invalid characters.
        """
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        filename = filename.strip(' .')
        
        # Ensure it's not empty
        if not filename:
            filename = 'unnamed'
            
        return filename
    
    def save_images_to_storage(self, image_files: List[str], 
                              backup_to_usb: bool = True) -> Dict[str, Any]:
        """
        Save images to internal storage and optionally backup to USB.
        Returns: Dictionary with save results
        """
        results = {
            'internal_success': False,
            'usb_success': False,
            'internal_paths': [],
            'usb_paths': [],
            'errors': []
        }
        
        try:
            # Images should already be saved to internal storage by camera controller
            # Just verify they exist
            for file_path in image_files:
                if os.path.exists(file_path):
                    results['internal_paths'].append(file_path)
                else:
                    results['errors'].append(f"Internal file not found: {file_path}")
            
            if results['internal_paths']:
                results['internal_success'] = True
                self.logger.info(f"Internal save successful: {len(results['internal_paths'])} files")
            
            # Backup to USB if requested
            if backup_to_usb:
                usb_drives = self.get_available_usb_drives()
                
                if usb_drives:
                    usb_path = usb_drives[0]  # Use first available USB drive
                    
                    for internal_file in results['internal_paths']:
                        try:
                            # Recreate directory structure on USB
                            internal_path = Path(internal_file)
                            relative_path = internal_path.relative_to(self.internal_path)
                            usb_file_path = Path(usb_path) / "core_photos" / relative_path
                            
                            # Create directories
                            usb_file_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Copy file
                            shutil.copy2(internal_file, str(usb_file_path))
                            results['usb_paths'].append(str(usb_file_path))
                            
                        except Exception as e:
                            results['errors'].append(f"USB backup failed for {internal_file}: {e}")
                    
                    if results['usb_paths']:
                        results['usb_success'] = True
                        self.logger.info(f"USB backup successful: {len(results['usb_paths'])} files")
                else:
                    results['errors'].append("No USB drives available for backup")
            
        except Exception as e:
            results['errors'].append(f"Storage operation failed: {e}")
            self.logger.error(f"Storage save error: {e}")
        
        return results
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """
        Clean up files older than specified days.
        Returns: Number of files deleted
        """
        deleted_count = 0
        
        try:
            import time
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            
            for root, dirs, files in os.walk(self.internal_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        if os.path.getmtime(file_path) < cutoff_time:
                            os.remove(file_path)
                            deleted_count += 1
                            self.logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {file_path}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Cleanup operation failed: {e}")
        
        return deleted_count
    
    def get_storage_summary(self) -> str:
        """
        Get a human-readable storage summary.
        """
        storage_info = self.check_storage_space()
        
        lines = []
        
        # Internal storage
        internal = storage_info['internal']
        lines.append(f"Internal: {internal['free_mb']}MB free / {internal['total_mb']}MB total")
        
        if internal['warning_level'] != 'ok':
            lines.append(f"⚠️ Internal storage {internal['warning_level']} space warning")
        
        # USB drives
        usb_drives = storage_info['usb_drives']
        if usb_drives:
            for i, usb in enumerate(usb_drives):
                lines.append(f"USB {i+1}: {usb['free_mb']}MB free / {usb['total_mb']}MB total")
                
                if usb['warning_level'] != 'ok':
                    lines.append(f"⚠️ USB {i+1} {usb['warning_level']} space warning")
        else:
            lines.append("No USB drives detected")
        
        return "\n".join(lines) 