# Raspberry Pi Deployment Guide

This guide explains how to update your Stereo Core Camera software on the Raspberry Pi from your GitHub repository.

## Prerequisites

### On Your Development Machine
- Git repository with your stereo camera code
- SSH access to your Raspberry Pi
- Network connection to reach your Pi

### On Your Raspberry Pi
- Raspberry Pi OS installed and configured
- SSH enabled (`sudo systemctl enable ssh`)
- Network connection (WiFi or Ethernet)
- Python 3.8+ installed
- Camera interface enabled (`sudo raspi-config` → Interface Options → Camera)

## Quick Deployment

### 1. Basic Deployment

Run the deployment script from your project directory:

```bash
./deploy_to_pi.sh
```

This will:
- Connect to your Pi at `pi@raspberrypi.local`
- Create a backup of existing installation
- Pull latest code from GitHub
- Install Python dependencies
- Set up systemd service for auto-start
- Start the camera application

### 2. Custom Pi Settings

If your Pi has different settings:

```bash
# Different username
PI_USER=myuser ./deploy_to_pi.sh

# Different hostname or IP address
PI_HOST=192.168.1.100 ./deploy_to_pi.sh

# Both custom settings
PI_USER=myuser PI_HOST=192.168.1.100 ./deploy_to_pi.sh
```

## Management Commands

### Check Status
```bash
./deploy_to_pi.sh status
```

### Stop Service
```bash
./deploy_to_pi.sh stop
```

### Start Service
```bash
./deploy_to_pi.sh start
```

### Restart Service
```bash
./deploy_to_pi.sh restart
```

## Manual SSH Commands

You can also manage the service directly via SSH:

```bash
# Connect to your Pi
ssh pi@raspberrypi.local

# Check service status
sudo systemctl status stereo-camera

# View real-time logs
sudo journalctl -u stereo-camera -f

# Restart service
sudo systemctl restart stereo-camera

# Stop service
sudo systemctl stop stereo-camera

# Start service
sudo systemctl start stereo-camera

# Disable auto-start
sudo systemctl disable stereo-camera

# Enable auto-start
sudo systemctl enable stereo-camera
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to Raspberry Pi
```bash
# Test basic connectivity
ping raspberrypi.local

# Try with IP address instead
ping 192.168.1.XXX

# Test SSH connection
ssh pi@raspberrypi.local
```

**Solution**: 
- Ensure Pi is powered on and connected to network
- Check if SSH is enabled: `sudo systemctl status ssh`
- Verify hostname or use IP address directly

### Service Issues

**Problem**: Service fails to start
```bash
# Check detailed logs
ssh pi@raspberrypi.local 'sudo journalctl -u stereo-camera --lines=50'

# Check if cameras are detected  
ssh pi@raspberrypi.local 'libcamera-hello --list-cameras'

# Test camera functionality
ssh pi@raspberrypi.local 'libcamera-still -o test.jpg'
```

**Common solutions**:
- Camera interface not enabled: `sudo raspi-config` → Interface Options → Camera
- Missing dependencies: Re-run deployment script
- Permission issues: Check file ownership in `/home/pi/stereo-core-camera`

### Storage Issues

**Problem**: Low disk space warnings
```bash
# Check disk usage
ssh pi@raspberrypi.local 'df -h'

# Clean old photos
ssh pi@raspberrypi.local 'sudo du -sh /home/pi/core_photos/*'

# Check USB storage
ssh pi@raspberrypi.local 'lsblk'
```

### Python Environment Issues

**Problem**: Module import errors
```bash
# Reinstall dependencies
ssh pi@raspberrypi.local 'cd /home/pi/stereo-core-camera && source venv/bin/activate && pip install -r requirements.txt'

# Check Python path
ssh pi@raspberrypi.local 'cd /home/pi/stereo-core-camera && source venv/bin/activate && python -c "import sys; print(sys.path)"'
```

## First-Time Setup on New Pi

If deploying to a fresh Raspberry Pi:

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable → Finish → Reboot

# 3. Enable SSH (if not already enabled)
sudo systemctl enable ssh
sudo systemctl start ssh

# 4. Install Git (if not installed)
sudo apt install -y git

# 5. Set up SSH keys (recommended)
ssh-copy-id pi@raspberrypi.local

# 6. Run deployment
./deploy_to_pi.sh
```

## Directory Structure on Pi

After deployment, your Pi will have:

```
/home/pi/
├── stereo-core-camera/          # Application code
│   ├── src/                     # Source code
│   ├── venv/                    # Python virtual environment
│   ├── config.yaml              # Configuration
│   └── requirements.txt         # Dependencies
├── core_photos/                 # Captured images
└── stereo_camera.log           # Application logs
```

## Monitoring

### View Real-time Logs
```bash
ssh pi@raspberrypi.local 'sudo journalctl -u stereo-camera -f'
```

### Check System Resources
```bash
ssh pi@raspberrypi.local '
echo "=== CPU/Memory Usage ==="
top -n1 -b | head -5
echo ""
echo "=== Disk Usage ==="
df -h
echo ""
echo "=== Camera Status ==="
vcgencmd get_camera
'
```

## Updating Configuration

To update configuration without full redeployment:

```bash
# Edit config locally
nano config.yaml

# Copy to Pi
scp config.yaml pi@raspberrypi.local:/home/pi/stereo-core-camera/

# Restart service to apply changes
./deploy_to_pi.sh restart
```

## Backup and Recovery

### Create Manual Backup
```bash
ssh pi@raspberrypi.local '
sudo tar -czf stereo_camera_backup_$(date +%Y%m%d).tar.gz \
    /home/pi/stereo-core-camera \
    /home/pi/core_photos \
    /etc/systemd/system/stereo-camera.service
'
```

### Restore from Backup
```bash
# Stop service
./deploy_to_pi.sh stop

# Restore files (adjust backup filename)
ssh pi@raspberrypi.local '
sudo tar -xzf stereo_camera_backup_YYYYMMDD.tar.gz -C /
sudo systemctl daemon-reload
'

# Start service
./deploy_to_pi.sh start
``` 