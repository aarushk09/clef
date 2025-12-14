"""
PDF to Image Conversion

Converts PDF pages to PIL Images for OMR processing.
"""

from pathlib import Path
from typing import List, Optional
from PIL import Image
import tempfile
import os


def pdf_to_images(
    pdf_path: str,
    dpi: int = 300,
    first_page: Optional[int] = None,
    last_page: Optional[int] = None,
) -> List[Image.Image]:
    """
    Convert PDF pages to PIL Images.
    
    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for rendering (higher = better quality but slower)
        first_page: First page to convert (1-indexed, None = first)
        last_page: Last page to convert (1-indexed, None = last)
    
    Returns:
        List of PIL Image objects, one per page
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError(
            "pdf2image is required for PDF transcription. "
            "Install it with: pip install pdf2image\n"
            "Also install poppler: https://github.com/osber/poppler-windows/releases (Windows) "
            "or 'brew install poppler' (macOS) or 'apt install poppler-utils' (Linux)"
        )
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.suffix.lower() == ".pdf":
        raise ValueError(f"File must be a PDF: {pdf_path}")
    
    # Convert PDF to images
    images = convert_from_path(
        str(pdf_path),
        dpi=dpi,
        first_page=first_page,
        last_page=last_page,
    )
    
    return images


def save_images_temp(images: List[Image.Image]) -> List[str]:
    """
    Save images to temporary files for processing.
    
    Args:
        images: List of PIL Images
    
    Returns:
        List of temporary file paths
    """
    temp_paths = []
    temp_dir = tempfile.mkdtemp(prefix="clef_omr_")
    
    for i, img in enumerate(images):
        temp_path = os.path.join(temp_dir, f"page_{i+1}.png")
        img.save(temp_path, "PNG")
        temp_paths.append(temp_path)
    
    return temp_paths


def cleanup_temp_files(paths: List[str]) -> None:
    """Remove temporary files."""
    for path in paths:
        try:
            os.remove(path)
        except OSError:
            pass
    
    # Try to remove the directory
    if paths:
        try:
            os.rmdir(os.path.dirname(paths[0]))
        except OSError:
            pass

