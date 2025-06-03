from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import uuid
import tempfile
import shutil
from datetime import datetime
import asyncio
import zipfile
import io

# Import your existing modules
from data_extractor import extract_and_save_text
from data_to_excel import process_pdf_to_xl
from chart_creator import create_distribution_charts
from formatting import format_xl
from create_section_sheets import create_section_sheets
from create_facet_table import create_facet_table
from personal_report import generate_personal_report
from utils import get_all_info, find_and_parse_mbti_scores, convert_scores_to_mbti_dict
import openpyxl as xl

app = FastAPI(
    title="MBTI Processing API",
    description="API for processing MBTI PDF reports and generating Excel/PDF outputs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class ProcessingStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    download_url: Optional[str] = None
    created_at: datetime


class MBTIInfo(BaseModel):
    name: Optional[str]
    date: Optional[str]
    type: Optional[str]
    dominant: Optional[str]


class ProcessingResponse(BaseModel):
    task_id: str
    status: str
    message: str


# In-memory task storage (use Redis or database in production)
task_storage: Dict[str, ProcessingStatus] = {}

# Temporary file storage configuration
TEMP_DIR = tempfile.mkdtemp()
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    os.makedirs(TEMP_DIR, exist_ok=True)
    print(f"FastAPI MBTI Service started. Temp directory: {TEMP_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    shutil.rmtree(TEMP_DIR, ignore_errors=True)


def create_task_id() -> str:
    """Generate a unique task ID"""
    return str(uuid.uuid4())


def update_task_status(task_id: str, status: str, message: str, download_url: Optional[str] = None):
    """Update task status in storage"""
    if task_id in task_storage:
        task_storage[task_id].status = status
        task_storage[task_id].message = message
        if download_url:
            task_storage[task_id].download_url = download_url


async def process_single_pdf_background(task_id: str, file_path: str, output_dir: str, report_type: str):
    """Background task for processing a single PDF"""
    try:
        update_task_status(task_id, "processing", "Extracting text from PDF...")

        # Extract text
        text_path = extract_and_save_text(file_path, output_dir)
        if not text_path:
            raise Exception("Failed to extract text from PDF")

        if report_type == "personal":
            update_task_status(task_id, "processing", "Generating personal report...")
            output_filename = f"personal_report_{task_id}.pdf"
            output_path = generate_personal_report(file_path, output_dir, output_filename)
        else:
            update_task_status(task_id, "processing", "Creating Excel report...")
            output_filename = f"mbti_results_{task_id}.xlsx"
            process_pdf_to_xl(text_path, output_dir, 'MBTI Results', output_filename)

            # Load workbook and add charts/formatting
            excel_path = os.path.join(output_dir, output_filename)
            workbook = xl.load_workbook(excel_path)

            update_task_status(task_id, "processing", "Adding charts and formatting...")
            create_distribution_charts(workbook)
            workbook.save(excel_path)
            format_xl(excel_path)

            output_path = excel_path

        # Create download URL
        download_url = f"/download/{task_id}/{os.path.basename(output_path)}"
        update_task_status(task_id, "completed", "Processing completed successfully", download_url)

    except Exception as e:
        update_task_status(task_id, "failed", f"Processing failed: {str(e)}")


async def process_multiple_pdfs_background(task_id: str, file_paths: List[str], output_dir: str):
    """Background task for processing multiple PDFs into a single Excel file"""
    try:
        update_task_status(task_id, "processing", "Processing multiple PDF files...")

        output_filename = f"group_mbti_results_{task_id}.xlsx"
        excel_path = os.path.join(output_dir, output_filename)

        # Remove existing file if it exists
        if os.path.exists(excel_path):
            os.remove(excel_path)

        textfiles_dir = os.path.join(output_dir, "textfiles")
        os.makedirs(textfiles_dir, exist_ok=True)

        # Process each PDF
        for i, pdf_path in enumerate(file_paths):
            update_task_status(task_id, "processing", f"Processing file {i + 1}/{len(file_paths)}")

            # Extract text
            text_path = extract_and_save_text(pdf_path, textfiles_dir)
            if text_path:
                process_pdf_to_xl(text_path, output_dir, 'MBTI Results', output_filename)

        # Load workbook and add enhancements
        update_task_status(task_id, "processing", "Adding charts and analysis...")
        workbook = xl.load_workbook(excel_path)

        # Add charts and sheets
        create_distribution_charts(workbook)
        create_section_sheets(textfiles_dir, workbook)
        create_facet_table(workbook)

        workbook.save(excel_path)

        # Apply formatting
        update_task_status(task_id, "processing", "Applying formatting...")
        format_xl(excel_path)

        # Create download URL
        download_url = f"/download/{task_id}/{output_filename}"
        update_task_status(task_id, "completed", "Group processing completed successfully", download_url)

    except Exception as e:
        update_task_status(task_id, "failed", f"Group processing failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MBTI Processing API",
        "version": "1.0.0",
        "endpoints": {
            "process_single": "/process/single",
            "process_group": "/process/group",
            "process_personal": "/process/personal",
            "get_status": "/status/{task_id}",
            "download": "/download/{task_id}/{filename}",
            "extract_info": "/extract/info"
        }
    }


@app.post("/process/single", response_model=ProcessingResponse)
async def process_single_pdf(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        report_type: str = Form(default="excel")  # "excel" or "personal"
):
    """Process a single PDF file"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size too large")

    task_id = create_task_id()
    task_dir = os.path.join(TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(task_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Initialize task status
    task_storage[task_id] = ProcessingStatus(
        task_id=task_id,
        status="pending",
        message="Task queued for processing",
        created_at=datetime.now()
    )

    # Start background processing
    background_tasks.add_task(
        process_single_pdf_background,
        task_id, file_path, task_dir, report_type
    )

    return ProcessingResponse(
        task_id=task_id,
        status="pending",
        message="PDF processing started"
    )


@app.post("/process/group", response_model=ProcessingResponse)
async def process_group_pdfs(
        background_tasks: BackgroundTasks,
        files: List[UploadFile] = File(...)
):
    """Process multiple PDF files into a single Excel report"""
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 50:  # Limit number of files
        raise HTTPException(status_code=400, detail="Too many files. Maximum 50 files allowed")

    # Validate all files
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} is too large")

    task_id = create_task_id()
    task_dir = os.path.join(TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    # Save all uploaded files
    file_paths = []
    for file in files:
        file_path = os.path.join(task_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(file_path)

    # Initialize task status
    task_storage[task_id] = ProcessingStatus(
        task_id=task_id,
        status="pending",
        message="Group processing queued",
        created_at=datetime.now()
    )

    # Start background processing
    background_tasks.add_task(
        process_multiple_pdfs_background,
        task_id, file_paths, task_dir
    )

    return ProcessingResponse(
        task_id=task_id,
        status="pending",
        message=f"Group processing started for {len(files)} files"
    )


@app.post("/extract/info", response_model=MBTIInfo)
async def extract_mbti_info(file: UploadFile = File(...)):
    """Extract basic MBTI information from a PDF without full processing"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size too large")

    # Create temporary file
    temp_id = str(uuid.uuid4())
    temp_dir = os.path.join(TEMP_DIR, temp_id)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Save uploaded file
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        text_path = extract_and_save_text(file_path, temp_dir)
        if not text_path:
            raise HTTPException(status_code=500, detail="Failed to extract text from PDF")

        # Get MBTI info
        info = get_all_info(text_path)

        return MBTIInfo(**info)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract MBTI info: {str(e)}")
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/status/{task_id}", response_model=ProcessingStatus)
async def get_task_status(task_id: str):
    """Get the status of a processing task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_storage[task_id]


@app.get("/download/{task_id}/{filename}")
async def download_file(task_id: str, filename: str):
    """Download the processed file"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    file_path = os.path.join(TEMP_DIR, task_id, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type based on file extension
    media_type = "application/octet-stream"
    if filename.lower().endswith('.xlsx'):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.lower().endswith('.pdf'):
        media_type = "application/pdf"

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )


@app.get("/tasks")
async def list_tasks():
    """List all tasks (for debugging/monitoring)"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task.status,
                "message": task.message,
                "created_at": task.created_at
            }
            for task_id, task in task_storage.items()
        ]
    }


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task and cleanup its files"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    # Remove task from storage
    del task_storage[task_id]

    # Cleanup files
    task_dir = os.path.join(TEMP_DIR, task_id)
    shutil.rmtree(task_dir, ignore_errors=True)

    return {"message": "Task deleted successfully"}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "temp_dir": TEMP_DIR,
        "active_tasks": len(task_storage)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )