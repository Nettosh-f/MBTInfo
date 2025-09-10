import PyPDF2
import os
from utils import sanitize_filename, safe_makedirs


def extract_and_save_text(filepath: str, output_folder: str) -> str:
    """Extract text from PDF with multiple fallback methods"""
    try:
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Create output filename
        filename = os.path.basename(filepath)
        base_name = os.path.splitext(filename)[0]
        sanitized_base_name = sanitize_filename(base_name + ".dummy").replace(".dummy", "")
        output_filename = f"{sanitized_base_name}_text.txt"
        output_path = os.path.join(output_folder, output_filename)

        print(f"🔄 Extracting text from: {filename}")
        print(f"📝 Output file will be: {output_filename}")

        text = ""

        # Method 1: Try PyPDF2 (your current method)
        try:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            if text.strip():
                print(f"✅ PyPDF2 extraction successful - {len(text)} characters")
            else:
                print(f"⚠️ PyPDF2 extracted no text, trying alternatives...")

        except Exception as e:
            print(f"❌ PyPDF2 failed: {e}")

        # Method 2: Try pypdf (newer version) if PyPDF2 didn't work well
        if not text.strip():
            try:
                from pypdf import PdfReader
                print("🔄 Trying pypdf...")
                reader = PdfReader(filepath)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                if text.strip():
                    print(f"✅ pypdf extraction successful - {len(text)} characters")

            except ImportError:
                print("❌ pypdf not installed")
            except Exception as e:
                print(f"❌ pypdf failed: {e}")

        # Method 3: Try PyMuPDF if still no text
        if not text.strip():
            try:
                import fitz  # PyMuPDF
                print("🔄 Trying PyMuPDF...")
                doc = fitz.open(filepath)
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text += page_text + "\n"
                doc.close()

                if text.strip():
                    print(f"✅ PyMuPDF extraction successful - {len(text)} characters")

            except ImportError:
                print("❌ PyMuPDF not installed")
            except Exception as e:
                print(f"❌ PyMuPDF failed: {e}")

        # Save the text if we got any
        if text.strip():
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(text)
            print(f"💾 Text saved to: {output_path}")
            return output_path
        else:
            print(f"❌ All extraction methods failed for {filename}")
            return ""

    except Exception as e:
        print(f"❌ Error processing {filepath}: {str(e)}")
        return ""


if __name__ == "__main__":
    filepath_test = r"F:\projects\MBTInfo\input\asaf-solomon-267149-4ae2ac9c-005e-ef11-bdfd-6045bd04b01a.pdf"
    output_folder = r"F:\projects\MBTInfo\output\textfiles"
    result = extract_and_save_text(filepath_test, output_folder)
    if result:
        print(f"Text saved to: {result}")
    else:
        print("Failed to extract and save text.")
