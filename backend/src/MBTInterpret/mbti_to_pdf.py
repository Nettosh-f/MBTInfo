import os
import re
import pathlib
import webbrowser
import base64
from weasyprint import HTML
from datetime import datetime
from extract_imageAI import extract_all_graphs
from constsAI import INPUT_PATH, OUTPUT_PATH, MEDIA_PATH


def generate_mbti_report(input_file, output_html, output_pdf, logo_path, first_title, image_list):
    # File paths
    base_name = os.path.splitext(os.path.basename(input_file))[0][:6]
    media_dir = MEDIA_PATH / "tmp" / base_name
    header_image_url = pathlib.Path(logo_path).absolute().as_uri()
    # Read and split text
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    pages = [p.strip() for p in text.split('--- Page ') if p.strip() and not p.strip().isdigit()]
    total_pages = len(pages)

    # Footer static text
    footer_static_text = 'All rights reserved. TEMBTI©.'
    # Build HTML
    html_content = generate_html_content(header_image_url, pages, image_list, footer_static_text, first_title)

    # Save HTML
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Generate PDF
    HTML(output_html).write_pdf(output_pdf)

    # Open HTML and PDF
    # webbrowser.open(f'file://{os.path.abspath(output_html)}')
    # webbrowser.open(f'file://{os.path.abspath(output_pdf)}')

    print("✅ MBTI report generated with page titles and numbers.")


def apply_formatting(text):
    # Bold and underline formatting
    text = re.sub(r'__\*\*(.*?)\*\*__', r'<b><u>\1</u></b>', text)

    # Bold formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    # Underline formatting
    text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)

    # Replace newlines with <br> tags
    text = text.replace('\n', '<br>')

    return text


def encode_image_base64(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    with open(path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def generate_html_content(header_image_url, pages, image_path_list, footer_static_text, first_page_title):
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_head = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@200&display=swap" rel="stylesheet">
        <style>
            @font-face {{
                font-family: 'Assistant';
                src: url('fonts/Assistant-Regular.woff2') format('woff2'),
                     url('fonts/Assistant-Regular.woff') format('woff');
                font-weight: 400;
                font-style: normal;
            }}
            @font-face {{
                font-family: 'Assistant';
                src: url('fonts/Assistant-Bold.woff2') format('woff2'),
                     url('fonts/Assistant-Bold.woff') format('woff');
                font-weight: 700;
                font-style: normal;
            }}
            @page {{
                size: A4;
                margin: 120px 60px 80px 60px;
                @bottom-center {{
                    content: "{footer_static_text}";
                    font-size: 12px;
                }}
                @bottom-left {{
                    content: counter(page);
                    font-size: 18px;
                    font-weight: bold;
                }}
            }}
            @page :first {{
                @bottom-left {{
                content: none;}}
            }}
            html, body {{
                height: 100%;
                overflow-y: scroll; /* Always show vertical scrollbar */
            }}
            body {{
                font-family: 'Assistant', sans-serif;
                direction: rtl;
                font-size: 16px;
                line-height: 1.3;
                color: #000;
                counter-reset: page 1;
                margin: 0; /* Ensure no default margin */
            }}
            b {{
                font-weight: bold;
            }}
            header {{
                position: fixed;
                top: -100px;
                left: 0;
                right: 0;
                text-align: center;
            }}
            header img {{
                height: 70px;
            }}
            .page {{
                page-break-after: always;
            }}
            main {{
                white-space: pre-wrap;
            }}
            .first-page {{
                text-align: center;
            }}
            .first-page-title {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 50px;
                color: #333;
                text-decoration: underline;
                padding-bottom: 10px;
            }}
            main img {{
                max-width: 100%;
                display: block;
                margin: 0 auto;
            }}
            b {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
    """

    html_body = ""
    page_count = 1
    for index, page in enumerate(pages):
        page_content = re.sub(r'^\d+\s+---\s*', '', page).replace('\n', '<br>')
        page_content = apply_formatting(page_content)
        
        # Skip empty pages
        if not page_content.strip():
            continue

        if index == 0:
            html_body += f"""
            <div class="page first-page">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <div class="first-page-title">{first_page_title}</div><p>{page_content}</p>
                </main>
            </div>
            """
        elif index == 2:
            html_body += f"""
            <div class="page page-{page_count}">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <p>{page_content}</p>
                    <img src="data:image/png;base64,{image_path_list[0]}" alt="first Graph">

                </main>
            </div>
            """
        elif index == 4:
            html_body += f"""
            <div class="page page-{page_count}">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <img src="data:image/png;base64,{image_path_list[1]}" alt="first Graph">
                    <p>{page_content}</p>
                </main>
            </div>
            """
        elif index == 5:
            html_body += f"""
            <div class="page page-{page_count}">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <img src="data:image/png;base64,{image_path_list[4]}" alt="first Graph">
                    <p>{page_content}</p>
                </main>
            </div>
            """
        elif index == 6:
            html_body += f"""
            <div class="page page-{page_count}">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <img src="data:image/png;base64,{image_path_list[2]}" alt="first Graph">
                    <p>{page_content}</p>
                </main>
            </div>
            """
        elif index == 7:
            html_body += f"""
            <div class="page page-{page_count}">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <img src="data:image/png;base64,{image_path_list[3]}" alt="first Graph">
                    <p>{page_content}</p>
                </main>
            </div>
            """
        elif index == 12:
            html_body += f"""
            <div class="page page-{page_count}">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <img src="data:image/png;base64,{image_path_list[5]}" alt="first Graph">
                    <p>{page_content}</p>
                </main>
            </div>
            """
        elif index == 15:
            html_body += f"""
            <div class="page page-{page_count}">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <img src="data:image/png;base64,{image_path_list[6]}" alt="first Graph">
                    <p>{page_content}</p>
                </main>
            </div>
            """
        else:
            html_body += f"""
            <div class="page page-{page_count}">
                <header><img src="{header_image_url}" alt="Header Image"></header>
                <main>
                    <p>{page_content}</p>
                </main>
            </div>
            """
        page_count += 1

    html_footer = "</body></html>"

    return html_head + html_body + html_footer


if __name__ == "__main__":
    input_file = r'F:\projects\MBTInteligence\MBTItranslated\asaf-solomon-MBTI-fixed.txt'
    output_html = r'F:\projects\MBTInteligence\html files\mbti_report.html'
    output_pdf = r'F:\projects\MBTInteligence\MBTIpdfs\mbti_report.pdf'
    logo_path = r"F:\projects\Temp\full_logo.png"
    first_page_title = "דו'ח בתרגום לעברית עבור: "

    generate_mbti_report(input_file, output_html, output_pdf, logo_path, first_page_title)