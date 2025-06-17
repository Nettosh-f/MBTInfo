import os
import webbrowser
import tempfile
from PIL import Image as PILImage
# local imports
from data_extractor import extract_and_save_text
from utils import get_all_info, find_and_parse_mbti_scores, convert_scores_to_mbti_dict, collect_qualities, get_dominant
from utils import get_three_repeating_explanations, get_facet_explanations, get_facet_descriptor
from consts import FACETS, dominant_functions, All_Facets, facet_chart_list


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

    # Get the dominant function based on the MBTI type
    mbti_type = info.get('type')
    if mbti_type:
        dominant_function = get_dominant(text_file_path)
        if dominant_function:
            info['dominant'] = dominant_function
            print(f"Dominant function: {dominant_function}")
        else:
            print(f"Warning: Could not determine dominant function for type {mbti_type}")

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

    # Get facets that appear exactly 3 times
    repeating_explanations = get_three_repeating_explanations(text_file_path)
    three_repeating_facets = list(repeating_explanations.keys())
    print(f"Three repeating facets: {three_repeating_facets}")

    # Get facet descriptors for each repeating facet
    facet_descriptors = {}
    for facet in three_repeating_facets:
        descriptor = get_facet_descriptor(text_file_path, facet)
        facet_descriptors[facet] = descriptor
        print(f"Descriptor for {facet}: {descriptor}")

    # Generate HTML report
    html_content = generate_html_report(info, mbti_dict, preferred_qualities, midzone_qualities, out_qualities,
                                        repeating_explanations, facet_descriptors, input_pdf_path)

    # Save HTML to a temporary file
    temp_html_path = os.path.join(output_dir, f"{os.path.splitext(output_filename)[0]}.html")
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Convert HTML to PDF using pdfkit or weasyprint
    output_path = os.path.join(output_dir, output_filename.replace('.xlsx', '.pdf'))

    try:
        # Try using WeasyPrint first (more reliable for complex layouts)
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(output_path)
        print(f"PDF generated successfully using WeasyPrint: {output_path}")
    except ImportError:
        try:
            # Fall back to pdfkit if WeasyPrint is not available
            import pdfkit
            options = {
                'page-size': 'Letter',
                'encoding': 'UTF-8',
                'enable-local-file-access': None,
                'quiet': None
            }
            pdfkit.from_string(html_content, output_path, options=options)
            print(f"PDF generated successfully using pdfkit: {output_path}")
        except ImportError:
            # If neither library is available, fall back to browser method
            print("PDF generation libraries not found. Falling back to browser method.")
            print(f"Opening HTML report in browser. Please save as PDF to: {output_path}")
            webbrowser.open(f"file://{os.path.abspath(temp_html_path)}")

    return output_path


