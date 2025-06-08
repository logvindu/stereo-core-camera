# IMX219 Discrete Focus Implementation

## Overview

This implementation adds discrete focus control for IMX219 cameras with 8 focus steps (0-7), matching the physical limitations of these cameras. The system provides precise focus control with proper boundary handling and independent camera management.

## 🎯 Key Features

### Discrete Focus Steps
- **8 discrete positions**: Steps 0-7 (inclusive)
- **Independent control**: Each camera maintains its own focus step
- **Boundary protection**: Cannot exceed min (0) or max (7) limits
- **Real-time feedback**: UI shows current step and limits

### Camera Controller Enhancements

#### New Properties
```python
self.focus_steps = 8                    # Total number of discrete positions
self.focus_step_0 = 3                   # Camera 0 current step (default: middle)
self.focus_step_1 = 3                   # Camera 1 current step (default: middle)
```

#### New Methods
```python
def get_focus_step(camera_index: int) -> int
    """Get current focus step for specified camera (0-7)"""

def set_focus_step(step: int, camera_index: int) -> bool
    """Set focus step directly (0-7)"""

def adjust_focus(direction: str, camera_index: int) -> bool
    """Adjust focus by ±1 step with boundary protection"""
```

### UI Integration

#### Focus Dialog Updates
- **Step display**: Shows "Focus Step: X/7" instead of continuous values
- **Boundary feedback**: Displays "(Max)" or "(Min)" when at limits
- **Camera switching**: Updates focus display when switching between cameras
- **Live preview**: Shows camera feed while adjusting focus

#### Button Behavior
- **"+" button**: Increments focus step by 1 (max: 7)
- **"−" button**: Decrements focus step by 1 (min: 0)
- **OK button**: Locks in the selected focus step
- **Camera selection**: Independent focus control per camera

## 🔧 Technical Implementation

### Focus Step Mapping
The discrete steps (0-7) are mapped to the camera's continuous focus range:

```python
lens_position = focus_range[0] + step * (focus_range[1] - focus_range[0]) / (focus_steps - 1)
```

For default config (range 0-1023):
- Step 0 → Lens position 0
- Step 1 → Lens position 146
- Step 2 → Lens position 292
- Step 3 → Lens position 438 (default)
- Step 4 → Lens position 585
- Step 5 → Lens position 731
- Step 6 → Lens position 877
- Step 7 → Lens position 1023

### Configuration Updates

```yaml
camera:
  focus_range: [0, 1023]           # Continuous range for API mapping
  focus_steps: 8                   # IMX219 discrete positions (0-7)
  default_focus_step: 3            # Start at middle position
```

### Error Handling
- **Invalid steps**: Rejects steps outside 0-7 range
- **Boundary conditions**: Returns false when at limits
- **Camera availability**: Works in development mode without real cameras
- **API failures**: Graceful handling of camera control errors

## 🎮 User Workflow

### Focus Adjustment Process
1. **Open Focus Dialog**: Click "FOCUS" button in main interface
2. **Select Camera**: Choose Camera 1 or Camera 2
3. **Live Preview**: View real-time camera feed
4. **Adjust Focus**: Use +/− buttons to change focus step
5. **Monitor Display**: Watch "Focus Step: X/7" indicator
6. **Lock Setting**: Press OK to apply the focus step

### Visual Feedback
- **Current step**: Always displayed as "Focus Step: X/7"
- **Boundary indication**: Shows "(Max)" or "(Min)" at limits
- **Camera identification**: Clear labeling of Camera 1/2
- **Live preview**: Real-time feed shows focus changes

## 🔍 Development Mode Support

### Mock Camera Integration
- **Simulated focus**: Mock cameras respond to focus commands
- **Console logging**: Focus changes logged to terminal
- **UI consistency**: Same interface behavior as real cameras
- **Testing support**: Full functionality without hardware

### Debug Information
```
MockCamera 0: Focus set to 438
Focus adjusted increase for camera 0: step 4 (lens position: 585)
Focus at boundary for camera 0: step 7
```

## 📊 Status Reporting

### Camera Status Updates
```python
status = {
    'camera_0': {'focus_step': 3},
    'camera_1': {'focus_step': 5},
    'focus_steps_total': 8,
    # ... other status info
}
```

### Logging Integration
- **Focus changes**: All adjustments logged with step and lens position
- **Boundary conditions**: Clear messages when limits reached
- **Error conditions**: Detailed error reporting for failures
- **Camera switching**: Logged when user changes camera selection

## 🚀 Benefits

### For Users
- **Precise control**: Exact focus positioning with 8 discrete steps
- **Visual feedback**: Clear indication of current focus position
- **Boundary safety**: Cannot accidentally exceed camera limits
- **Independent cameras**: Separate focus control for each camera

### For Developers
- **Clean API**: Simple methods for focus control
- **Error handling**: Robust boundary and error checking
- **Mock support**: Full development without hardware
- **Extensible**: Easy to modify for different camera types

## 🔧 Integration Points

### Main Application
- Focus dialog accessible from all main windows
- Consistent behavior across Qt5/Qt6 interfaces
- Proper integration with camera lifecycle

### Camera Controller
- Thread-safe focus operations
- Proper resource management
- Mock camera support for development

### Configuration System
- Flexible focus step configuration
- Backward compatibility with existing settings
- Easy customization for different camera models

## 📝 Usage Examples

### Basic Focus Adjustment
```python
# Increase focus by one step
camera.adjust_focus('increase', camera_index=0)

# Set specific focus step
camera.set_focus_step(5, camera_index=1)

# Get current focus step
current_step = camera.get_focus_step(camera_index=0)
```

### UI Integration
```python
# Update focus display
focus_step = camera.get_focus_step(self.current_camera)
self.focus_status_label.setText(f"Focus Step: {focus_step}/7")

# Handle boundary conditions
if not success:
    self.focus_status_label.setText(f"Focus Step: {focus_step}/7 (Max)")
```

This implementation provides a complete, robust solution for discrete focus control that matches the physical characteristics of IMX219 cameras while maintaining excellent user experience and developer-friendly APIs. 