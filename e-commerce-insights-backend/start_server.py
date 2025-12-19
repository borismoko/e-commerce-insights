#!/usr/bin/env python3
"""
Startup script for the E-Commerce Insights API server
"""
import uvicorn
import os
import sys

def main():
    """Start the FastAPI server"""
    print("🚀 Starting E-Commerce Insights API Server...")
    print("📁 Working directory:", os.getcwd())
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled for development")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
