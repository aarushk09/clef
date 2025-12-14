"""
Clef Code Generator

Converts recognized music data into Clef source code.
"""

from typing import List, Optional, TextIO
from io import StringIO

from .omr import (
    RecognizedScore,
    RecognizedStaff,
    RecognizedMeasure,
    RecognizedNote,
    RecognizedRest,
    RecognizedChord,
)


class ClefCodeGenerator:
    """Generates Clef source code from recognized music data."""
    
    def __init__(self, indent: str = "    "):
        """
        Initialize the generator.
        
        Args:
            indent: Indentation string (default: 4 spaces)
        """
        self.indent = indent
        self._output: StringIO = StringIO()
        self._indent_level: int = 0
    
    def generate(self, score: RecognizedScore) -> str:
        """
        Generate Clef code from a recognized score.
        
        Args:
            score: The recognized score data
        
        Returns:
            Clef source code as a string
        """
        self._output = StringIO()
        self._indent_level = 0
        
        # Generate header comment
        self._write_header(score)
        
        # Open score block
        self._writeln("score {")
        self._indent_level += 1
        
        # Write score-level properties
        self._write_score_properties(score)
        
        # Write each staff
        for staff in score.staves:
            self._write_staff(staff, score)
        
        # Close score block
        self._indent_level -= 1
        self._writeln("}")
        
        return self._output.getvalue()
    
    def _write(self, text: str) -> None:
        """Write text without newline."""
        self._output.write(text)
    
    def _writeln(self, text: str = "") -> None:
        """Write indented line."""
        if text:
            self._output.write(self.indent * self._indent_level + text + "\n")
        else:
            self._output.write("\n")
    
    def _write_header(self, score: RecognizedScore) -> None:
        """Write header comment with metadata."""
        self._writeln("// Clef Score")
        if score.title:
            self._writeln(f"// Title: {score.title}")
        if score.composer:
            self._writeln(f"// Composer: {score.composer}")
        self._writeln("// Transcribed from PDF using Clef OMR")
        self._writeln()
    
    def _write_score_properties(self, score: RecognizedScore) -> None:
        """Write score-level properties (tempo, time signature, key)."""
        # Tempo
        if score.tempo:
            self._writeln(f"tempo {score.tempo}")
        
        # Time signature
        if score.time_signature:
            num, denom = score.time_signature
            self._writeln(f"time {num}/{denom}")
        
        # Key signature
        if score.key_signature:
            self._writeln(f"key {score.key_signature}")
        
        self._writeln()
    
    def _write_staff(self, staff: RecognizedStaff, score: RecognizedScore) -> None:
        """Write a staff block."""
        # Sanitize staff name for identifier
        name = self._sanitize_name(staff.name)
        instrument = self._sanitize_instrument(staff.instrument)
        
        self._writeln(f"staff {name} : {instrument} {{")
        self._indent_level += 1
        
        # Group measures by voice if needed
        voices = self._group_by_voice(staff.measures)
        
        if len(voices) == 1:
            # Single voice - write measures directly
            self._write_measures(staff.measures, score)
        else:
            # Multiple voices - write voice blocks
            for voice_num, measures in sorted(voices.items()):
                self._writeln(f"voice {voice_num} {{")
                self._indent_level += 1
                self._write_measures(measures, score)
                self._indent_level -= 1
                self._writeln("}")
        
        self._indent_level -= 1
        self._writeln("}")
        self._writeln()
    
    def _write_measures(self, measures: List[RecognizedMeasure], score: RecognizedScore) -> None:
        """Write measure blocks."""
        for measure in measures:
            self._write_measure(measure, score)
    
    def _write_measure(self, measure: RecognizedMeasure, score: RecognizedScore) -> None:
        """Write a single measure block."""
        self._writeln(f"measure {measure.number} {{")
        self._indent_level += 1
        
        # Time signature change in this measure
        if measure.time_signature:
            num, denom = measure.time_signature
            self._writeln(f"time {num}/{denom}")
        
        # Dynamics at start of measure
        for dynamic in measure.dynamics:
            dyn_mark = self._convert_dynamic(dynamic)
            if dyn_mark:
                self._writeln(dyn_mark)
        
        # Write contents
        for item in measure.contents:
            self._write_content(item)
        
        self._indent_level -= 1
        self._writeln("}")
    
    def _write_content(self, item) -> None:
        """Write a note, rest, or chord."""
        if isinstance(item, RecognizedNote):
            self._write_note(item)
        elif isinstance(item, RecognizedRest):
            self._write_rest(item)
        elif isinstance(item, RecognizedChord):
            self._write_chord(item)
    
    def _write_note(self, note: RecognizedNote) -> None:
        """Write a note."""
        parts = [note.pitch, note.duration]
        
        # Add articulations
        for art in note.articulations:
            parts.append(art)
        
        # Add tie
        if note.tied:
            parts.append("tie")
        
        self._writeln(" ".join(parts))
    
    def _write_rest(self, rest: RecognizedRest) -> None:
        """Write a rest."""
        self._writeln(f"rest {rest.duration}")
    
    def _write_chord(self, chord: RecognizedChord) -> None:
        """Write a chord."""
        pitches = " ".join(chord.pitches)
        parts = [f"[{pitches}]", chord.duration]
        
        # Add articulations
        for art in chord.articulations:
            parts.append(art)
        
        # Add tie
        if chord.tied:
            parts.append("tie")
        
        self._writeln(" ".join(parts))
    
    def _group_by_voice(self, measures: List[RecognizedMeasure]) -> dict:
        """Group measure contents by voice number."""
        voices = {}
        
        for measure in measures:
            # Check which voices are present in this measure
            measure_voices = set()
            for item in measure.contents:
                if hasattr(item, 'voice'):
                    measure_voices.add(item.voice)
            
            if not measure_voices:
                measure_voices = {1}
            
            # If only one voice, return single group
            if len(measure_voices) == 1:
                voice_num = list(measure_voices)[0]
                if voice_num not in voices:
                    voices[voice_num] = []
                voices[voice_num].append(measure)
            else:
                # Multiple voices in this measure
                for voice_num in measure_voices:
                    if voice_num not in voices:
                        voices[voice_num] = []
                    
                    # Create measure copy with only this voice's contents
                    voice_measure = RecognizedMeasure(
                        number=measure.number,
                        contents=[c for c in measure.contents 
                                  if hasattr(c, 'voice') and c.voice == voice_num],
                        time_signature=measure.time_signature,
                        key_signature=measure.key_signature,
                        tempo=measure.tempo,
                        dynamics=measure.dynamics if voice_num == min(measure_voices) else [],
                    )
                    voices[voice_num].append(voice_measure)
        
        return voices if voices else {1: measures}
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as identifier."""
        if not name:
            return "staff1"
        
        # Replace spaces and special chars with underscores
        result = ""
        for c in name.lower():
            if c.isalnum() or c == "_":
                result += c
            elif c in " -":
                result += "_"
        
        # Ensure it starts with a letter
        if result and not result[0].isalpha():
            result = "s_" + result
        
        return result or "staff1"
    
    def _sanitize_instrument(self, instrument: str) -> str:
        """Sanitize instrument name."""
        if not instrument:
            return "piano"
        
        # Map common instrument names to GM names
        instrument_map = {
            "piano": "piano",
            "acoustic grand piano": "piano",
            "grand piano": "piano",
            "violin": "violin",
            "viola": "viola",
            "cello": "cello",
            "violoncello": "cello",
            "flute": "flute",
            "clarinet": "clarinet",
            "oboe": "oboe",
            "bassoon": "bassoon",
            "trumpet": "trumpet",
            "horn": "french_horn",
            "french horn": "french_horn",
            "trombone": "trombone",
            "tuba": "tuba",
            "guitar": "acoustic_guitar_nylon",
            "acoustic guitar": "acoustic_guitar_nylon",
            "electric guitar": "electric_guitar_clean",
            "bass": "acoustic_bass",
            "electric bass": "electric_bass_finger",
            "organ": "church_organ",
            "harpsichord": "harpsichord",
            "harp": "harp",
            "timpani": "timpani",
            "xylophone": "xylophone",
            "vibraphone": "vibraphone",
            "marimba": "marimba",
        }
        
        inst_lower = instrument.lower().strip()
        return instrument_map.get(inst_lower, "piano")
    
    def _convert_dynamic(self, dynamic: str) -> Optional[str]:
        """Convert dynamic marking to Clef format."""
        dynamic_map = {
            "ppp": "ppp",
            "pp": "pp",
            "p": "p",
            "mp": "mp",
            "mf": "mf",
            "f": "f",
            "ff": "ff",
            "fff": "fff",
            "sfz": "sfz",
            "sf": "sf",
            "fp": "fp",
        }
        
        return dynamic_map.get(dynamic.lower().strip())