def generate_html_report(info, mbti_dict, preferred_qualities, midzone_qualities, out_qualities,
                         three_repeating_explanations, facet_descriptors, input_pdf_path):
    """Generate HTML content for the MBTI report"""

    # Helper function to map facet name to image path
    def get_facet_image_path(facet_name):
        from consts import facet_chart_list
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

        # Get the PDF file name from the input_pdf_path
        pdf_base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]

        for filename, facets in facet_chart_list.items():
            if facet_name.lower() in [f.lower() for f in facets]:
                # Use the PDF file name as part of the path
                image_path = os.path.join(project_root, 'backend/media', pdf_base_name, 'screenshots', filename)

                # Check if the file exists
                if os.path.isfile(image_path):
                    # Convert to data URL for embedding in HTML
                    try:
                        with open(image_path, 'rb') as img_file:
                            import base64
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            img_ext = os.path.splitext(image_path)[1].lstrip('.')
                            return f"data:image/{img_ext};base64,{img_data}"
                    except Exception as e:
                        print(f"Error converting facet image to data URL: {str(e)}")
                        return ""
                else:
                    print(f"Warning: Facet image file not found: {image_path}")

        print(f"No matching facet chart found for: {facet_name}")
        return ""

    mbti_type = info.get('type', '')
    dominant_function = info.get('dominant', '')
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    print(f"Project root: {project_root}")

    # Initialize image paths dictionary
    image_paths = {}

    # Only proceed if we have a valid MBTI type
    if mbti_type and mbti_type in [
        'ESTJ', 'ENTJ', 'ESFJ', 'ENFJ', 'ISTJ', 'ISFJ', 'INTJ', 'INFJ',
        'ESTP', 'ESFP', 'ENTP', 'ENFP', 'ISTP', 'ISFP', 'INTP', 'INFP'
    ]:
        # General image based on MBTI type
        general_path = os.path.join(project_root, f'Media/Personal_Report_Media/General_Pics/{mbti_type}_General.png')
        if os.path.isfile(general_path):
            image_paths['general'] = general_path
        else:
            print(f"Warning: General image not found for type {mbti_type}: {general_path}")

        # Dominant function image based on MBTI type
        if dominant_function:
            dominant_path = os.path.join(project_root,
                                         f'Media/Personal_Report_Media/Dominant_Pics/{mbti_type}_Dominant.png')
            if os.path.isfile(dominant_path):
                image_paths['dominant'] = dominant_path
            else:
                print(f"Warning: Dominant function image not found for type {mbti_type}: {dominant_path}")

        # External function image based on MBTI type
        external_path = os.path.join(project_root,
                                     f'Media/Personal_Report_Media/External_Pics/{mbti_type}_External.png')
        if os.path.isfile(external_path):
            image_paths['external'] = external_path
        else:
            print(f"Warning: External function image not found for type {mbti_type}: {external_path}")

        # Internal function image based on MBTI type
        internal_path = os.path.join(project_root,
                                     f'Media/Personal_Report_Media/Internal_Pics/{mbti_type}_Internal.png')
        if os.path.isfile(internal_path):
            image_paths['internal'] = internal_path
        else:
            print(f"Warning: Internal function image not found for type {mbti_type}: {internal_path}")

    # Convert images to base64
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
    
    # Load the logo image
    logo_path = os.path.join(project_root, 'Media/full_logo.png')
    logo_data_url = ""
    if os.path.isfile(logo_path):
        try:
            with open(logo_path, 'rb') as img_file:
                import base64
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                logo_data_url = f"data:image/png;base64,{img_data}"
        except Exception as e:
            print(f"Error converting logo to data URL: {str(e)}")
    else:
        print(f"Warning: Logo file not found: {logo_path}")

    three_repeating_facets = list(three_repeating_explanations.keys())

    # Generate facet sections
    facet_sections_html = ""
    if not three_repeating_facets:
        facet_sections_html = """
        <div class="page-break"></div>
        <div class="content-wrapper page-content">
            <h2>Personal Focus Areas</h2>
            <div class="section">
                <p>No facets were identified as appearing consistently across all three contexts 
                (communication, managing change, and managing conflict).</p>
                <p>This suggests that you may use different approaches depending on the context.</p>
            </div>
        </div>
        """
    else:
        for facet in three_repeating_facets:
            descriptor = facet_descriptors.get(facet, f"No descriptor available for {facet}.")
            explanations = three_repeating_explanations.get(facet, [])
            while len(explanations) < 3:
                explanations.append(f"No explanation available for {facet}.")

            display_facet = facet.capitalize()
            facet_image_path = get_facet_image_path(facet)
            facet_image_tag = f'<div class="facet-image-container"><img src="{facet_image_path}" alt="{display_facet} Chart"></div>' if facet_image_path else ""

            facet_sections_html += f"""
            <div class="page-break"></div>
            <div class="content-wrapper page-content" style="margin-bottom: 5px;">
                <h2>Personal Focus: {display_facet}</h2>
                <p style="text-align: center;">
                היבטים המופיעים במספר מימדים לאורך הדו"ח שלך
                </p>

                {facet_image_tag}

                <div class="section">
                    <h3>General Description</h3>
                    <p>{descriptor}</p>
                </div>

                <div class="section">
                    <h3>{display_facet} in <u>Communication</u></h3>
                    <p>{explanations[0]}</p>
                </div>

                <div class="section">
                    <h3>{display_facet} in <u>Managing Change</u></h3>
                    <p>{explanations[1]}</p>
                </div>

                <div class="section">
                    <h3>{display_facet} in <u>Managing Conflict</u></h3>
                    <p>{explanations[2]}</p>
                </div>
            </div>
            """

    # Final HTML Template
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
                    margin-bottom: 40px; /* Ensure space for footer */
                }}
                body {{
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }}
                .page-break {{
                    page-break-before: always;
                }}
                .no-break {{
                    page-break-inside: avoid;
                }}
                .footer {{
                    position: fixed;
                    bottom: 0px;
                    left: 0;
                    right: 0;
                }}
                .logo {{
                    position: fixed;
                    top: -50px;  /* Moved closer to the top */
                    left: 50%;
                    transform: translateX(-50%);
                    width: 100px; /* Adjust size as needed */
                    height: auto;
                    z-index: 1000;
                }}
                .logo img {{
                    border: none;
                    padding: 0;
                    background: none;
                }}
            }}
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 8.5in;
                margin: 0 auto;
                padding: 0;
                text-align: center;
            }}
            .logo {{
                position: fixed;
                top: -50px;
                left: 50%;
                transform: translateX(-50%);
                width: 100px;
                height: auto;
                z-index: 1000;
            }}
            .logo img {{
                width: 100%;
                height: auto;
                border: none;
                padding: 0;
                background: none;
            }}
            /* Add padding to the top of each page to make room for the logo */
            .page-content {{
                padding-top: 10px; /* Adjust based on logo size */
            }}
            h1, h2, h3 {{
                color: #2c3e50;
                text-align: center;
            }}
            h1 {{ font-size: 20pt; margin-bottom: 5px; }}
            h2 {{ 
                text-decoration: underline;
                font-size: 16pt; 
                padding-bottom: 5px; 
                margin-top: 5px;
                margin-bottom: 0px; /* Reduce bottom margin */
                display: inline-block; 
                padding: 0 5px 5px; 
                }}
            h3 {{ font-size: 12pt; margin-top: 5px; margin-bottom: 5px; }}
            p {{ text-align: justify; margin: 5px auto 10px; max-width: 100%; }}
            .info-box p {{ text-align: center;}}
            .type-header {{ font-size: 20pt; font-weight: bold; text-align: center; margin: 5px 0; }}
            .image-container {{text-align: center; margin: 5px auto; max-width: 65%; max-height: 40% }}
            .image-container img {{ 
                max-width: 100%; 
                height: auto; 
                display: block; 
                margin: 0 auto; 
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); /* Right-bottom drop shadow */
            }}
            .dominant-image img {{ max-width: 90%; max-height: 50%; }}
            .facet-image-container {{ text-align: center; margin: 5px auto; width: 100%; }}
            .facet-image-container img {{ 
                width: 75%; 
                height: auto; 
                display: block; 
                margin: 0 auto; 
                margin-bottom: 10px; 
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); /* Right-bottom drop shadow */
            }}
            table {{ width: 80%; border-collapse: collapse; margin: 5px auto; }}

            table, th, td {{ border: 1px solid #ddd; }}
            th, td {{ padding: 5px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
            .chart-container {{ margin: 5px auto; height: 300px; width: 80%; }}
            .section {{
                margin: 5px auto; 
                max-width: 90%; 
            }}
            .section p {{
                text-align: left !important;
                margin: 5px auto 10px;
                max-width: 100%;
            }}
            .content-wrapper {{
                text-align: center;
            }}
            .first-page {{ 
                min-height: 90vh; 
                text-align: center;
            }}
            .first-page .image-container {{ 
                max-width: 33%; 
                max-height: 33%; 
                padding-bottom: 30px; 
            }}
            /* Add a frame to all images */
            img {{
                border: 1px solid #2c3e50;
                padding: 3px;
                background-color: white;
            }}
            .general-image {{
                padding:0;
                margin:0;
            }}
            .IntExtimg img {{ 
                max-width: 80%; 
                max-height: 50%;
                display: block; 
                margin: 10px auto 20px auto; 
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); /* Right-bottom drop shadow */
            }}
            .functionality-description {{
                text-align: center;
                margin: 5px auto 10px;
                max-width: 80%;
            }}
            .footer {{
                position: fixed;
                bottom: 20px;
                left: 0;
                right: 0;
                text-align: center;
                font-size: 9pt;
                color: #666;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 10px;
            }}
            .footer img {{
                height: 20px;
                width: auto;
                vertical-align: middle;
                border: none;
                padding: 0;
                background: none;
            }}
        </style>
    </head>
    <body>
        <div class="logo">
            <img src="{logo_data_url}" alt="Company Logo">
        </div>

        <div class="first-page no-break page-content">
            <h1>{info['name']} - MBTI Personal Report</h1>
            <div class="info-box">
                <p>Your MBTI Type:<strong> {info['type']}</strong></p>
            </div>
            <div class="image-container">
                <img class="general-image" src="{image_data_urls.get('general', '')}" alt="MBTI Type General Image">
            </div>
            <h2>הפונקציה המנטלית</h2>
            <div class="type-header">{info.get('dominant', 'Not specified')}</div>
            <div class="dominant-image">
                <img src="{image_data_urls.get('dominant', '')}" alt="MBTI Dominant Function Image">
            </div>
        </div>

        <div class="page-break"></div>
        <div class="content-wrapper page-content">
            <h2>אותיות חיצוניות</h2>
            <p class="functionality-description">מדברות על נראות חיצונית, וייב, גישה לחיים והתנהלות ביום-יום</p>
            <div class="IntExtimg" style="margin-bottom: 5px">
                <img src="{image_data_urls.get('external', '')}" alt="MBTI External Function Image" style="width: 185px; height: 300px; object-fit: contain;">
            </div>

            <h2>אותיות פנימיות</h2>
            <p class="functionality-description">מדברות על תחומי עניין, סוג הקשר עם אחרים, תשוקה פנימית, מה "עושלי את זה", וכן על גבי איזה "פנימיות" רוכבת או מתבססת ההתנהלות שמתוארת ע"י האותיות החיצוניות</p>
            <div class="IntExtimg">
                <img src="{image_data_urls.get('internal', '')}" alt="MBTI Internal Function Image" style="width: 209px; height: 300px; object-fit: contain;">
            </div>
        </div>

        {facet_sections_html}

        <div class="footer">
            All rights reserved © <img src="{logo_data_url}" alt="TEMBTI Logo">
        </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    # For testing purposes
    input_pdf_path = r"C:\Users\user\Downloads\Shiri-Ben Sinai.pdf"
    output_dir = r"F:\projects\MBTInfo\output"
    output_filename = "Shiri-Ben Sinai_Personal_MBTI_Report_Test.pdf"

    if os.path.exists(input_pdf_path):
        output_path = generate_personal_report(input_pdf_path, output_dir, output_filename)
        print(f"Personal MBTI report generated at: {output_path}")
    else:
        print(f"Input file not found: {input_pdf_path}")
        print("Please provide a valid PDF file path for testing.")
