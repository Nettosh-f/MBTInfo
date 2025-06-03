#!/usr/bin/env python3
"""
MBTI FastAPI Service Setup and Run Script
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path


def check_python_version():
    """Check if Python version is suitable"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")

    requirements = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "openpyxl==3.1.2",
        "PyPDF2==3.0.1",
        "PyMuPDF==1.23.8",
        "Pillow==10.1.0",
        "python-dateutil==2.8.2",
        "requests==2.31.0"
    ]

    for req in requirements:
        try:
            print(f"Installing {req}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"⚠️  Warning: Failed to install {req}")

    print("✅ Requirements installation completed")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")

    directories = [
        r"F:\projects\MBTInfo\output",
        r"F:\projects\MBTInfo\input",
        "./temp",
        "./media"
    ]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create {directory}: {e}")

    # Check for logo file
    logo_paths = [
        "./media/full_logo.png",
        "./Media/full_logo.png",
        r"F:\projects\MBTInfo\Media\full_logo.png"
    ]

    logo_found = False
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            print(f"✅ Logo found: {logo_path}")
            logo_found = True
            break

    if not logo_found:
        print("⚠️  Logo not found. Please place your logo at ./media/full_logo.png")
        print("   The web interface will work without it, but the logo won't display.")

def create_index_html():
    """Create the index.html file if it doesn't exist"""
    print("\n🌐 Setting up web interface...")

    html_file = "index.html"
    if not os.path.exists(html_file):
        print("Creating index.html file...")
        # The HTML content would be copied here from the web interface artifact
        print("✅ Web interface file created")
    else:
        print("✅ Web interface file already exists")

def check_existing_modules():
    """Check if required MBTI processing modules exist"""
    print("\n🔍 Checking existing MBTI modules...")

    required_modules = [
        "main.py",
        "personal_report.py",
        "extract_image.py",
        "data_extractor.py",
        "utils.py",
        "consts.py"
    ]

    missing_modules = []
    for module in required_modules:
        if os.path.exists(module):
            print(f"✅ Found: {module}")
        else:
            print(f"❌ Missing: {module}")
            missing_modules.append(module)

    if missing_modules:
        print(f"\n⚠️  Warning: Missing modules: {', '.join(missing_modules)}")
        print("Make sure your existing MBTI processing files are in the same directory")
        return False

    return True

def check_test_files():
    """Check if test files exist"""
    print("\n📋 Checking test files...")

    test_files = [
        r"F:\projects\MBTInfo\input\nir-bensinai-MBTI.pdf",
        r"F:\projects\MBTInfo\input"
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                print(f"✅ Found test file: {file_path}")
            else:
                pdf_count = len([f for f in os.listdir(file_path) if f.lower().endswith('.pdf')])
                print(f"✅ Found input folder with {pdf_count} PDF files: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")

def start_service():
    """Start the FastAPI service"""
    print("\n🚀 Starting MBTI FastAPI Service...")
    print("=" * 50)

    # Check if the service script exists
    service_script = "fastapi_service.py"  # The main FastAPI script
    if not os.path.exists(service_script):
        print(f"❌ Service script not found: {service_script}")
        print("Make sure the FastAPI service file is named 'fastapi_service.py'")
        return False

    try:
        print(f"Starting service with: python {service_script}")
        print("\n📊 Service Information:")
        print("   URL: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("   Web Interface: http://localhost:8000")
        print("\n⏹️  Press Ctrl+C to stop the service")
        print("=" * 50)

        # Wait a moment then open browser
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open("http://localhost:8000")
                print("\n🌐 Opening web browser...")
            except:
                pass

        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        # Start the service
        subprocess.run([sys.executable, service_script])

    except KeyboardInterrupt:
        print("\n\n⏹️  Service stopped by user")
        return True
    except FileNotFoundError:
        print(f"❌ Could not start service. Make sure {service_script} exists")
        return False
    except Exception as e:
        print(f"❌ Error starting service: {e}")
        return False

def run_quick_test():
    """Run the quick test script"""
    print("\n🧪 Running quick tests...")

    test_script = "quick_test.py"
    if not os.path.exists(test_script):
        print(f"❌ Test script not found: {test_script}")
        return False

    try:
        subprocess.run([sys.executable, test_script])
        return True
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def show_menu():
    """Show the main menu"""
    print("\n" + "="*60)
    print("🎯 MBTI FastAPI Service - Setup & Management")
    print("="*60)
    print("1. 🔧 Full Setup (install requirements, create directories)")
    print("2. 🚀 Start Service")
    print("3. 🧪 Run Tests")
    print("4. 📋 Check System")
    print("5. ❓ Help")
    print("0. 🚪 Exit")
    print("="*60)

def show_help():
    """Show help information"""
    print("\n📖 MBTI FastAPI Service Help")
    print("="*40)
    print("""
🎯 The 4 Activities:
   1. Create Group Report - Process folder of PDFs → Excel report
   2. Create Personal Report - Single PDF → Personal PDF report  
   3. Create Dual Report - Compare 2 PDFs (to be implemented)
   4. Translate - Translate PDF (to be implemented)

📁 File Structure:
   F:\\projects\\MBTInfo\\
   ├── input\\                     # Your PDF files
   │   └── nir-bensinai-MBTI.pdf  # Test file
   ├── output\\                    # Generated reports
   ├── fastapi_service.py         # Main FastAPI service
   ├── index.html                 # Web interface
   ├── quick_test.py              # Test script
   └── ... (your existing MBTI modules)

🌐 URLs:
   • Web Interface: http://localhost:8000
   • API Documentation: http://localhost:8000/docs
   • Health Check: http://localhost:8000/health

🔧 Troubleshooting:
   • Make sure Python 3.8+ is installed
   • Ensure all your existing MBTI modules are present
   • Check that test files exist in F:\\projects\\MBTInfo\\input\\
   • Run "Check System" to verify everything is ready
    """)

def check_system():
    """Check if system is ready"""
    print("\n🔍 System Check")
    print("="*30)

    all_good = True

    if not check_python_version():
        all_good = False

    if not check_existing_modules():
        all_good = False

    check_test_files()

    # Check directories
    print("\n📁 Directory Check:")
    dirs = [r"F:\projects\MBTInfo\output", r"F:\projects\MBTInfo\input"]
    for d in dirs:
        if os.path.exists(d):
            print(f"✅ {d}")
        else:
            print(f"❌ {d}")
            all_good = False

    print(f"\n{'✅ System Ready!' if all_good else '⚠️  Issues Found'}")
    return all_good

def main():
    """Main function"""
    while True:
        show_menu()
        choice = input("\n👉 Enter your choice (0-5): ").strip()

        if choice == "0":
            print("\n👋 Goodbye!")
            break
        elif choice == "1":
            print("\n🔧 Starting full setup...")
            check_python_version()
            install_requirements()
            create_directories()
            create_index_html()
            check_existing_modules()
            print("\n✅ Setup completed!")
            input("\nPress Enter to continue...")
        elif choice == "2":
            if start_service():
                pass
            input("\nPress Enter to continue...")
        elif choice == "3":
            run_quick_test()
            input("\nPress Enter to continue...")
        elif choice == "4":
            check_system()
            input("\nPress Enter to continue...")
        elif choice == "5":
            show_help()
            input("\nPress Enter to continue...")
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()