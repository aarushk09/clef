"""
Parser for the Clef music language.

Uses Lark to parse Clef source code and transform it into an AST.
"""

from __future__ import annotations
from fractions import Fraction
from pathlib import Path
from typing import Optional, Union, List, Any

from lark import Lark, Transformer, v_args, Token, Tree
from lark.exceptions import LarkError, UnexpectedInput, UnexpectedCharacters, UnexpectedToken

from clef.ast.nodes import (
    Location,
    Score,
    Staff,
    Voice,
    Measure,
    TimeSignature,
    TempoMark,
    KeySignature,
    Note,
    Rest,
    Chord,
    GraceNote,
    Pitch,
    Duration,
    Accidental,
    Tuplet,
    Slur,
    Dynamic,
    Hairpin,
    HairpinType,
    Articulation,
    ArticulationType,
    Ornament,
    OrnamentType,
    Trill,
    Pedal,
    PedalType,
    InstrumentChange,
)


class ClefParseError(Exception):
    """Exception raised for parsing errors."""
    
    def __init__(self, message: str, line: Optional[int] = None, 
                 column: Optional[int] = None, context: Optional[str] = None):
        self.message = message
        self.line = line
        self.column = column
        self.context = context
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        parts = [self.message]
        if self.line is not None:
            parts.append(f" at line {self.line}")
            if self.column is not None:
                parts.append(f", column {self.column}")
        if self.context:
            parts.append(f"\n{self.context}")
        return "".join(parts)


def _get_location(token_or_tree: Union[Token, Tree]) -> Optional[Location]:
    """Extract location information from a token or tree."""
    if isinstance(token_or_tree, Token):
        return Location(
            line=token_or_tree.line,
            column=token_or_tree.column,
            end_line=token_or_tree.end_line,
            end_column=token_or_tree.end_column,
        )
    elif hasattr(token_or_tree, 'meta') and token_or_tree.meta:
        meta = token_or_tree.meta
        return Location(
            line=getattr(meta, 'line', 1),
            column=getattr(meta, 'column', 1),
            end_line=getattr(meta, 'end_line', None),
            end_column=getattr(meta, 'end_column', None),
        )
    return None


