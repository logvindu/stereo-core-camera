# Enhanced Stereo Core Camera System - Complete Workflow Guide

## Overview

The Enhanced Stereo Core Camera System implements a complete operator workflow for capturing, reviewing, and managing stereo core photographs. The system provides real-time camera preview, image quality review, automatic file organization, and USB backup functionality.

## System Features

### Complete Operator Workflow
- **Project Setup**: Enter project and borehole names
- **Live Preview**: Real-time camera preview for positioning
- **Depth Management**: Automatic depth progression with manual adjustment
- **Image Capture**: Simultaneous stereo pair photography
- **Quality Review**: Sequential review of both camera images
- **File Management**: Automatic file naming and directory organization
- **USB Backup**: Automatic backup to inserted USB drives
- **Storage Monitoring**: Real-time storage space warnings

### Camera Controls
- **Exposure Adjustment**: BRIGHTER/DARKER buttons for lighting control
- **Focus Control**: Individual camera focus adjustment with live preview
- **Dual Camera Support**: Independent control of left and right cameras
- **Live Preview**: Real-time feed during positioning and focus adjustment

## Operator Workflow

### 1. System Startup
1. Power on the device using the POWER button
2. The system displays the main interface with project input fields
3. Live camera preview shows positioning feed

### 2. Project Setup
1. Using the Bluetooth keyboard, enter:
   - **Project Name**: Identifier for the project
   - **Borehole Name**: Specific borehole identifier
2. Press **OK** to proceed to positioning mode

### 3. Camera Positioning and Setup
1. Position cameras above the desired core interval
2. The live preview shows real-time feed from Camera 1
3. Adjust camera settings as needed:
   - **BRIGHTER/DARKER**: Adjust exposure for lighting conditions
   - **FOCUS**: Open focus adjustment dialog for precise focusing

### 4. Focus Adjustment (Optional)
1. Press **FOCUS** button to open focus dialog
2. Select Camera 1 or Camera 2 using toggle buttons
3. Use **+/-** buttons to adjust focus while viewing live preview
4. Press **OK** to confirm focus settings

### 5. Depth Range Entry
1. Enter depth range for the interval:
   - **Depth From (m)**: Starting depth of the interval
   - **Depth To (m)**: Ending depth of the interval
2. Use **+/-** buttons to adjust "Depth To" in 0.05m increments
3. Press **CAPTURE** when ready to photograph

### 6. Image Capture and Review
1. System captures images from both cameras simultaneously
2. **Camera 1 Review**: 
   - Review image quality and clarity
   - Press **OK** if satisfied, **NO** to retake
3. **Camera 2 Review**:
   - Review second camera image
   - Press **OK** to save both images, **NO** to retake

### 7. File Saving and Organization
1. Images are saved automatically with naming convention:
   - `ProjectName/BoreholeName/BoreholeName-From-To-1.jpg` (Camera 1)
   - `ProjectName/BoreholeName/BoreholeName-From-To-2.jpg` (Camera 2)
2. Files are saved to both internal storage and USB drive (if available)
3. System displays save confirmation

### 8. Automatic Progression
1. After successful save, system automatically:
   - Updates "Depth From" to previous "Depth To" value
   - Sets new "Depth To" to "From" + 0.5 meters
   - Returns to positioning mode for next interval

### 9. Manual Adjustments
- **+/-** buttons: Adjust "Depth To" value by ±0.05m
- **NO** button: Cancel current operation and return to project setup
- Depth values can be manually edited using the keyboard

### 10. Session End
1. Complete all required intervals
2. Power off the device using POWER button
3. Remove USB drive containing backup photos

## File Organization

### Directory Structure
```
Internal Storage / USB Drive:
├── ProjectName1/
│   ├── BoreholeName1/
│   │   ├── BoreholeName1-0_00-0_50-1.jpg
│   │   ├── BoreholeName1-0_00-0_50-2.jpg
│   │   ├── BoreholeName1-0_50-1_00-1.jpg
│   │   ├── BoreholeName1-0_50-1_00-2.jpg
│   │   └── ...
│   └── BoreholeName2/
│       └── ...
└── ProjectName2/
    └── ...
```

