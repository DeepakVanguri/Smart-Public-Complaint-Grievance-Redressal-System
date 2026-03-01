import subprocess
import sys
import os

print("=" * 45)
print("  SmartGov Complaint System - Starting...")
print("=" * 45)
print()

# Move to backend folder
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
os.chdir(backend_dir)

# Install dependencies
print("[1/2] Installing dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "fastapi", "uvicorn[standard]", "python-multipart", "pydantic[email]"], 
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("      Done!")
print()

# Start server
print("[2/2] Starting server...")
print()
print("=" * 45)
print("  Server is running!")
print("  Open in browser: http://localhost:8000")
print("=" * 45)
print()
print("  Press Ctrl+C to stop the server.")
print()

subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
