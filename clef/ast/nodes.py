"""
AST Node definitions for the Clef music language.

All nodes are immutable dataclasses representing the abstract syntax tree
of a Clef score. These nodes capture the complete notation semantics
including timing, dynamics, articulation, and polyphony.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from fractions import Fraction
from typing import Optional, Tuple


@dataclass(frozen=True)
class Location:
    """Source location for error reporting."""
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    
    def __str__(self) -> str:
        if self.end_line is not None:
            return f"line {self.line}, column {self.column} to line {self.end_line}, column {self.end_column}"
        return f"line {self.line}, column {self.column}"


@dataclass(frozen=True, kw_only=True)
class Node:
    """Base class for all AST nodes."""
    location: Optional[Location] = field(default=None, compare=False)


# ============================================================
# Accidentals
# ============================================================

class Accidental(Enum):
    """Accidental types."""
    NATURAL = auto()
    SHARP = auto()
    DOUBLE_SHARP = auto()
    FLAT = auto()
    DOUBLE_FLAT = auto()
    
    @classmethod
    def from_str(cls, s: str) -> "Accidental":
        mapping = {
            "n": cls.NATURAL,
            "#": cls.SHARP,
            "##": cls.DOUBLE_SHARP,
            "b": cls.FLAT,
            "bb": cls.DOUBLE_FLAT,
        }
        return mapping.get(s, cls.NATURAL)
    
    def semitone_offset(self) -> int:
        """Return the semitone offset for this accidental."""
        return {
            Accidental.DOUBLE_FLAT: -2,
            Accidental.FLAT: -1,
            Accidental.NATURAL: 0,
            Accidental.SHARP: 1,
            Accidental.DOUBLE_SHARP: 2,
        }[self]


# ============================================================
# Pitch
# ============================================================

@dataclass(frozen=True)
class Pitch(Node):
    """
    Represents a musical pitch.
    
    Attributes:
        name: The note name (C, D, E, F, G, A, B)
        octave: The octave number (0-9, where 4 is middle C octave)
        accidental: Optional accidental (sharp, flat, natural, etc.)
    """
    name: str  # C, D, E, F, G, A, B
    octave: int
    accidental: Optional[Accidental] = None
    
    def midi_number(self) -> int:
        """Convert pitch to MIDI note number."""
        # C4 = 60 (middle C)
        base_notes = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
        note = base_notes[self.name.upper()]
        midi = (self.octave + 1) * 12 + note
        if self.accidental:
            midi += self.accidental.semitone_offset()
        return midi
    
    def __str__(self) -> str:
        acc_str = ""
        if self.accidental:
            acc_map = {
                Accidental.SHARP: "#",
                Accidental.DOUBLE_SHARP: "##",
                Accidental.FLAT: "b",
                Accidental.DOUBLE_FLAT: "bb",
                Accidental.NATURAL: "n",
            }
            acc_str = acc_map.get(self.accidental, "")
        return f"{self.name}{acc_str}{self.octave}"
    
    def enharmonic_equal(self, other: "Pitch") -> bool:
        """Check if two pitches are enharmonically equivalent."""
        return self.midi_number() == other.midi_number()


# ============================================================
# Duration
# ============================================================

@dataclass(frozen=True)
class Duration(Node):
    """
    Represents a note or rest duration using rational arithmetic.
    
    Attributes:
        base_value: The base duration as a fraction of a whole note
        dots: Number of dots (each dot adds half the previous value)
    """
    base_value: Fraction  # As fraction of a whole note (1 = whole, 1/4 = quarter, etc.)
    dots: int = 0
    
    @classmethod
    def from_name(cls, name: str, dots: int = 0, location: Optional[Location] = None) -> "Duration":
        """Create a duration from a standard name."""
        mapping = {
            "w": Fraction(1, 1),      # whole
            "h": Fraction(1, 2),      # half
            "q": Fraction(1, 4),      # quarter
            "e": Fraction(1, 8),      # eighth
            "s": Fraction(1, 16),     # sixteenth
            "t": Fraction(1, 32),     # thirty-second
            "x": Fraction(1, 64),     # sixty-fourth
        }
        if name not in mapping:
            raise ValueError(f"Unknown duration name: {name}")
        return cls(base_value=mapping[name], dots=dots, location=location)
    
    @classmethod
    def from_fraction(cls, numerator: int, denominator: int, 
                     dots: int = 0, location: Optional[Location] = None) -> "Duration":
        """Create a duration from a fraction."""
        return cls(base_value=Fraction(numerator, denominator), dots=dots, location=location)
    
    def total_value(self) -> Fraction:
        """Calculate the total duration including dots."""
        value = self.base_value
        dot_value = value
        for _ in range(self.dots):
            dot_value = dot_value / 2
            value = value + dot_value
        return value
    
    def __str__(self) -> str:
        name_map = {
            Fraction(1, 1): "w",
            Fraction(1, 2): "h",
            Fraction(1, 4): "q",
            Fraction(1, 8): "e",
            Fraction(1, 16): "s",
            Fraction(1, 32): "t",
            Fraction(1, 64): "x",
        }
        name = name_map.get(self.base_value, f"{self.base_value.numerator}/{self.base_value.denominator}")
        return name + ("." * self.dots)


# ============================================================
# Articulations
# ============================================================

class ArticulationType(Enum):
    """Types of articulations."""
    STACCATO = auto()
    STACCATISSIMO = auto()
    LEGATO = auto()
    ACCENT = auto()
    TENUTO = auto()
    MARCATO = auto()
    FERMATA = auto()
    
    @classmethod
    def from_str(cls, s: str) -> "ArticulationType":
        mapping = {
            "staccato": cls.STACCATO,
            "staccatissimo": cls.STACCATISSIMO,
            "legato": cls.LEGATO,
            "accent": cls.ACCENT,
            "tenuto": cls.TENUTO,
            "marcato": cls.MARCATO,
            "fermata": cls.FERMATA,
        }
        return mapping[s.lower()]


@dataclass(frozen=True)
class Articulation(Node):
    """Represents an articulation marking."""
    type: ArticulationType


# ============================================================
# Ornaments
# ============================================================

class OrnamentType(Enum):
    """Types of ornaments."""
    MORDENT = auto()
    TURN = auto()
    INVERTED_TURN = auto()
    SHAKE = auto()
    TRILL = auto()
    
    @classmethod
    def from_str(cls, s: str) -> "OrnamentType":
        mapping = {
            "mordent": cls.MORDENT,
            "turn": cls.TURN,
            "inverted_turn": cls.INVERTED_TURN,
            "shake": cls.SHAKE,
            "trill": cls.TRILL,
        }
        return mapping[s.lower()]


@dataclass(frozen=True)
class Ornament(Node):
    """Represents an ornament marking."""
    type: OrnamentType


@dataclass(frozen=True)
class Trill(Ornament):
    """Represents a trill, optionally with auxiliary note."""
    type: OrnamentType = field(default=OrnamentType.TRILL)
    auxiliary_pitch: Optional[Pitch] = None


# ============================================================
# Notes, Rests, and Chords
# ============================================================

@dataclass(frozen=True)
class GraceNote(Node):
    """Represents a grace note (appoggiatura or acciaccatura)."""
    pitch: Pitch
    slashed: bool = False  # True for acciaccatura


@dataclass(frozen=True)
class Note(Node):
    """
    Represents a single note.
    
    Attributes:
        pitch: The pitch of the note
        duration: The duration of the note
        articulations: List of articulations
        ornaments: List of ornaments
        tied: Whether this note is tied to the next
        grace_notes: Optional grace notes preceding this note
    """
    pitch: Pitch
    duration: Duration
    articulations: Tuple[Articulation, ...] = ()
    ornaments: Tuple[Ornament, ...] = ()
    tied: bool = False
    grace_notes: Tuple[GraceNote, ...] = ()


@dataclass(frozen=True)
class Rest(Node):
    """Represents a rest."""
    duration: Duration


@dataclass(frozen=True)
class Chord(Node):
    """
    Represents a chord (multiple simultaneous pitches).
    
    All pitches in a chord share the same duration, articulations, and ornaments.
    """
    pitches: Tuple[Pitch, ...]
    duration: Duration
    articulations: Tuple[Articulation, ...] = ()
    ornaments: Tuple[Ornament, ...] = ()
    tied: bool = False
    grace_notes: Tuple[GraceNote, ...] = ()


# ============================================================
# Ties and Slurs
# ============================================================

@dataclass(frozen=True)
class Tie(Node):
    """Marker for a tie connecting to the next note."""
    pass


@dataclass(frozen=True)
class Slur(Node):
    """
    Represents a slur grouping notes together.
    
    Slurs indicate phrasing and legato playing.
    """
    contents: Tuple[Node, ...]  # Notes, rests, chords within the slur


# ============================================================
# Tuplets
# ============================================================

@dataclass(frozen=True)
class Tuplet(Node):
    """
    Represents a tuplet (e.g., triplet, quintuplet).
    
    A tuplet of "n in m" means n notes in the space of m.
    For example, a triplet is 3 in 2 (3 notes in the space of 2).
    
    Attributes:
        actual: The actual number of notes (e.g., 3 for triplet)
        normal: The normal number of notes they replace (e.g., 2 for triplet)
        contents: The notes/rests within the tuplet
    """
    actual: int
    normal: int
    contents: Tuple[Node, ...]
    
    def ratio(self) -> Fraction:
        """Return the tuplet ratio for duration modification."""
        return Fraction(self.normal, self.actual)


# ============================================================
# Dynamics
# ============================================================

@dataclass(frozen=True)
class Dynamic(Node):
    """
    Represents a dynamic marking.
    
    Velocity mappings (approximate MIDI values):
        ppp: 16
        pp: 33
        p: 49
        mp: 64
        mf: 80
        f: 96
        ff: 112
        fff: 127
        fp: forte then piano
        sfz: sforzando
        sf: sforzato
    """
    marking: str  # ppp, pp, p, mp, mf, f, ff, fff, fp, sfz, sf
    
    def velocity(self) -> int:
        """Convert dynamic marking to MIDI velocity (0-127)."""
        mapping = {
            "ppp": 16,
            "pp": 33,
            "p": 49,
            "mp": 64,
            "mf": 80,
            "f": 96,
            "ff": 112,
            "fff": 127,
            "fp": 96,   # Initial forte
            "sfz": 127,
            "sf": 112,
        }
        return mapping.get(self.marking, 80)


class HairpinType(Enum):
    """Types of hairpin dynamics."""
    CRESCENDO = auto()
    DECRESCENDO = auto()
    DIMINUENDO = auto()
    
    @classmethod
    def from_str(cls, s: str) -> "HairpinType":
        mapping = {
            "cresc": cls.CRESCENDO,
            "decresc": cls.DECRESCENDO,
            "dim": cls.DIMINUENDO,
        }
        return mapping[s.lower()]


@dataclass(frozen=True)
class Hairpin(Node):
    """
    Represents a crescendo or decrescendo hairpin.
    
    Attributes:
        type: CRESCENDO, DECRESCENDO, or DIMINUENDO
        duration: Duration of the hairpin as a fraction
    """
    type: HairpinType
    duration: Fraction  # In beats


# ============================================================
# Pedal
# ============================================================

class PedalType(Enum):
    """Types of pedal markings."""
    DOWN = auto()     # Press pedal
    UP = auto()       # Release pedal
    CHANGE = auto()   # Release and press (pedal change)
    
    @classmethod
    def from_str(cls, s: str) -> "PedalType":
        mapping = {
            "ped": cls.DOWN,
            "ped_up": cls.UP,
            "ped_change": cls.CHANGE,
        }
        return mapping[s.lower()]


@dataclass(frozen=True)
class Pedal(Node):
    """Represents a sustain pedal marking."""
    type: PedalType


# ============================================================
# Time and Tempo
# ============================================================

@dataclass(frozen=True)
class TimeSignature(Node):
    """
    Represents a time signature.
    
    Attributes:
        numerator: Number of beats per measure
        denominator: Note value that gets one beat
    """
    numerator: int
    denominator: int
    
    def beats_per_measure(self) -> Fraction:
        """Return the total duration of one measure in whole notes."""
        return Fraction(self.numerator, self.denominator)
    
    def __str__(self) -> str:
        return f"{self.numerator}/{self.denominator}"


@dataclass(frozen=True)
class TempoMark(Node):
    """
    Represents a tempo marking in BPM.
    
    Attributes:
        bpm: Beats per minute (quarter note = one beat by default)
        beat_unit: The note value that represents one beat (default: quarter)
    """
    bpm: int
    beat_unit: Duration = field(default_factory=lambda: Duration.from_name("q"))
    
    def __str__(self) -> str:
        return f"♩ = {self.bpm}"


@dataclass(frozen=True)
class KeySignature(Node):
    """
    Represents a key signature.
    
    Attributes:
        root: The root pitch name (C, D, E, etc.)
        accidental: Optional accidental on the root
        mode: 'major' or 'minor'
    """
    root: str
    mode: str  # 'major' or 'minor'
    accidental: Optional[Accidental] = None
    
    def __str__(self) -> str:
        acc_str = ""
        if self.accidental:
            acc_map = {
                Accidental.SHARP: "#",
                Accidental.FLAT: "b",
            }
            acc_str = acc_map.get(self.accidental, "")
        return f"{self.root}{acc_str} {self.mode}"


# ============================================================
# Instrument
# ============================================================

@dataclass(frozen=True)
class InstrumentChange(Node):
    """Represents an instrument change within a staff."""
    instrument: str


# ============================================================
# Measures, Voices, Staves, Score
# ============================================================

@dataclass(frozen=True)
class Measure(Node):
    """
    Represents a measure (bar) of music.
    
    Attributes:
        number: Optional measure number
        contents: Notes, rests, chords, dynamics, etc. in the measure
    """
    contents: Tuple[Node, ...]
    number: Optional[int] = None


@dataclass(frozen=True)
class Voice(Node):
    """
    Represents a voice within a staff.
    
    Multiple voices allow for independent melodic lines on the same staff.
    
    Attributes:
        number: Voice number (1, 2, etc.)
        contents: Measures and other content in this voice
    """
    number: int
    contents: Tuple[Node, ...]


@dataclass(frozen=True)
class Staff(Node):
    """
    Represents a staff in the score.
    
    Attributes:
        name: Identifier for the staff (e.g., 'piano', 'violin')
        instrument: The instrument for this staff
        contents: Voices, measures, and other content
    """
    name: str
    contents: Tuple[Node, ...]
    instrument: Optional[str] = None


@dataclass(frozen=True)
class Score(Node):
    """
    Root node representing an entire musical score.
    
    Attributes:
        staves: All staves in the score
        tempo: Initial tempo marking
        time_signature: Initial time signature
        key_signature: Initial key signature
    """
    staves: Tuple[Staff, ...]
    tempo: Optional[TempoMark] = None
    time_signature: Optional[TimeSignature] = None
    key_signature: Optional[KeySignature] = None


# ============================================================
# Type alias for convenience
# ============================================================

DottedDuration = Duration  # Alias for clarity when dots > 0

