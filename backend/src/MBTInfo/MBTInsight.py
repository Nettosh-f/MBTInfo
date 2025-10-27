import base64
import os
import tempfile

import openai
import pandas as pd
import PyPDF2
from dotenv import load_dotenv
from pdf2image import convert_from_path
from weasyprint import HTML

from .consts import (
    ALL_MBTI_TYPES,
    COL_DOMINANT,
    COL_MBTI_TYPE,
    COL_NAME,
    COL_TYPE,
    COUNT_KEY,
    DATE_FORMAT_REPORT,
    DICHOTOMY_NAMES,
    DOMINANT_FUNCTIONS,
    DOMINANT_FUNCTIONS_LIST,
    FILE_SUFFIX_PNG,
    GROUP_INSIGHT_SYSTEM_PROMPT,
    IMAGE_FORMAT_PNG,
    INSIGHT_COUPLE_SYSTEM_PROMPT,
    INSIGHT_FILENAME_TRUNCATE_LENGTH,
    INSIGHT_PREFIX,
    INSIGHT_SYSTEM_PROMPT,
    MBTI_TYPES_KEY,
    MEDIA_PATH,
    MODEL_GPT4_TURBO,
    MODEL_GPT4O,
    MODEL_GPT4O_MINI,
    OPENAI_FILE_PURPOSE_USER_DATA,
    PDF_IMAGE_DPI,
    PERCENTAGE_KEY,
    POPPLER_PATH,
    REPORT_DATA_PDF,
    REPORT_DUAL_PDF,
    SHEET_NAME_DATA,
    SHEET_NAME_MBTI_RESULTS,
    UNKNOWN_VALUE,
    VALIDATION_SYSTEM_PROMPT,
)
from .html_templates import get_html_report_template

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()


def extract_data_from_excel_fixed(
    excel_path, sheet_name=SHEET_NAME_DATA, output_dir=None
):

    if output_dir is None:
        output_dir = str(MEDIA_PATH / "tmp")

    os.makedirs(output_dir, exist_ok=True)

    print("Reading MBTI Results sheet (the actual data)...")
    mbti_df = pd.read_excel(excel_path, sheet_name=SHEET_NAME_MBTI_RESULTS)

    print(f"MBTI Results shape: {mbti_df.shape}")
    print("Sample data:")
    print(mbti_df.head())

    # Create the summary that the Data sheet was supposed to show
    type_counts = mbti_df[COL_TYPE].value_counts()
    print("\nMBTI Type Counts:")
    print(type_counts)

    # Create a proper data structure for the PDF
    summary_data = {MBTI_TYPES_KEY: [], COUNT_KEY: [], PERCENTAGE_KEY: []}

    total_people = len(mbti_df)

    for mbti_type in ALL_MBTI_TYPES:
        count = type_counts.get(mbti_type, 0)
        percentage = (count / total_people * 100) if total_people > 0 else 0
        summary_data[MBTI_TYPES_KEY].append(mbti_type)
        summary_data[COUNT_KEY].append(count)
        summary_data[PERCENTAGE_KEY].append(f"{percentage:.1f}%")

    summary_df = pd.DataFrame(summary_data)

    # Function to determine dominant function
    def get_dominant_function(mbti_type):
        """Determine dominant cognitive function based on MBTI type"""
        if not mbti_type or len(mbti_type) != 4:
            return UNKNOWN_VALUE

        return DOMINANT_FUNCTIONS.get(mbti_type, UNKNOWN_VALUE)

    individual_results = []
    for _, row in mbti_df.iterrows():
        name = row.get(COL_NAME, UNKNOWN_VALUE)
        mbti_type = row.get(COL_TYPE, UNKNOWN_VALUE)
        dominant = get_dominant_function(mbti_type)
        individual_results.append(
            {COL_NAME: name, COL_MBTI_TYPE: mbti_type, COL_DOMINANT: dominant}
        )

    individual_df = pd.DataFrame(individual_results)

    dichotomy_data = calculate_dichotomy_analysis(mbti_df, total_people)
    dichotomy_df = pd.DataFrame(dichotomy_data)

    # Add dominant function analysis
    dominant_counts = individual_df[COL_DOMINANT].value_counts()
    dominant_analysis = []
    for func in DOMINANT_FUNCTIONS_LIST:
        count = dominant_counts.get(func, 0)
        percentage = (count / total_people * 100) if total_people > 0 else 0
        dominant_analysis.append(
            {
                "Dominant Function": func,
                "Count": count,
                "Percentage": f"{percentage:.1f}%",
            }
        )

    dominant_df = pd.DataFrame(dominant_analysis)

    # Create comprehensive HTML using template
    analysis_date = pd.Timestamp.now().strftime(DATE_FORMAT_REPORT)
    html_content = get_html_report_template(
        total_people=total_people,
        analysis_date=analysis_date,
        summary_table_html=summary_df.to_html(index=False, escape=False),
        dichotomy_table_html=dichotomy_df.to_html(index=False, escape=False),
        dominant_table_html=dominant_df.to_html(index=False, escape=False),
        individual_table_html=individual_df.to_html(index=False, escape=False),
    )

    output_path = os.path.join(output_dir, REPORT_DATA_PDF)
    HTML(string=html_content).write_pdf(output_path)
    print(f"Enhanced data report saved to: {output_path}")
    return output_path


