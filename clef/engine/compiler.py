"""
Event compiler for the Clef music language.

Transforms an AST into a time-aligned event graph for playback.
Uses rational arithmetic throughout to ensure exact timing.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional, List, Dict, Tuple, Set, Any

from clef.ast.nodes import (
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
    Pitch,
    Duration,
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
    GraceNote,
)
from clef.engine.events import (
    Event,
    NoteEvent,
    RestEvent,
    TempoEvent,
    TimeSignatureEvent,
    DynamicEvent,
    PedalEvent,
    ProgramChangeEvent,
    ControlChangeEvent,
    EventGraph,
)


# General MIDI instrument mapping
GM_INSTRUMENTS: Dict[str, int] = {
    # Piano
    "piano": 0,
    "acoustic_grand_piano": 0,
    "bright_acoustic_piano": 1,
    "electric_grand_piano": 2,
    "honky_tonk_piano": 3,
    "electric_piano_1": 4,
    "electric_piano_2": 5,
    "harpsichord": 6,
    "clavinet": 7,
    # Chromatic Percussion
    "celesta": 8,
    "glockenspiel": 9,
    "music_box": 10,
    "vibraphone": 11,
    "marimba": 12,
    "xylophone": 13,
    "tubular_bells": 14,
    "dulcimer": 15,
    # Organ
    "drawbar_organ": 16,
    "percussive_organ": 17,
    "rock_organ": 18,
    "church_organ": 19,
    "organ": 19,
    "reed_organ": 20,
    "accordion": 21,
    "harmonica": 22,
    "tango_accordion": 23,
    # Guitar
    "acoustic_guitar_nylon": 24,
    "acoustic_guitar_steel": 25,
    "electric_guitar_jazz": 26,
    "electric_guitar_clean": 27,
    "electric_guitar_muted": 28,
    "overdriven_guitar": 29,
    "distortion_guitar": 30,
    "guitar_harmonics": 31,
    "guitar": 25,
    # Bass
    "acoustic_bass": 32,
    "electric_bass_finger": 33,
    "electric_bass_pick": 34,
    "fretless_bass": 35,
    "slap_bass_1": 36,
    "slap_bass_2": 37,
    "synth_bass_1": 38,
    "synth_bass_2": 39,
    "bass": 33,
    # Strings
    "violin": 40,
    "viola": 41,
    "cello": 42,
    "contrabass": 43,
    "tremolo_strings": 44,
    "pizzicato_strings": 45,
    "orchestral_harp": 46,
    "timpani": 47,
    # Ensemble
    "string_ensemble_1": 48,
    "string_ensemble_2": 49,
    "synth_strings_1": 50,
    "synth_strings_2": 51,
    "choir_aahs": 52,
    "voice_oohs": 53,
    "synth_choir": 54,
    "orchestra_hit": 55,
    "strings": 48,
    "choir": 52,
    # Brass
    "trumpet": 56,
    "trombone": 57,
    "tuba": 58,
    "muted_trumpet": 59,
    "french_horn": 60,
    "brass_section": 61,
    "synth_brass_1": 62,
    "synth_brass_2": 63,
    "brass": 61,
    # Reed
    "soprano_sax": 64,
    "alto_sax": 65,
    "tenor_sax": 66,
    "baritone_sax": 67,
    "oboe": 68,
    "english_horn": 69,
    "bassoon": 70,
    "clarinet": 71,
    # Pipe
    "piccolo": 72,
    "flute": 73,
    "recorder": 74,
    "pan_flute": 75,
    "blown_bottle": 76,
    "shakuhachi": 77,
    "whistle": 78,
    "ocarina": 79,
    "woodwinds": 73,
    # Synth Lead
    "lead_square": 80,
    "lead_sawtooth": 81,
    "lead_calliope": 82,
    "lead_chiff": 83,
    "lead_charang": 84,
    "lead_voice": 85,
    "lead_fifths": 86,
    "lead_bass": 87,
    "synth": 81,
    # Synth Pad
    "pad_new_age": 88,
    "pad_warm": 89,
    "pad_polysynth": 90,
    "pad_choir": 91,
    "pad_bowed": 92,
    "pad_metallic": 93,
    "pad_halo": 94,
    "pad_sweep": 95,
    # Synth Effects
    "fx_rain": 96,
    "fx_soundtrack": 97,
    "fx_crystal": 98,
    "fx_atmosphere": 99,
    "fx_brightness": 100,
    "fx_goblins": 101,
    "fx_echoes": 102,
    "fx_sci_fi": 103,
    # Ethnic
    "sitar": 104,
    "banjo": 105,
    "shamisen": 106,
    "koto": 107,
    "kalimba": 108,
    "bagpipe": 109,
    "fiddle": 110,
    "shanai": 111,
    # Percussive
    "tinkle_bell": 112,
    "agogo": 113,
    "steel_drums": 114,
    "woodblock": 115,
    "taiko_drum": 116,
    "melodic_tom": 117,
    "synth_drum": 118,
    "reverse_cymbal": 119,
    "drums": 118,
    "percussion": 47,
    # Sound Effects
    "guitar_fret_noise": 120,
    "breath_noise": 121,
    "seashore": 122,
    "bird_tweet": 123,
    "telephone_ring": 124,
    "helicopter": 125,
    "applause": 126,
    "gunshot": 127,
}


@dataclass
class CompilerContext:
    """Context for the event compiler."""
    # Current position in whole notes
    current_time: Fraction = field(default_factory=lambda: Fraction(0))
    
    # Current staff and voice
    staff_id: str = ""
    voice_id: int = 1
    channel: int = 0
    
    # Timing context
    tempo: int = 120
    time_signature: Tuple[int, int] = (4, 4)
    
    # Dynamics
    current_velocity: int = 80
    
    # Ties: maps (staff, voice, midi) -> NoteEvent for pending ties
    pending_ties: Dict[Tuple[str, int, int], NoteEvent] = field(default_factory=dict)
    
    # Channel allocation
    next_channel: int = 0
    staff_channels: Dict[str, int] = field(default_factory=dict)
    
    # Instrument programs per channel
    channel_programs: Dict[int, int] = field(default_factory=dict)


class EventCompiler:
    """
    Compiles a Clef AST into an event graph.
    
    The compiler traverses the AST and generates time-aligned events
    using rational arithmetic to ensure exact timing.
    """
    
    def __init__(self):
        self.ctx: CompilerContext = CompilerContext()
        self.graph: EventGraph = EventGraph()
    
    def compile(self, score: Score) -> EventGraph:
        """
        Compile a score AST into an event graph.
        
        Args:
            score: The validated Score AST
            
        Returns:
            An EventGraph ready for playback
        """
        self.ctx = CompilerContext()
        self.graph = EventGraph()
        
        # Set initial tempo and time signature
        if score.tempo:
            self.ctx.tempo = score.tempo.bpm
            self.graph.initial_tempo = score.tempo.bpm
            self.graph.add(TempoEvent(
                start_time=Fraction(0),
                staff_id="__global__",
                voice_id=0,
                bpm=score.tempo.bpm,
            ))
        
        if score.time_signature:
            self.ctx.time_signature = (
                score.time_signature.numerator,
                score.time_signature.denominator,
            )
            self.graph.initial_time_signature = self.ctx.time_signature
            self.graph.add(TimeSignatureEvent(
                start_time=Fraction(0),
                staff_id="__global__",
                voice_id=0,
                numerator=score.time_signature.numerator,
                denominator=score.time_signature.denominator,
            ))
        
        # Compile each staff
        for staff in score.staves:
            self._compile_staff(staff)
        
        # Sort events by time
        self.graph.sort()
        
        return self.graph
    
    def _allocate_channel(self, staff_id: str) -> int:
        """Allocate a MIDI channel for a staff."""
        if staff_id in self.ctx.staff_channels:
            return self.ctx.staff_channels[staff_id]
        
        channel = self.ctx.next_channel
        # Skip channel 9 (percussion)
        if channel == 9:
            channel = 10
            self.ctx.next_channel = 10
        
        self.ctx.staff_channels[staff_id] = channel
        self.ctx.next_channel = channel + 1
        return channel
    
    def _compile_staff(self, staff: Staff) -> None:
        """Compile a staff into events."""
        self.ctx.staff_id = staff.name
        self.ctx.channel = self._allocate_channel(staff.name)
        self.ctx.current_time = Fraction(0)
        
        # Set instrument if specified
        if staff.instrument:
            program = GM_INSTRUMENTS.get(staff.instrument.lower(), 0)
            self.ctx.channel_programs[self.ctx.channel] = program
            self.graph.add(ProgramChangeEvent(
                start_time=Fraction(0),
                staff_id=staff.name,
                voice_id=0,
                program=program,
                channel=self.ctx.channel,
            ))
        
        # Separate voices from direct measures
        voices: List[Voice] = []
        direct_content: List[Any] = []
        
        for item in staff.contents:
            if isinstance(item, Voice):
                voices.append(item)
            else:
                direct_content.append(item)
        
        # Compile voices
        for voice in voices:
            self._compile_voice(voice)
        
        # Compile direct content as voice 1
        if direct_content:
            self.ctx.voice_id = 1
            self.ctx.current_time = Fraction(0)
            for item in direct_content:
                self._compile_content(item)
    
    def _compile_voice(self, voice: Voice) -> None:
        """Compile a voice into events."""
        self.ctx.voice_id = voice.number
        self.ctx.current_time = Fraction(0)
        
        for item in voice.contents:
            self._compile_content(item)
    
    def _compile_content(self, item: Any, tuplet_ratio: Fraction = Fraction(1)) -> Fraction:
        """
        Compile a content item into events.
        
        Returns the duration consumed.
        """
        if isinstance(item, Measure):
            return self._compile_measure(item)
        elif isinstance(item, Note):
            return self._compile_note(item, tuplet_ratio)
        elif isinstance(item, Chord):
            return self._compile_chord(item, tuplet_ratio)
        elif isinstance(item, Rest):
            return self._compile_rest(item, tuplet_ratio)
        elif isinstance(item, Tuplet):
            return self._compile_tuplet(item, tuplet_ratio)
        elif isinstance(item, Slur):
            return self._compile_slur(item, tuplet_ratio)
        elif isinstance(item, Dynamic):
            return self._compile_dynamic(item)
        elif isinstance(item, Hairpin):
            return self._compile_hairpin(item)
        elif isinstance(item, Pedal):
            return self._compile_pedal(item)
        elif isinstance(item, TempoMark):
            return self._compile_tempo(item)
        elif isinstance(item, TimeSignature):
            return self._compile_time_signature(item)
        elif isinstance(item, InstrumentChange):
            return self._compile_instrument_change(item)
        else:
            return Fraction(0)
    
    def _compile_measure(self, measure: Measure) -> Fraction:
        """Compile a measure into events."""
        start = self.ctx.current_time
        
        # Check if measure contains voice blocks (for synchronized hands)
        voice_blocks = {}
        other_content = []
        
        for item in measure.contents:
            if isinstance(item, tuple) and len(item) == 3 and item[0] == "voice":
                # This is a voice block within the measure
                voice_num = item[1]
                voice_content = item[2]
                if voice_num not in voice_blocks:
                    voice_blocks[voice_num] = []
                voice_blocks[voice_num].append(voice_content)
            else:
                other_content.append(item)
        
        if voice_blocks:
            # Measure contains voice blocks - compile all voices starting at the same time
            measure_start = self.ctx.current_time
            saved_voice_id = self.ctx.voice_id
            
            # Track the end time for each voice
            voice_end_times = {}
            
            # Compile each voice starting from measure_start
            for voice_num in sorted(voice_blocks.keys()):
                self.ctx.voice_id = voice_num
                self.ctx.current_time = measure_start
                voice_start = measure_start
                
                for voice_item in voice_blocks[voice_num]:
                    self._compile_content(voice_item)
                
                voice_end_times[voice_num] = self.ctx.current_time
            
            # Restore voice context
            self.ctx.voice_id = saved_voice_id
            
            # Compile other content (dynamics, pedal, etc.) in the measure at measure_start
            self.ctx.current_time = measure_start
            for item in other_content:
                self._compile_content(item)
            
            # Measure duration is the maximum end time across all voices
            max_end = max(voice_end_times.values()) if voice_end_times else measure_start
            self.ctx.current_time = max_end
            return max_end - measure_start
        else:
            # Normal measure - compile content sequentially
            for item in measure.contents:
                self._compile_content(item)
            return self.ctx.current_time - start
    
    def _compile_note(self, note: Note, tuplet_ratio: Fraction = Fraction(1)) -> Fraction:
        """Compile a note into events."""
        duration = note.duration.total_value() * tuplet_ratio
        midi_note = note.pitch.midi_number()
        
        # Compile grace notes first (they steal time from the main note)
        grace_duration = Fraction(0)
        if note.grace_notes:
            grace_unit = duration * Fraction(1, 8)  # Grace notes take 1/8 of the main note
            for grace in note.grace_notes:
                self.graph.add(NoteEvent(
                    start_time=self.ctx.current_time + grace_duration,
                    staff_id=self.ctx.staff_id,
                    voice_id=self.ctx.voice_id,
                    midi_note=grace.pitch.midi_number(),
                    duration=grace_unit,
                    velocity=self.ctx.current_velocity,
                    channel=self.ctx.channel,
                ))
                grace_duration += grace_unit
        
        # Get articulation flags
        articulation_flags = frozenset(
            art.type.name.lower() for art in note.articulations
        )
        
        # Check for incoming tie
        tie_key = (self.ctx.staff_id, self.ctx.voice_id, midi_note)
        is_tied_from = tie_key in self.ctx.pending_ties
        
        if is_tied_from:
            # Extend the previous note's duration
            prev_event = self.ctx.pending_ties.pop(tie_key)
            # Create a new event with extended duration
            extended = NoteEvent(
                start_time=prev_event.start_time,
                staff_id=prev_event.staff_id,
                voice_id=prev_event.voice_id,
                midi_note=prev_event.midi_note,
                duration=prev_event.duration + duration,
                velocity=prev_event.velocity,
                articulations=prev_event.articulations,
                is_tied_from=prev_event.is_tied_from,
                is_tied_to=note.tied,
                channel=prev_event.channel,
            )
            # Remove old event and add extended
            self.graph.events = [e for e in self.graph.events if e != prev_event]
            self.graph.add(extended)
            
            if note.tied:
                self.ctx.pending_ties[tie_key] = extended
        else:
            # Create new note event
            event = NoteEvent(
                start_time=self.ctx.current_time + grace_duration,
                staff_id=self.ctx.staff_id,
                voice_id=self.ctx.voice_id,
                midi_note=midi_note,
                duration=duration - grace_duration,
                velocity=self.ctx.current_velocity,
                articulations=articulation_flags,
                is_tied_from=False,
                is_tied_to=note.tied,
                channel=self.ctx.channel,
            )
            self.graph.add(event)
            
            if note.tied:
                self.ctx.pending_ties[tie_key] = event
        
        # Handle ornaments (trills, etc.)
        for ornament in note.ornaments:
            self._apply_ornament(ornament, note, duration)
        
        self.ctx.current_time += duration
        return duration
    
    def _compile_chord(self, chord: Chord, tuplet_ratio: Fraction = Fraction(1)) -> Fraction:
        """Compile a chord into events."""
        duration = chord.duration.total_value() * tuplet_ratio
        
        # Get articulation flags
        articulation_flags = frozenset(
            art.type.name.lower() for art in chord.articulations
        )
        
        for pitch in chord.pitches:
            midi_note = pitch.midi_number()
            tie_key = (self.ctx.staff_id, self.ctx.voice_id, midi_note)
            is_tied_from = tie_key in self.ctx.pending_ties
            
            if is_tied_from:
                prev_event = self.ctx.pending_ties.pop(tie_key)
                extended = NoteEvent(
                    start_time=prev_event.start_time,
                    staff_id=prev_event.staff_id,
                    voice_id=prev_event.voice_id,
                    midi_note=prev_event.midi_note,
                    duration=prev_event.duration + duration,
                    velocity=prev_event.velocity,
                    articulations=prev_event.articulations,
                    is_tied_from=prev_event.is_tied_from,
                    is_tied_to=chord.tied,
                    channel=prev_event.channel,
                )
                self.graph.events = [e for e in self.graph.events if e != prev_event]
                self.graph.add(extended)
                
                if chord.tied:
                    self.ctx.pending_ties[tie_key] = extended
            else:
                event = NoteEvent(
                    start_time=self.ctx.current_time,
                    staff_id=self.ctx.staff_id,
                    voice_id=self.ctx.voice_id,
                    midi_note=midi_note,
                    duration=duration,
                    velocity=self.ctx.current_velocity,
                    articulations=articulation_flags,
                    is_tied_from=False,
                    is_tied_to=chord.tied,
                    channel=self.ctx.channel,
                )
                self.graph.add(event)
                
                if chord.tied:
                    self.ctx.pending_ties[tie_key] = event
        
        self.ctx.current_time += duration
        return duration
    
    def _compile_rest(self, rest: Rest, tuplet_ratio: Fraction = Fraction(1)) -> Fraction:
        """Compile a rest into events."""
        duration = rest.duration.total_value() * tuplet_ratio
        
        self.graph.add(RestEvent(
            start_time=self.ctx.current_time,
            staff_id=self.ctx.staff_id,
            voice_id=self.ctx.voice_id,
            duration=duration,
        ))
        
        self.ctx.current_time += duration
        return duration
    
    def _compile_tuplet(self, tuplet: Tuplet, outer_ratio: Fraction = Fraction(1)) -> Fraction:
        """Compile a tuplet into events."""
        # Calculate the inner ratio: actual notes in the time of normal
        inner_ratio = tuplet.ratio() * outer_ratio
        
        total_duration = Fraction(0)
        for item in tuplet.contents:
            total_duration += self._compile_content(item, inner_ratio)
        
        return total_duration
    
    def _compile_slur(self, slur: Slur, tuplet_ratio: Fraction = Fraction(1)) -> Fraction:
        """Compile a slur into events with legato articulation."""
        # Save current velocity to restore after
        total_duration = Fraction(0)
        
        for item in slur.contents:
            duration = self._compile_content(item, tuplet_ratio)
            total_duration += duration
        
        return total_duration
    
    def _compile_dynamic(self, dynamic: Dynamic) -> Fraction:
        """Compile a dynamic marking."""
        self.ctx.current_velocity = dynamic.velocity()
        
        self.graph.add(DynamicEvent(
            start_time=self.ctx.current_time,
            staff_id=self.ctx.staff_id,
            voice_id=self.ctx.voice_id,
            marking=dynamic.marking,
            velocity=dynamic.velocity(),
        ))
        
        return Fraction(0)  # Dynamics don't consume time
    
    def _compile_hairpin(self, hairpin: Hairpin) -> Fraction:
        """Compile a hairpin (crescendo/decrescendo)."""
        # Calculate target velocity based on current
        if hairpin.type == HairpinType.CRESCENDO:
            target = min(127, self.ctx.current_velocity + 30)
        else:  # DECRESCENDO or DIMINUENDO
            target = max(20, self.ctx.current_velocity - 30)
        
        self.graph.add(DynamicEvent(
            start_time=self.ctx.current_time,
            staff_id=self.ctx.staff_id,
            voice_id=self.ctx.voice_id,
            marking=hairpin.type.name.lower(),
            velocity=self.ctx.current_velocity,
            is_hairpin=True,
            hairpin_duration=hairpin.duration,
            target_velocity=target,
        ))
        
        return Fraction(0)  # Hairpins don't consume time by themselves
    
    def _compile_pedal(self, pedal: Pedal) -> Fraction:
        """Compile a pedal event."""
        if pedal.type == PedalType.DOWN:
            self.graph.add(PedalEvent.down(
                start_time=self.ctx.current_time,
                staff_id=self.ctx.staff_id,
                voice_id=self.ctx.voice_id,
            ))
        elif pedal.type == PedalType.UP:
            self.graph.add(PedalEvent.up(
                start_time=self.ctx.current_time,
                staff_id=self.ctx.staff_id,
                voice_id=self.ctx.voice_id,
            ))
        elif pedal.type == PedalType.CHANGE:
            # Pedal change: quick up then down
            self.graph.add(PedalEvent.up(
                start_time=self.ctx.current_time,
                staff_id=self.ctx.staff_id,
                voice_id=self.ctx.voice_id,
            ))
            self.graph.add(PedalEvent.down(
                start_time=self.ctx.current_time,
                staff_id=self.ctx.staff_id,
                voice_id=self.ctx.voice_id,
            ))
        
        return Fraction(0)
    
    def _compile_tempo(self, tempo: TempoMark) -> Fraction:
        """Compile a tempo change."""
        self.ctx.tempo = tempo.bpm
        
        self.graph.add(TempoEvent(
            start_time=self.ctx.current_time,
            staff_id=self.ctx.staff_id,
            voice_id=self.ctx.voice_id,
            bpm=tempo.bpm,
        ))
        
        return Fraction(0)
    
    def _compile_time_signature(self, time_sig: TimeSignature) -> Fraction:
        """Compile a time signature change."""
        self.ctx.time_signature = (time_sig.numerator, time_sig.denominator)
        
        self.graph.add(TimeSignatureEvent(
            start_time=self.ctx.current_time,
            staff_id=self.ctx.staff_id,
            voice_id=self.ctx.voice_id,
            numerator=time_sig.numerator,
            denominator=time_sig.denominator,
        ))
        
        return Fraction(0)
    
    def _compile_instrument_change(self, change: InstrumentChange) -> Fraction:
        """Compile an instrument change."""
        program = GM_INSTRUMENTS.get(change.instrument.lower(), 0)
        self.ctx.channel_programs[self.ctx.channel] = program
        
        self.graph.add(ProgramChangeEvent(
            start_time=self.ctx.current_time,
            staff_id=self.ctx.staff_id,
            voice_id=self.ctx.voice_id,
            program=program,
            channel=self.ctx.channel,
        ))
        
        return Fraction(0)
    
    def _apply_ornament(self, ornament: Ornament, note: Note, 
                       duration: Fraction) -> None:
        """Apply an ornament to a note, generating additional events."""
        if isinstance(ornament, Trill) or ornament.type == OrnamentType.TRILL:
            # Generate trill notes
            trill_note = note.pitch.midi_number() + 2  # Whole step up by default
            if isinstance(ornament, Trill) and ornament.auxiliary_pitch:
                trill_note = ornament.auxiliary_pitch.midi_number()
            
            # Generate alternating notes
            trill_unit = duration / 8  # 8 alternations per beat
            current_pos = self.ctx.current_time - duration  # Go back to start
            main_note = note.pitch.midi_number()
            
            for i in range(8):
                pitch = main_note if i % 2 == 0 else trill_note
                self.graph.add(NoteEvent(
                    start_time=current_pos,
                    staff_id=self.ctx.staff_id,
                    voice_id=self.ctx.voice_id,
                    midi_note=pitch,
                    duration=trill_unit,
                    velocity=self.ctx.current_velocity,
                    channel=self.ctx.channel,
                ))
                current_pos += trill_unit
        
        elif ornament.type == OrnamentType.MORDENT:
            # Quick alternation: main -> upper -> main
            mordent_unit = duration / 8
            main_note = note.pitch.midi_number()
            upper_note = main_note + 2
            
            start = self.ctx.current_time - duration
            # Main note (short)
            self.graph.add(NoteEvent(
                start_time=start,
                staff_id=self.ctx.staff_id,
                voice_id=self.ctx.voice_id,
                midi_note=main_note,
                duration=mordent_unit,
                velocity=self.ctx.current_velocity,
                channel=self.ctx.channel,
            ))
            # Upper note (short)
            self.graph.add(NoteEvent(
                start_time=start + mordent_unit,
                staff_id=self.ctx.staff_id,
                voice_id=self.ctx.voice_id,
                midi_note=upper_note,
                duration=mordent_unit,
                velocity=self.ctx.current_velocity,
                channel=self.ctx.channel,
            ))
            # Main note (remaining)
            # Note: the main note event was already added in _compile_note
        
        elif ornament.type == OrnamentType.TURN:
            # Turn: upper -> main -> lower -> main
            turn_unit = duration / 4
            main_note = note.pitch.midi_number()
            upper_note = main_note + 2
            lower_note = main_note - 2
            
            start = self.ctx.current_time - duration
            notes = [upper_note, main_note, lower_note, main_note]
            for i, pitch in enumerate(notes):
                self.graph.add(NoteEvent(
                    start_time=start + (turn_unit * i),
                    staff_id=self.ctx.staff_id,
                    voice_id=self.ctx.voice_id,
                    midi_note=pitch,
                    duration=turn_unit,
                    velocity=self.ctx.current_velocity,
                    channel=self.ctx.channel,
                ))


def compile_score(score: Score) -> EventGraph:
    """
    Compile a score AST into an event graph.
    
    This is a convenience function that creates a compiler and runs it.
    
    Args:
        score: The validated Score AST
        
    Returns:
        An EventGraph ready for playback
    """
    compiler = EventCompiler()
    return compiler.compile(score)

