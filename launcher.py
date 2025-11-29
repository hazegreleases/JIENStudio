import subprocess
import threading
import time
import os
import sys
from bridge.server import BridgeServer

def start_bridge():
    server = BridgeServer()
    server.start()
    return server

def run_blender_factory():
    # Check if blender is in PATH
    try:
        subprocess.run(["blender", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: 'blender' command not found. Please ensure Blender is installed and added to your PATH.")
        return

    script_path = os.path.abspath("factory/render_test.py")
    print(f"Launching Blender Factory with script: {script_path}")
    
    # Run Blender in background mode
    cmd = ["blender", "--background", "--python", script_path]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Blender Output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Blender Failed:\n", e.stderr)

if __name__ == "__main__":
    print("--- JIET Studio Launcher Prototype ---")
    
    # 1. Start the Bridge (The Brain)
    print("[1/2] Starting Bridge Server...")
    bridge = start_bridge()
    time.sleep(1) # Give it a moment to bind
    
    # 2. Run the Factory (Blender)
    print("[2/2] Running Factory Task...")
    run_blender_factory()
    
    print("--- Test Complete. Shutting down. ---")
    bridge.stop()
    sys.exit(0)
