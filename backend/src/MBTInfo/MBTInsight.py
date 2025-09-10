import os
import sys
import time
import base64
import openai
import tempfile
import pandas as pd
from weasyprint import HTML
from pdf2image import convert_from_path
from dotenv import load_dotenv
from pathlib import Path
import PyPDF2
from consts import INSIGHT_SYSTEM_PROMPT, VALIDATION_SYSTEM_PROMPT, INSIGHT_COUPLE_SYSTEM_PROMPT, POPPLER_PATH, \
    MEDIA_PATH
from consts import GROUP_INSIGHT_SYSTEM_PROMPT

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()


def extract_data_from_excel_fixed(excel_path, sheet_name="Data", output_dir=r"F:\projects\MBTInfo\backend\media\tmp"):
    """FIXED: The issue was that the Data sheet has formulas referencing Table1 which doesn't exist.
    Solution: Read the MBTI Results sheet instead, or force Excel to calculate formulas properly."""
    import os
    import pandas as pd
    from weasyprint import HTML
    import openpyxl

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # SOLUTION 1: Read the actual data from MBTI Results sheet and create our own summary
    print("Reading MBTI Results sheet (the actual data)...")
    mbti_df = pd.read_excel(excel_path, sheet_name="MBTI Results")

    print(f"MBTI Results shape: {mbti_df.shape}")
    print("Sample data:")
    print(mbti_df.head())

    # Create the summary that the Data sheet was supposed to show
    type_counts = mbti_df['Type'].value_counts()
    print(f"\nMBTI Type Counts:")
    print(type_counts)

    # Create a proper data structure for the PDF
    summary_data = {
        'MBTI Type': [],
        'Count': [],
        'Percentage': []
    }

    total_people = len(mbti_df)
    all_types = ['ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP',
                 'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ']

    for mbti_type in all_types:
        count = type_counts.get(mbti_type, 0)
        percentage = (count / total_people * 100) if total_people > 0 else 0
        summary_data['MBTI Type'].append(mbti_type)
        summary_data['Count'].append(count)
        summary_data['Percentage'].append(f"{percentage:.1f}%")

    summary_df = pd.DataFrame(summary_data)

    # Function to determine dominant function
    def get_dominant_function(mbti_type):
        """Determine dominant cognitive function based on MBTI type"""
        if not mbti_type or len(mbti_type) != 4:
            return "Unknown"

        dominant_functions = {
            'ISTJ': 'Si', 'ISFJ': 'Si', 'INFJ': 'Ni', 'INTJ': 'Ni',
            'ISTP': 'Ti', 'ISFP': 'Fi', 'INFP': 'Fi', 'INTP': 'Ti',
            'ESTP': 'Se', 'ESFP': 'Se', 'ENFP': 'Ne', 'ENTP': 'Ne',
            'ESTJ': 'Te', 'ESFJ': 'Fe', 'ENFJ': 'Fe', 'ENTJ': 'Te'
        }
        return dominant_functions.get(mbti_type, "Unknown")

    # Create individual results table with dominant function
    individual_results = []
    for _, row in mbti_df.iterrows():
        name = row.get('Name', 'Unknown')
        mbti_type = row.get('Type', 'Unknown')
        dominant = get_dominant_function(mbti_type)
        individual_results.append({
            'Name': name,
            'MBTI Type': mbti_type,
            'Dominant': dominant
        })

    individual_df = pd.DataFrame(individual_results)

    # Also add dichotomy analysis
    dichotomy_data = {}
    if total_people > 0:
        # E/I analysis
        e_count = len([t for t in mbti_df['Type'] if t and t[0] == 'E'])
        i_count = len([t for t in mbti_df['Type'] if t and t[0] == 'I'])

        # S/N analysis
        s_count = len([t for t in mbti_df['Type'] if t and t[1] == 'S'])
        n_count = len([t for t in mbti_df['Type'] if t and t[1] == 'N'])

        # T/F analysis
        t_count = len([t for t in mbti_df['Type'] if t and t[2] == 'T'])
        f_count = len([t for t in mbti_df['Type'] if t and t[2] == 'F'])

        # J/P analysis
        j_count = len([t for t in mbti_df['Type'] if t and t[3] == 'J'])
        p_count = len([t for t in mbti_df['Type'] if t and t[3] == 'P'])

        dichotomy_data = {
            'Dichotomy': ['Extroversion', 'Introversion', 'Sensing', 'Intuition',
                          'Thinking', 'Feeling', 'Judging', 'Perceiving'],
            'Count': [e_count, i_count, s_count, n_count, t_count, f_count, j_count, p_count],
            'Percentage': [f"{c / total_people * 100:.1f}%" for c in
                           [e_count, i_count, s_count, n_count, t_count, f_count, j_count, p_count]]
        }

    dichotomy_df = pd.DataFrame(dichotomy_data)

    # Add dominant function analysis
    dominant_counts = individual_df['Dominant'].value_counts()
    dominant_analysis = []
    for func in ['Te', 'Ti', 'Fe', 'Fi', 'Se', 'Si', 'Ne', 'Ni']:
        count = dominant_counts.get(func, 0)
        percentage = (count / total_people * 100) if total_people > 0 else 0
        dominant_analysis.append({
            'Dominant Function': func,
            'Count': count,
            'Percentage': f"{percentage:.1f}%"
        })

    dominant_df = pd.DataFrame(dominant_analysis)

    # Create comprehensive HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .section {{ margin: 30px 0; }}
            h2 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
            .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>MBTI Analysis Report</h1>

        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Participants:</strong> {total_people}</p>
            <p><strong>Analysis Date:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>

        <div class="section">
            <h2>MBTI Type Distribution</h2>
            {summary_df.to_html(index=False, escape=False)}
        </div>

        <div class="section">
            <h2>Dichotomy Analysis</h2>
            {dichotomy_df.to_html(index=False, escape=False)}
        </div>

        <div class="section">
            <h2>Dominant Function Analysis</h2>
            {dominant_df.to_html(index=False, escape=False)}
        </div>

        <div class="section">
            <h2>Individual Results</h2>
            {individual_df.to_html(index=False, escape=False)}
        </div>
    </body>
    </html>
    """

    output_path = os.path.join(output_dir, "data.pdf")
    HTML(string=html_content).write_pdf(output_path)
    print(f"Enhanced data report saved to: {output_path}")
    return output_path


def convert_pdf_to_images(pdf_path):
    return convert_from_path(pdf_path, dpi=200, poppler_path=POPPLER_PATH)


def convert_image_to_base64_url(image):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        image_path = tmp_file.name
        image.save(image_path, format="PNG")

    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{encoded}"
            }
        }
    finally:
        os.remove(image_path)


def group_user_prompt(group_name, industry, team_type, number_of_members, duration_together, analysis_goal, roles=None,
                      existing_challenges=None, communication_style=None, upcoming_context=None):
    GROUP_USER_PROMPT = f"""
        our group name is: {group_name}. we work in the {industry} industry. we are a team of {team_type}.
         we are looking for analysis in {analysis_goal}.
