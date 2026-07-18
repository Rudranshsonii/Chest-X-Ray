import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
import base64
from PIL import Image
import io


class FileManager:
    """Utility class for handling file uploads, storage, and cleanup."""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
    
    def save_uploaded_file(self, file: UploadFile) -> Tuple[str, bytes]:
        """
        Save uploaded file to disk and return file path and bytes.
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            Tuple of (file_path, file_bytes)
            
        Raises:
            HTTPException: If file validation fails
        """
        # Validate file
        self._validate_image_file(file)
        
        # Generate unique filename
        file_extension = self._get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        try:
            # Read file content
            file_bytes = file.file.read()
            
            # Validate image can be opened
            self._validate_image_content(file_bytes)
            
            # Save to disk
            with open(file_path, "wb") as buffer:
                buffer.write(file_bytes)
            
            return str(file_path), file_bytes
            
        except Exception as e:
            # Clean up if file was partially created
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
    
    def cleanup_file(self, file_path: str) -> bool:
        """
        Remove file from disk.
        
        Args:
            file_path: Path to file to remove
            
        Returns:
            True if file was removed, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Remove files older than specified hours.
        
        Args:
            max_age_hours: Maximum age of files to keep
            
        Returns:
            Number of files removed
        """
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        removed_count = 0
        
        try:
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        removed_count += 1
        except Exception:
            pass
        
        return removed_count
    
    def _validate_image_file(self, file: UploadFile) -> None:
        """Validate uploaded file is a valid image."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        allowed_extensions = {'.png', '.jpg', '.jpeg'}
        file_extension = self._get_file_extension(file.filename).lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
            
        if file.content_type not in ['image/png', 'image/jpeg', 'image/jpg']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid content type. Must be PNG or JPEG"
            )
    
    def _validate_image_content(self, file_bytes: bytes) -> None:
        """Validate that file bytes represent a valid image."""
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify()  # Verify it's a valid image
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        return Path(filename).suffix.lower()


def image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string.
    
    Args:
        image: PIL Image object
        
    Returns:
        Base64 encoded string
    """
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')


def create_error_response(message: str, status_code: int = 500) -> dict:
    """
    Create standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        
    Returns:
        Error response dictionary
    """
    return {
        "success": False,
        "error": message,
        "status_code": status_code
    }


def create_success_response(data: dict) -> dict:
    """
    Create standardized success response.
    
    Args:
        data: Response data
        
    Returns:
        Success response dictionary
    """
    return {
        "success": True,
        "data": data
    }


# Global file manager instance
file_manager = FileManager()
