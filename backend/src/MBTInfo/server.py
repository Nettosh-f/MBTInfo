from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import uuid
import tempfile
import traceback
import tempfile
import shutil
from datetime import datetime, timedelta
import signal
import atexit
import asyncio
import sys
import uvicorn
# Import your existing modules
from main import process_files  # Your group processing function
from personal_report import generate_personal_report
from extract_image import extract_multiple_graphs_from_pdf


TEMP_DIR = tempfile.mkdtemp()
OUTPUT_DIR = r"F:\projects\MBTInfo\output"


# @app.on_event("startup")
# async def startup_event():
#     """Initialize the application"""
#     os.makedirs(TEMP_DIR, exist_ok=True)
#     os.makedirs(OUTPUT_DIR, exist_ok=True)
#     print(f"FastAPI MBTI Service started. Temp directory: {TEMP_DIR}")
#     print(f"Output directory: {OUTPUT_DIR}")


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


# Pydantic models
class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    download_url: Optional[str] = None
    file_type: Optional[str] = None  # "html", "pdf", "xlsx", etc.
    created_at: datetime


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


# In-memory task storage
task_storage: Dict[str, TaskStatus] = {}

# Configuration - Fixed paths for testing
TEMP_DIR = tempfile.mkdtemp()
OUTPUT_DIR = r"F:\projects\MBTInfo\output"
OUTPUT_DIR_FACET_GRAPH = r"F:\projects\MBTInfo\backend\media"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Media cleanup configuration
MEDIA_DIRECTORIES_TO_CHECK = [
    "backend/media",
    "./backend/media",
    "../backend/media",
    "media",
    "./media"
]


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
        print("📁 No media directory found, skipping cleanup")
        return

    print(f"📁 Cleaning media directory: {active_media_dir}")

    # Items to keep (whitelist)
    keep_items = {
        "Personal_Report_Media",  # Folder to keep
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
        from personal_report import generate_html_report
        from data_extractor import extract_mbti_data

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
            "Content-Disposition": f'{content_disposition}, filename"=\"{filename}\"',
            "Cache-Control": "no-cache"
        }
    )


# Background task functions
async def create_group_report_background(task_id: str, folder_path: str):
    """Background task for creating group report from folder"""
    try:
        update_task_status(task_id, "processing", "Creating group report...")

        # Use your existing process_files function with fixed output directory
        textfiles_dir = os.path.join(OUTPUT_DIR, "textfiles")
        os.makedirs(textfiles_dir, exist_ok=True)
        output_filename = f"group_report_{task_id}.xlsx"

        # Call your main.py process_files function
        workbook = process_files(folder_path, OUTPUT_DIR, output_filename, textfiles_dir)

        output_path = os.path.join(OUTPUT_DIR, output_filename)
        download_url = f"/output/{output_filename}"

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

        # Generate personal report using your personal_report.py - save to fixed output directory
        output_filename = f"personal_report_{task_id}.pdf"
        output_html = f"personal_report_{task_id}.html"
        output_path = generate_personal_report(pdf_path, OUTPUT_DIR, output_filename)

        download_url = f"/output/{output_html}"
        
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

        # For now, just create a placeholder message in fixed output directory
        output_filename = f"dual_report_{task_id}.txt"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, 'w') as f:
            f.write(f"Dual report for:\n")
            f.write(f"File 1: {os.path.basename(pdf1_path)}\n")
            f.write(f"File 2: {os.path.basename(pdf2_path)}\n")
            f.write(f"Status: To be implemented\n")
            f.write(f"Created: {datetime.now()}\n")
            f.write(f"Output Directory: {OUTPUT_DIR}\n")

        download_url = f"/download/{task_id}/{output_filename}"
        update_task_status(task_id, "completed", "Dual report placeholder created (to be implemented)", download_url)

    except Exception as e:
        update_task_status(task_id, "failed", f"Dual report creation failed: {str(e)}")


async def translate_pdf_background(task_id: str, pdf_path: str):
    """Background task for PDF translation (to be implemented)"""
    try:
        update_task_status(task_id, "processing", "Processing translation request...")

        # Simulate some processing time
        await asyncio.sleep(1)

        # Create a message file in fixed output directory
        output_filename = f"translation_{task_id}.txt"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, 'w') as f:
            f.write(f"Translation request for: {os.path.basename(pdf_path)}\n")
            f.write(f"Status: To be implemented\n")
            f.write(f"Created: {datetime.now()}\n")
            f.write(f"Output Directory: {OUTPUT_DIR}\n")

        download_url = f"/download/{task_id}/{output_filename}"
        update_task_status(task_id, "completed", "Translation: To be implemented", download_url)

    except Exception as e:
        update_task_status(task_id, "failed", f"Translation request failed: {str(e)}")


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
                    <li><strong>Translation:</strong> POST /translate</li>
                </ul>
            </div>

            <div class="endpoint">
                <a href="/docs" class="btn">View API Documentation</a>
            </div>
        </div>
    </body>
    </html>
    """)


@app.post("/create-group-report", response_model=TaskResponse)
async def create_group_report(
        background_tasks: BackgroundTasks,
        folder_path: str = Form(..., description="Path to folder containing PDF files")
):
    """Create a group Excel report from a folder of PDF files"""
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Folder path does not exist")

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
        message="Dual report queued (to be implemented)",
        created_at=datetime.now()
    )

    # Start background processing
    background_tasks.add_task(create_dual_report_background, task_id, file1_path, file2_path)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Dual report processing started for {file1.filename} and {file2.filename}"
    )


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
        message="Translation queued (to be implemented)",
        created_at=datetime.now()
    )

    # Start background processing
    background_tasks.add_task(translate_pdf_background, task_id, file_path)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Translation processing started for {file.filename} (to be implemented)"
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
            "kept_items": ["Personal_Report_Media/", "full_logo.png"]
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
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "active_tasks": len(task_storage),
        "output_dir": OUTPUT_DIR,
        "output_dir_exists": os.path.exists(OUTPUT_DIR),
        "cleanup_on_exit": "enabled"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8443, reload=True)