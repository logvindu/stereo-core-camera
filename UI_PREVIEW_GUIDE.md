# 📱 UI Preview Guide

## What You Should See

### 🖥️ Main Window Layout (800x600 pixels)

```
┌─────────────────────────────────────────────────────────────────┐
│                 Stereo Core Camera System                      │
│                      (Header Title)                            │
├─────────────────────────────────────────────────────────────────┤
│ Project Name:    [Enter project name...              ]        │
│ Borehole Name:   [Enter borehole name...             ]        │
│ Depth From (m):  [0.00                               ]        │
│ Depth To (m):    [0.50                               ]        │
├─────────────────────────────────────────────────────────────────┤
│                    Camera Preview                              │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │          Camera Preview                                     │ │
│ │      (Mock Mode - Development)                             │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      [OK]    [NO]                             │
│                                                                │
│                    [+]      [−]                               │
│                                                                │
│                [BRIGHTER]  [DARKER]                           │
│                                                                │
│              [FOCUS]                                           │
├─────────────────────────────────────────────────────────────────┤
│ System Status:                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [12:34:56] Camera not initialized - Running in Dev Mode    │ │
│ │ [12:34:57] Storage manager initialized                     │ │
│ │ [12:34:58] UI Demo Mode started                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ Progress: [████████████████████████████████] (hidden)          │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Interactive Elements

### ✅ **Input Fields** (Top Section)
- **Project Name**: Large text field with placeholder text
- **Borehole Name**: Large text field with placeholder text  
- **Depth From**: Numerical input, starts with "0.00"
- **Depth To**: Numerical input, starts with "0.50"
- All fields have **40px height** for easy touch interaction

### 📷 **Camera Preview** (Middle Section)
- **320x240 pixel** black preview area
- Shows "Camera Preview (Mock Mode - Development)" text
- Gray border for clear definition
- In production: would show live camera feed

### 🎮 **Control Buttons** (Bottom-Middle Section)

#### Main Actions:
- **🟢 OK Button**: Green background, white text, 100x60px
- **🔴 NO Button**: Red background, white text, 100x60px

#### Adjustments:
- **➕ Plus (+)**: 80x50px, increases depth_to by 0.05m
- **➖ Minus (−)**: 80x50px, decreases depth_to by 0.05m

#### Camera Controls:
- **🔆 BRIGHTER**: 100x50px, increases exposure
- **🔅 DARKER**: 100x50px, decreases exposure
- **🎯 FOCUS**: 120x50px, blue background, opens focus dialog

### 📊 **Status Display** (Bottom Section)
- **Status Text**: Scrollable area showing timestamped messages
- **Progress Bar**: Appears during operations, hidden by default
- **Courier font** for clear technical readability

## 🔧 Testing the Demo

### 1. **Basic Input Testing**
```
✓ Type "TestProject" in Project Name
✓ Type "BH-001" in Borehole Name  
✓ Observe green borders when fields are focused
✓ Check validation by leaving fields empty and clicking OK
```

### 2. **Mock Capture Workflow**
```
1. Fill in project information
2. Click [OK] → See "Capturing stereo pair..." status
3. Progress bar appears briefly
4. "Preview: Camera 1" dialog opens showing mock image
5. Click [OK] → "Preview: Camera 2" dialog opens
6. Click [OK] → See save confirmation and depth advancement
```

### 3. **Depth Adjustment**
```
✓ Click [+] → Watch Depth To increase: 0.50 → 0.55 → 0.60
✓ Click [−] → Watch Depth To decrease: 0.60 → 0.55 → 0.50
✓ Check status messages for each adjustment
```

### 4. **Camera Controls**
```
✓ Click [BRIGHTER] → See "Exposure increased (brighter) - Mock Mode"
✓ Click [DARKER] → See "Exposure decreased (darker) - Mock Mode"
✓ Click [FOCUS] → Focus adjustment dialog opens
    - Use dialog [+]/[−] for focus simulation
    - Click [OK] to close dialog
```

### 5. **Error Handling**
```
✓ Try clicking [OK] with empty project name → Error dialog
✓ Try invalid depth values → Error messages
✓ Test [NO] button during capture → "Current capture discarded"
```

## 🎨 Visual Style Features

### **Color Scheme**
- **Background**: Light gray (#f0f0f0)
- **Panels**: White with rounded corners and subtle shadows
- **Borders**: Light gray (#ddd) with green focus highlights (#4CAF50)
- **Buttons**: Hover and press states for tactile feedback

### **Typography**
- **Title**: 18pt bold font
- **Labels**: 12pt standard font
- **Inputs**: 12pt font with 40px height
- **Status**: 9pt Courier font for technical readability

### **Touch-Friendly Design**
- **Minimum button size**: 50px height
- **Large click targets**: All interactive elements sized for fingers
- **Clear visual feedback**: Hover states and pressed animations
- **Adequate spacing**: 10px margins between sections

## 🚀 Expected Workflow Demo

**Step-by-step operation simulation:**

1. **Setup** → Enter "GeologyProject" and "CoreBH-001"
2. **Position** → Adjust depths if needed with +/− buttons  
3. **Capture** → Click OK → Progress bar → Camera 1 preview
4. **Review** → Click OK → Camera 2 preview
5. **Save** → Click OK → Success message → Auto-advance to next segment
6. **Continue** → Notice depths updated: From: 0.50, To: 1.00

## 📏 Screen Size Notes

**Optimized for 5-inch touchscreen:**
- **Window size**: 800x600 pixels (configurable)
- **Fullscreen mode**: Available for production (disabled in demo)
- **Responsive layout**: Adapts to different screen sizes
- **Portrait/landscape**: Works in both orientations

The UI is designed to be **professional, intuitive, and robust** for field operations with geological core samples. 