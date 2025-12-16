#!/usr/bin/env python3
"""
Development Startup Script - Kayos Cloud Licensing
Script para iniciar o ambiente de desenvolvimento local
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if development environment is properly set up"""
    print(" Checking development environment...")
    
    # Check if .env.local exists
    if not Path(".env.local").exists():
        print(" .env.local not found. Creating from template...")
        with open(".env.local", "w") as f:
            f.write("""# Environment
ENVIRONMENT=development
debug=False

# Database
DATABASE_URL=sqlite:///./kayos_licensing.db

# Security (CHANGE THESE IN PRODUCTION!)
JWT_SECRET=dev-super-secret-key-change-in-production
MASTER_KEY=dev-master-key-change-in-production

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000

# Development Settings
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
""")
        print(" Created .env.local from template")
    
    # Check if virtual environment exists
    if not Path("venv").exists() and not Path(".venv").exists():
        print(" Virtual environment not found. Please create one:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\\\Scripts\\\\activate  # Windows")
        print("   pip install -r requirements.txt")
        return False
    
    # Check if requirements are installed
    try:
        import fastapi
        import cryptography
        print(" Python dependencies are installed")
    except ImportError as e:
        print(f" Missing dependencies: {e}")
        print("   Please run: pip install -r requirements.txt")
        return False
    
    return True

def start_development_server():
    """Start the FastAPI development server"""
    print(" Starting Kayos Cloud Licensing Development Server...")
    
    # Set environment
    os.environ["ENVIRONMENT"] = "development"
    
    try:
        # Start uvicorn server with auto-reload
        import uvicorn
        uvicorn.run(
            "app.api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n Development server stopped")
    except Exception as e:
        print(f" Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main entry point"""
    print("=" * 60)
    print(" Kayos Cloud Licensing - Development Environment")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Start server
    start_development_server()

if __name__ == "__main__":
    main()
