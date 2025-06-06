#!/usr/bin/env python3
"""
Web-based demo for the Stereo Core Camera System.
Uses Python's built-in HTTP server - works on all platforms!
"""

import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stereo Core Camera System - Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(45deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.8;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            border-left: 5px solid #3498db;
        }
        .section h2 {
            margin-top: 0;
            color: #2c3e50;
            font-size: 1.5em;
        }
        .input-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .input-field {
            display: flex;
            flex-direction: column;
        }
        .input-field label {
            font-weight: bold;
            margin-bottom: 8px;
            color: #555;
        }
        .input-field input {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .input-field input:focus {
            outline: none;
            border-color: #3498db;
        }
        .preview-area {
            background: #2a2a2a;
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin: 20px 0;
        }
        .preview-area h3 {
            margin-top: 0;
            font-size: 1.8em;
        }
        .camera-specs {
            background: #34495e;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 25px;
        }
        .btn {
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
        }
        .btn-ok {
            background: #27ae60;
            color: white;
        }
        .btn-ok:hover {
            background: #229954;
            transform: translateY(-2px);
        }
        .btn-no {
            background: #e74c3c;
            color: white;
        }
        .btn-no:hover {
            background: #c0392b;
            transform: translateY(-2px);
        }
        .btn-adjust {
            background: #f39c12;
            color: white;
        }
        .btn-adjust:hover {
            background: #e67e22;
            transform: translateY(-2px);
        }
        .btn-exposure {
            background: #8e44ad;
            color: white;
        }
        .btn-exposure:hover {
            background: #7d3c98;
            transform: translateY(-2px);
        }
        .btn-focus {
            background: #2980b9;
            color: white;
        }
        .btn-focus:hover {
            background: #1f618d;
            transform: translateY(-2px);
        }
        .status-log {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 20px;
        }
        .specs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }
        .spec-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .spec-card h4 {
            margin-top: 0;
            color: #2c3e50;
        }
        .spec-card .value {
            font-size: 1.5em;
            font-weight: bold;
            color: #3498db;
        }
        @media (max-width: 768px) {
            .input-group {
                grid-template-columns: 1fr;
            }
            .controls {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎥 Stereo Core Camera System</h1>
            <p>Professional Geological Core Photography System</p>
        </div>
        
        <div class="content">
            <!-- Project Information -->
            <div class="section">
                <h2>📋 Project Information</h2>
                <div class="input-group">
                    <div class="input-field">
                        <label for="project">Project Name:</label>
                        <input type="text" id="project" value="TestProject" placeholder="Enter project name...">
                    </div>
                    <div class="input-field">
                        <label for="borehole">Borehole Name:</label>
                        <input type="text" id="borehole" value="BH-001" placeholder="Enter borehole name...">
                    </div>
                </div>
                <div class="input-group">
                    <div class="input-field">
                        <label for="depth-from">Depth From (m):</label>
                        <input type="number" id="depth-from" value="0.00" step="0.01">
                    </div>
                    <div class="input-field">
                        <label for="depth-to">Depth To (m):</label>
                        <input type="number" id="depth-to" value="0.50" step="0.01">
                    </div>
                </div>
            </div>

            <!-- Camera Preview -->
            <div class="section">
                <h2>📷 Camera Preview</h2>
                <div class="preview-area">
                    <h3>Dual IMX219 Stereo Camera Feed</h3>
                    <p>🎬 Live Preview Area</p>
                    <p>This would show real-time stereo camera feeds from both cameras</p>
                    <div class="camera-specs">
                        <strong>Camera Specifications:</strong><br>
                        Resolution: 3280×2464 pixels<br>
                        Sensor: Sony IMX219<br>
                        Format: JPEG<br>
                        Configuration: Stereo Pair
                    </div>
                </div>
            </div>

            <!-- Controls -->
            <div class="section">
                <h2>🎮 Controls</h2>
                <div class="controls">
                    <button class="btn btn-ok" onclick="captureImages()">✅ OK</button>
                    <button class="btn btn-no" onclick="rejectCapture()">❌ NO</button>
                    <button class="btn btn-adjust" onclick="adjustDepth('plus')">➕ Plus</button>
                    <button class="btn btn-adjust" onclick="adjustDepth('minus')">➖ Minus</button>
                    <button class="btn btn-exposure" onclick="adjustExposure('brighter')">🔆 Brighter</button>
                    <button class="btn btn-exposure" onclick="adjustExposure('darker')">🔅 Darker</button>
                    <button class="btn btn-focus" onclick="openFocusDialog()">🎯 Focus</button>
                </div>
            </div>

            <!-- System Status -->
            <div class="section">
                <h2>📊 System Status</h2>
                <div class="specs-grid">
                    <div class="spec-card">
                        <h4>Storage Space</h4>
                        <div class="value">87%</div>
                        <p>Available</p>
                    </div>
                    <div class="spec-card">
                        <h4>Images Captured</h4>
                        <div class="value" id="image-count">0</div>
                        <p>This Session</p>
                    </div>
                    <div class="spec-card">
                        <h4>Current Segment</h4>
                        <div class="value" id="current-segment">0.00-0.50m</div>
                        <p>Depth Range</p>
                    </div>
                    <div class="spec-card">
                        <h4>System Status</h4>
                        <div class="value">✅ Ready</div>
                        <p>All Systems</p>
                    </div>
                </div>
                
                <div class="status-log" id="status-log">
                    <div>🎬 Web Demo started - Mock mode</div>
                    <div>📷 Camera system initialized</div>
                    <div>💾 Storage system ready</div>
                    <div>✅ All systems operational</div>
                    <div>🔧 Ready for capture operations</div>
                </div>
            </div>

            <!-- Hardware Information -->
            <div class="section">
                <h2>🔧 Hardware Specifications</h2>
                <div class="specs-grid">
                    <div class="spec-card">
                        <h4>Processor</h4>
                        <div class="value">RPi 5</div>
                        <p>4GB RAM</p>
                    </div>
                    <div class="spec-card">
                        <h4>Cameras</h4>
                        <div class="value">2×IMX219</div>
                        <p>8MP Each</p>
                    </div>
                    <div class="spec-card">
                        <h4>Display</h4>
                        <div class="value">5"</div>
                        <p>HDMI Touch</p>
                    </div>
                    <div class="spec-card">
                        <h4>Core Length</h4>
                        <div class="value">3.4m</div>
                        <p>Frame System</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let imageCount = 0;
        let currentDepthFrom = 0.00;
        let currentDepthTo = 0.50;

        function logStatus(message) {
            const log = document.getElementById('status-log');
            const timestamp = new Date().toLocaleTimeString();
            log.innerHTML += `<div>[${timestamp}] ${message}</div>`;
            log.scrollTop = log.scrollHeight;
        }

        function captureImages() {
            logStatus('🎬 Starting capture sequence...');
            setTimeout(() => {
                logStatus('📷 Camera 1: Image captured');
                setTimeout(() => {
                    logStatus('📷 Camera 2: Image captured');
                    setTimeout(() => {
                        imageCount += 2;
                        document.getElementById('image-count').textContent = imageCount;
                        
                        // Advance depth
                        currentDepthFrom = currentDepthTo;
                        currentDepthTo += 0.5;
                        
                        document.getElementById('depth-from').value = currentDepthFrom.toFixed(2);
                        document.getElementById('depth-to').value = currentDepthTo.toFixed(2);
                        document.getElementById('current-segment').textContent = 
                            `${currentDepthFrom.toFixed(2)}-${currentDepthTo.toFixed(2)}m`;
                        
                        logStatus(`💾 Images saved: Project/BH-001/BH-001-${currentDepthFrom.toFixed(2)}-${(currentDepthFrom + 0.5).toFixed(2)}-C.jpg`);
                        logStatus(`✅ Capture complete! Advanced to next segment.`);
                    }, 800);
                }, 800);
            }, 500);
        }

        function rejectCapture() {
            logStatus('❌ Capture rejected - ready for retry');
        }

        function adjustDepth(direction) {
            const step = 0.05;
            if (direction === 'plus') {
                currentDepthFrom += step;
                currentDepthTo += step;
                logStatus(`➕ Depth adjusted: +${step}m`);
            } else {
                currentDepthFrom -= step;
                currentDepthTo -= step;
                logStatus(`➖ Depth adjusted: -${step}m`);
            }
            
            document.getElementById('depth-from').value = currentDepthFrom.toFixed(2);
            document.getElementById('depth-to').value = currentDepthTo.toFixed(2);
            document.getElementById('current-segment').textContent = 
                `${currentDepthFrom.toFixed(2)}-${currentDepthTo.toFixed(2)}m`;
        }

        function adjustExposure(direction) {
            if (direction === 'brighter') {
                logStatus('🔆 Exposure increased');
            } else {
                logStatus('🔅 Exposure decreased');
            }
        }

        function openFocusDialog() {
            logStatus('🎯 Focus adjustment mode activated');
            alert('Focus Adjustment\\n\\nUse the +/- buttons to adjust focus.\\nMonitor the preview for optimal sharpness.\\nClick OK when satisfied.');
            logStatus('🎯 Focus adjustment complete');
        }

        // Update project info on change
        document.getElementById('project').addEventListener('input', function() {
            logStatus(`📝 Project updated: ${this.value}`);
        });

        document.getElementById('borehole').addEventListener('input', function() {
            logStatus(`📝 Borehole updated: ${this.value}`);
        });
    </script>
</body>
</html>'''

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode())

def open_browser():
    time.sleep(1)
    webbrowser.open('http://localhost:8080')

def main():
    PORT = 8080
    
    print("🎬 Starting Stereo Core Camera Web Demo...")
    print(f"🌐 Server starting on http://localhost:{PORT}")
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start server
    with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
        print("✅ Demo server running!")
        print("🔧 Demo Features:")
        print("   • Complete UI layout preview")
        print("   • Interactive controls")
        print("   • Mock capture workflow")
        print("   • Real-time status updates")
        print("   • Responsive design")
        print("")
        print("🎯 Try the workflow:")
        print("   1. Modify project information")
        print("   2. Click OK to simulate capture")
        print("   3. Watch automatic depth advancement")
        print("   4. Test all control buttons")
        print("")
        print("⏹️  Press Ctrl+C to stop the demo")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Demo stopped!")

if __name__ == "__main__":
    main() 