### File Naming Convention
- **Format**: `BoreholeName-From-To-C.jpg`
- **BoreholeName**: Sanitized borehole identifier
- **From**: Starting depth with decimal point as underscore
- **To**: Ending depth with decimal point as underscore  
- **C**: Camera number (1 for left camera, 2 for right camera)

**Examples**:
- `BORE_A1-0_00-0_50-1.jpg` (Camera 1, 0.00-0.50m)
- `BORE_A1-0_00-0_50-2.jpg` (Camera 2, 0.00-0.50m)
- `BORE_A1-0_50-1_00-1.jpg` (Camera 1, 0.50-1.00m)

## Storage Management

### Storage Monitoring
- Real-time storage space monitoring
- Visual indicators for storage status:
  - ✓ **Storage OK**: Sufficient space available
  - ✓ **Storage OK (USB)**: USB drive connected and available
  - ⚠️ **Storage Low**: Space below warning threshold
  - ⚠️ **Storage Critical**: Space critically low

### USB Backup
- Automatic detection of inserted USB drives
- Simultaneous save to internal storage and USB
- Directory structure replicated on USB drive
- Warning if USB backup fails

### Storage Warnings
- **Low Space Warning**: 1GB remaining
- **Critical Space Warning**: 500MB remaining
- Visual and logged warnings when thresholds exceeded

## Error Handling and Recovery

### Image Quality Issues
- **Poor Image Quality**: Press **NO** during review to retake
- **Incorrect Depth Values**: Press **NO** to return and correct values
- **Camera Issues**: Check camera connections and restart system

### Storage Issues
- **USB Drive Full**: Continue with internal storage only
- **Internal Storage Full**: Critical warning displayed, must free space
- **Save Failures**: Error messages displayed with retry options

### System Recovery
- **Camera Initialization Failure**: System runs in development mode
- **Hardware Issues**: Detailed error logging for troubleshooting
- **Application Crashes**: Automatic resource cleanup and error reporting

## Technical Specifications

### Camera Configuration
- **Resolution**: 3280x2464 pixels (IMX219 sensors)
- **Image Format**: JPEG with 95% quality
- **Frame Rate**: 15 FPS for live preview
- **Dual Camera Setup**: Independent left and right cameras

### System Requirements
- **Platform**: Raspberry Pi with dual camera modules
- **Storage**: Internal SD card + USB drive backup
- **Interface**: 5-inch touchscreen + Bluetooth keyboard
- **Operating System**: Raspberry Pi OS

### Configuration Settings
- **Default Segment Length**: 0.5 meters
- **Adjustment Step**: 0.05 meters  
- **Preview Frame Rate**: 10 FPS
- **Storage Thresholds**: Configurable in `config.yaml`

## Running the Enhanced System

### Standard Launch
```bash
# Run the enhanced system with complete workflow
python src/main_enhanced.py
```

### Development Mode
```bash
# Run original system for development
python src/main.py
```

### Configuration
Edit `config.yaml` to customize:
- Camera settings (resolution, exposure ranges)
- UI preferences (segment lengths, adjustment steps)
- Storage paths and thresholds
- Logging levels and file locations

## Troubleshooting

### Common Issues
1. **Camera Not Found**: Check camera connections and enable camera interface
2. **USB Not Detected**: Ensure USB drive is properly formatted (FAT32/exFAT)
3. **Storage Full**: Free space on internal storage or insert new USB drive
4. **Focus Not Working**: Some camera modules may not support focus control

### Log Files
- System logs: `/home/pi/stereo_camera.log`
- Application logs include detailed error information
- Log rotation prevents disk space issues

### Support Information
- All operations are logged with timestamps
- Error conditions include detailed diagnostic information
- System status monitoring provides real-time health checks

## Keyboard Shortcuts

- **Enter**: Equivalent to OK button
- **Escape**: Equivalent to NO button  
- **Tab**: Navigate between input fields
- **Arrow Keys**: Navigate UI elements
- **Space**: Activate focused button

This enhanced system provides a complete, production-ready workflow for stereo core photography with comprehensive error handling, storage management, and operator guidance. 