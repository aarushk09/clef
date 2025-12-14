"""
Event definitions for the Clef event engine.

Events represent time-aligned musical actions with exact rational timing.
These events are the intermediate representation between AST and audio playback.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from fractions import Fraction
from typing import Optional, List, Set, FrozenSet


class EventType(Enum):
    """Types of events in the event graph."""
    NOTE_ON = auto()
    NOTE_OFF = auto()
    REST = auto()
    TEMPO_CHANGE = auto()
    TIME_SIGNATURE = auto()
    DYNAMIC = auto()
    PEDAL = auto()
    PROGRAM_CHANGE = auto()  # Instrument change
    CONTROL_CHANGE = auto()


@dataclass(frozen=True)
class Event:
    """
    Base class for all events.
    
    All events have:
    - start_time: Absolute position in whole notes from the beginning
    - staff_id: Which staff this event belongs to
    - voice_id: Which voice within the staff
    """
    start_time: Fraction  # Absolute time in whole notes
    staff_id: str
    voice_id: int
    
    def __lt__(self, other: "Event") -> bool:
        """Events are ordered by start time."""
        if not isinstance(other, Event):
            return NotImplemented
        return self.start_time < other.start_time


@dataclass(frozen=True)
class NoteEvent(Event):
    """
    Represents a note being played.
    
    Attributes:
        midi_note: MIDI note number (0-127)
        duration: Duration in whole notes
        velocity: MIDI velocity (0-127)
        articulations: Set of articulation flags
        is_tied_from: Whether this note continues from a tie
        is_tied_to: Whether this note ties to the next
        channel: MIDI channel (0-15)
    """
    midi_note: int
    duration: Fraction
    velocity: int = 80
    articulations: FrozenSet[str] = field(default_factory=frozenset)
    is_tied_from: bool = False
    is_tied_to: bool = False
    channel: int = 0
    
    def end_time(self) -> Fraction:
        """Return the end time of this note."""
        return self.start_time + self.duration
    
    def effective_duration(self) -> Fraction:
        """Return the effective playing duration considering articulations."""
        if "staccato" in self.articulations:
            return self.duration * Fraction(1, 2)
        elif "staccatissimo" in self.articulations:
            return self.duration * Fraction(1, 4)
        elif "tenuto" in self.articulations or "legato" in self.articulations:
            return self.duration  # Full duration
        else:
            # Default slight separation
            return self.duration * Fraction(9, 10)


@dataclass(frozen=True)
class RestEvent(Event):
    """Represents a rest (silence)."""
    duration: Fraction
    
    def end_time(self) -> Fraction:
        """Return the end time of this rest."""
        return self.start_time + self.duration


@dataclass(frozen=True)
class TempoEvent(Event):
    """
    Represents a tempo change.
    
    Attributes:
        bpm: Beats per minute (quarter note = 1 beat)
        beat_unit: The note value that gets one beat (as fraction of whole)
    """
    bpm: int
    beat_unit: Fraction = field(default_factory=lambda: Fraction(1, 4))
    
    def seconds_per_whole_note(self) -> Fraction:
        """Calculate seconds per whole note at this tempo."""
        # bpm is beats per minute where beat = beat_unit
        # beats per whole note = 1 / beat_unit
        # seconds per beat = 60 / bpm
        # seconds per whole note = (1 / beat_unit) * (60 / bpm)
        beats_per_whole = Fraction(1) / self.beat_unit
        seconds_per_beat = Fraction(60, self.bpm)
        return beats_per_whole * seconds_per_beat


@dataclass(frozen=True)
class TimeSignatureEvent(Event):
    """Represents a time signature change."""
    numerator: int
    denominator: int


@dataclass(frozen=True)
class DynamicEvent(Event):
    """
    Represents a dynamic marking.
    
    Affects velocity of subsequent notes until the next dynamic.
    """
    marking: str
    velocity: int
    
    # For hairpins (crescendo/diminuendo)
    is_hairpin: bool = False
    hairpin_duration: Optional[Fraction] = None
    target_velocity: Optional[int] = None


@dataclass(frozen=True)
class PedalEvent(Event):
    """
    Represents a sustain pedal event.
    
    Attributes:
        value: 0 = up, 127 = down
    """
    value: int  # 0-127
    
    @classmethod
    def down(cls, start_time: Fraction, staff_id: str, 
             voice_id: int = 1, channel: int = 0) -> "PedalEvent":
        return cls(
            start_time=start_time,
            staff_id=staff_id,
            voice_id=voice_id,
            value=127,
        )
    
    @classmethod
    def up(cls, start_time: Fraction, staff_id: str,
           voice_id: int = 1, channel: int = 0) -> "PedalEvent":
        return cls(
            start_time=start_time,
            staff_id=staff_id,
            voice_id=voice_id,
            value=0,
        )


@dataclass(frozen=True)
class ProgramChangeEvent(Event):
    """
    Represents an instrument (program) change.
    
    Attributes:
        program: General MIDI program number (0-127)
        channel: MIDI channel (0-15)
    """
    program: int
    channel: int = 0


@dataclass(frozen=True)
class ControlChangeEvent(Event):
    """
    Represents a MIDI control change.
    
    Common controllers:
    - 1: Modulation
    - 7: Volume
    - 10: Pan
    - 11: Expression
    - 64: Sustain pedal
    - 91: Reverb
    - 93: Chorus
    """
    controller: int
    value: int
    channel: int = 0


@dataclass
class EventGraph:
    """
    A time-ordered collection of events representing a score.
    
    The event graph maintains events sorted by time and provides
    methods for playback and MIDI export.
    """
    events: List[Event] = field(default_factory=list)
    
    # Metadata
    initial_tempo: int = 120
    initial_time_signature: tuple = (4, 4)
    
    def add(self, event: Event) -> None:
        """Add an event to the graph."""
        self.events.append(event)
    
    def add_all(self, events: List[Event]) -> None:
        """Add multiple events to the graph."""
        self.events.extend(events)
    
    def sort(self) -> None:
        """Sort events by time."""
        self.events.sort(key=lambda e: (e.start_time, self._event_priority(e)))
    
    def _event_priority(self, event: Event) -> int:
        """Get sorting priority within same time (lower = earlier)."""
        # Tempo and time sig changes should come first
        if isinstance(event, TempoEvent):
            return 0
        elif isinstance(event, TimeSignatureEvent):
            return 1
        elif isinstance(event, ProgramChangeEvent):
            return 2
        elif isinstance(event, DynamicEvent):
            return 3
        elif isinstance(event, PedalEvent):
            return 4
        elif isinstance(event, NoteEvent):
            return 10
        else:
            return 20
    
    def get_duration(self) -> Fraction:
        """Get the total duration of the score in whole notes."""
        max_end = Fraction(0)
        for event in self.events:
            if isinstance(event, NoteEvent):
                end = event.end_time()
                if end > max_end:
                    max_end = end
            elif isinstance(event, RestEvent):
                end = event.end_time()
                if end > max_end:
                    max_end = end
        return max_end
    
    def get_events_in_range(self, start: Fraction, end: Fraction) -> List[Event]:
        """Get all events that start within the given time range."""
        return [e for e in self.events if start <= e.start_time < end]
    
    def get_note_events(self) -> List[NoteEvent]:
        """Get all note events."""
        return [e for e in self.events if isinstance(e, NoteEvent)]
    
    def get_events_for_staff(self, staff_id: str) -> List[Event]:
        """Get all events for a specific staff."""
        return [e for e in self.events if e.staff_id == staff_id]
    
    def __iter__(self):
        """Iterate over events in time order."""
        self.sort()
        return iter(self.events)
    
    def __len__(self):
        return len(self.events)

