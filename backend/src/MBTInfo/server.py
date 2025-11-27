import asyncio
import atexit
import glob
import logging
import os
import re
import shutil
import signal
import sys
import tempfile
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

import pandas as pd
import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from weasyprint import HTML as WeasyHTML

from MBTInterpret.main import create_translated_pdf

from .consts import (
    MEDIA_DIRECTORIES_TO_CHECK,
    MEDIA_DIRECTORY_KEEP_ITEMS,
    PROJECT_BASE_DIR,
)
from .dual_report import generate_dual_report
from .extract_image import extract_multiple_graphs_from_pdf
from .group_report import process_group_report_fixed
from .MBTInsight import (
    extract_data_from_excel_fixed,
    group_user_prompt,
    process_pdf_with_gpt,
)
from .personal_report import generate_personal_report
from .utils import sanitize_filename, sanitize_path_component

TEMP_DIR = "/tmp/tmp_pdf"
os.makedirs(TEMP_DIR, exist_ok=True)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", str(PROJECT_BASE_DIR / "output"))
INPUT_DIR = os.getenv("INPUT_DIR", str(PROJECT_BASE_DIR / "input"))
MEDIA_DIR = os.getenv("MEDIA_DIR", str(PROJECT_BASE_DIR / "backend" / "media"))


class ProcessingResponse(BaseModel):
    task_id: str
    status: str
    message: str


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("mbti_server")
logger.info("MBTI Processing Service initializing...")


