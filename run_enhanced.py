#!/usr/bin/env python3
"""
Simple launcher for the Enhanced Stereo Core Camera System.
This script provides an easy way to run the complete workflow implementation.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the enhanced stereo core camera system."""
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("=" * 60)
    print("  Enhanced Stereo Core Camera System")
    print("  Complete Workflow Implementation")
    print("=" * 60)
    print()
    
    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Virtual environment detected")
    else:
        print("⚠️  Warning: No virtual environment detected")
        print("   Consider running: source venv/bin/activate")
        print()
    
    # Check for required files
    required_files = [
        "config.yaml",
        "src/main_enhanced.py",
        "src/ui/enhanced_main_window.py",
        "src/ui/preview_dialog.py",
        "src/ui/focus_dialog.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print()
        print("Please ensure all files are present before running.")
        return 1
    
    print("✓ All required files found")
    print()
    
    # Launch the enhanced system
    print("Starting Enhanced Stereo Core Camera System...")
    print("Features:")
    print("  • Complete operator workflow")
    print("  • Live camera preview")
    print("  • Image quality review")
    print("  • Automatic file organization")
    print("  • USB backup support")
    print("  • Storage monitoring")
    print("  • Focus adjustment with live preview")
    print()
    
    try:
        # Import and run the enhanced system
        sys.path.insert(0, str(script_dir))
        from src.main_enhanced import main as enhanced_main
        return enhanced_main()
        
    except KeyboardInterrupt:
        print("\nSystem interrupted by user")
        return 0
    except Exception as e:
        print(f"\nError starting enhanced system: {e}")
        print("\nFor development mode, try: python src/main.py")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 