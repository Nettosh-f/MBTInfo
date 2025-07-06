from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import pandas as pd
import uuid
import tempfile
from zipfile import ZipFile
import rarfile
import glob
import re
import traceback
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta
import signal
import atexit
import asyncio
import sys
import uvicorn
import logging
from datetime import datetime
# Import your existing modules
from group_report import process_group_report
from consts import GROUP_INSIGHT_SYSTEM_PROMPT
from MBTInsight import extract_data_from_excel, group_user_prompt, ask_gpt_with_images
from personal_report import generate_personal_report, generate_html_report
from extract_image import extract_multiple_graphs_from_pdf
from utils import get_all_info
from data_extractor import extract_and_save_text
from dual_report import generate_dual_report
from utils import get_all_info
from MBTInsight import process_pdf_with_gpt

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'MBTInterpret'))
sys.path.append(parent_dir)
from main import create_translated_pdf


TEMP_DIR = tempfile.mkdtemp()
OUTPUT_DIR = r"F:\projects\MBTInfo\output"
INPUT_DIR = r"F:\projects\MBTInfo\input"
OUTPUT_DIR_FACET_GRAPH = r"F:\projects\MBTInfo\backend\media"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Create a logger for this module
logger = logging.getLogger("mbti_server")

# Log startup information
logger.info("MBTI Processing Service initializing...")


# Add this with your other Pydantic models at the top of the file
class ProcessingResponse(BaseModel):
    task_id: str
    status: str
    message: str


app = FastAPI(
    title="MBTI Processing Service",
    description="Service for MBTI report processing with 4 main activities",
    version="1.0.0"
)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    app.state.start_time = datetime.now()

    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logger.info(f"FastAPI MBTI Service started at {app.state.start_time.isoformat()}")
    logger.info(f"Temp directory: {TEMP_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")


# Pydantic models
class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    download_url: Optional[str] = None
    file_type: Optional[str] = None  # "html", "pdf", "xlsx", etc.
    created_at: datetime
    excel_path: Optional[str] = None  # <-- ADD THIS LINE!


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


# In-memory task storage
task_storage: Dict[str, TaskStatus] = {}


# Media cleanup configuration
MEDIA_DIRECTORIES_TO_CHECK = [
    "backend/media",
    "./backend/media",
    "../backend/media",
    "media",
    "./media",
    "../media",
    r"F:\projects\MBTInfo\backend\media",
    r"F:\projects\MBTInfo\output\textfiles",

]


def cleanup_output_directory():
    """Clean up the output directory by removing the 'textfiles' folder"""
    print("\n🧹 Starting output directory cleanup...")

    textfiles_dir = os.path.join(OUTPUT_DIR, "textfiles")

    if os.path.exists(textfiles_dir):
        try:
            shutil.rmtree(textfiles_dir)
            print(f"🗑️  Removed folder: textfiles")
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
        print(f"📁 No media directory found in, skipping cleanup")
        return

    print(f"📁 Cleaning media directory: {active_media_dir}")

    # Items to keep (whitelist)
    keep_items = {
        "Personal_Report_Media",  # Folder to keep
        "Dual_Report_Media",  # Folder to keep
        "full_logo.png"  # File to keep
    }

    try:
        items_in_media = os.listdir(active_media_dir)
        removed_count = 0

        for item in items_in_media:
            if item not in keep_items:
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
    except:
        pass

    print("👋 Service stopped cleanly")


# Register cleanup function to run on exit
atexit.register(cleanup_on_exit)


# Handle termination signals
def signal_handler(signum, frame):
    """Handle termination signals"""
    print(f"\n⚠️  Received signal {signum}, shutting down gracefully...")
    cleanup_on_exit()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

if os.name != 'nt':  # Unix/Linux specific signals
    signal.signal(signal.SIGHUP, signal_handler)  # Hangup signal
    signal.signal(signal.SIGQUIT, signal_handler)  # Quit signal


def create_task_id() -> str:
    return str(uuid.uuid4())


def update_task_status(task_id: str, status: str, message: str, download_url: Optional[str] = None):
    if task_id in task_storage:
        task_storage[task_id].status = status
        task_storage[task_id].message = message
        if download_url:
            task_storage[task_id].download_url = download_url