def calculate_dichotomy_analysis(mbti_df, total_people):
    dichotomy_data = {}
    if total_people > 0:
        e_count = len([t for t in mbti_df[COL_TYPE] if t and t[0] == "E"])
        i_count = len([t for t in mbti_df[COL_TYPE] if t and t[0] == "I"])
        s_count = len([t for t in mbti_df[COL_TYPE] if t and t[1] == "S"])
        n_count = len([t for t in mbti_df[COL_TYPE] if t and t[1] == "N"])
        t_count = len([t for t in mbti_df[COL_TYPE] if t and t[2] == "T"])
        f_count = len([t for t in mbti_df[COL_TYPE] if t and t[2] == "F"])
        j_count = len([t for t in mbti_df[COL_TYPE] if t and t[3] == "J"])
        p_count = len([t for t in mbti_df[COL_TYPE] if t and t[3] == "P"])

        dichotomy_data = {
            "Dichotomy": DICHOTOMY_NAMES,
            "Count": [
                e_count,
                i_count,
                s_count,
                n_count,
                t_count,
                f_count,
                j_count,
                p_count,
            ],
            "Percentage": [
                f"{c / total_people * 100:.1f}%"
                for c in [
                    e_count,
                    i_count,
                    s_count,
                    n_count,
                    t_count,
                    f_count,
                    j_count,
                    p_count,
                ]
            ],
        }
    return dichotomy_data


def convert_pdf_to_images(pdf_path):
    return convert_from_path(pdf_path, dpi=PDF_IMAGE_DPI, poppler_path=POPPLER_PATH)


def convert_image_to_base64_url(image):
    with tempfile.NamedTemporaryFile(suffix=FILE_SUFFIX_PNG, delete=False) as tmp_file:
        image_path = tmp_file.name
        image.save(image_path, format=IMAGE_FORMAT_PNG)

    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded}"},
        }
    finally:
        os.remove(image_path)


def group_user_prompt(
    group_name,
    industry,
    team_type,
    analysis_goal,
    roles=None,
    existing_challenges=None,
):
    GROUP_USER_PROMPT = f"""
        our group name is: {group_name}. we work in the {industry} industry. we are a team of {team_type}.
         we are looking for analysis in {analysis_goal}.
"""
    if roles is not None:
        GROUP_USER_PROMPT += f" our team has {roles}."
    if existing_challenges is not None:
        GROUP_USER_PROMPT += f" we have existing challenges: {existing_challenges}."
    return GROUP_USER_PROMPT.strip()


def ask_gpt_with_images(content_blocks, prompt, model=MODEL_GPT4O):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content_blocks},
    ]
    response = openai.chat.completions.create(model=model, messages=messages)
    print("AI Prompt Call:")
    print("Model:", model)
    print("Messages:", messages)
    return response.choices[0].message.content.strip()


def process_pdf_with_gpt(pdf_path, content_blocks):
    print("Converting PDF to images...")
    validation_text = ""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_page = 0
            page = pdf_reader.pages[num_page]
            validation_text = page.extract_text()
    except Exception as e:
        print("Failed to extract text from PDF page:", e)
    image_blocks = []
    try:
        images = convert_pdf_to_images(pdf_path)
        for img in images:
            image_block = convert_image_to_base64_url(img)
            image_blocks.append(image_block)
    except Exception as e:
        print("PDF to image conversion failed:", e)
    all_blocks = []
    if image_blocks:
        all_blocks.extend(image_blocks)
    if content_blocks:
        all_blocks.extend(content_blocks)

    if pdf_path.endswith(REPORT_DUAL_PDF):
        PROMPT = INSIGHT_COUPLE_SYSTEM_PROMPT
    elif pdf_path.endswith(REPORT_DATA_PDF):
        PROMPT = GROUP_INSIGHT_SYSTEM_PROMPT
    else:
        PROMPT = INSIGHT_SYSTEM_PROMPT

    print("prompt is:", PROMPT, "\n", "")
    print("Validating MBTI relevance...")
    validation_response = ask_gpt_with_images(
        validation_text, VALIDATION_SYSTEM_PROMPT, MODEL_GPT4O_MINI
    )

    print("Validation:", validation_response)

    if validation_response.upper().startswith("YES"):
        print("Generating insight...")
        insight_response = ask_gpt_with_images(all_blocks, PROMPT)
        print(insight_response)
        insight_response = insight_response.replace("```html", "")
        insight_response = insight_response.replace("```", "")
        print(insight_response)
        # Create the insight.html file
        pdf_stub = os.path.splitext(os.path.basename(pdf_path))[0][
            :INSIGHT_FILENAME_TRUNCATE_LENGTH
        ]
        insight_html_filename = f"{INSIGHT_PREFIX}{pdf_stub}.html"
        output_path = os.path.join(os.path.dirname(pdf_path), insight_html_filename)
        with open(output_path, "w", encoding="utf-8") as html_file:
            html_file.write(insight_response)

        return {
            "status": "ok",
            "insight": insight_response,
            "insight_path": output_path,
        }
    else:
        return {"status": "not_mbti", "reason": validation_response}


def upload_file_and_ask_question(
    file_path, question, system_prompt, model=MODEL_GPT4_TURBO
):
    # Upload the file to OpenAI
    with open(file_path, "rb") as file:
        uploaded_file = client.files.create(
            file=file, purpose=OPENAI_FILE_PURPOSE_USER_DATA
        )

    # Create a chat completion with the uploaded file
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {
                            "file_id": uploaded_file.id,
                        },
                    },
                    {
                        "type": "text",
                        "text": question,
                    },
                ],
            },
        ],
    )

    return completion.choices[0].message.content.strip()


if __name__ == "__main__":
    # path_to_pdf = r"F:\projects\MBTInfo\output\MBTI_translate_nir-be.pdf"
    extract_data_from_excel_fixed(
        r"F:\projects\MBTInfo\output\group_report_all_pdfs(4).xlsx"
    )
