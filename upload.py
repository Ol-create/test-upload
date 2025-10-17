import os
import tempfile
import shutil
import logging
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from typing import Dict, Any

# NOTE: You MUST ensure your app.auth and app.utils.storage modules are available
# Replace with your actual imports for auth and storage
# HARDCODED for testing: This function will bypass actual token verification
# and return a fixed user_id payload.
def verify_token() -> Dict[str, Any]:
    # Placeholder user ID for testing purposes
    return {"user_id": "test-user-123-hardcoded", "scope": ["user"]}

# Original line commented out:
# from app.auth import verify_token 
from storage import upload_audio 

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/upload-test")
async def simple_audio_upload(
    audio: UploadFile, # Removed Form(...) for robust file handling
    token_data: dict = Depends(verify_token),
):
    """
    A simple endpoint to test file upload and S3 connectivity.
    It takes an audio file, saves it temporarily, uploads it to S3, 
    and deletes the local temporary file.
    """
    user_id = token_data.get("user_id")
    if not user_id:
        # This should theoretically not be hit with the hardcoded verify_token,
        # but kept for safety.
        raise HTTPException(status_code=401, detail="Invalid token payload")

    if not audio or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid or missing audio file.")

    tmpdir = None
    try:
        # 1. Save uploaded audio temporarily
        tmpdir = tempfile.mkdtemp()
        audio_path = os.path.join(tmpdir, audio.filename)
        
        # Read file content in chunks to prevent memory overload and check size
        size = 0
        with open(audio_path, "wb") as f:
            while True:
                chunk = await audio.read(1024 * 1024) # Read 1MB chunk
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="Audio file is too large (max 10MB).")
                f.write(chunk)

        # 2. Upload audio to S3 (using the user_id as the 'folder' name)
        # Note: 'upload_audio' must be configured with S3 credentials/permissions
        s3_uri = upload_audio(audio_path, user_id, audio.filename)

        return {
            "message": "Upload successful and S3 path returned.",
            "filename": audio.filename,
            "size_bytes": size,
            "s3_uri": s3_uri,
            "user_id": user_id
        }

    except HTTPException:
        # Re-raise explicit HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Test upload failed for user {user_id}: {e}")
        # Use 500 status code for internal failures like S3/permission issues
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error during upload or S3 operation: {e}"
        )

    finally:
        # 3. Clean up temporary directory
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)

# You would need to update your main.py to include this new router:
# from app.routes import test_upload
# app.include_router(test_upload.router)