async def process_personal_report(task_id: str, file_path: str):
    """Process a personal MBTI report"""
    try:
        # Update task status
        task_storage[task_id].status = "processing"
        task_storage[task_id].message = "Extracting data from PDF"

        # Get the output directory
        output_dir = os.path.join(TEMP_DIR, task_id)
        os.makedirs(output_dir, exist_ok=True)

        # Process the PDF and generate the HTML report

        # Extract data from the PDF
        mbti_data = extract_mbti_data(file_path)

        # Generate the HTML report
        html_content = generate_html_report(
            info=mbti_data.get('info', {}),
            mbti_dict=mbti_data.get('mbti_dict', {}),
            preferred_qualities=mbti_data.get('preferred_qualities', {}),
            midzone_qualities=mbti_data.get('midzone_qualities', {}),
            out_qualities=mbti_data.get('out_qualities', {}),
            three_repeating_explanations=mbti_data.get('three_repeating_explanations', {}),
            facet_descriptors=mbti_data.get('facet_descriptors', {}),
            input_pdf_path=file_path
        )

        # Save the HTML report
        output_filename = "Personal_MBTI_Report.html"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Update task status to completed
        task_storage[task_id].status = "completed"
        task_storage[task_id].message = "Personal report generated successfully"
        task_storage[task_id].download_url = f"/output/{output_filename}"

        # Add a flag to indicate this is an HTML file that should be opened in browser
        task_storage[task_id].file_type = "html"

    except Exception as e:
        # Update task status to failed
        task_storage[task_id].status = "failed"
        task_storage[task_id].message = f"Error processing personal report: {str(e)}"
        print(f"Error processing personal report: {str(e)}")
        traceback.print_exc()


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
    if filename.lower().endswith('.html'):
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)

    # Determine media type based on file extension
    media_type = "application/octet-stream"
    if filename.lower().endswith('.xlsx'):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.lower().endswith('.pdf'):
        media_type = "application/pdf"
    elif filename.lower().endswith('.txt'):
        media_type = "text/plain"

    # Set Content-Disposition based on file_type in task_storage
    # For PDF files that should be viewed in browser, use 'inline' instead of 'attachment'
    content_disposition = "attachment"
    if hasattr(task, 'file_type') and task.file_type == "pdf_view" and filename.lower().endswith('.pdf'):
        content_disposition = "inline"

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type,
        headers={
            "Content-Disposition": f'{content_disposition}, filename"="{filename}"',
            "Cache-Control": "no-cache"
        }
    )


async def insight_background(task_id: str, pdf_path: str):
    try:
        update_task_status(task_id, "processing", "Generating MBTI Insight with GPT-4o...")
        result = process_pdf_with_gpt(pdf_path)
        pdf_stub = os.path.splitext(os.path.basename(pdf_path))[0][:6]
        insight_html_filename = f"insight_{pdf_stub}.html"
        insight_html_path = os.path.join(os.path.dirname(pdf_path), insight_html_filename)

        if result.get("status") == "ok" and "insight" in result:
            # Save the AI's HTML to disk
            with open(insight_html_path, "w", encoding="utf-8") as f:
                f.write(result["insight"])
            # Report status and correct download_url
            update_task_status(
                task_id, "completed", "Insight generated successfully.",
                download_url=f"/output/{os.path.basename(os.path.dirname(pdf_path))}/{insight_html_filename}"
            )
            task_storage[task_id].file_type = "html"
        else:
            update_task_status(
                task_id, "failed",
                f"Insight generation failed: {result.get('reason', 'Unknown error')}"
            )
    except Exception as e:
        update_task_status(task_id, "failed", f"Insight error: {str(e)}")


async def translate_pdf_background(task_id: str, pdf_path: str):
    """Background task for translating a PDF"""
    try:
        update_task_status(task_id, "processing", "Translating PDF...")

        # Create a directory for the PDF if it doesn't exist
        person_name = os.path.basename(pdf_path).replace(" ", "_").replace("-", "_").replace(".pdf", "")
        person_dir = os.path.join(OUTPUT_DIR, person_name)
        os.makedirs(person_dir, exist_ok=True)

        # Await the create_translated_pdf function
        output_pdf_path = await create_translated_pdf(pdf_path, person_dir)

        download_url = f"/output/{person_name}/{os.path.basename(output_pdf_path)}"
        update_task_status(task_id, "completed", "Translation completed successfully", download_url)

    except Exception as e:
        update_task_status(task_id, "failed", f"Translation failed: {str(e)}")
        print(f"Error translating PDF: {str(e)}")
        traceback.print_exc()
        
        
