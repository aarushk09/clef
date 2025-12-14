"""
Main Transcription Module

Orchestrates PDF → Image → OMR → Clef Code pipeline.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import os

from .pdf_reader import pdf_to_images, save_images_temp, cleanup_temp_files
from .omr import (
    RecognizedScore,
    recognize_with_oemer,
    recognize_from_musicxml,
    recognize_from_midi,
)
from .generator import ClefCodeGenerator


@dataclass
class TranscriptionResult:
    """Result of a transcription operation."""
    success: bool
    clef_code: str
    score: Optional[RecognizedScore] = None
    warnings: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


def transcribe_pdf(
    pdf_path: str,
    output_path: Optional[str] = None,
    dpi: int = 300,
    first_page: Optional[int] = None,
    last_page: Optional[int] = None,
    use_oemer: bool = True,
) -> TranscriptionResult:
    """
    Transcribe a PDF sheet music file to Clef code.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to write the Clef code (optional)
        dpi: Resolution for PDF rendering (higher = better but slower)
        first_page: First page to process (1-indexed)
        last_page: Last page to process (1-indexed)
        use_oemer: Whether to use oemer for OMR (requires TensorFlow)
    
    Returns:
        TranscriptionResult with the generated Clef code
    """
    warnings = []
    errors = []
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        return TranscriptionResult(
            success=False,
            clef_code="",
            errors=[f"PDF file not found: {pdf_path}"],
        )
    
    # Step 1: Convert PDF to images
    try:
        print(f"Converting PDF to images (DPI={dpi})...")
        images = pdf_to_images(
            str(pdf_path),
            dpi=dpi,
            first_page=first_page,
            last_page=last_page,
        )
        print(f"  Extracted {len(images)} page(s)")
    except Exception as e:
        return TranscriptionResult(
            success=False,
            clef_code="",
            errors=[f"Failed to convert PDF to images: {e}"],
        )
    
    # Step 2: Save images temporarily
    temp_paths = save_images_temp(images)
    
    try:
        # Step 3: Run OMR
        print("Running Optical Music Recognition...")
        
        if use_oemer:
            try:
                score = recognize_with_oemer(temp_paths)
            except ImportError as e:
                warnings.append(f"oemer not available: {e}")
                # Fall back to empty score
                score = RecognizedScore()
                score.staves = []
        else:
            score = RecognizedScore()
        
        if not score.staves:
            warnings.append("No music notation detected. Creating empty template.")
            # Create a basic template
            score = _create_template_score(pdf_path.stem)
        
        # Step 4: Generate Clef code
        print("Generating Clef code...")
        generator = ClefCodeGenerator()
        clef_code = generator.generate(score)
        
        # Step 5: Write output if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(clef_code, encoding="utf-8")
            print(f"  Written to: {output_path}")
        
        return TranscriptionResult(
            success=True,
            clef_code=clef_code,
            score=score,
            warnings=warnings,
        )
        
    finally:
        # Cleanup temp files
        cleanup_temp_files(temp_paths)


def transcribe_musicxml(
    musicxml_path: str,
    output_path: Optional[str] = None,
) -> TranscriptionResult:
    """
    Transcribe a MusicXML file to Clef code.
    
    Args:
        musicxml_path: Path to the MusicXML file
        output_path: Path to write the Clef code (optional)
    
    Returns:
        TranscriptionResult with the generated Clef code
    """
    musicxml_path = Path(musicxml_path)
    if not musicxml_path.exists():
        return TranscriptionResult(
            success=False,
            clef_code="",
            errors=[f"MusicXML file not found: {musicxml_path}"],
        )
    
    try:
        print("Parsing MusicXML...")
        score = recognize_from_musicxml(str(musicxml_path))
        
        print("Generating Clef code...")
        generator = ClefCodeGenerator()
        clef_code = generator.generate(score)
        
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(clef_code, encoding="utf-8")
            print(f"  Written to: {output_path}")
        
        return TranscriptionResult(
            success=True,
            clef_code=clef_code,
            score=score,
        )
        
    except Exception as e:
        return TranscriptionResult(
            success=False,
            clef_code="",
            errors=[f"Failed to parse MusicXML: {e}"],
        )


def transcribe_midi(
    midi_path: str,
    output_path: Optional[str] = None,
) -> TranscriptionResult:
    """
    Transcribe a MIDI file to Clef code.
    
    Args:
        midi_path: Path to the MIDI file
        output_path: Path to write the Clef code (optional)
    
    Returns:
        TranscriptionResult with the generated Clef code
    """
    midi_path = Path(midi_path)
    if not midi_path.exists():
        return TranscriptionResult(
            success=False,
            clef_code="",
            errors=[f"MIDI file not found: {midi_path}"],
        )
    
    try:
        print("Parsing MIDI...")
        score = recognize_from_midi(str(midi_path))
        
        print("Generating Clef code...")
        generator = ClefCodeGenerator()
        clef_code = generator.generate(score)
        
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(clef_code, encoding="utf-8")
            print(f"  Written to: {output_path}")
        
        return TranscriptionResult(
            success=True,
            clef_code=clef_code,
            score=score,
        )
        
    except Exception as e:
        return TranscriptionResult(
            success=False,
            clef_code="",
            errors=[f"Failed to parse MIDI: {e}"],
        )


def _create_template_score(title: str = "Untitled") -> RecognizedScore:
    """Create a basic template score when OMR fails."""
    from .omr import RecognizedStaff, RecognizedMeasure
    
    score = RecognizedScore(
        title=title,
        tempo=120,
        time_signature=(4, 4),
        key_signature="C major",
    )
    
    # Create a basic piano staff with empty measures
    staff = RecognizedStaff(
        name="piano",
        instrument="piano",
        measures=[
            RecognizedMeasure(number=1, contents=[]),
            RecognizedMeasure(number=2, contents=[]),
            RecognizedMeasure(number=3, contents=[]),
            RecognizedMeasure(number=4, contents=[]),
        ],
    )
    
    score.staves = [staff]
    return score

