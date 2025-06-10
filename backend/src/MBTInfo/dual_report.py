import os
import base64
from weasyprint import HTML
from image_manipulation import create_dual_facet_graphs


def encode_image_base64(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def generate_dual_report_with_graphs_from_pdfs(pdf1_path, pdf2_path, output_pdf_path):
    # Generate overlaid facet graphs
    media_path = rf"F:\projects\MBTInfo\backend\media\tmp"
    graph_paths = create_dual_facet_graphs(pdf1_path, pdf2_path, media_path)

    # Construct the output directory for the PDF
    first_name_part = os.path.basename(pdf1_path)[:6]
    second_name_part = os.path.basename(pdf2_path)[:6]
    identifier = f"{first_name_part}_{second_name_part}"
    output_dir = os.path.join(output_pdf_path, identifier)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract short names
    name1 = os.path.splitext(os.path.basename(pdf1_path))[0].split('-')[0]
    name2 = os.path.splitext(os.path.basename(pdf2_path))[0].split('-')[0]

    # Encode graphs to base64
    ei_graph_base64 = encode_image_base64(graph_paths["EIGraph"])
    sn_graph_base64 = encode_image_base64(graph_paths["SNgraph"])
    tf_graph_base64 = encode_image_base64(graph_paths["TFgraph"])
    jp_graph_base64 = encode_image_base64(graph_paths["JPgraph"])

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
                margin: 40px;
                color: #333;
            }}
            h1, h2 {{
                text-align: center;
                color: #2c3e50;
            }}
            .section {{
                margin-top: 40px;
            }}
            .graph {{
                text-align: center;
                margin: 20px 0;
            }}
            .names {{
                font-size: 18px;
                text-align: center;
                margin-bottom: 10px;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ccc;
                padding: 10px;
                background: #f9f9f9;
            }}
            footer {{
                margin-top: 60px;
                text-align: center;
                font-size: 12px;
                color: #888;
            }}
        </style>
    </head>
    <body>

        <h1>MBTI Dual Comparison Report</h1>
        <div class="names"><strong>{name1}</strong> &amp; <strong>{name2}</strong></div>

        <div class="section">
            <h2>Extraversion vs. Introversion</h2>
            <div class="graph">
                <img src="data:image/png;base64,{ei_graph_base64}" alt="EI Graph">
            </div>
        </div>

        <div class="section">
            <h2>Sensing vs. Intuition</h2>
            <div class="graph">
                <img src="data:image/png;base64,{sn_graph_base64}" alt="SN Graph">
            </div>
        </div>

        <div class="section">
            <h2>Thinking vs. Feeling</h2>
            <div class="graph">
                <img src="data:image/png;base64,{tf_graph_base64}" alt="TF Graph">
            </div>
        </div>

        <div class="section">
            <h2>Judging vs. Perceiving</h2>
            <div class="graph">
                <img src="data:image/png;base64,{jp_graph_base64}" alt="JP Graph">
            </div>
        </div>

        <footer>
            Generated on: PLACEHOLDER_DATE
        </footer>

    </body>
    </html>
    """

    # Create the PDF
    HTML(string=html_template, base_url=".").write_pdf(os.path.join(output_dir, "dual_report.pdf"))
    print(f"✅ PDF report created at: {os.path.join(output_dir, 'dual_report.pdf')}")


# Example usage
if __name__ == "__main__":
    pdf1 = r"F:\projects\MBTInfo\input\ADAM-POMERANTZ-267149-e4b6edb5-1a5f-ef11-bdfd-6045bd04b01a.pdf"
    pdf2 = r"F:\projects\MBTInfo\input\Adi-Chen-267149-30ffb71f-a3fd-ef11-90cb-000d3a58c2b2.pdf"
    # identifier = f"{first_name_part}_{second_name_part}"
    output_pdf = fr"F:\projects\MBTInfo\output"

    generate_dual_report_with_graphs_from_pdfs(pdf1, pdf2, output_pdf)