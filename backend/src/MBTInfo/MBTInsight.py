import os
import sys
import time
import base64
import openai
import tempfile
from pdf2image import convert_from_path
from dotenv import load_dotenv
from consts import INSIGHT_SYSTEM_PROMPT, VALIDATION_SYSTEM_PROMPT, INSIGHT_COUPLE_SYSTEM_PROMPT

POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


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


def ask_gpt_with_images(content_blocks, prompt):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content_blocks}
    ]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content.strip()


def process_pdf_with_gpt(pdf_path):
    print("Converting PDF to images...")
    images = convert_pdf_to_images(pdf_path)
    content_blocks = [convert_image_to_base64_url(img) for img in images]
    if pdf_path.endswith("dual_report.pdf"):
        PROMPT = INSIGHT_COUPLE_SYSTEM_PROMPT

    else:
        PROMPT = INSIGHT_SYSTEM_PROMPT

    print("Validating MBTI relevance...")
    validation_response = ask_gpt_with_images(content_blocks, VALIDATION_SYSTEM_PROMPT)
    print("Validation:", validation_response)

    if validation_response.upper().startswith("YES"):
        print("Generating insight...")
        insight_response = ask_gpt_with_images(content_blocks, PROMPT)
        insight_response.replace("```html", "")
        insight_response.replace("```", "")
        # Create the insight.html file
        output_path = os.path.join(os.path.dirname(pdf_path), "insight.html")
        with open(output_path, "w", encoding="utf-8") as html_file:
            html_file.write(insight_response)

        return {"status": "ok", "insight": insight_response}
    else:
        return {"status": "not_mbti", "reason": validation_response}


if __name__ == "__main__":
    path_to_pdf = r"F:\projects\MBTInfo\output\MBTI_translate_nir-be.pdf"
    print(process_pdf_with_gpt(path_to_pdf))
    # import sys
    # if len(sys.argv) < 2:
    #     print("Usage: python mbti_assistant.py path/to/pdf")
    #     exit(1)
    #
    # result = get_mbti_insight_from_pdf(sys.argv[1])
    # print("\n--- Result ---")
    # print(result["insight"] if result["status"] == "ok" else f"Not MBTI-related: {result['reason']}")