@v_args(inline=True)
class ClefTransformer(Transformer):
    """Transform Lark parse tree into Clef AST nodes."""
    
    # ========== Terminals ==========
    
    def INTEGER(self, token: Token) -> int:
        return int(token.value)
    
    def IDENTIFIER(self, token: Token) -> str:
        return str(token.value)
    
    def PITCH_NAME(self, token: Token) -> str:
        return token.value.upper()
    
    def OCTAVE(self, token: Token) -> int:
        return int(token.value)
    
    def ACCIDENTAL(self, token: Token) -> Accidental:
        return Accidental.from_str(token.value)
    
    def DURATION_NAME(self, token: Token) -> str:
        return token.value
    
    def FRACTION(self, token: Token) -> Fraction:
        parts = token.value.split("/")
        return Fraction(int(parts[0]), int(parts[1]))
    
    def DYNAMIC_MARK(self, token: Token) -> str:
        return token.value
    
    def HAIRPIN_TYPE(self, token: Token) -> str:
        return token.value
    
    def ARTICULATION_TYPE(self, token: Token) -> str:
        return token.value
    
    def ORNAMENT_TYPE(self, token: Token) -> str:
        return token.value
    
    def PEDAL_TYPE(self, token: Token) -> str:
        return token.value
    
    def MODE(self, token: Token) -> str:
        return token.value
    
    # ========== Pitch ==========
    
    def pitch(self, name: str, *args) -> Pitch:
        accidental = None
        octave = 4  # default
        for arg in args:
            if isinstance(arg, Accidental):
                accidental = arg
            elif isinstance(arg, int):
                octave = arg
        return Pitch(name=name, octave=octave, accidental=accidental)
    
    # ========== Duration ==========
    
    def duration(self, value: Union[str, Fraction]) -> Duration:
        if isinstance(value, str):
            return Duration.from_name(value)
        else:
            return Duration(base_value=value)
    
    def dotting(self) -> int:
        return 1  # Each dot token represents one dot
    
    # ========== Notes and Chords ==========
    
    def grace_note(self, pitch: Pitch) -> GraceNote:
        return GraceNote(pitch=pitch)
    
    def note(self, *args) -> Note:
        grace_notes: List[GraceNote] = []
        pitch: Optional[Pitch] = None
        duration: Optional[Duration] = None
        dots = 0
        
        for arg in args:
            if isinstance(arg, GraceNote):
                grace_notes.append(arg)
            elif isinstance(arg, Pitch):
                pitch = arg
            elif isinstance(arg, Duration):
                duration = arg
            elif isinstance(arg, int):
                dots += arg
        
        if pitch is None or duration is None:
            raise ClefParseError("Note requires pitch and duration")
        
        # Apply dots to duration
        if dots > 0:
            duration = Duration(base_value=duration.base_value, dots=dots)
        
        return Note(
            pitch=pitch,
            duration=duration,
            grace_notes=tuple(grace_notes),
        )
    
    def chord(self, *args) -> Chord:
        pitches: List[Pitch] = []
        duration: Optional[Duration] = None
        dots = 0
        
        for arg in args:
            if isinstance(arg, Pitch):
                pitches.append(arg)
            elif isinstance(arg, Duration):
                duration = arg
            elif isinstance(arg, int):
                dots += arg
        
        if not pitches or duration is None:
            raise ClefParseError("Chord requires at least one pitch and a duration")
        
        # Apply dots
        if dots > 0:
            duration = Duration(base_value=duration.base_value, dots=dots)
        
        return Chord(pitches=tuple(pitches), duration=duration)
    
    def note_or_chord(self, *args) -> Union[Note, Chord]:
        note_or_chord: Optional[Union[Note, Chord]] = None
        articulations: List[Articulation] = []
        ornaments: List[Ornament] = []
        tied = False
        
        for arg in args:
            if isinstance(arg, (Note, Chord)):
                note_or_chord = arg
            elif isinstance(arg, Articulation):
                articulations.append(arg)
            elif isinstance(arg, Ornament):
                ornaments.append(arg)
            elif arg == "tie":
                tied = True
        
        if note_or_chord is None:
            raise ClefParseError("Expected note or chord")
        
        # Create new note/chord with articulations, ornaments, and tie
        if isinstance(note_or_chord, Note):
            return Note(
                pitch=note_or_chord.pitch,
                duration=note_or_chord.duration,
                articulations=tuple(articulations),
                ornaments=tuple(ornaments),
                tied=tied,
                grace_notes=note_or_chord.grace_notes,
            )
        else:
            return Chord(
                pitches=note_or_chord.pitches,
                duration=note_or_chord.duration,
                articulations=tuple(articulations),
                ornaments=tuple(ornaments),
                tied=tied,
                grace_notes=note_or_chord.grace_notes,
            )
    
    def tie(self) -> str:
        return "tie"
    
    # ========== Rest ==========
    
    def rest(self, duration: Duration, *dots) -> Rest:
        total_dots = sum(1 for d in dots if d == 1)
        if total_dots > 0:
            duration = Duration(base_value=duration.base_value, dots=total_dots)
        return Rest(duration=duration)
    
    # ========== Articulations and Ornaments ==========
    
    def articulation(self, type_str: str) -> Articulation:
        return Articulation(type=ArticulationType.from_str(type_str))
    
    def ornament(self, item) -> Ornament:
        # If it's already a Trill, return it
        if isinstance(item, Trill):
            return item
        # Otherwise it's a string type
        return Ornament(type=OrnamentType.from_str(item))
    
    def trill(self, *args) -> Trill:
        aux_pitch = args[0] if args and isinstance(args[0], Pitch) else None
        return Trill(auxiliary_pitch=aux_pitch)
    
    # ========== Tuplet ==========
    
    def tuplet(self, actual: int, normal: int, *contents) -> Tuplet:
        return Tuplet(actual=actual, normal=normal, contents=tuple(contents))
    
    # ========== Slur ==========
    
    def slur_group(self, *contents) -> Slur:
        return Slur(contents=tuple(contents))
    
    # ========== Dynamics ==========
    
    def dynamic(self, marking: str) -> Dynamic:
        return Dynamic(marking=marking)
    
    def hairpin(self, type_str: str, beats: int, *args) -> Hairpin:
        # Handle fraction if provided
        if args and isinstance(args[0], int):
            duration = Fraction(beats, args[0])
        else:
            duration = Fraction(beats, 1)
        return Hairpin(type=HairpinType.from_str(type_str), duration=duration)
    
    # ========== Pedal ==========
    
    def pedal(self, type_str: str) -> Pedal:
        return Pedal(type=PedalType.from_str(type_str))
    
    # ========== Time and Tempo ==========
    
    def tempo_mark(self, bpm: int) -> TempoMark:
        return TempoMark(bpm=bpm)
    
    def time_signature(self, numerator: int, denominator: int) -> TimeSignature:
        return TimeSignature(numerator=numerator, denominator=denominator)
    
    def key_signature(self, *args) -> KeySignature:
        root = args[0]
        accidental = None
        mode = "major"
        for arg in args[1:]:
            if isinstance(arg, Accidental):
                accidental = arg
            elif isinstance(arg, str):
                mode = arg
        return KeySignature(root=root, mode=mode, accidental=accidental)
    
    # ========== Instrument ==========
    
    def instrument_change(self, name: str) -> InstrumentChange:
        return InstrumentChange(instrument=name)
    
    def instrument_spec(self, name: str) -> str:
        return name
    
    # ========== Measure ==========
    
    def measure_content(self, item: Any) -> Any:
        return item
    
    def voice_in_measure(self, number: int, *contents) -> tuple:
        """Return a tuple (voice_number, contents) for measure-level voice grouping."""
        return ("voice_in_measure", number, tuple(contents))
    
    def measure(self, *args) -> Measure:
        number = None
        contents: List[Any] = []
        for arg in args:
            if isinstance(arg, int) and number is None:
                number = arg
            elif isinstance(arg, tuple) and len(arg) == 3 and arg[0] == "voice_in_measure":
                # Handle voice_in_measure: expand it into the measure contents
                # with voice context markers
                voice_num, voice_contents = arg[1], arg[2]
                for item in voice_contents:
                    # Mark items with voice number for later processing
                    if hasattr(item, '__dict__'):
                        # Store voice info in a way the compiler can access
                        contents.append(("voice", voice_num, item))
                    else:
                        contents.append(("voice", voice_num, item))
            else:
                contents.append(arg)
        return Measure(contents=tuple(contents), number=number)
    
    # ========== Voice ==========
    
    def voice_item(self, item: Any) -> Any:
        return item
    
    def voice(self, number: int, *contents) -> Voice:
        return Voice(number=number, contents=tuple(contents))
    
    # ========== Staff ==========
    
    def staff_item(self, item: Any) -> Any:
        return item
    
    def staff(self, name: str, *args) -> Staff:
        instrument = None
        contents: List[Any] = []
        for arg in args:
            if isinstance(arg, str):
                instrument = arg
            else:
                contents.append(arg)
        return Staff(name=name, contents=tuple(contents), instrument=instrument)
    
    # ========== Score ==========
    
    def score_item(self, item: Any) -> Any:
        return item
    
    def score(self, *items) -> Score:
        tempo: Optional[TempoMark] = None
        time_sig: Optional[TimeSignature] = None
        key_sig: Optional[KeySignature] = None
        staves: List[Staff] = []
        
        for item in items:
            if isinstance(item, TempoMark):
                tempo = item
            elif isinstance(item, TimeSignature):
                time_sig = item
            elif isinstance(item, KeySignature):
                key_sig = item
            elif isinstance(item, Staff):
                staves.append(item)
        
        return Score(
            staves=tuple(staves),
            tempo=tempo,
            time_signature=time_sig,
            key_signature=key_sig,
        )
    
    def start(self, score: Score) -> Score:
        return score