"""
    if roles is not None:
        GROUP_USER_PROMPT += f" our team has {roles}."
    if existing_challenges is not None:
        GROUP_USER_PROMPT += f" we have existing challenges: {existing_challenges}."
    return GROUP_USER_PROMPT.strip()


def ask_gpt_with_images(content_blocks, prompt, model="gpt-4o"):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content_blocks}
    ]
    response = openai.chat.completions.create(
        model=model,
        messages=messages
    )
    print("AI Prompt Call:")
    print("Model:", model)
    print("Messages:", messages)
    return response.choices[0].message.content.strip()


def process_pdf_with_gpt(pdf_path, content_blocks):
    print("Converting PDF to images...")
    validation_text = ''
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_page = 0
            page = pdf_reader.pages[num_page]
            validation_text = page.extract_text()
    except Exception as e:
        print("Failed to extract text from PDF page:", e)
    image_blocks = []
    try:
        images = convert_pdf_to_images(pdf_path)
        for i, img in enumerate(images):
            image_block = convert_image_to_base64_url(img)
            image_blocks.append(image_block)
    except Exception as e:
        print("PDF to image conversion failed:", e)
    all_blocks = []
    if image_blocks:
        all_blocks.extend(image_blocks)
    if content_blocks:
        all_blocks.extend(content_blocks)

    if pdf_path.endswith("dual_report.pdf"):
        PROMPT = INSIGHT_COUPLE_SYSTEM_PROMPT
    elif pdf_path.endswith("data.pdf"):
        PROMPT = GROUP_INSIGHT_SYSTEM_PROMPT
    else:
        PROMPT = INSIGHT_SYSTEM_PROMPT

    print("prompt is:", PROMPT, "\n", "")
    print("Validating MBTI relevance...")
    validation_response = ask_gpt_with_images(validation_text, VALIDATION_SYSTEM_PROMPT, "gpt-4o-mini")

    print("Validation:", validation_response)

    if validation_response.upper().startswith("YES"):
        print("Generating insight...")
        insight_response = ask_gpt_with_images(all_blocks, PROMPT)
        print(insight_response)
        insight_response = insight_response.replace("```html", "")
        insight_response = insight_response.replace("```", "")
        print(insight_response)
        # Create the insight.html file
        pdf_stub = os.path.splitext(os.path.basename(pdf_path))[0][:6]
        insight_html_filename = f"insight_{pdf_stub}.html"
        output_path = os.path.join(os.path.dirname(pdf_path), insight_html_filename)
        with open(output_path, "w", encoding="utf-8") as html_file:
            html_file.write(insight_response)

        return {"status": "ok", "insight": insight_response, "insight_path": output_path}
    else:
        return {"status": "not_mbti", "reason": validation_response}


def upload_file_and_ask_question(file_path, question, system_prompt, model="gpt-4.1-2025-04-14"):
    # Upload the file to OpenAI
    with open(file_path, "rb") as file:
        uploaded_file = client.files.create(
            file=file,
            purpose="user_data"
        )

    # Create a chat completion with the uploaded file
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {
                            "file_id": uploaded_file.id,
                        }
                    },
                    {
                        "type": "text",
                        "text": question,
                    },
                ]
            }
        ]
    )

    return completion.choices[0].message.content.strip()


if __name__ == "__main__":
    # path_to_pdf = r"F:\projects\MBTInfo\output\MBTI_translate_nir-be.pdf"
    extract_data_from_excel_fixed(r"F:\projects\MBTInfo\output\group_report_all_pdfs(4).xlsx")
    # process_pdf_with_gpt(r"F:\projects\MBTInfo\output\data.pdf")
