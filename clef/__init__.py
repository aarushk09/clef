"""
Clef - A notation-complete music programming language.

Clef can represent 100% of Western sheet music with accurate timing,
dynamics, articulation, and polyphony, using rational number timing.
"""

__version__ = "0.1.0"
__author__ = "Clef Contributors"

from clef.parser.parser import parse
from clef.semantic.analyzer import analyze
from clef.engine.compiler import compile_score
from clef.backends.fluidsynth_backend import FluidSynthBackend

__all__ = [
    "parse",
    "analyze", 
    "compile_score",
    "FluidSynthBackend",
    "__version__",
]

# Transcription support (optional, requires extra dependencies)
def transcribe_pdf(pdf_path: str, output_path: str = None, **kwargs):
    """
    Transcribe PDF sheet music to Clef code.
    
    Requires: pip install clef-lang[transcribe]
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to write the Clef code (optional)
        **kwargs: Additional options (dpi, first_page, last_page)
    
    Returns:
        TranscriptionResult with the generated Clef code
    """
    from clef.transcribe import transcribe_pdf as _transcribe_pdf
    return _transcribe_pdf(pdf_path, output_path, **kwargs)

