import os
import webbrowser
import tempfile
from PIL import Image as PILImage
from data_extractor import extract_and_save_text
from utils import get_all_info, find_and_parse_mbti_scores, convert_scores_to_mbti_dict, collect_qualities, get_dominant
from consts import FACETS, type_descriptions, career_insights, dominant_functions


def generate_personal_report(input_pdf_path, output_dir, output_filename):
    """
    Generate a personal MBTI report from a PDF file using HTML and convert to PDF.
    
    Args:
        input_pdf_path (str): Path to the input PDF file
        output_dir (str): Directory to save the output PDF file
        output_filename (str): Name of the output PDF file
    
    Returns:
        str: Path to the generated PDF file
    """
    # Extract text from PDF
    text_file_path = extract_and_save_text(input_pdf_path, output_dir)
    print(f"Text extracted to: {text_file_path}")
    if not text_file_path:
        raise ValueError("Failed to extract text from PDF file")
    
    # Create textfiles directory if it doesn't exist
    textfiles_dir = os.path.join(output_dir, 'textfiles')
    os.makedirs(textfiles_dir, exist_ok=True)
    
    # Read the extracted text content
    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        print(f"Successfully read {len(text_content)} characters from {text_file_path}")
    except Exception as e:
        print(f"Error reading text file: {str(e)}")
        raise ValueError(f"Failed to read extracted text: {str(e)}")
    
    # Save a copy to the textfiles directory
    base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
    textfiles_copy_path = os.path.join(textfiles_dir, f"{base_name}_text.txt")
    
    if text_file_path != textfiles_copy_path:  # Only copy if paths are different
        try:
            with open(textfiles_copy_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"Text content copied to: {textfiles_copy_path}")
        except Exception as e:
            print(f"Warning: Failed to copy text to textfiles directory: {str(e)}")
            # Continue execution even if copy fails
    
    # Extract MBTI information
    info = get_all_info(text_file_path)
    print(f"MBTI Information: {info}")
    if not info:
        info = {'name': 'Unknown', 'date': 'Unknown', 'type': 'Unknown'}
    
    qualities = find_and_parse_mbti_scores(text_file_path)
    if not qualities:
        qualities = {}
    
    mbti_dict = convert_scores_to_mbti_dict(qualities)
    if not mbti_dict:
        # Create a default dictionary with zeros
        mbti_dict = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    
    # Handle potential None values from collect_qualities
    try:
        result = collect_qualities(text_file_path)
        if result is None or len(result) != 3:
            preferred_qualities, midzone_qualities, out_qualities = [], [], []
        else:
            preferred_qualities, midzone_qualities, out_qualities = result
    except Exception as e:
        print(f"Error collecting qualities: {str(e)}")
        preferred_qualities, midzone_qualities, out_qualities = [], [], []
    
    # Generate HTML report
    html_content = generate_html_report(info, mbti_dict, preferred_qualities, midzone_qualities, out_qualities)
    
    # Save HTML to a temporary file
    temp_html_path = os.path.join(output_dir, f"{os.path.splitext(output_filename)[0]}.html")
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Convert HTML to PDF
    output_path = os.path.join(output_dir, output_filename.replace('.xlsx', '.pdf'))
    
    # Open HTML in browser for printing to PDF
    print(f"Opening HTML report in browser. Please save as PDF to: {output_path}")
    webbrowser.open(f"file://{os.path.abspath(temp_html_path)}")
    
    return output_path


