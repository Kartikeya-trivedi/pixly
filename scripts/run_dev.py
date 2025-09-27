#!/usr/bin/env python3
"""
Development runner script for Game Overlay AI.
Starts both backend and frontend in development mode.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path


def run_command(cmd, cwd=None, shell=True):
    """Run a command and return the process."""
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )


def main():
    """Main development runner."""
    print("🚀 Starting Game Overlay AI Development Environment")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Start backend
    print("📡 Starting FastAPI backend...")
    backend_cmd = "uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload"
    backend_process = run_command(backend_cmd, cwd=project_root)
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start Electron frontend
    print("🖥️  Starting Electron overlay...")
    frontend_cmd = "npm run dev"
    frontend_process = run_command(frontend_cmd, cwd=project_root / "static")
    
    print("\n✅ Development environment started!")
    print("📡 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🖥️  Overlay: Electron window should open")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Monitor processes
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping development environment...")
        
        # Terminate processes
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for graceful shutdown
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("⚠️  Force killing processes...")
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ Development environment stopped")


if __name__ == "__main__":
    main()
