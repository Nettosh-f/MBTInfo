"""
Simple client example for the 4 MBTI processing activities
"""
import requests
import time
import os

class MBTIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def create_group_report(self, folder_path: str) -> str:
        """
        Activity 1: Create group report from folder of PDFs
        """
        response = requests.post(
            f"{self.base_url}/create-group-report",
            data={'folder_path': folder_path}
        )
        response.raise_for_status()
        return response.json()['task_id']

    def create_personal_report(self, pdf_file_path: str) -> str:
        """
        Activity 2: Create personal report from single PDF
        """
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"File not found: {pdf_file_path}")

        with open(pdf_file_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_file_path), f, 'application/pdf')}
            response = requests.post(
                f"{self.base_url}/create-personal-report",
                files=files
            )
            response.raise_for_status()
            return response.json()['task_id']

    def create_dual_report(self, pdf1_path: str, pdf2_path: str) -> str:
        """
        Activity 3: Create dual report from two PDFs (to be implemented)
        """
        if not os.path.exists(pdf1_path) or not os.path.exists(pdf2_path):
            raise FileNotFoundError("One or both PDF files not found")

        with open(pdf1_path, 'rb') as f1, open(pdf2_path, 'rb') as f2:
            files = [
                ('file1', (os.path.basename(pdf1_path), f1, 'application/pdf')),
                ('file2', (os.path.basename(pdf2_path), f2, 'application/pdf'))
            ]
            response = requests.post(
                f"{self.base_url}/create-dual-report",
                files=files
            )
            response.raise_for_status()
            return response.json()['task_id']

    def translate_pdf(self, pdf_file_path: str) -> str:
        """
        Activity 4: Translate PDF (to be implemented)
        """
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"File not found: {pdf_file_path}")

        with open(pdf_file_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_file_path), f, 'application/pdf')}
            response = requests.post(
                f"{self.base_url}/translate",
                files=files
            )
            response.raise_for_status()
            return response.json()['task_id']

    def get_status(self, task_id: str) -> dict:
        """Get task status"""
        response = requests.get(f"{self.base_url}/status/{task_id}")
        response.raise_for_status()
        return response.json()

    def wait_for_completion(self, task_id: str, max_wait: int = 300) -> dict:
        """Wait for task to complete"""
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status = self.get_status(task_id)
            print(f"Status: {status['status']} - {status['message']}")

            if status['status'] in ['completed', 'failed']:
                return status

            time.sleep(5)

        raise TimeoutError(f"Task {task_id} did not complete within {max_wait} seconds")

    def download_file(self, task_id: str, filename: str, save_path: str = None) -> str:
        """Download completed file"""
        response = requests.get(f"{self.base_url}/download/{task_id}/{filename}")
        response.raise_for_status()

        if save_path is None:
            save_path = filename

        with open(save_path, 'wb') as f:
            f.write(response.content)

        return save_path


def example_usage():
    """Example usage of all 4 activities with your specific file paths"""
    client = MBTIClient()

    print("=== MBTI Processing Service - 4 Activities Demo ===\n")

    # Activity 1: Create Group Report
    print("1. CREATE GROUP REPORT")
    print("-" * 30)
    try:
        folder_path = r"/input"
        print(f"Processing folder: {folder_path}")

        task_id = client.create_group_report(folder_path)
        print(f"Task started: {task_id}")

        final_status = client.wait_for_completion(task_id)
        if final_status['status'] == 'completed':
            # Extract filename from download URL
            filename = final_status['download_url'].split('/')[-1]
            downloaded_file = client.download_file(task_id, filename)
            print(f"✓ Group report downloaded: {downloaded_file}")
        else:
            print(f"✗ Failed: {final_status['message']}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "="*50 + "\n")

    # Activity 2: Create Personal Report
    print("2. CREATE PERSONAL REPORT")
    print("-" * 30)
    try:
        pdf_path = r"/input/nir-bensinai-MBTI.pdf"
        print(f"Processing file: {pdf_path}")

        task_id = client.create_personal_report(pdf_path)
        print(f"Task started: {task_id}")

        final_status = client.wait_for_completion(task_id)
        if final_status['status'] == 'completed':
            filename = final_status['download_url'].split('/')[-1]
            downloaded_file = client.download_file(task_id, filename)
            print(f"✓ Personal report downloaded: {downloaded_file}")
        else:
            print(f"✗ Failed: {final_status['message']}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "="*50 + "\n")

    # Activity 3: Create Dual Report
    print("3. CREATE DUAL REPORT (To be implemented)")
    print("-" * 30)
    try:
        # Using two files from your input folder for dual report example
        pdf1_path = r"/input/nir-bensinai-MBTI.pdf"
        # You can add another PDF file path here when you have multiple files
        pdf2_path = r"/input/nir-bensinai-MBTI.pdf"  # Using same file for demo
        print(f"Processing files: {os.path.basename(pdf1_path)} and {os.path.basename(pdf2_path)}")

        task_id = client.create_dual_report(pdf1_path, pdf2_path)
        print(f"Task started: {task_id}")

        final_status = client.wait_for_completion(task_id)
        if final_status['status'] == 'completed':
            filename = final_status['download_url'].split('/')[-1]
            downloaded_file = client.download_file(task_id, filename)
            print(f"✓ Dual report placeholder downloaded: {downloaded_file}")
        else:
            print(f"✗ Failed: {final_status['message']}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "="*50 + "\n")

    # Activity 4: Translate PDF
    print("4. TRANSLATE PDF (To be implemented)")
    print("-" * 30)
    try:
        pdf_path = r"/input/nir-bensinai-MBTI.pdf"
        print(f"Translating file: {os.path.basename(pdf_path)}")

        task_id = client.translate_pdf(pdf_path)
        print(f"Task started: {task_id}")

        final_status = client.wait_for_completion(task_id)
        if final_status['status'] == 'completed':
            filename = final_status['download_url'].split('/')[-1]
            downloaded_file = client.download_file(task_id, filename)
            print(f"✓ Translation message downloaded: {downloaded_file}")
        else:
            print(f"✗ Failed: {final_status['message']}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "="*50)
    print("Demo completed!")


if __name__ == "__main__":
    example_usage()