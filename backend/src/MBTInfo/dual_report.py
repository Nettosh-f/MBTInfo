import os
import base64
from weasyprint import HTML
from image_manipulation import create_all_graphs
from pathlib import Path
from data_extractor import extract_and_save_text

from utils import get_all_info


def _first_or_none(iterable):
    for x in iterable:
        return x
    return None


def path_exists(p) -> bool:
    try:
        return isinstance(p, (str, bytes, Path)) and os.path.exists(p)
    except Exception:
        return False


def _encode_or_placeholder(p):
    try:
        return encode_image_base64(p) if path_exists(p) else create_placeholder_image_base64()
    except Exception:
        return create_placeholder_image_base64()


def find_graph_by_suffix(media_tmp_root: str, identifier: str, suffix: str) -> str | None:
    """
    Look for any file that ends with '_<suffix>' under .../tmp/<identifier>/.
    We first try the common 'final' subdir, then fall back to a recursive search.
    """
    root = Path(media_tmp_root) / identifier

    # 1) Try the common final dir (fast path)
    final_dir = root / "final"
    exact = final_dir / f"{identifier}_{suffix}"
    if exact.exists():
        return str(exact)

    # 2) Try anywhere under the identifier folder for an exact filename
    exact_any = _first_or_none(root.rglob(f"{identifier}_{suffix}"))
    if exact_any:
        return str(exact_any)

    # 3) Relax: any file that ends with the requested suffix (e.g., *_EIGraph_final.png)
    loose = _first_or_none(root.rglob(f"*_{suffix}"))
    if loose:
        return str(loose)

    return None


def sanitize_filename(filename):
    """
    Sanitize filename by replacing spaces and other problematic characters with hyphens
    """
    # Remove file extension first
    name, ext = os.path.splitext(filename)
    # Replace spaces and other problematic characters with hyphens
    sanitized = name.replace(" ", "-").replace("_", "-")
    # Remove multiple consecutive hyphens
    while "--" in sanitized:
        sanitized = sanitized.replace("--", "-")
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip("-")
    return sanitized + ext


def sanitize_path_component(path_component):
    """
    Sanitize a path component (folder or file name) by replacing spaces with hyphens
    """
    return path_component.replace(" ", "-").replace("_", "-")


def encode_image_base64(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def create_placeholder_image_base64():
    """
    Creates a simple placeholder image as base64 when actual graph is missing
    """
    from PIL import Image, ImageDraw, ImageFont
    import io

    # Create a simple placeholder image
    img = Image.new('RGB', (800, 400), color='lightgray')
    draw = ImageDraw.Draw(img)

    # Add text
    text = "Graph not available"
    try:
        # Try to use a better font if available
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    x = (800 - text_width) // 2
    y = (400 - text_height) // 2

    draw.text((x, y), text, fill='black', font=font)

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def generate_dual_report(pdf1_path, pdf2_path, output_pdf_path):
    text_folder = fr"F:\projects\MBTInfo\output\textfiles"
    os.makedirs(text_folder, exist_ok=True)

    # Extract and save text files (this will create files with sanitized names)
    extract_and_save_text(pdf1_path, text_folder)
    extract_and_save_text(pdf2_path, text_folder)

    # Create sanitized names that match what extract_and_save_text creates
    original_name1 = os.path.basename(pdf1_path).replace(".pdf", "")
    original_name2 = os.path.basename(pdf2_path).replace(".pdf", "")

    # Sanitize the names to match the files that were created
    sanitized_name1 = sanitize_filename(original_name1 + ".dummy").replace(".dummy", "")
    sanitized_name2 = sanitize_filename(original_name2 + ".dummy").replace(".dummy", "")

    # Build text file paths using sanitized names
    text1 = os.path.join(text_folder, f"{sanitized_name1}_text.txt")
    text2 = os.path.join(text_folder, f"{sanitized_name2}_text.txt")

    # Debug: Check if files exist
    print(f"DEBUG: Looking for text files:")
    print(f"  PDF1 text file: {text1} (exists: {os.path.exists(text1)})")
    print(f"  PDF2 text file: {text2} (exists: {os.path.exists(text2)})")

    if not os.path.exists(text1):
        raise FileNotFoundError(f"Text file not found: {text1}")
    if not os.path.exists(text2):
        raise FileNotFoundError(f"Text file not found: {text2}")

    # Get info from text files
    info_pdf1 = get_all_info(text1)
    info_pdf2 = get_all_info(text2)

    # Create sanitized identifier for folder/file creation
    first_name_part = sanitize_path_component(os.path.basename(pdf1_path)[:6])
    second_name_part = sanitize_path_component(os.path.basename(pdf2_path)[:6])
    identifier = f"{first_name_part}_{second_name_part}"

    media_path = os.path.join(r"F:\projects\MBTInfo\backend\media\tmp", identifier)

    try:
        create_all_graphs(pdf1_path, pdf2_path, media_path)
    except Exception as e:
        print(f"WARNING: Graph creation failed: {e}")
        print("Continuing with available graphs...")

    logo_path = r'F:\projects\MBTInfo\backend\media\full_logo.png'

    # Construct the output directory for the PDF
    output_dir = output_pdf_path
    final_images_path = rf"F:\projects\MBTInfo\backend\media\tmp\{identifier}\final"

    # Define all expected image paths
    media_tmp_root = r"F:\projects\MBTInfo\backend\media\tmp"
    graph_suffixes = [
        "first_graph_final.png",
        "EIGraph_final.png",
        "TFgraph_final.png",
        "JPgraph_final.png",
        "SNgraph_final.png",
        "dominant_final_final.png",
    ]

    all_images_path = [
        find_graph_by_suffix(media_tmp_root, identifier, suf) for suf in graph_suffixes
    ]
    # Check which images actually exist
    print("DEBUG: Checking for generated images:")
    for i, p in enumerate(all_images_path):
        exists_flag = path_exists(p)
        print(f"  {i}: {p} (exists: {exists_flag})")

    first_graph_base64 = _encode_or_placeholder(all_images_path[0])
    ei_graph_base64 = _encode_or_placeholder(all_images_path[1])
    tf_graph_base64 = _encode_or_placeholder(all_images_path[2])
    jp_graph_base64 = _encode_or_placeholder(all_images_path[3])
    sn_graph_base64 = _encode_or_placeholder(all_images_path[4])
    dominant_graph_base64 = _encode_or_placeholder(all_images_path[5])

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
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

    # Encode graphs to base64 with fallback for missing images
    try:
        first_graph_base64 = encode_image_base64(all_images_path[0]) if os.path.exists(
            all_images_path[0]) else create_placeholder_image_base64()
    except Exception as e:
        print(f"Error encoding first graph: {e}")
        first_graph_base64 = create_placeholder_image_base64()

    try:
        ei_graph_base64 = encode_image_base64(all_images_path[1]) if os.path.exists(
            all_images_path[1]) else create_placeholder_image_base64()
    except Exception as e:
        print(f"Error encoding EI graph: {e}")
        ei_graph_base64 = create_placeholder_image_base64()

    try:
        sn_graph_base64 = encode_image_base64(all_images_path[4]) if os.path.exists(
            all_images_path[4]) else create_placeholder_image_base64()
    except Exception as e:
        print(f"Error encoding SN graph: {e}")
        sn_graph_base64 = create_placeholder_image_base64()

    try:
        tf_graph_base64 = encode_image_base64(all_images_path[2]) if os.path.exists(
            all_images_path[2]) else create_placeholder_image_base64()
    except Exception as e:
        print(f"Error encoding TF graph: {e}")
        tf_graph_base64 = create_placeholder_image_base64()

    try:
        jp_graph_base64 = encode_image_base64(all_images_path[3]) if os.path.exists(
            all_images_path[3]) else create_placeholder_image_base64()
    except Exception as e:
        print(f"Error encoding JP graph: {e}")
        jp_graph_base64 = create_placeholder_image_base64()

    try:
        dominant_graph_base64 = encode_image_base64(all_images_path[5]) if os.path.exists(
            all_images_path[5]) else create_placeholder_image_base64()
    except Exception as e:
        print(f"Error encoding dominant graph: {e}")
        dominant_graph_base64 = create_placeholder_image_base64()

    try:
        full_logo_base64 = encode_image_base64(logo_path) if os.path.exists(logo_path) else ""
    except Exception as e:
        print(f"Error encoding logo: {e}")
        full_logo_base64 = ""

    # HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Dual MBTI Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 10px;
                color: #333;
            }}
            h1, h2 {{
                text-align: center;
                color: #2c3e50;
            }}
            .section {{
                margin-top: 20px;
            }}
            .graph {{
                text-align: center;
                padding: 5px 5px 5px 5px;
                padding-bottom: 10px;
            }}
            .names {{
                font-size: 18px;
                text-align: center;
                margin-bottom: 30px;

            }}
            img {{
                max-width: 100%;
                height: auto;

                border: 1px solid #ccc;
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
            .name1 {{
                font-weight: bold;
                color: red;
                text-decoration: underline;
            }}
            .name2 {{
                font-weight: bold;
                color: #0000ad;
                text-decoration: underline;
            }}
            .hebrewText {{
                direction: rtl;
                margin-bottom: 10px;
                }}
            .header-table {{
                width: 80%;
                margin-left: auto;
                margin-right: auto;
                border-collapse: collapse;
            }}
            .header-table td {{
                vertical-align: top;
                padding-right: 10px;
                pedding-left: 10px;
            }}
            .tableContent {{
                text-decoration: none;
                font-size: 16px;
            }}
            .page-break {{
                page-break-before: always;
            }}   
            .logo {{
                position: fixed;
                top: -40px;  /* Changed from -20px to make it visible */
                left: 20px;  /* Changed from -20px to make it visible */
                z-index: 1000;
                margin: 0;
                padding: 0;
            }}
            .logo img {{
                width: 100px;  /* Set a fixed width instead of percentage */
                height: auto;
                padding: 0;  /* Override the general img padding */
            }}  
        </style>
    </head>
    <body>
        {('<div class="logo"><img src="data:image/png;base64,' + full_logo_base64 + '" alt="Company Logo"></div>') if full_logo_base64 else ''}
        <h1>
        ?מה האשיות הזוגית שלכם
        </h1>
        <div class="names"><b class="name1">{info_pdf1['name']}</b> | <b class="name2">  {info_pdf2['name']}</b></div>
        <div class="hebrewText">
        בשכלול הזוגי שלהלן מופיעים מרכיבי האישיות שלכם - במופע משותף.
        </div>
        <div class="hebrewText">
        נסו לזהות היכן הם נוטים לאותו כיוון והיכן הם שונים.
        </div>
        <div class="hebrewText">
        במקומות בהן הנטייה <strong>דומה</strong>, אמנם יש לכם צד חזק מאוד, באישיות המשותפת שלכם, אולם ייתכן גם שיש לכם, "אזורי עיוורון". נסו לתת על זה את דעתכם, ולחשוב, כיצד אתם יכולים להתפתח באזורים אילו.
        </div>
        <div class="hebrewText">
במקומות בהם אתם <strong>שונים</strong> יכולות, מצד אחד, להתפתח דינאמיקות "משלימות" המייצרות 2<1+1. אילו נקודות חוזקה זוגיות אותן מומלץ להמשיך ולפתח. לעומת זאת,
ייתכן וישנם מקומות של שוני המיצרים חילוקי דעות, חיכוחים וקונפליקטים. נסו להבין לעומק את מקומכם ואת מקומו של בן הזוג בהם.
פיתוח מודעות שכזו עשויה להביא להבנה טובה יותר של אי ההבנות והחיכוחים ובהמשך קבלה והכלה שלהם. הצעד הבא הוא לחשוב על דרכים
למנף את השוני ולנסות להפוך אותו לשלם הגדול מסך חלקיו, ע"י למשל, פיתוח הבנה שמה שיש לבן הזוג שלי יכול לעזור לי (להפך).
        </div>

        <div class="section">
            <table class="header-table">
                <tr>
                    <td class="name1 tableContent">{info_pdf1['name']} | {info_pdf1['type']}</td>
                    <td class="name2 tableContent" style="text-align: right;">{info_pdf2['name']} | {info_pdf2['type']}</td>
                </tr>
            </table>
            <div class="graph">
                <img src="data:image/png;base64,{first_graph_base64}" alt="first Graph">
            </div>
        </div> 
        <div class="section">
            <div class="graph">
                <img src="data:image/png;base64,{dominant_graph_base64}" alt="Dominant Graph">
            </div>
        </div>        
            <div class="page-break"></div>
        <div class="section">
            <h2>Extraversion vs. Introversion</h2>
            <table class="header-table">
                <tr>
                    <td class="name1 tableContent">{info_pdf1['name']} | {info_pdf1['type']}</td>
                    <td class="name2 tableContent" style="text-align: right;">{info_pdf2['name']} | {info_pdf2['type']}</td>
                </tr>
            </table>
            <div class="graph">
                <img src="data:image/png;base64,{ei_graph_base64}" alt="EI Graph">
            </div>
        </div>

        <div class="section">
            <h2>Sensing vs. Intuition</h2>
            <table class="header-table">
                <tr>
                    <td class="name1 tableContent">{info_pdf1['name']} | {info_pdf1['type']}</td>
                    <td class="name2 tableContent" style="text-align: right;">{info_pdf2['name']} | {info_pdf2['type']}</td>
                </tr>
            </table>
            <div class="graph">
                <img src="data:image/png;base64,{sn_graph_base64}" alt="SN Graph">
            </div>
        </div>

        <div class="section page-break">
            <h2>Thinking vs. Feeling</h2>
            <table class="header-table">
                <tr>
                    <td class="name1 tableContent">{info_pdf1['name']} | {info_pdf1['type']}</td>
                    <td class="name2 tableContent" style="text-align: right;">{info_pdf2['name']} | {info_pdf2['type']}</td>
                </tr>
            </table>
            <div class="graph">
                <img src="data:image/png;base64,{tf_graph_base64}" alt="TF Graph">
            </div>
        </div>

        <div class="section">
            <h2>Judging vs. Perceiving</h2>
            <table class="header-table">
                <tr>
                    <td class="name1 tableContent">{info_pdf1['name']} | {info_pdf1['type']}</td>
                    <td class="name2 tableContent" style="text-align: right;">{info_pdf2['name']} | {info_pdf2['type']}</td>
                </tr>
            </table>
            <div class="graph">
                <img src="data:image/png;base64,{jp_graph_base64}" alt="JP Graph">
            </div>
        </div>

        <footer class="footer">
            All rights reserved © {('<img src="' + logo_data_url + '" alt="TEMBTI Logo">') if logo_data_url else 'TEMBTI'}
        </footer>

    </body>
    </html>
    """

    try:
        # Create the PDF
        final_path = os.path.join(output_dir, f"{identifier}_dual_report.pdf")
        HTML(string=html_template, base_url=".").write_pdf(final_path)
        print(f"✅ PDF report created at: {final_path}")
        return identifier, final_path
    except Exception as e:
        print(f"ERROR creating PDF: {e}")
        # Save HTML as fallback
        html_path = os.path.join(output_dir, f"{identifier}_dual_report.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"✅ HTML report created as fallback at: {html_path}")
        return identifier, html_path


# Example usage
if __name__ == "__main__":
    pdf1 = r"F:\projects\MBTInfo\input\eran-turko-267149-e33d49cd-c629-f011-8b3d-000d3a381fe7.pdf"
    pdf2 = r"F:\projects\MBTInfo\input\Tomer-Shimon-Haiman-267149-7381d4d8-6235-f011-8b3d-000d3a381fe7.pdf"

    output_pdf = fr"F:\projects\MBTInfo\output"

    generate_dual_report(pdf1, pdf2, output_pdf)