app = FastAPI(
    title="MBTI Processing Service",
    description="Service for MBTI report processing with 4 main activities",
    version="1.0.0",
    root_path="/api",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# CORS configuration - allow specific origins in production
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
if cors_origins == ["*"]:
    # In production, you should set CORS_ORIGINS to specific domains
    logger.warning("CORS is set to allow all origins. For production, set CORS_ORIGINS environment variable.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def cleanup_old_temp_files():
    """Periodically clean up temporary files older than 1 hour"""
    while True:
        try:
            if not os.path.exists(TEMP_DIR):
                await asyncio.sleep(1800)
                continue

            current_time = datetime.now().timestamp()
            deleted_count = 0

            for item in os.listdir(TEMP_DIR):
                item_path = os.path.join(TEMP_DIR, item)
                if os.path.isdir(item_path):
                    try:
                        mod_time = os.path.getmtime(item_path)
                        age_hours = (current_time - mod_time) / 3600

                        if age_hours > 1:
                            shutil.rmtree(item_path, ignore_errors=True)
                            deleted_count += 1
                            logger.info(
                                f"Deleted old temp directory: {item} (age: {age_hours:.1f} hours)"
                            )
                    except Exception as e:
                        logger.warning(f"Error checking/deleting {item}: {e}")

            if deleted_count > 0:
                logger.info(f"Cleanup completed: {deleted_count} directories removed")
        except Exception as e:
            logger.error(f"Error during temp cleanup: {e}")

        await asyncio.sleep(1800)


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    app.state.start_time = datetime.now()

    logger.info(f"FastAPI MBTI Service started at {app.state.start_time.isoformat()}")
    logger.info(f"Temp directory: {TEMP_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")

    asyncio.create_task(cleanup_old_temp_files())


# Pydantic models
class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    file_type: Optional[str] = None  # "html", "pdf", "xlsx", etc.
    created_at: datetime
    excel_path: Optional[str] = None  # Add this as a proper field
    insight_pdf_url: Optional[str] = None
    file_path: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    message: str
    file_type: Optional[str] = None
    created_at: datetime
    excel_path: Optional[str] = None
    insight_pdf_url: Optional[str] = None
    file_path: Optional[str] = None


# In-memory task storage
task_storage: dict[str, TaskStatus] = {}


def cleanup_output_directory():
    """Clean up the output directory by removing the 'textfiles' folder"""
    print("\n🧹 Starting output directory cleanup...")

    textfiles_dir = os.path.join(OUTPUT_DIR, "textfiles")

    if os.path.exists(textfiles_dir):
        try:
            shutil.rmtree(textfiles_dir)
            print("🗑️  Removed folder: textfiles")
        except Exception as e:
            print(f"⚠️  Could not remove 'textfiles' folder: {str(e)}")
    else:
        print("✨ 'textfiles' folder does not exist, no cleanup needed")


def cleanup_media_directory():
    """Clean up media directory, keeping only Personal_Report_Media folder and full_logo.png"""
    print("\n🧹 Starting media directory cleanup...")

    # Find the active media directory
    active_media_dir = None
    for media_path in MEDIA_DIRECTORIES_TO_CHECK:
        if os.path.exists(media_path):
            active_media_dir = media_path
            break

    if not active_media_dir:
        print("📁 No media directory found in, skipping cleanup")
        return

    print(f"📁 Cleaning media directory: {active_media_dir}")

    try:
        items_in_media = os.listdir(active_media_dir)
        removed_count = 0

        for item in items_in_media:
            if item not in MEDIA_DIRECTORY_KEEP_ITEMS:
                item_path = os.path.join(active_media_dir, item)

                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        print(f"🗑️  Removed folder: {item}")
                        removed_count += 1
                    elif os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"🗑️  Removed file: {item}")
                        removed_count += 1
                except Exception as e:
                    print(f"⚠️  Could not remove {item}: {str(e)}")
            else:
                print(f"✅ Kept: {item}")

        if removed_count == 0:
            print("✨ Media directory was already clean")
        else:
            print(f"✅ Cleanup completed: {removed_count} items removed")

    except Exception as e:
        print(f"❌ Error during media cleanup: {str(e)}")


def cleanup_on_exit():
    """Cleanup function called when service exits"""
    print("\n🛑 MBTI Processing Service shutting down...")
    cleanup_media_directory()
    cleanup_output_directory()
    delete_uuid_folders_from(INPUT_DIR)
    delete_uuid_folders_from(TEMP_DIR)
    # Cleanup temp directory
    try:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        print("🧹 Temporary files cleaned up")
    except Exception:
        pass

    print("👋 Service stopped cleanly")


# Register cleanup function to run on exit
atexit.register(cleanup_on_exit)


# Handle termination signals
def signal_handler(signum, frame):
    """Handle termination signals"""
    print(f"⚠️ Received signal {signum}, shutting down gracefully...")
    cleanup_on_exit()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

if os.name != "nt":  # Unix/Linux specific signals
    signal.signal(signal.SIGHUP, signal_handler)  # Hangup signal
    signal.signal(signal.SIGQUIT, signal_handler)  # Quit signal


def create_task_id() -> str:
    return str(uuid.uuid4())


def update_task_status(
    task_id: str, status: str, message: str, file_path: Optional[str] = None
):
    if task_id in task_storage:
        task_storage[task_id].status = status
        task_storage[task_id].message = message
        if file_path:
            task_storage[task_id].file_path = file_path


@app.get("/output/{filename}")
async def download_file(task_id: str, filename: str):
    """Download the processed file or view HTML/PDF content"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    # Check if file is in TEMP_DIR first (for HTML reports)
    temp_file_path = os.path.join(TEMP_DIR, task_id, filename)
    if os.path.exists(temp_file_path):
        file_path = temp_file_path
    else:
        # Otherwise check in OUTPUT_DIR (for other files)
        file_path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(file_path):
            print(file_path)

            raise HTTPException(status_code=404, detail="File not found")

    # For HTML files, return the content as HTML response
    if filename.lower().endswith(".html"):
        with open(file_path, encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)

    # Determine media type based on file extension
    media_type = "application/octet-stream"
    if filename.lower().endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.lower().endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.lower().endswith(".txt"):
        media_type = "text/plain"

    # Set Content-Disposition based on file_type in task_storage
    # For PDF files that should be viewed in browser, use 'inline' instead of 'attachment'
    content_disposition = "attachment"
    if (
        hasattr(task, "file_type")
        and task.file_type == "pdf_view"
        and filename.lower().endswith(".pdf")
    ):
        content_disposition = "inline"

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type,
        headers={
            "Content-Disposition": f'{content_disposition}, filename"="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@app.get("/insight/{task_id}/html")
async def download_insight_html(task_id: str):
    """Download HTML insight file from a completed insight task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    if not hasattr(task, "file_path") or not task.file_path:
        raise HTTPException(
            status_code=404, detail="Insight file not found for this task"
        )

    file_path = task.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    filename = os.path.basename(file_path)

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/html",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@app.get("/insight/{task_id}/pdf")
async def download_insight_pdf(task_id: str):
    """Download PDF insight file from a completed insight task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    if not hasattr(task, "insight_pdf_url") or not task.insight_pdf_url:
        raise HTTPException(
            status_code=404, detail="PDF insight not available for this task"
        )

    pdf_url = task.insight_pdf_url
    if pdf_url.startswith("/output/"):
        pdf_url = pdf_url[8:]
    file_path = os.path.join(OUTPUT_DIR, pdf_url)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    # Validate file is actually a PDF
    if not file_path.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File is not a PDF")

    filename = os.path.basename(file_path)

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@app.get("/insight/{task_id}/excel")
async def download_insight_excel(task_id: str):
    """Download Excel insight file from a completed insight task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    # Check for insight Excel file - insights may not always have Excel files
    # First check if there's a specific insight_excel_url attribute
    if hasattr(task, "insight_excel_url") and task.insight_excel_url:
        excel_url = task.insight_excel_url
        if excel_url.startswith("/output/"):
            excel_url = excel_url[8:]
        file_path = os.path.join(OUTPUT_DIR, excel_url)
    elif hasattr(task, "excel_path") and task.excel_path:
        # Fallback to excel_path if available (for group insights that use Excel)
        file_path = task.excel_path
    else:
        raise HTTPException(
            status_code=404, detail="Excel insight not available for this task"
        )

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Excel file not found")

    # Validate file is actually an Excel file
    if not file_path.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File is not an Excel file")

    filename = os.path.basename(file_path)

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@app.get("/report/{task_id}/pdf")
async def download_report_pdf(task_id: str):
    """Download PDF report file from a completed task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    # Validate it's not an HTML insight task
    if hasattr(task, "file_type") and task.file_type == "html":
        raise HTTPException(
            status_code=400, detail="Use /insight/{task_id} endpoints for insight files"
        )

    # Find PDF file
    if hasattr(task, "file_path") and task.file_path:
        file_path = task.file_path
        # Validate it's a PDF
        if not file_path.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400, detail="Task file is not a PDF. Use /report/{task_id}/excel for Excel files."
            )
    else:
        # Search for PDF in task directory
        task_dir = os.path.join(TEMP_DIR, task_id)
        pdf_files = glob.glob(os.path.join(task_dir, "*.pdf"))
        if not pdf_files:
            raise HTTPException(status_code=404, detail="PDF file not found for this task")
        file_path = pdf_files[0]

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    filename = os.path.basename(file_path)

    # Determine content disposition
    content_disposition = "inline"
    if hasattr(task, "file_type") and task.file_type == "pdf_view":
        content_disposition = "inline"
    else:
        content_disposition = "attachment"

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'{content_disposition}; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@app.get("/report/{task_id}/excel")
async def download_report_excel(task_id: str):
    """Download Excel report file from a completed task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    # Validate it's not an HTML insight task
    if hasattr(task, "file_type") and task.file_type == "html":
        raise HTTPException(
            status_code=400, detail="Use /insight/{task_id} endpoints for insight files"
        )

    # Find Excel file
    if hasattr(task, "excel_path") and task.excel_path:
        file_path = task.excel_path
    else:
        raise HTTPException(
            status_code=404, detail="Excel file not found for this task"
        )

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Excel file not found")

    # Validate file is actually an Excel file
    if not file_path.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File is not an Excel file")

    filename = os.path.basename(file_path)

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


def wrap_html_with_header(
    content_html,
    report_title="MBTI Insight Report",
    subject_name="",
    logo_url="/media/full_logo.png",
):
    """Wraps the provided HTML content with full HTML structure, CSS, and header."""
    # Build the logo image HTML if logo_url is provided
    logo_html = f'<img src="{logo_url}" alt="Logo" />' if logo_url else ""

    # Build the title HTML
    title_html = f"<h1>{report_title}</h1>" if report_title else ""
    subtitle_html = f"<h2>{subject_name}</h2>" if subject_name else ""

    # Build the header section
    header_html = ""
    if logo_html or title_html or subtitle_html:
        header_html = f"""
    <div class="inner-header">
        {logo_html}
        {title_html}
        {subtitle_html}
    </div>
"""

    full_html = f"""<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8">
    <title>{report_title} - {subject_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            background: #fff;
            color: #222;
            margin: 0;
            padding: 0;
        }}
        .inner-header {{
            text-align: center;
            padding: 32px 0 12px 0;
            border-bottom: 2px solid #eee;
            margin-bottom: 24px;
            background: #f6f9ff;
        }}
        .inner-header img {{
            height: 48px;
            vertical-align: middle;
            margin-bottom: 10px;
        }}
        .inner-header h1 {{
            margin: 10px 0 0 0;
            font-size: 2.2rem;
            color: #254C7D;
            letter-spacing: 2px;
        }}
        .inner-header h2 {{
            margin: 0;
            font-size: 1.3rem;
            color: #555;
            font-weight: normal;
        }}
        .report-content {{
            max-width: 800px;
            margin: 0 auto;
            padding: 36px 24px 24px 24px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(90,100,130,0.08);
        }}
        h2, h3, h4 {{
            color: #254C7D;
        }}
    </style>
</head>
<body>
    {header_html}
    <div class="report-content">
        {content_html}
    </div>
</body>
</html>
"""
    return full_html


async def group_insight_background(task_id: str, excel_path: str, req_data: dict):
    """Background task for generating group insight"""
    try:
        update_task_status(task_id, "processing", "Extracting data from Excel...")

        table_pdf_path = extract_data_from_excel_fixed(excel_path)
        print(f"Data table PDF generated at: {table_pdf_path}")

        update_task_status(task_id, "processing", "Building analysis prompt...")

        user_prompt = group_user_prompt(
            req_data.get("group_name", ""),
            req_data.get("industry", ""),
            req_data.get("team_type", ""),
            req_data.get("analysis_goal", ""),
            req_data.get("roles", ""),
            req_data.get("existing_challenges", ""),
        )
        print("GROUP USER PROMPT:", user_prompt)

        update_task_status(task_id, "processing", "Analyzing team data with AI...")

        df = pd.read_excel(excel_path, sheet_name="Data")
        html_table = df.to_html(index=False)
        content_blocks = [
            {"type": "text", "text": user_prompt},
            {"type": "text", "text": html_table},
        ]

        ai_result = process_pdf_with_gpt(table_pdf_path, content_blocks)
        print("AI RESULT:", ai_result)

        if ai_result.get("status") != "ok" or "insight" not in ai_result:
            update_task_status(
                task_id,
                "failed",
                f"AI analysis failed: {ai_result.get('reason', 'Unknown error')}",
            )
            return

        update_task_status(task_id, "processing", "Generating insight report...")

        output_dir = os.path.join(OUTPUT_DIR, "insights")
        os.makedirs(output_dir, exist_ok=True)

        insight_filename = f"group_insight_{task_id[:8]}.html"
        insight_path = os.path.join(output_dir, insight_filename)

        wrapped_html = wrap_html_with_header(
            ai_result["insight"],
            report_title="Group MBTI Analysis",
            subject_name=req_data.get("group_name", ""),
            logo_url="/media/full_logo.png",
        )

        with open(insight_path, "w", encoding="utf-8") as f:
            f.write(wrapped_html)

        # Generate PDF version
        insight_pdf_filename = f"group_insight_{task_id[:8]}.pdf"
        insight_pdf_path = os.path.join(output_dir, insight_pdf_filename)

        try:
            WeasyHTML(insight_path).write_pdf(insight_pdf_path)
            insight_pdf_url = f"/output/insights/{insight_pdf_filename}"
        except Exception as e:
            print(f"PDF generation failed: {e}")
            insight_pdf_url = None

        # Update task status
        task_storage[task_id].status = "completed"
        task_storage[task_id].message = "Group insight generated successfully"
        task_storage[task_id].file_path = insight_path
        task_storage[task_id].file_type = "html"
        if insight_pdf_url:
            task_storage[task_id].insight_pdf_url = insight_pdf_url

    except Exception as e:
        update_task_status(
            task_id, "failed", f"Group insight generation failed: {str(e)}"
        )
        print(f"Error in group insight background: {str(e)}")
        traceback.print_exc()


async def insight_background(
    task_id: str,
    pdf_path: str,
    relationship_type: str = None,
    relationship_goals: str = None,
):
    """Background task for generating MBTI insights for personal/dual reports"""
    try:
        update_task_status(
            task_id, "processing", "Generating MBTI Insight with GPT-4o..."
        )

        # Build user prompt for dual reports with relationship context
        user_prompt = ""
        if relationship_type:
            user_prompt += "Supplementary information for MBTI couple report:\n"
            user_prompt += f"Relationship type: {relationship_type}\n"
        if relationship_goals:
            user_prompt += f"Relationship goals: {relationship_goals}\n"

        # Build content blocks for GPT
        content_blocks = []
        if user_prompt:
            content_blocks.append({"type": "text", "text": user_prompt})

        # Process the PDF with GPT
        result = process_pdf_with_gpt(
            pdf_path, content_blocks if content_blocks else None
        )

        # Generate file names based on PDF
        pdf_stub = os.path.splitext(os.path.basename(pdf_path))[0][:6]
        insight_html_filename = f"insight_{pdf_stub}.html"
        insight_html_path = os.path.join(
            os.path.dirname(pdf_path), insight_html_filename
        )

        if result.get("status") == "ok" and "insight" in result:
            # Extract subject name for header (from filename)
            subject_name = ""
            try:
                base_name = os.path.basename(pdf_path)
                if "_" in base_name:
                    subject_name = (
                        base_name.replace(".pdf", "").replace("_", " ").strip()
                    )
            except Exception:
                subject_name = ""

            # Wrap with header and structure
            html_with_header = wrap_html_with_header(
                result["insight"],
                report_title="MBTI Insight Report",
                subject_name=subject_name,
                logo_url="/media/full_logo.png",
            )

            # Save HTML for preview/download
            with open(insight_html_path, "w", encoding="utf-8") as f:
                f.write(html_with_header)

            # Generate PDF from HTML
            insight_pdf_filename = f"insight_{pdf_stub}.pdf"
            insight_pdf_path = os.path.join(
                os.path.dirname(pdf_path), insight_pdf_filename
            )

            try:
                WeasyHTML(insight_html_path).write_pdf(insight_pdf_path)
                print(f"PDF generated successfully: {insight_pdf_path}")
            except Exception as e:
                print(f"PDF generation from insight HTML failed: {e}")
                insight_pdf_path = None

            insight_pdf_url = None
            if insight_pdf_path and os.path.exists(insight_pdf_path):
                rel_dir = os.path.relpath(os.path.dirname(pdf_path), OUTPUT_DIR)
                insight_pdf_url = f"/output/{rel_dir}/{insight_pdf_filename}".replace(
                    "\\", "/"
                )

            # Update task status with completion
            task_storage[task_id].status = "completed"
            task_storage[task_id].message = "Insight generated successfully."
            task_storage[task_id].file_path = insight_html_path
            task_storage[task_id].file_type = "html"
            if insight_pdf_url:
                task_storage[task_id].insight_pdf_url = insight_pdf_url

            print(
                f"Insight generated successfully. HTML: {insight_html_path}, PDF: {insight_pdf_url}"
            )

        else:
            update_task_status(
                task_id,
                "failed",
                f"Insight generation failed: {result.get('reason', 'Unknown error')}",
            )
    except Exception as e:
        print(f"Error in insight_background: {str(e)}")
        traceback.print_exc()
        update_task_status(task_id, "failed", f"Insight error: {str(e)}")


async def translate_pdf_background(task_id: str, pdf_path: str):
    """Background task for translating a PDF"""
    try:
        update_task_status(task_id, "processing", "Translating PDF...")

        # Create task-specific directory in TEMP_DIR
        task_dir = os.path.join(TEMP_DIR, task_id)
        os.makedirs(task_dir, exist_ok=True)

        # Await the create_translated_pdf function
        output_pdf_path = await create_translated_pdf(pdf_path, task_dir)

        # Store file_path in task storage (existing /report/{task_id}/pdf endpoint will handle serving)
        # Set file_type to enable Get Insight button
        if task_id in task_storage:
            task_storage[task_id].file_type = "pdf_view"
        update_task_status(
            task_id,
            "completed",
            "Translation completed successfully",
            output_pdf_path,
        )

    except Exception as e:
        update_task_status(task_id, "failed", f"Translation failed: {str(e)}")
        print(f"Error translating PDF: {str(e)}")
        traceback.print_exc()


# Background task functions


async def create_group_report_background(task_id: str, folder_path: str):
    """Simple fixed version of group report background task"""
    try:
        update_task_status(
            task_id, "processing", "Creating group report (with fixes)..."
        )

        # Use task_id for unique filename since folder_path is now "all_pdfs"
        output_filename = f"group_report_{task_id}.xlsx"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Remove existing file if present
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                print(f"Removed existing: {output_path}")
            except PermissionError:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"group_report_{task_id}_{timestamp}.xlsx"
                output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Debug: List PDF files before processing
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
        print(f"📄 About to process {len(pdf_files)} PDF files:")
        for i, pdf in enumerate(pdf_files[:5]):  # Show first 5
            print(f"  {i + 1}. {pdf}")
        if len(pdf_files) > 5:
            print(f"  ... and {len(pdf_files) - 5} more")

        # Use the fixed processing function
        workbook = process_group_report_fixed(folder_path, OUTPUT_DIR, output_filename)

        if workbook and hasattr(workbook, "close"):
            workbook.close()

        # Verify the output file exists
        if os.path.exists(output_path):
            print(f"✅ Excel file created successfully: {output_path}")

            # Update task status with excel_path stored properly
            if task_id in task_storage:
                task_storage[task_id] = TaskStatus(
                    task_id=task_id,
                    status="completed",
                    message="Group report created successfully",
                    excel_path=output_path,  # Store the full path
                    created_at=task_storage[task_id].created_at,
                    file_type="xlsx",
                )
        else:
            # File wasn't created - this is a failure
            error_msg = f"Excel file was not created at {output_path}. Check PDF processing logs."
            print(f"❌ {error_msg}")
            update_task_status(task_id, "failed", error_msg)

    except Exception as e:
        error_msg = f"Group report creation failed: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback

        traceback.print_exc()
        update_task_status(task_id, "failed", error_msg)


async def create_personal_report_background(task_id: str, pdf_path: str):
    """Background task for creating personal report"""
    try:
        update_task_status(task_id, "processing", "Extracting images from PDF...")
        page_rectangles = {
            4: {"EIGraph": (0.1, 0.12, 0.9, 0.44)},
            5: {"SNgraph": (0.1, 0.12, 0.9, 0.44)},
            6: {"TFgraph": (0.1, 0.12, 0.9, 0.44)},
            7: {"JPgraph": (0.1, 0.12, 0.9, 0.44)},
        }

        for page_num in [4, 5, 6, 7]:
            rect_coords_dict = page_rectangles.get(page_num)
            extract_multiple_graphs_from_pdf(
                pdf_path, MEDIA_DIR, page_num, rect_coords_dict, zoom=2
            )

        update_task_status(task_id, "processing", "Generating personal report...")
        name_without_ext = Path(pdf_path).stem
        person_name = sanitize_filename(name_without_ext)

        task_dir = os.path.join(TEMP_DIR, task_id)
        os.makedirs(task_dir, exist_ok=True)

        output_filename = f"{person_name}_personal_report_{task_id}.pdf"
        full_output_path = os.path.join(task_dir, output_filename)

        generate_personal_report(pdf_path, task_dir, output_filename)

        if not os.path.exists(full_output_path):
            raise FileNotFoundError(f"Failed to generate PDF at {full_output_path}")

        file_path = full_output_path

        if task_id in task_storage:
            task_storage[task_id].status = "completed"
            task_storage[task_id].message = "Personal report created successfully"
            task_storage[task_id].file_type = "pdf_view"
            task_storage[task_id].file_path = file_path
        else:
            update_task_status(
                task_id,
                "completed",
                "Personal report created successfully",
                file_path,
            )

    except Exception as e:
        update_task_status(
            task_id, "failed", f"Personal report creation failed: {str(e)}"
        )


async def create_dual_report_background(
    task_id: str, pdf1_path: str, pdf2_path: str, output_path: str
):
    """Background task for creating dual report (to be implemented)"""
    try:
        update_task_status(task_id, "processing", "Creating dual report...")
        print(output_path)
        first_name = sanitize_path_component(pdf1_path)
        second_name = sanitize_path_component(pdf2_path)
        identifier = f"{first_name}_{second_name}"
        output_dir = os.path.join(output_path, identifier)
        os.makedirs(output_dir, exist_ok=True)
        _, final_path = generate_dual_report(pdf1_path, pdf2_path, output_dir)

        if not os.path.exists(final_path):
            raise FileNotFoundError(f"Generated dual report not found at {final_path}")

        if task_id in task_storage:
            task_storage[task_id].status = "completed"
            task_storage[task_id].message = (
                "Dual comparison report created successfully"
            )
            task_storage[task_id].file_type = "pdf_view"
            task_storage[task_id].file_path = final_path
        else:
            update_task_status(
                task_id,
                "completed",
                "Dual comparison report created successfully",
                final_path,
            )

    except Exception as e:
        update_task_status(task_id, "failed", f"Dual report creation failed: {str(e)}")
        print(f"Error processing dual report: {str(e)}")
        traceback.print_exc()


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    try:
        # Try to read the HTML file from the same directory
        html_file = os.path.join(os.path.dirname(__file__), "index.html")
        if os.path.exists(html_file):
            with open(html_file, encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    except Exception:
        pass

    # If file not found, return a simple HTML interface
    return HTMLResponse(
        content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MBTI Processing Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .endpoint { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 5px; }
            .btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>MBTI Processing Service</h1>
            <p>Welcome to the MBTI Processing Service API. Use the endpoints below to process your files.</p>

            <div class="endpoint">
                <h3>Available Services:</h3>
                <ul>
                    <li><strong>Group Report:</strong> POST /create-group-report</li>
                    <li><strong>Personal Report:</strong> POST /create-personal-report</li>
                    <li><strong>Dual Report:</strong> POST /create-dual-report</li>
                    <li><strong>Translation:</strong> POST /translate-pdf</li>
                </ul>
            </div>

            <div class="endpoint">
                <a href="/docs" class="btn">View API Documentation</a>
            </div>
        </div>
    </body>
    </html>
    """
    )


@app.post("/upload-zip-group-report", response_model=TaskResponse)
async def upload_zip_group_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="ZIP archive containing MBTI PDFs"),
):
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".zip"]:
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")

    task_id = create_task_id()
    # Use task_id as folder name in TEMP_DIR for proper cleanup
    task_dir = os.path.join(TEMP_DIR, task_id)

    # Create clean folder (optional: clear if already exists)
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir)
    os.makedirs(task_dir, exist_ok=True)

    # Save uploaded file
    zip_path = os.path.join(task_dir, file.filename)
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(task_dir)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error extracting ZIP: {str(e)}"
        ) from e

    os.remove(zip_path)

    # Recursively find PDFs
    pdf_files = glob.glob(os.path.join(task_dir, "**", "*.pdf"), recursive=True)
    if not pdf_files:
        raise HTTPException(status_code=400, detail="No PDF files found in archive")

    # Flatten PDFs into one directory
    flat_pdf_dir = os.path.join(task_dir, "all_pdfs")
    os.makedirs(flat_pdf_dir, exist_ok=True)
    for pdf in pdf_files:
        base = os.path.basename(pdf)
        new_name = f"{uuid.uuid4().hex[:8]}_{base}"
        shutil.copy2(pdf, os.path.join(flat_pdf_dir, new_name))

    # Queue background task
    task_storage[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        message="Group report queued from archive",
        created_at=datetime.now(),
    )
    background_tasks.add_task(create_group_report_background, task_id, flat_pdf_dir)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Group report processing started for {file.filename}",
    )


@app.post("/insight/{task_id}", response_model=TaskResponse)
async def get_mbti_insight_by_task_id(
    background_tasks: BackgroundTasks,
    task_id: str,
    relationship_type: Optional[str] = None,
    relationship_goals: Optional[str] = None,
):
    """Generate MBTI insight from a task ID"""
    try:
        source_task_id = task_id
        print(f"Received insight request for task_id: {source_task_id}")
        print(f"Relationship type: {relationship_type}")
        print(f"Relationship goals: {relationship_goals}")

        if source_task_id not in task_storage:
            raise HTTPException(
                status_code=404, detail=f"Task not found: {source_task_id}"
            )

        task = task_storage[source_task_id]

        if hasattr(task, "file_path") and task.file_path:
            file_path = task.file_path
            print(f"Using file_path from task storage: {file_path}")
        else:
            task_dir = os.path.join(TEMP_DIR, source_task_id)
            pdf_files = glob.glob(os.path.join(task_dir, "*.pdf"))
            if not pdf_files:
                raise HTTPException(
                    status_code=404,
                    detail=f"PDF file not found for task: {source_task_id}",
                )
            file_path = pdf_files[0]
            print(f"Found PDF in task directory: {file_path}")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        # Create new task for insight generation
        task_id = create_task_id()
        task_storage[task_id] = TaskStatus(
            task_id=task_id,
            status="pending",
            message="MBTI Insight queued",
            created_at=datetime.now(),
        )

        # Start background task with the correct function name
        background_tasks.add_task(
            insight_background,  # This is the function we just defined
            task_id,
            file_path,
            relationship_type,
            relationship_goals,
        )

        filename = os.path.basename(file_path)

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message=f"MBTI Insight processing started for {filename}",
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_mbti_insight_by_task_id: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        ) from e


@app.post("/create-group-report", response_model=TaskResponse)
async def create_group_report(
    background_tasks: BackgroundTasks,
    folder_path: str = Form(..., description="Path to folder containing PDF files"),
):
    """Create a group Excel report from a folder of PDF files"""
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Folder path doesarest not exist")

    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Path is not a directory")

    # Check if folder contains PDF files
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(
            status_code=400, detail="No PDF files found in the specified folder"
        )

    task_id = create_task_id()

    # Initialize task status
    task_storage[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        message=f"Group report queued for {len(pdf_files)} PDF files",
        created_at=datetime.now(),
    )

    # Start background processing
    background_tasks.add_task(create_group_report_background, task_id, folder_path)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Group report processing started for {len(pdf_files)} files",
    )


@app.post("/create-personal-report", response_model=TaskResponse)
async def create_personal_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Single PDF file for personal report"),
):
    """Create a personal PDF report from a single PDF file"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    task_id = create_task_id()
    task_dir = os.path.join(TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(task_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Initialize task status
    task_storage[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        message="Personal report queued",
        created_at=datetime.now(),
    )

    # Start background processing
    background_tasks.add_task(create_personal_report_background, task_id, file_path)
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Personal report processing started for {file.filename}",
    )


@app.post("/create-dual-report", response_model=TaskResponse)
async def create_dual_report(
    background_tasks: BackgroundTasks,
    file1: UploadFile = File(..., description="First PDF file"),
    file2: UploadFile = File(..., description="Second PDF file"),
):
    """Create a dual comparison report from two PDF files"""
    if not file1.filename.lower().endswith(
        ".pdf"
    ) or not file2.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    task_id = create_task_id()
    task_dir = os.path.join(TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    # Save uploaded files
    file1_path = os.path.join(task_dir, file1.filename)
    file2_path = os.path.join(task_dir, file2.filename)

    with open(file1_path, "wb") as buffer:
        shutil.copyfileobj(file1.file, buffer)

    with open(file2_path, "wb") as buffer:
        shutil.copyfileobj(file2.file, buffer)

    # Initialize task status
    task_storage[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        message="Dual report queued",
        created_at=datetime.now(),
    )

    # Start background processing
    background_tasks.add_task(
        create_dual_report_background, task_id, file1_path, file2_path, task_dir
    )

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Dual report processing started for {file1.filename} and {file2.filename}",
    )


class GroupInsightRequest(BaseModel):
    group_task_id: str
    group_name: str
    industry: str
    team_type: str
    analysis_goal: str
    roles: Optional[str] = None
    existing_challenges: Optional[str] = None


@app.post("/group-insight", response_model=TaskResponse)
async def group_insight(background_tasks: BackgroundTasks, req: GroupInsightRequest):
    try:
        print(f"Received group insight request: {req}")

        # 1. Look up the Excel file for this group task
        group_task = task_storage.get(req.group_task_id)
        if not group_task:
            raise HTTPException(
                status_code=400, detail="Invalid group task ID - task not found"
            )

        print(f"Found group task: {group_task}")

        if group_task.status != "completed":
            raise HTTPException(
                status_code=400, detail="Group report is not completed yet"
            )

        # 2. Get Excel path from the task - IMPROVED VERSION
        excel_path = None

        # Try to get from excel_path attribute first
        if hasattr(group_task, "excel_path") and group_task.excel_path:
            excel_path = group_task.excel_path
            print(f"Got excel_path from task attribute: {excel_path}")

        # Additional fallback - search for recent Excel files
        if not excel_path or not os.path.exists(excel_path):
            print(f"Excel path not found or doesn't exist: {excel_path}")
            # Search for Excel files in OUTPUT_DIR that might match
            excel_files = glob.glob(os.path.join(OUTPUT_DIR, "group_report_*.xlsx"))
            if excel_files:
                # Get the most recent one
                excel_path = max(excel_files, key=os.path.getctime)
                print(f"Using most recent Excel file: {excel_path}")

        if not excel_path or not os.path.exists(excel_path):
            # Try to list what files are available for debugging
            try:
                available_files = os.listdir(OUTPUT_DIR)
                excel_files = [f for f in available_files if f.endswith(".xlsx")]
                print(f"Available Excel files in output directory: {excel_files}")
            except Exception:
                pass

            raise HTTPException(
                status_code=400,
                detail=f"Excel file not found for this group report. Expected: {excel_path}",
            )

        print(f"Using Excel file: {excel_path}")

        # 3. Create new task for insight generation
        task_id = create_task_id()
        task_storage[task_id] = TaskStatus(
            task_id=task_id,
            status="pending",
            message="Group insight queued",
            created_at=datetime.now(),
        )

        # 4. Convert request to dict for background task
        req_data = {
            "group_name": req.group_name,
            "industry": req.industry,
            "team_type": req.team_type,
            "analysis_goal": req.analysis_goal,
            "roles": req.roles,
            "existing_challenges": req.existing_challenges,
        }

        # 5. Start background processing
        background_tasks.add_task(
            group_insight_background, task_id, excel_path, req_data
        )

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message="Group insight processing started",
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /group-insight: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        ) from e


@app.get("/debug/task/{task_id}")
async def debug_task(task_id: str):
    """Debug endpoint to see task details"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]

    # Convert to dict to see all attributes
    task_dict = (
        task.dict()
        if hasattr(task, "dict")
        else {
            "task_id": task.task_id,
            "status": task.status,
            "message": task.message,
            "download_url": getattr(task, "download_url", None),
            "excel_path": getattr(task, "excel_path", None),
            "file_type": getattr(task, "file_type", None),
            "created_at": str(task.created_at),
        }
    )

    # Add file existence check if excel_path is present
    if "excel_path" in task_dict and task_dict["excel_path"]:
        task_dict["excel_file_exists"] = os.path.exists(task_dict["excel_path"])

    # List available Excel files for reference
    try:
        excel_files = glob.glob(os.path.join(OUTPUT_DIR, "*.xlsx"))
        task_dict["available_excel_files"] = [os.path.basename(f) for f in excel_files]
    except Exception:
        task_dict["available_excel_files"] = []

    return task_dict


@app.post("/translate", response_model=TaskResponse)
async def translate_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file to translate"),
):
    """Translate a PDF file"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    task_id = create_task_id()
    task_dir = os.path.join(TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(task_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Initialize task status
    task_storage[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        message="Translation queued",
        created_at=datetime.now(),
    )

    # Start background processing
    background_tasks.add_task(translate_pdf_background, task_id, file_path)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Translation processing started for {file.filename}",
    )


@app.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of a processing task."""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_storage[task_id]

    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        message=task.message,
        file_type=getattr(task, "file_type", None),
        created_at=task.created_at,
        excel_path=getattr(task, "excel_path", None),
        insight_pdf_url=getattr(task, "insight_pdf_url", None),
        file_path=getattr(task, "file_path", None),
    )


@app.post("/admin/cleanup-media")
async def manual_media_cleanup():
    """Manual endpoint to trigger media directory cleanup"""
    try:
        cleanup_media_directory()
        return {
            "status": "success",
            "message": "Media directory cleanup completed",
            "timestamp": datetime.now(),
            "kept_items": MEDIA_DIRECTORY_KEEP_ITEMS,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}") from e


@app.get("/admin/media-status")
async def get_media_status():
    """Get current media directory status"""
    try:
        # Find active media directory
        active_media_dir = None
        for media_path in MEDIA_DIRECTORIES_TO_CHECK:
            if os.path.exists(media_path):
                active_media_dir = media_path
                break

        if not active_media_dir:
            return {
                "status": "no_media_directory",
                "message": "No media directory found",
            }

        items_in_media = os.listdir(active_media_dir)

        current_items = []
        items_to_remove = []

        for item in items_in_media:
            item_path = os.path.join(active_media_dir, item)
            item_info = {
                "name": item,
                "type": "folder" if os.path.isdir(item_path) else "file",
                "should_keep": item in MEDIA_DIRECTORY_KEEP_ITEMS,
            }
            current_items.append(item_info)

            if item not in MEDIA_DIRECTORY_KEEP_ITEMS:
                items_to_remove.append(item)

        return {
            "status": "success",
            "media_directory": active_media_dir,
            "current_items": current_items,
            "items_to_remove": items_to_remove,
            "cleanup_needed": len(items_to_remove) > 0,
            "timestamp": datetime.now(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"getting media status failed: {str(e)}"
        ) from e


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    current_time = datetime.now()
    return {
        "status": "healthy",
        "timestamp": current_time,
        "timestamp_iso": current_time.isoformat(),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "active_tasks": len(task_storage),
        "output_dir": OUTPUT_DIR,
        "output_dir_exists": os.path.exists(OUTPUT_DIR),
        "cleanup_on_exit": "enabled",
        "server_uptime": (
            str(current_time - app.state.start_time)
            if hasattr(app.state, "start_time")
            else "unknown"
        ),
    }


def is_uuid_folder(name: str) -> bool:
    """Check if folder name looks like a UUID task ID"""
    uuid_regex = re.compile(
        r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", re.IGNORECASE
    )
    return bool(uuid_regex.match(name))


def delete_uuid_folders_from(directory):
    """Delete folders named like task_ids in the given directory"""
    if not os.path.exists(directory):
        return

    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        if os.path.isdir(path) and is_uuid_folder(item):
            try:
                shutil.rmtree(path)
                print(f"🗑️  Removed task folder: {item}")
            except Exception as e:
                print(f"⚠️  Could not remove {item}: {e}")


if __name__ == "__main__":
    parent_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "MBTInterpret")
    )
    sys.path.append(parent_dir)

    uvicorn.run("server:app", host="127.0.0.1", port=3000, reload=True)