# Background task functions

async def create_group_report_background(task_id: str, folder_path: str):
    try:
        update_task_status(task_id, "processing", "Creating group report...")
        folder_name = os.path.basename(os.path.normpath(folder_path))
        textfiles_dir = os.path.join(OUTPUT_DIR, "textfiles")
        os.makedirs(textfiles_dir, exist_ok=True)
        output_filename = f"group_report_{folder_name}.xlsx"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        if os.path.exists(output_path):
            os.remove(output_path)

        workbook = process_group_report(folder_path, OUTPUT_DIR, output_filename)
        download_url = f"/output/{output_filename}"

        # Here, directly assign excel_path to the task object:
        if task_id in task_storage:
            task_storage[task_id].status = "completed"
            task_storage[task_id].message = "Group report created successfully"
            task_storage[task_id].download_url = download_url
            task_storage[task_id].excel_path = output_path  # <-- FIXED HERE
        else:
            update_task_status(task_id, "completed", "Group report created successfully", download_url)

    except Exception as e:
        update_task_status(task_id, "failed", f"Group report creation failed: {str(e)}")


async def create_personal_report_background(task_id: str, pdf_path: str):
    """Background task for creating personal report"""
    try:
        update_task_status(task_id, "processing", "Extracting images from PDF...")

        # Extract images using your extract_image.py - save to fixed output directory
        page_rectangles = {
            4: {"EIGraph": (0.1, 0.12, 0.9, 0.44)},
            5: {"SNgraph": (0.1, 0.12, 0.9, 0.44)},
            6: {"TFgraph": (0.1, 0.12, 0.9, 0.44)},
            7: {"JPgraph": (0.1, 0.12, 0.9, 0.44)}
        }

        for page_num in [4, 5, 6, 7]:
            rect_coords_dict = page_rectangles.get(page_num)
            extract_multiple_graphs_from_pdf(
                pdf_path, OUTPUT_DIR_FACET_GRAPH, page_num, rect_coords_dict, zoom=2
            )

        update_task_status(task_id, "processing", "Generating personal report...")
        person_name = os.path.basename(pdf_path)
        person_name = person_name.replace(" ", "_").replace("-", "_").replace(".pdf", "")

        # Create a directory for the PDF if it doesn't exist
        person_dir = os.path.join(OUTPUT_DIR, person_name)
        os.makedirs(person_dir, exist_ok=True)

        # Generate personal report using your personal_report.py - save to the person's directory
        output_filename = f"{person_name}_personal_report_{task_id}.pdf"
        output_path = generate_personal_report(pdf_path, person_dir, output_filename)
        print(person_name)
        download_url = f"/output/{person_name}/{output_filename}"

        # Update task status with file_type set to "pdf_view" to indicate it should be opened in browser
        if task_id in task_storage:
            task_storage[task_id].status = "completed"
            task_storage[task_id].message = "Personal report created successfully"
            task_storage[task_id].download_url = download_url
            task_storage[task_id].file_type = "pdf_view"  # Add this flag to indicate browser opening
        else:
            update_task_status(task_id, "completed", "Personal report created successfully", download_url)

    except Exception as e:
        update_task_status(task_id, "failed", f"Personal report creation failed: {str(e)}")


