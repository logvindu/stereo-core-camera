#!/bin/bash

# Stereo Core Camera System - Raspberry Pi Deployment Script
# This script updates the software on the Raspberry Pi from GitHub

set -e  # Exit on any error

# Configuration
PI_USER="${PI_USER:-pi}"
PI_HOST="${PI_HOST:-raspberrypi.local}"
REPO_URL="${REPO_URL:-https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')}"
APP_NAME="stereo-core-camera"
REMOTE_PATH="/home/$PI_USER/$APP_NAME"
SERVICE_NAME="stereo-camera"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we can connect to the Pi
check_connection() {
    print_status "Checking connection to Raspberry Pi..."
    if ssh -o ConnectTimeout=10 "$PI_USER@$PI_HOST" "echo 'Connected'" > /dev/null 2>&1; then
        print_success "Connected to $PI_USER@$PI_HOST"
    else
        print_error "Cannot connect to $PI_USER@$PI_HOST"
        echo "Please ensure:"
        echo "  1. Your Raspberry Pi is powered on and connected to the network"
        echo "  2. SSH is enabled on the Pi"
        echo "  3. You can reach the Pi at $PI_HOST"
        echo "  4. You have SSH key access or can enter password"
        echo ""
        echo "You can set custom values:"
        echo "  PI_USER=myuser PI_HOST=192.168.1.100 $0"
        exit 1
    fi
}

# Function to create backup
create_backup() {
    print_status "Creating backup of current installation..."
    ssh "$PI_USER@$PI_HOST" "
        if [ -d '$REMOTE_PATH' ]; then
            sudo cp -r '$REMOTE_PATH' '${REMOTE_PATH}_backup_$(date +%Y%m%d_%H%M%S)' || true
            echo 'Backup created'
        else
            echo 'No existing installation found, skipping backup'
        fi
    "
}

# Function to stop the service if it exists
stop_service() {
    print_status "Stopping stereo camera service if running..."
    ssh "$PI_USER@$PI_HOST" "
        if systemctl is-active --quiet $SERVICE_NAME 2>/dev/null; then
            sudo systemctl stop $SERVICE_NAME
            echo 'Service stopped'
        else
            echo 'Service not running or not installed'
        fi
    " || true
}

# Function to update system packages
update_system() {
    print_status "Updating system packages on Raspberry Pi..."
    ssh "$PI_USER@$PI_HOST" "
        sudo apt update && sudo apt upgrade -y
        sudo apt install -y python3-pip python3-venv git
    "
    print_success "System packages updated"
}

# Function to deploy code
deploy_code() {
    print_status "Deploying code from GitHub..."
    ssh "$PI_USER@$PI_HOST" "
        # Remove old installation if exists
        if [ -d '$REMOTE_PATH' ]; then
            rm -rf '$REMOTE_PATH'
        fi
        
        # Clone fresh copy
        git clone '$REPO_URL' '$REMOTE_PATH'
        cd '$REMOTE_PATH'
        
        # Create virtual environment
        python3 -m venv venv
        source venv/bin/activate
        
        # Install Python dependencies
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create necessary directories
        mkdir -p /home/$PI_USER/core_photos
        
        # Set proper permissions
        chmod +x src/main.py
        chown -R $PI_USER:$PI_USER '$REMOTE_PATH'
        chown -R $PI_USER:$PI_USER /home/$PI_USER/core_photos
    "
    print_success "Code deployed successfully"
}

# Function to setup systemd service
setup_service() {
    print_status "Setting up systemd service..."
    ssh "$PI_USER@$PI_HOST" "
        sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Stereo Core Camera System
After=graphical.target network.target

[Service]
Type=simple
User=$PI_USER
Group=$PI_USER
WorkingDirectory=$REMOTE_PATH
Environment=DISPLAY=:0
Environment=PYTHONPATH=$REMOTE_PATH
ExecStart=$REMOTE_PATH/venv/bin/python src/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

        # Reload systemd and enable service
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
    "
    print_success "Systemd service configured"
}

# Function to start the service
start_service() {
    print_status "Starting stereo camera service..."
    ssh "$PI_USER@$PI_HOST" "
        sudo systemctl start $SERVICE_NAME
        sleep 3
        if systemctl is-active --quiet $SERVICE_NAME; then
            echo 'Service started successfully'
        else
            echo 'Service failed to start. Checking logs...'
            sudo journalctl -u $SERVICE_NAME --lines=20 --no-pager
            exit 1
        fi
    "
    print_success "Service started successfully"
}

# Function to check service status
check_status() {
    print_status "Checking service status..."
    ssh "$PI_USER@$PI_HOST" "
        echo '=== Service Status ==='
        sudo systemctl status $SERVICE_NAME --no-pager --lines=10
        echo ''
        echo '=== Recent Logs ==='
        sudo journalctl -u $SERVICE_NAME --lines=10 --no-pager
        echo ''
        echo '=== Storage Info ==='
        df -h /home/$PI_USER/core_photos 2>/dev/null || echo 'Storage directory not found'
    "
}

# Main deployment function
main() {
    echo "======================================"
    echo "Stereo Core Camera - Pi Deployment"
    echo "======================================"
    echo ""
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "This script must be run from the git repository directory"
        exit 1
    fi
    
    # Show current settings
    echo "Deployment Configuration:"
    echo "  Pi User: $PI_USER"
    echo "  Pi Host: $PI_HOST"
    echo "  Repository: $REPO_URL"
    echo "  Remote Path: $REMOTE_PATH"
    echo ""
    
    # Ask for confirmation
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    # Execute deployment steps
    check_connection
    create_backup
    stop_service
    update_system
    deploy_code
    setup_service
    start_service
    check_status
    
    echo ""
    echo "======================================"
    print_success "Deployment completed successfully!"
    echo "======================================"
    echo ""
    echo "The stereo camera system is now running on your Raspberry Pi."
    echo "You can:"
    echo "  • Check status: ssh $PI_USER@$PI_HOST 'sudo systemctl status $SERVICE_NAME'"
    echo "  • View logs: ssh $PI_USER@$PI_HOST 'sudo journalctl -u $SERVICE_NAME -f'"
    echo "  • Stop service: ssh $PI_USER@$PI_HOST 'sudo systemctl stop $SERVICE_NAME'"
    echo "  • Start service: ssh $PI_USER@$PI_HOST 'sudo systemctl start $SERVICE_NAME'"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    "status")
        check_connection
        check_status
        ;;
    "stop")
        check_connection
        stop_service
        ;;
    "start")
        check_connection
        start_service
        ;;
    "restart")
        check_connection
        stop_service
        start_service
        ;;
    *)
        main
        ;;
esac 