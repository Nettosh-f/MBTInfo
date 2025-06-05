"""
Quick test script for the MBTI FastAPI service
Run this after starting the service with: python main.py
"""
import requests
import time
import os

# Your specific file paths
SINGLE_PDF = r"F:\projects\MBTInfo\input\nir-bensinai-MBTI.pdf"
FOLDER_PATH = r"/input"
OUTPUT_DIR = r"/output"
BASE_URL = "http://localhost:8000"


def test_service_health():
    """Test if the service is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✓ Service is running and healthy")
            print(f"  - Status: {health_data.get('status')}")
            print(f"  - Active tasks: {health_data.get('active_tasks')}")
            print(f"  - Timestamp: {health_data.get('timestamp')}")
            return True
        else:
            print(f"✗ Service health check failed with status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError as e:
        print("✗ Cannot connect to service. Make sure it's running on http://localhost:8000")
        print(f"  Error details: {str(e)}")
        return False
    except requests.exceptions.Timeout:
        print("✗ Connection to service timed out. The server might be overloaded or not responding.")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during health check: {str(e)}")
        return False


def test_personal_report():
    """Test Activity 2: Personal Report"""
    print("\n" + "=" * 50)
    print("TESTING PERSONAL REPORT")
    print("=" * 50)

    if not os.path.exists(SINGLE_PDF):
        print(f"✗ Test file not found: {SINGLE_PDF}")
        return

    print(f"Using file: {SINGLE_PDF}")

    # Upload file and start processing
    with open(SINGLE_PDF, 'rb') as f:
        files = {'file': (os.path.basename(SINGLE_PDF), f, 'application/pdf')}
        response = requests.post(f"{BASE_URL}/create-personal-report", files=files)

    if response.status_code != 200:
        print(f"✗ Failed to start personal report: {response.text}")
        return

    task_id = response.json()['task_id']
    print(f"✓ Task started: {task_id}")

    # Wait for completion
    max_wait = 120  # 2 minutes
    start_time = time.time()

    while time.time() - start_time < max_wait:
        status_response = requests.get(f"{BASE_URL}/status/{task_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"Status: {status['status']} - {status['message']}")

            if status['status'] == 'completed':
                print("✓ Personal report completed successfully!")
                download_url = status.get('download_url')
                if download_url:
                    print(f"Download URL: {BASE_URL}{download_url}")
                break
            elif status['status'] == 'failed':
                print(f"✗ Personal report failed: {status['message']}")
                break

        time.sleep(5)
    else:
        print("✗ Timeout waiting for personal report completion")


def test_group_report():
    """Test Activity 1: Group Report"""
    print("\n" + "=" * 50)
    print("TESTING GROUP REPORT")
    print("=" * 50)

    if not os.path.exists(FOLDER_PATH):
        print(f"✗ Folder not found: {FOLDER_PATH}")
        return

    # Check if folder has PDF files
    pdf_files = [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"✗ No PDF files found in: {FOLDER_PATH}")
        return

    print(f"Using folder: {FOLDER_PATH}")
    print(f"Found {len(pdf_files)} PDF files: {pdf_files}")

    # Start group processing
    response = requests.post(
        f"{BASE_URL}/create-group-report",
        data={'folder_path': FOLDER_PATH}
    )

    if response.status_code != 200:
        print(f"✗ Failed to start group report: {response.text}")
        return

    task_id = response.json()['task_id']
    print(f"✓ Task started: {task_id}")

    # Wait for completion
    max_wait = 300  # 5 minutes for group processing
    start_time = time.time()

    while time.time() - start_time < max_wait:
        status_response = requests.get(f"{BASE_URL}/status/{task_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"Status: {status['status']} - {status['message']}")

            if status['status'] == 'completed':
                print("✓ Group report completed successfully!")
                download_url = status.get('download_url')
                if download_url:
                    print(f"Download URL: {BASE_URL}{download_url}")
                break
            elif status['status'] == 'failed':
                print(f"✗ Group report failed: {status['message']}")
                break

        time.sleep(10)
    else:
        print("✗ Timeout waiting for group report completion")


def test_dual_report():
    """Test Activity 3: Dual Report (placeholder)"""
    print("\n" + "=" * 50)
    print("TESTING DUAL REPORT (Placeholder)")
    print("=" * 50)

    if not os.path.exists(SINGLE_PDF):
        print(f"✗ Test file not found: {SINGLE_PDF}")
        return

    print(f"Using file twice for demo: {SINGLE_PDF}")

    # Upload both files (same file for demo)
    with open(SINGLE_PDF, 'rb') as f1, open(SINGLE_PDF, 'rb') as f2:
        files = [
            ('file1', (os.path.basename(SINGLE_PDF), f1, 'application/pdf')),
            ('file2', (os.path.basename(SINGLE_PDF) + "_copy", f2, 'application/pdf'))
        ]
        response = requests.post(f"{BASE_URL}/create-dual-report", files=files)

    if response.status_code != 200:
        print(f"✗ Failed to start dual report: {response.text}")
        return

    task_id = response.json()['task_id']
    print(f"✓ Task started: {task_id}")

    # Wait for completion (should be quick since it's just a placeholder)
    time.sleep(3)
    status_response = requests.get(f"{BASE_URL}/status/{task_id}")
    if status_response.status_code == 200:
        status = status_response.json()
        print(f"Status: {status['status']} - {status['message']}")
        if status['status'] == 'completed':
            print("✓ Dual report placeholder completed!")


def test_translate():
    """Test Activity 4: Translate (placeholder)"""
    print("\n" + "=" * 50)
    print("TESTING TRANSLATE (Placeholder)")
    print("=" * 50)

    if not os.path.exists(SINGLE_PDF):
        print(f"✗ Test file not found: {SINGLE_PDF}")
        return

    print(f"Using file: {SINGLE_PDF}")

    # Upload file for translation
    with open(SINGLE_PDF, 'rb') as f:
        files = {'file': (os.path.basename(SINGLE_PDF), f, 'application/pdf')}
        response = requests.post(f"{BASE_URL}/translate", files=files)

    if response.status_code != 200:
        print(f"✗ Failed to start translation: {response.text}")
        return

    task_id = response.json()['task_id']
    print(f"✓ Task started: {task_id}")

    # Wait for completion (should be quick since it's just a placeholder)
    time.sleep(2)
    status_response = requests.get(f"{BASE_URL}/status/{task_id}")
    if status_response.status_code == 200:
        status = status_response.json()
        print(f"Status: {status['status']} - {status['message']}")
        if status['status'] == 'completed':
            print("✓ Translation placeholder completed!")


def main():
    """Run all tests"""
    print("MBTI FastAPI Service - Quick Test")
    print("=" * 50)

    # Check if service is running
    if not test_service_health():
        print("\nPlease start the service first:")
        print("python main.py")
        return

    print(f"\nUsing test files:")
    print(f"Single PDF: {SINGLE_PDF}")
    print(f"Folder: {FOLDER_PATH}")

    # Test all activities
    test_personal_report()
    test_group_report()
    test_dual_report()
    test_translate()

    print("\n" + "=" * 50)
    print("All tests completed!")
    print(f"Check the {OUTPUT_DIR} folder for generated files.")
    print("Visit http://localhost:8000/docs for the API documentation.")

    # List files in output directory
    if os.path.exists(OUTPUT_DIR):
        files = os.listdir(OUTPUT_DIR)
        if files:
            print(f"\nFiles in output directory ({OUTPUT_DIR}):")
            for file in files:
                print(f"  - {file}")
        else:
            print(f"\nOutput directory is empty: {OUTPUT_DIR}")
    else:
        print(f"\nOutput directory does not exist: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()