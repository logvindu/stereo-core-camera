# Stereo Core Camera System

A professional stereo camera system for photographing geological drill core samples using Raspberry Pi 5 and dual IMX219 cameras.

## Overview

This system captures high-quality stereo photographs of geological core samples laid on a 3.4m-long frame. The stereo camera is mounted on a manually movable carriage that operators slide along the core to capture sequential 0.5-meter segments.

## Hardware Requirements

### Core Components
- **Raspberry Pi 5 (4GB RAM)** - Main processing unit
- **2x Waveshare IMX219 8MP MIPI-CSI cameras** - Stereo imaging
- **5-inch HDMI touchscreen** - User interface
- **Bluetooth keyboard** - Text input support
- **Internal storage** - Primary image storage
- **USB storage device** - Backup storage

### Mechanical Setup
- Manual sliding carriage system
- Cameras mounted perpendicular to each other and to the core axis
- 3.4m core frame for sample positioning

## Software Features

### Main Interface
- **Input Fields**: Project name, Borehole name, Depth from/to
- **Control Buttons**: OK, NO, +/−, BRIGHTER, DARKER, FOCUS
- **Live Preview**: Real-time camera preview on touchscreen
- **Status Display**: System information and operation feedback

### Capture Workflow
1. Operator enters project metadata
2. Positions carriage at desired location
3. Presses OK to capture stereo pair
4. Reviews each image individually
5. Accepts or rejects captures
6. System automatically advances to next segment

### File Management
- **Naming Convention**: `ProjectName/BoreholeName/BoreholeName-From-To-C.jpg`
- **Dual Storage**: Automatic backup to USB drive
- **Space Monitoring**: Warnings for low disk space
- **Automatic Progression**: Depth ranges update after successful captures

## Installation

### 1. Raspberry Pi Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-venv git

# Enable camera interface
sudo raspi-config
# Navigate to Interface Options > Camera > Enable

# Reboot to apply changes
sudo reboot
```

### 2. Install Application

```bash
# Clone repository
git clone <repository-url> stereo-core-camera
cd stereo-core-camera

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configuration

Edit `config.yaml` to match your hardware setup:

```yaml
camera:
  resolution: [3280, 2464]  # IMX219 max resolution
  camera_0_id: 0           # Left camera ID
  camera_1_id: 1           # Right camera ID

storage:
  internal_path: "/home/pi/core_photos"
  usb_mount_paths:
    - "/media/pi"
    - "/mnt/usb"

ui:
  fullscreen: true
  default_segment_length: 0.5  # meters
```

### 4. Auto-start Setup (Optional)

Create a systemd service for automatic startup:

```bash
sudo nano /etc/systemd/system/stereo-camera.service
```

```ini
[Unit]
Description=Stereo Core Camera System
After=graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/stereo-core-camera
Environment=DISPLAY=:0
ExecStart=/home/pi/stereo-core-camera/venv/bin/python src/main.py
Restart=always

[Install]
WantedBy=graphical.target
```

```bash
sudo systemctl enable stereo-camera.service
sudo systemctl start stereo-camera.service
```

## Usage

### Starting the Application

```bash
cd stereo-core-camera
source venv/bin/activate
python src/main.py
```

### Basic Operation

1. **Enter Project Information**
   - Fill in Project Name and Borehole Name
   - Set initial Depth From and Depth To values

2. **Position and Capture**
   - Move carriage to desired position
   - Use preview to frame the shot
   - Adjust exposure if needed (BRIGHTER/DARKER)
   - Use FOCUS mode for manual focus adjustment
   - Press OK to capture stereo pair

3. **Review Images**
   - First camera image preview appears
   - Press OK to accept, NO to retry
   - Second camera image preview appears
   - Press OK to save both images

4. **Continue Workflow**
   - System automatically advances depth ranges
   - Use +/− buttons for fine adjustments
   - Repeat capture process for next segment

### Focus Adjustment

1. Press FOCUS button to enter focus mode
2. Use +/− buttons to adjust focus
3. Monitor live preview for sharpness
4. Press OK when satisfied

### Storage Management

- System monitors internal and USB storage space
- Warnings appear when space is low
- Images are automatically backed up to USB drive
- Check status display for storage information

## Troubleshooting

### Camera Issues

**Problem**: Cameras not detected
```bash
# Check camera connections
vcgencmd get_camera

# List available cameras
libcamera-hello --list-cameras

# Test camera functionality
libcamera-still -o test.jpg
```

**Problem**: Poor image quality
- Check camera focus settings
- Adjust exposure using BRIGHTER/DARKER buttons
- Ensure adequate lighting
- Clean camera lenses

### Storage Issues

**Problem**: USB drive not detected
```bash
# List connected drives
lsblk

# Check mount points
df -h

# Manual mount (if needed)
sudo mount /dev/sda1 /media/pi/usb
```

### Performance Issues

**Problem**: Slow operation
- Ensure adequate cooling for Raspberry Pi
- Check available memory: `free -h`
- Monitor CPU usage: `htop`
- Consider reducing image resolution in config

### Application Errors

**Problem**: Application won't start
```bash
# Check logs
tail -f /home/pi/stereo_camera.log

# Test configuration
python -c "from src.config import ConfigManager; print(ConfigManager().load_config())"

# Validate dependencies
pip check
```

## File Structure

```
stereo-core-camera/
├── src/
│   ├── camera/
│   │   ├── controller.py      # Camera management
│   │   └── calibration.py     # Stereo calibration
│   ├── ui/
│   │   ├── main_window.py     # Main interface
│   │   ├── preview_dialog.py  # Image preview
│   │   └── focus_dialog.py    # Focus adjustment
│   ├── storage/
│   │   └── manager.py         # File & USB management
│   ├── config/
│   │   └── manager.py         # Configuration handling
│   └── utils/
│       └── helpers.py         # Utility functions
├── config.yaml               # Configuration file
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug logging
PYTHONPATH=. python src/main.py --debug
```

### Testing on Non-Pi Systems

The application includes mock camera functionality for development on systems without Picamera2:

```python
# Mock cameras are automatically used when Picamera2 is unavailable
# This allows UI development and testing on desktop systems
```

### Adding Features

1. Camera features: Modify `src/camera/controller.py`
2. UI components: Add to `src/ui/`
3. Storage features: Extend `src/storage/manager.py`
4. Configuration: Update `config.yaml` and `src/config/manager.py`

## Support

### Log Files

- Application logs: `/home/pi/stereo_camera.log`
- System logs: `journalctl -u stereo-camera.service`

### Configuration

- Main config: `config.yaml`
- Camera settings: Adjust resolution, exposure, focus ranges
- UI settings: Window size, segment lengths, timeouts
- Storage settings: Paths, warning thresholds

### Hardware Validation

```bash
# Run hardware check
python -c "from src.utils.helpers import validate_camera_hardware; print(validate_camera_hardware())"
```

## License

[Specify your license here]

## Contributing

[Contribution guidelines if applicable] 