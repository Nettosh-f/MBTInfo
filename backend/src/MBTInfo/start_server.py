"""
Script to start the FastAPI MBTI Processing Server
"""
import uvicorn
import os
import sys

def main():
    # Add the parent directory to the path so we can import our modules
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("Starting MBTI Processing API server...")
    print("The server will be available at http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "MBTInfo.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()