async def create_dual_report_background(task_id: str, pdf1_path: str, pdf2_path: str):
    """Background task for creating dual report (to be implemented)"""
    try:
        update_task_status(task_id, "processing", "Creating dual report...")

        # Simulate some processing time
        await asyncio.sleep(2)
        first_name_part = os.path.basename(pdf1_path)[:6]
        second_name_part = os.path.basename(pdf2_path)[:6]
        identifier = f"{first_name_part}_{second_name_part}"
        # For now, just create a placeholder message in fixed output directory
        output_filename = f"dual_report_{identifier}_{task_id[:6]}.pdf"
        output_path = OUTPUT_DIR
        generate_dual_report(pdf1_path, pdf2_path, output_path)
        download_url = f"/output/{identifier}_dual_report.pdf"

        if task_id in task_storage:
            task_storage[task_id].status = "completed"
            task_storage[task_id].message = "Dual comparison report created successfully"
            task_storage[task_id].download_url = download_url
            task_storage[task_id].file_type = "pdf_view"  # Add this flag to indicate browser opening
        else:
            update_task_status(task_id, "completed", "Dual comparison report created successfully", download_url)

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
            with open(html_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
    except:
        pass

    # If file not found, return a simple HTML interface
    return HTMLResponse(content="""
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
    """)


@app.post("/upload-zip-group-report", response_model=TaskResponse)
async def upload_zip_group_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="ZIP archive containing MBTI PDFs")
    ):
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".zip"]:
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")

    task_id = create_task_id()
    # Use archive filename (without extension) as folder name
    base_name = os.path.splitext(os.path.basename(file.filename))[0]
    task_dir = os.path.join(INPUT_DIR, base_name)

    # Create clean folder (optional: clear if already exists)
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir)
    os.makedirs(task_dir, exist_ok=True)

    # Save uploaded file
    zip_path = os.path.join(task_dir, file.filename)
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(task_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting ZIP: {str(e)}")

    os.remove(zip_path)

    # Recursively find PDFs
    pdf_files = glob.glob(os.path.join(task_dir, '**', '*.pdf'), recursive=True)
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
        created_at=datetime.now()
    )
    background_tasks.add_task(create_group_report_background, task_id, flat_pdf_dir)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Group report processing started for {file.filename}"
    )


@app.post("/insight-by-download-url", response_model=TaskResponse)
async def get_mbti_insight_by_download_url(
    background_tasks: BackgroundTasks,
    download_url: str = Form(...)
):
    # Example: "/output/PersonName/filename.pdf"
    parts = download_url.strip("/").split("/")
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail="Invalid download_url format")
    person_name = parts[-2]
    filename = parts[-1]
    file_path = os.path.join(OUTPUT_DIR, person_name, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    task_id = create_task_id()
    task_storage[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        message="MBTI Insight queued",
        created_at=datetime.now()
    )
    background_tasks.add_task(insight_background, task_id, file_path)
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"MBTI Insight processing started for {filename}"
    )


@app.post("/create-group-report", response_model=TaskResponse)
async def create_group_report(
        background_tasks: BackgroundTasks,
        folder_path: str = Form(..., description="Path to folder containing PDF files")
):
    """Create a group Excel report from a folder of PDF files"""
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Folder path doesarest not exist")

    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Path is not a directory")

    # Check if folder contains PDF files
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        raise HTTPException(status_code=400, detail="No PDF files found in the specified folder")

    task_id = create_task_id()

    # Initialize task status
    task_storage[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        message=f"Group report queued for {len(pdf_files)} PDF files",
        created_at=datetime.now()
    )

    # Start background processing
    background_tasks.add_task(create_group_report_background, task_id, folder_path)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Group report processing started for {len(pdf_files)} files"
    )


@app.post("/create-personal-report", response_model=TaskResponse)
async def create_personal_report(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(..., description="Single PDF file for personal report")
):
    """Create a personal PDF report from a single PDF file"""
    if not file.filename.lower().endswith('.pdf'):
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
        created_at=datetime.now()
    )

    # Start background processing
    background_tasks.add_task(create_personal_report_background, task_id, file_path)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Personal report processing started for {file.filename}"
    )


@app.post("/create-dual-report", response_model=TaskResponse)
async def create_dual_report(
        background_tasks: BackgroundTasks,
        file1: UploadFile = File(..., description="First PDF file"),
        file2: UploadFile = File(..., description="Second PDF file")
):
    """Create a dual comparison report from two PDF files"""
    if not file1.filename.lower().endswith('.pdf') or not file2.filename.lower().endswith('.pdf'):
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
        created_at=datetime.now()
    )

    # Start background processing
    background_tasks.add_task(create_dual_report_background, task_id, file1_path, file2_path)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Dual report processing started for {file1.filename} and {file2.filename}"
    )


class GroupInsightRequest(BaseModel):
    group_task_id: str
    group_name: str
    industry: str
    team_type: str
    number_of_members: str
    duration_together: str
    analysis_goal: str
    roles: Optional[str] = None
    existing_challenges: Optional[str] = None
    communication_style: Optional[str] = None
    upcoming_context: Optional[str] = None


