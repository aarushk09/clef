"""
Optical Music Recognition (OMR) Module

Uses deep learning to recognize music notation from images.
Supports multiple backends:
1. oemer (primary) - Python-native deep learning OMR
2. music21 MusicXML import (for pre-processed files)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from fractions import Fraction
from PIL import Image
import tempfile
import os


class OMRBackend(Enum):
    """Available OMR backends."""
    OEMER = "oemer"
    MUSICXML = "musicxml"


@dataclass
class RecognizedNote:
    """A note recognized from sheet music."""
    pitch: str  # e.g., "C4", "F#5", "Bb3"
    duration: str  # e.g., "q", "h", "w", "e", "s"
    dots: int = 0
    tied: bool = False
    articulations: List[str] = field(default_factory=list)
    voice: int = 1
    staff: int = 1


@dataclass
class RecognizedRest:
    """A rest recognized from sheet music."""
    duration: str
    dots: int = 0
    voice: int = 1
    staff: int = 1


@dataclass
class RecognizedChord:
    """A chord recognized from sheet music."""
    pitches: List[str]
    duration: str
    dots: int = 0
    tied: bool = False
    articulations: List[str] = field(default_factory=list)
    voice: int = 1
    staff: int = 1


@dataclass
class RecognizedMeasure:
    """A measure recognized from sheet music."""
    number: int
    contents: List[Any] = field(default_factory=list)  # Notes, rests, chords
    time_signature: Optional[Tuple[int, int]] = None
    key_signature: Optional[str] = None
    tempo: Optional[int] = None
    dynamics: List[str] = field(default_factory=list)


@dataclass
class RecognizedStaff:
    """A staff recognized from sheet music."""
    name: str
    instrument: str
    measures: List[RecognizedMeasure] = field(default_factory=list)
    clef: str = "treble"


@dataclass
class RecognizedScore:
    """Complete recognized score from sheet music."""
    title: Optional[str] = None
    composer: Optional[str] = None
    tempo: Optional[int] = None
    time_signature: Optional[Tuple[int, int]] = None
    key_signature: Optional[str] = None
    staves: List[RecognizedStaff] = field(default_factory=list)


def _duration_to_clef(duration_type: str, dots: int = 0) -> str:
    """Convert music21 duration type to Clef duration."""
    duration_map = {
        "whole": "w",
        "half": "h",
        "quarter": "q",
        "eighth": "e",
        "16th": "s",
        "32nd": "t",
        "64th": "x",
        "breve": "d",  # double whole
    }
    
    base = duration_map.get(duration_type, "q")
    # Ensure dots is an integer
    if not isinstance(dots, int):
        dots = int(dots) if dots else 0
    return base + "." * dots


def _get_dots(duration) -> int:
    """Get the number of dots from a music21 duration object."""
    try:
        # music21 Duration.dots can be an int or a tuple
        dots = duration.dots
        if isinstance(dots, (list, tuple)):
            return len(dots)
        elif isinstance(dots, int):
            return dots
        else:
            return 0
    except:
        return 0


def _pitch_to_clef(pitch) -> str:
    """Convert music21 pitch to Clef pitch string."""
    # Handle music21 pitch object
    name = pitch.name  # e.g., "C", "F#", "B-"
    octave = pitch.octave
    
    # Convert music21 accidentals to Clef format
    if "-" in name:
        name = name.replace("-", "b")
    
    return f"{name}{octave}"


def recognize_with_oemer(image_paths: List[str]) -> RecognizedScore:
    """
    Recognize music using oemer (Optical Music Recognition).
    
    Args:
        image_paths: List of image file paths
    
    Returns:
        RecognizedScore with extracted music data
    """
    try:
        from oemer import predict as oemer_predict
        from oemer.inference import inference
    except ImportError:
        raise ImportError(
            "oemer is required for OMR. Install it with:\n"
            "pip install oemer\n"
            "Note: oemer requires TensorFlow. This may take a while to install."
        )
    
    score = RecognizedScore()
    all_measures = []
    
    for page_num, image_path in enumerate(image_paths):
        try:
            # Run oemer inference
            result = inference(image_path)
            
            # Parse oemer output (MusicXML)
            if result and hasattr(result, 'to_musicxml'):
                musicxml_path = tempfile.mktemp(suffix=".musicxml")
                result.to_musicxml(musicxml_path)
                
                # Parse the MusicXML
                page_score = recognize_from_musicxml(musicxml_path)
                
                # Merge into main score
                if page_score.tempo and not score.tempo:
                    score.tempo = page_score.tempo
                if page_score.time_signature and not score.time_signature:
                    score.time_signature = page_score.time_signature
                if page_score.key_signature and not score.key_signature:
                    score.key_signature = page_score.key_signature
                
                # Merge staves
                for staff in page_score.staves:
                    existing = next((s for s in score.staves if s.name == staff.name), None)
                    if existing:
                        existing.measures.extend(staff.measures)
                    else:
                        score.staves.append(staff)
                
                # Cleanup
                try:
                    os.remove(musicxml_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"Warning: Failed to process page {page_num + 1}: {e}")
            continue
    
    return score


def recognize_from_musicxml(musicxml_path: str) -> RecognizedScore:
    """
    Parse a MusicXML file into RecognizedScore.
    
    Args:
        musicxml_path: Path to MusicXML file
    
    Returns:
        RecognizedScore with parsed music data
    """
    try:
        import music21
    except ImportError:
        raise ImportError(
            "music21 is required for MusicXML parsing. "
            "Install it with: pip install music21"
        )
    
    # Parse MusicXML
    parsed = music21.converter.parse(musicxml_path)
    
    return _music21_to_recognized(parsed)


def recognize_from_midi(midi_path: str) -> RecognizedScore:
    """
    Parse a MIDI file into RecognizedScore.
    
    Args:
        midi_path: Path to MIDI file
    
    Returns:
        RecognizedScore with parsed music data
    """
    try:
        import music21
    except ImportError:
        raise ImportError(
            "music21 is required for MIDI parsing. "
            "Install it with: pip install music21"
        )
    
    # Parse MIDI
    parsed = music21.converter.parse(midi_path)
    
    return _music21_to_recognized(parsed)


def _music21_to_recognized(parsed) -> RecognizedScore:
    """Convert music21 parsed score to RecognizedScore."""
    import music21
    
    score = RecognizedScore()
    
    # Extract metadata
    if parsed.metadata:
        score.title = parsed.metadata.title
        score.composer = parsed.metadata.composer
    
    # Extract tempo
    tempos = parsed.flat.getElementsByClass(music21.tempo.MetronomeMark)
    if tempos:
        score.tempo = int(tempos[0].number)
    
    # Extract time signature
    time_sigs = parsed.flat.getElementsByClass(music21.meter.TimeSignature)
    if time_sigs:
        ts = time_sigs[0]
        score.time_signature = (ts.numerator, ts.denominator)
    
    # Extract key signature
    keys = parsed.flat.getElementsByClass(music21.key.KeySignature)
    if keys:
        key = keys[0]
        # Convert to Clef format (e.g., "C major", "G minor")
        if hasattr(key, 'asKey'):
            key_obj = key.asKey()
            score.key_signature = f"{key_obj.tonic.name} {key_obj.mode}"
    
    # Extract parts/staves
    parts = parsed.parts if hasattr(parsed, 'parts') else [parsed]
    
    for part_num, part in enumerate(parts):
        staff = RecognizedStaff(
            name=part.partName or f"staff{part_num + 1}",
            instrument=_get_instrument_name(part),
        )
        
        # Get clef
        clefs = part.flat.getElementsByClass(music21.clef.Clef)
        if clefs:
            staff.clef = clefs[0].sign.lower()
        
        # Process measures
        measures = part.getElementsByClass(music21.stream.Measure)
        
        for measure in measures:
            rec_measure = RecognizedMeasure(
                number=measure.number if measure.number else len(staff.measures) + 1
            )
            
            # Check for time signature in this measure
            ts_in_measure = measure.getElementsByClass(music21.meter.TimeSignature)
            if ts_in_measure:
                ts = ts_in_measure[0]
                rec_measure.time_signature = (ts.numerator, ts.denominator)
            
            # Check for dynamics
            dynamics = measure.getElementsByClass(music21.dynamics.Dynamic)
            for dyn in dynamics:
                rec_measure.dynamics.append(dyn.value)
            
            # Process notes, rests, chords
            for element in measure.notesAndRests:
                dots = _get_dots(element.duration)
                
                # Get voice number (default to 1)
                voice_num = _get_voice_number(element)
                
                if isinstance(element, music21.chord.Chord):
                    pitches = [_pitch_to_clef(p) for p in element.pitches]
                    rec_chord = RecognizedChord(
                        pitches=pitches,
                        duration=_duration_to_clef(element.duration.type, dots),
                        dots=dots,
                        tied=element.tie is not None and element.tie.type in ('start', 'continue'),
                        articulations=_get_articulations(element),
                        voice=voice_num,
                    )
                    rec_measure.contents.append(rec_chord)
                    
                elif isinstance(element, music21.note.Note):
                    rec_note = RecognizedNote(
                        pitch=_pitch_to_clef(element.pitch),
                        duration=_duration_to_clef(element.duration.type, dots),
                        dots=dots,
                        tied=element.tie is not None and element.tie.type in ('start', 'continue'),
                        articulations=_get_articulations(element),
                        voice=voice_num,
                    )
                    rec_measure.contents.append(rec_note)
                    
                elif isinstance(element, music21.note.Rest):
                    rec_rest = RecognizedRest(
                        duration=_duration_to_clef(element.duration.type, dots),
                        dots=dots,
                        voice=voice_num,
                    )
                    rec_measure.contents.append(rec_rest)
            
            staff.measures.append(rec_measure)
        
        score.staves.append(staff)
    
    return score


def _get_instrument_name(part) -> str:
    """Get instrument name from a music21 part."""
    import music21
    
    instruments = part.getElementsByClass(music21.instrument.Instrument)
    if instruments:
        inst = instruments[0]
        if inst.instrumentName:
            return inst.instrumentName.lower()
    
    # Default based on part name
    part_name = (part.partName or "").lower()
    if "piano" in part_name:
        return "piano"
    elif "violin" in part_name:
        return "violin"
    elif "guitar" in part_name:
        return "acoustic_guitar_nylon"
    elif "flute" in part_name:
        return "flute"
    
    return "piano"


def _get_voice_number(element) -> int:
    """Get a clean voice number from a music21 element."""
    # Try to get the voice from the element itself
    if hasattr(element, 'voice') and element.voice:
        try:
            return int(element.voice)
        except (ValueError, TypeError):
            pass
    
    # Default to voice 1
    return 1


def _get_articulations(element) -> List[str]:
    """Extract articulations from a music21 element."""
    articulations = []
    
    if hasattr(element, 'articulations'):
        for art in element.articulations:
            art_name = type(art).__name__.lower()
            if 'staccato' in art_name:
                articulations.append('staccato')
            elif 'accent' in art_name:
                articulations.append('accent')
            elif 'tenuto' in art_name:
                articulations.append('tenuto')
            elif 'marcato' in art_name:
                articulations.append('marcato')
    
    return articulations

