"""
Clef Transcription Module

Converts PDF sheet music into Clef code using Optical Music Recognition (OMR).
"""

from .transcriber import transcribe_pdf, TranscriptionResult
from .generator import ClefCodeGenerator

__all__ = ["transcribe_pdf", "TranscriptionResult", "ClefCodeGenerator"]