@app.post("/group-insight", response_model=TaskResponse)
async def group_insight(req: GroupInsightRequest):
    try:
        # 1. Look up the Excel file for this group task
        group_task = task_storage.get(req.group_task_id)
        if not group_task or not hasattr(group_task, 'download_url'):
            raise HTTPException(status_code=400, detail="Invalid or unknown group report task ID.")

        # Extract Excel path from download_url or your new excel_path property
        # If using download_url:
        if Path(group_task.download_url).suffix == ".xlsx":
            excel_path = os.path.join(OUTPUT_DIR, group_task.download_url.split("/")[-1])
        elif hasattr(group_task, 'excel_path'):
            excel_path = group_task.excel_path
        else:
            raise HTTPException(status_code=400, detail="Excel file not found for this group report task.")

        # Step 1: Extract data from Excel (convert to PDF and HTML table)
        table_pdf_path = extract_data_from_excel(excel_path)
        print(f"Data table PDF generated at: {table_pdf_path}")

        # Step 2: Build the prompt
        user_prompt = group_user_prompt(
            req.group_name,
            req.industry,
            req.team_type,
            req.number_of_members,
            req.duration_together,
            req.analysis_goal,
            req.roles,
            req.existing_challenges,
            req.communication_style,
            req.upcoming_context
        )
        print("GROUP USER PROMPT:", user_prompt)

        # Step 3: Prepare Excel data as an HTML table block (you could also add as image if needed)

        df = pd.read_excel(excel_path, sheet_name="Data")
        html_table = df.to_html(index=False)
        content_blocks = [
            {"type": "text", "text": user_prompt},
            {"type": "text", "text": html_table}
        ]

        # Step 4: Call GPT (with system prompt = group prompt, user content = data table)

        ai_result = process_pdf_with_gpt(table_pdf_path, content_blocks)
        print("AI RESULT:", ai_result)

        # Step 5: Save result as HTML (optional)
        task_id = create_task_id()
        output_dir = os.path.join(OUTPUT_DIR, "insights")
        os.makedirs(output_dir, exist_ok=True)
        insight_filename = f"group_insight_{task_id[:8]}.html"
        insight_path = os.path.join(output_dir, insight_filename)
        with open(insight_path, "w", encoding="utf-8") as f:
            f.write(ai_result["insight"])
        download_url = f"/output/insights/{insight_filename}"

        # Register in task storage if you want progress/status
        task_storage[task_id] = TaskStatus(
            task_id=task_id,
            status="completed",
            message="Group insight generated",
            download_url=download_url,
            file_type="html",
            created_at=datetime.now()
        )

        return TaskResponse(
            task_id=task_id,
            status="completed",
            message="Group insight generated successfully."
        )
    except Exception as e:
        print("Error in /group-insight:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate", response_model=TaskResponse)
async def translate_pdf(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(..., description="PDF file to translate")
):
    """Translate a PDF file"""
    if not file.filename.lower().endswith('.pdf'):
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
        created_at=datetime.now()
    )

    # Start background processing
    background_tasks.add_task(translate_pdf_background, task_id, file_path)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Translation processing started for {file.filename}"
    )


@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a processing task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_storage[task_id]


@app.post("/admin/cleanup-media")
async def manual_media_cleanup():
    """Manual endpoint to trigger media directory cleanup"""
    try:
        cleanup_media_directory()
        return {
            "status": "success",
            "message": "Media directory cleanup completed",
            "timestamp": datetime.now(),
            "kept_items": ["Personal_Report_Media/", "Dual_Report_Media/", "full_logo.png"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


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
                "message": "No media directory found"
            }

        items_in_media = os.listdir(active_media_dir)
        keep_items = {"Personal_Report_Media", "full_logo.png"}

        current_items = []
        items_to_remove = []

        for item in items_in_media:
            item_path = os.path.join(active_media_dir, item)
            item_info = {
                "name": item,
                "type": "folder" if os.path.isdir(item_path) else "file",
                "should_keep": item in keep_items
            }
            current_items.append(item_info)

            if item not in keep_items:
                items_to_remove.append(item)

        return {
            "status": "success",
            "media_directory": active_media_dir,
            "current_items": current_items,
            "items_to_remove": items_to_remove,
            "cleanup_needed": len(items_to_remove) > 0,
            "timestamp": datetime.now()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"getting media status failed: {str(e)}")


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
        "server_uptime": str(current_time - app.state.start_time) if hasattr(app.state, "start_time") else "unknown"
    }


def is_uuid_folder(name: str) -> bool:
    """Check if folder name looks like a UUID task ID"""
    uuid_regex = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", re.IGNORECASE)
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
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=3000, reload=True)