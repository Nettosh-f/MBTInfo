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
from consts import INSIGHT_SYSTEM_PROMPT, VALIDATION_SYSTEM_PROMPT, INSIGHT_COUPLE_SYSTEM_PROMPT, POPPLER_PATH, \
    MEDIA_PATH
from consts import GROUP_INSIGHT_SYSTEM_PROMPT

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_data_from_excel(excel_path, sheet_name="Data", output_dir=r"F:\projects\MBTInfo\backend\media\tmp"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    df = df.fillna("")
    html_content = df.to_html(index=False)
    output_path = os.path.join(output_dir, "data.pdf")
    HTML(string=html_content).write_pdf(output_path)
    print("Data extracted and saved to data.pdf")
    return output_path


def group_user_prompt(group_name, industry, team_type, number_of_members, duration_together, analysis_goal, roles=None,
                      existing_challenges=None, communication_style=None, upcoming_context=None):
    GROUP_USER_PROMPT = f"""
        our group name is: {group_name}. we work in the {industry} industry. we are a team of {team_type} with
        {number_of_members} members, we have been working together for {duration_together}. we are looking for analysis
        in {analysis_goal}.
"""
    if roles is not None:
        GROUP_USER_PROMPT += f" our team has {roles}."
    if existing_challenges is not None:
        GROUP_USER_PROMPT += f" we have existing challenges: {existing_challenges}."
    if communication_style is not None:
        GROUP_USER_PROMPT += f" our communication style is {communication_style}."
    if upcoming_context is not None:
        GROUP_USER_PROMPT += f" we are considering the upcoming context: {upcoming_context}."
    return GROUP_USER_PROMPT.strip()


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


def process_pdf_with_gpt(pdf_path, content_blocks=None):
    print("Converting PDF to images...")
    images = convert_pdf_to_images(pdf_path)
    if content_blocks is None:
        content_blocks = [convert_image_to_base64_url(img) for img in images]
    if pdf_path.endswith("dual_report.pdf"):
        PROMPT = INSIGHT_COUPLE_SYSTEM_PROMPT
    elif pdf_path.endswith("data.pdf"):
        PROMPT = GROUP_INSIGHT_SYSTEM_PROMPT
    else:
        PROMPT = INSIGHT_SYSTEM_PROMPT
    print("prompt is:", PROMPT, "\n", "")
    print("Validating MBTI relevance...")
    print("Content blocks:", content_blocks)
    validation_response = ask_gpt_with_images(content_blocks, VALIDATION_SYSTEM_PROMPT, "gpt-4o-mini")
    print("Validation:", validation_response)

    if validation_response.upper().startswith("YES"):
        print("Generating insight...")
        insight_response = ask_gpt_with_images(content_blocks, PROMPT)
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


if __name__ == "__main__":
    # path_to_pdf = r"F:\projects\MBTInfo\output\MBTI_translate_nir-be.pdf"
    print(process_pdf_with_gpt(path_to_pdf))
    extract_data_from_excel(r"F:\projects\MBTInfo\output\group_report_all_pdfs (11).xlsx")
