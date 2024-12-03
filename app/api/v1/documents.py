"""Document processing endpoints."""

from fastapi import APIRouter, UploadFile, File
from typing import Dict, Any
from pathlib import Path
import tempfile
import os

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/process")
async def process_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Process an uploaded document and return basic analysis."""
    # Create a temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Basic file analysis
        file_size = os.path.getsize(temp_path)
        
        return {
            "filename": file.filename,
            "size_bytes": file_size,
            "content_type": file.content_type,
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)