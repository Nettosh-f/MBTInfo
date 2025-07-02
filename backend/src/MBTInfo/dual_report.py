import os
import base64
from weasyprint import HTML
from image_manipulation import create_all_graphs

from data_extractor import extract_and_save_text

from utils import get_all_info


def encode_image_base64(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def generate_dual_report(pdf1_path, pdf2_path, output_pdf_path):
    text_folder = fr"F:\projects\MBTInfo\output\textfiles"
    os.makedirs(text_folder, exist_ok=True)

    # get all info from text files
    name1 = os.path.basename(pdf1_path).replace(".pdf", "")
    name2 = os.path.basename(pdf2_path).replace(".pdf", "")
    text1 = fr"F:\projects\MBTInfo\output\textfiles\{name1}_text.txt"
    text2 = fr"F:\projects\MBTInfo\output\textfiles\{name2}_text.txt"
    extract_and_save_text(pdf1_path, text_folder)
    extract_and_save_text(pdf2_path, text_folder)
    info_pdf1 = get_all_info(text1)
    info_pdf2 = get_all_info(text2)
    first_name_part = os.path.basename(pdf1_path)[:6]
    second_name_part = os.path.basename(pdf2_path)[:6]
    identifier = f"{first_name_part}_{second_name_part}"
    media_path = os.path.join(r"F:\projects\MBTInfo\backend\media\tmp", identifier)
    create_all_graphs(pdf1_path, pdf2_path, media_path)
    logo_path = r'F:\projects\MBTInfo\backend\media\full_logo.png'
    # Construct the output directory for the PDF

    output_dir = output_pdf_path
    final_images_path = rf"F:\projects\MBTInfo\backend\media\tmp\{identifier}\final"
    all_images_path = [os.path.join(final_images_path, f"{identifier}_first_graph_final.png"),
                       os.path.join(final_images_path, f"{identifier}_EIGraph_final.png"),
                       os.path.join(final_images_path, f"{identifier}_TFgraph_final.png"),
                       os.path.join(final_images_path, f"{identifier}_JPgraph_final.png"),
                       os.path.join(final_images_path, f"{identifier}_SNgraph_final.png"),
                       os.path.join(final_images_path, f"{identifier}_dominant_final_final.png")]
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

    # Encode graphs to base64
    first_graph_base64 = encode_image_base64(all_images_path[0])
    ei_graph_base64 = encode_image_base64(all_images_path[1])
    sn_graph_base64 = encode_image_base64(all_images_path[4])
    tf_graph_base64 = encode_image_base64(all_images_path[2])
    jp_graph_base64 = encode_image_base64(all_images_path[3])
    dominant_graph_base64 = encode_image_base64(all_images_path[5])
    full_logo_base64 = encode_image_base64(logo_path)
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
        <div class="logo">
            <img src="data:image/png;base64,{full_logo_base64}" alt="Company Logo">
        </div>
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
                <img src="data:image/png;base64,{dominant_graph_base64}" alt="EI Graph">
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
            All rights reserved © <img src="{logo_data_url}" alt="TEMBTI Logo">
        </footer>

    </body>
    </html>
    """

    # Create the PDF
    final_path = os.path.join(output_dir, f"{identifier}_dual_report.pdf")
    HTML(string=html_template, base_url=".").write_pdf(final_path)
    print(f"✅ PDF report created at: {os.path.join(output_dir, f"{identifier}_dual_report.pdf")}")
    return identifier, final_path


# Example usage
if __name__ == "__main__":
    pdf1 = r"F:\projects\MBTInfo\input\ADAM-POMERANTZ-267149-e4b6edb5-1a5f-ef11-bdfd-6045bd04b01a.pdf"
    pdf2 = r"F:\projects\MBTInfo\input\Adi-Chen-267149-30ffb71f-a3fd-ef11-90cb-000d3a58c2b2.pdf"

    output_pdf = fr"F:\projects\MBTInfo\output"

    generate_dual_report(pdf1, pdf2, output_pdf)