class ClefParser:
    """
    Parser for the Clef music language.
    
    Uses Lark with the LALR(1) parser for efficient parsing.
    """
    
    def __init__(self):
        grammar_path = Path(__file__).parent.parent / "grammar.lark"
        with open(grammar_path, "r", encoding="utf-8") as f:
            grammar = f.read()
        
        self._parser = Lark(
            grammar,
            parser="lalr",
            propagate_positions=True,
            maybe_placeholders=False,
        )
        self._transformer = ClefTransformer()
    
    def parse(self, source: str, filename: str = "<string>") -> Score:
        """
        Parse Clef source code and return an AST.
        
        Args:
            source: The Clef source code
            filename: Optional filename for error reporting
            
        Returns:
            The parsed Score AST
            
        Raises:
            ClefParseError: If the source contains syntax errors
        """
        try:
            tree = self._parser.parse(source)
            return self._transformer.transform(tree)
        except UnexpectedCharacters as e:
            raise ClefParseError(
                f"Unexpected character '{e.char}'",
                line=e.line,
                column=e.column,
                context=self._get_context(source, e.line),
            )
        except UnexpectedToken as e:
            expected = ", ".join(sorted(e.expected)[:5])
            if len(e.expected) > 5:
                expected += ", ..."
            raise ClefParseError(
                f"Unexpected token '{e.token}', expected one of: {expected}",
                line=e.line,
                column=e.column,
                context=self._get_context(source, e.line),
            )
        except LarkError as e:
            raise ClefParseError(f"Parse error: {e}")
    
    def _get_context(self, source: str, line: int) -> str:
        """Get source context around the error line."""
        lines = source.splitlines()
        if 0 < line <= len(lines):
            return lines[line - 1]
        return ""


# Module-level parser instance for convenience
_parser: Optional[ClefParser] = None


def parse(source: str, filename: str = "<string>") -> Score:
    """
    Parse Clef source code and return an AST.
    
    This is a convenience function that uses a shared parser instance.
    
    Args:
        source: The Clef source code
        filename: Optional filename for error reporting
        
    Returns:
        The parsed Score AST
        
    Raises:
        ClefParseError: If the source contains syntax errors
    """
    global _parser
    if _parser is None:
        _parser = ClefParser()
    return _parser.parse(source, filename)