def generate_html_report(info, mbti_dict, preferred_qualities, midzone_qualities, out_qualities):
    """Generate HTML content for the MBTI report"""
    
    # Get image paths
    mbti_type = info['type']
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    image_paths = {}
    if mbti_type and mbti_type in ['ESTJ', 'ENTJ', 'ESFJ', 'ENFJ', 'ISTJ', 'ISFJ', 'INTJ', 'INFJ', 
                                   'ESTP', 'ESFP', 'ENTP', 'ENFP', 'ISTP', 'ISFP', 'INTP', 'INFP']:
        image_paths = {
            'general': os.path.join(project_root, f'Media/Personal_Report_Media/General_Pics/{mbti_type}_General.png'),
            'dominant': os.path.join(project_root, f'Media/Personal_Report_Media/Dominant_Pics/{mbti_type}_Dominant.png'),
            'external': os.path.join(project_root, f'Media/Personal_Report_Media/External_Pics/{mbti_type}_External.png'),
            'internal': os.path.join(project_root, f'Media/Personal_Report_Media/Internal_Pics/{mbti_type}_Internal.png')
        }
    
    # Convert image paths to data URLs for embedding in HTML
    image_data_urls = {}
    for key, path in image_paths.items():
        if os.path.isfile(path):
            try:
                with open(path, 'rb') as img_file:
                    import base64
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    img_ext = os.path.splitext(path)[1].lstrip('.')
                    image_data_urls[key] = f"data:image/{img_ext};base64,{img_data}"
            except Exception as e:
                print(f"Error converting image to data URL: {str(e)}")
                image_data_urls[key] = ""
        else:
            print(f"Warning: Image file not found: {path}")
            image_data_urls[key] = ""
    
    # Generate HTML content
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{info['name']} - MBTI Personal Report</title>
        <style>
            @media print {{
                @page {{
                    size: letter portrait;
                    margin: 0.5in;
                }}
                body {{
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }}
            }}
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 8.5in;
                margin: 0 auto;
                padding: 0.5in;
                text-align: center;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
                text-align: center;
            }}
            h1 {{
                font-size: 24pt;
                margin-bottom: 20px;
            }}
            h2 {{
                font-size: 18pt;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
                margin-top: 30px;
                display: inline-block;
                padding: 0 20px 5px;
            }}
            h3 {{
                font-size: 14pt;
                margin-top: 20px;
            }}
            p {{
                text-align: center;
            }}
            .info-box {{
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin: 20px auto;
                max-width: 80%;
                text-align: center;
            }}
            .type-header {{
                font-size: 20pt;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
            }}
            .image-container {{
                text-align: center;
                margin: 20px auto;
                max-width: 90%;
            }}
            .image-container img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 0 auto;
            }}
            .page-break {{
                page-break-before: always;
            }}
            table {{
                width: 80%;
                border-collapse: collapse;
                margin: 20px auto;
            }}
            table, th, td {{
                border: 1px solid #ddd;
            }}
            th, td {{
                padding: 10px;
                text-align: center;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .chart-container {{
                margin: 20px auto;
                height: 300px;
                width: 80%;
            }}
            .section {{
                margin: 30px auto;
                max-width: 90%;
            }}
            .content-wrapper {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 80vh;
            }}
        </style>
    </head>
    <body>
        <div class="content-wrapper">
            <h1>{info['name']} - MBTI Personal Report</h1>
            
            <div class="info-box">
                <p><strong>Your MBTI Type:</strong> {info['type']}</p>
                <p><strong>Date:</strong> {info.get('date', 'Not specified')}</p>
            </div>
            
            <div class="image-container">
                <img src="{image_data_urls.get('general', '')}" alt="MBTI Type General Image">
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="content-wrapper">
            <h2>Mental Functionality Type</h2>
            <div class="type-header">{info.get('dominant', 'Not specified')}</div>
            
            <div class="image-container">
                <img src="{image_data_urls.get('dominant', '')}" alt="MBTI Dominant Function Image">
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="content-wrapper">
            <h2>External Functionality</h2>
            <div class="image-container">
                <img src="{image_data_urls.get('external', '')}" alt="MBTI External Function Image">
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="content-wrapper">
            <h2>Internal Functionality</h2>
            <div class="image-container">
                <img src="{image_data_urls.get('internal', '')}" alt="MBTI Internal Function Image">
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="content-wrapper">
            <h2>MBTI Preferences</h2>
            <div class="section">
                <table>
                    <tr>
                        <th>Dimension</th>
                        <th>Score</th>
                    </tr>
                    <tr>
                        <td>Extraversion (E) - Introversion (I)</td>
                        <td>E: {mbti_dict.get('E', 0)} - I: {mbti_dict.get('I', 0)}</td>
                    </tr>
                    <tr>
                        <td>Sensing (S) - Intuition (N)</td>
                        <td>S: {mbti_dict.get('S', 0)} - N: {mbti_dict.get('N', 0)}</td>
                    </tr>
                    <tr>
                        <td>Thinking (T) - Feeling (F)</td>
                        <td>T: {mbti_dict.get('T', 0)} - F: {mbti_dict.get('F', 0)}</td>
                    </tr>
                    <tr>
                        <td>Judging (J) - Perceiving (P)</td>
                        <td>J: {mbti_dict.get('J', 0)} - P: {mbti_dict.get('P', 0)}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <script>
            // Add print dialog when page loads
            window.onload = function() {{
                setTimeout(function() {{
                    window.print();
                }}, 1000);
            }};
        </script>
    </body>
    </html>
    """
    
    return html


if __name__ == "__main__":
    # For testing purposes
    input_pdf_path = r"F:\projects\MBTInfo\input\ADAM-POMERANTZ-267149-e4b6edb5-1a5f-ef11-bdfd-6045bd04b01a.pdf"
    output_dir = r"F:\projects\MBTInfo\output"
    output_filename = "Personal_MBTI_Report_Test.pdf"
    
    if os.path.exists(input_pdf_path):
        output_path = generate_personal_report(input_pdf_path, output_dir, output_filename)
        print(f"Personal MBTI report generated at: {output_path}")
    else:
        print(f"Input file not found: {input_pdf_path}")
        print("Please provide a valid PDF file path for testing.")
