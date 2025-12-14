"""
Semantic analyzer for the Clef music language.

Validates that parsed scores are musically and structurally correct,
checking measure durations, tie validity, tuplet math, voice alignment,
and other semantic constraints.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional, List, Dict, Set, Tuple, Any

from clef.ast.nodes import (
    Node,
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
    Pitch,
    Duration,
    Tuplet,
    Slur,
    Dynamic,
    Hairpin,
    Articulation,
    Ornament,
    Pedal,
    PedalType,
    InstrumentChange,
    GraceNote,
)


class SemanticError(Exception):
    """Exception raised for semantic validation errors."""
    
    def __init__(self, message: str, location: Optional[Location] = None,
                 context: Optional[str] = None):
        self.message = message
        self.location = location
        self.context = context
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        parts = [self.message]
        if self.location:
            parts.append(f" at {self.location}")
        if self.context:
            parts.append(f"\n  Context: {self.context}")
        return "".join(parts)


@dataclass
class ValidationContext:
    """Context for validation, tracking state during analysis."""
    current_time_signature: TimeSignature = field(
        default_factory=lambda: TimeSignature(numerator=4, denominator=4)
    )
    current_tempo: Optional[TempoMark] = None
    current_key: Optional[KeySignature] = None
    current_staff: Optional[str] = None
    current_voice: Optional[int] = None
    current_measure: Optional[int] = None
    
    # Track tied notes awaiting resolution
    pending_ties: Dict[Tuple[str, int, int], Pitch] = field(default_factory=dict)
    # Key: (staff_name, voice_number, midi_number) -> Pitch
    
    # Track pedal state
    pedal_down: bool = False
    
    # Known instruments for validation
    known_instruments: Set[str] = field(default_factory=lambda: {
        "piano", "acoustic_grand_piano", "bright_acoustic_piano",
        "electric_grand_piano", "honky_tonk_piano", "electric_piano_1",
        "electric_piano_2", "harpsichord", "clavinet",
        "celesta", "glockenspiel", "music_box", "vibraphone",
        "marimba", "xylophone", "tubular_bells", "dulcimer",
        "drawbar_organ", "percussive_organ", "rock_organ", "church_organ",
        "reed_organ", "accordion", "harmonica", "tango_accordion",
        "acoustic_guitar_nylon", "acoustic_guitar_steel", "electric_guitar_jazz",
        "electric_guitar_clean", "electric_guitar_muted", "overdriven_guitar",
        "distortion_guitar", "guitar_harmonics",
        "acoustic_bass", "electric_bass_finger", "electric_bass_pick",
        "fretless_bass", "slap_bass_1", "slap_bass_2", "synth_bass_1", "synth_bass_2",
        "violin", "viola", "cello", "contrabass", "tremolo_strings",
        "pizzicato_strings", "orchestral_harp", "timpani",
        "string_ensemble_1", "string_ensemble_2", "synth_strings_1", "synth_strings_2",
        "choir_aahs", "voice_oohs", "synth_choir", "orchestra_hit",
        "trumpet", "trombone", "tuba", "muted_trumpet", "french_horn",
        "brass_section", "synth_brass_1", "synth_brass_2",
        "soprano_sax", "alto_sax", "tenor_sax", "baritone_sax",
        "oboe", "english_horn", "bassoon", "clarinet",
        "piccolo", "flute", "recorder", "pan_flute", "blown_bottle", "shakuhachi", "whistle", "ocarina",
        "lead_square", "lead_sawtooth", "lead_calliope", "lead_chiff",
        "lead_charang", "lead_voice", "lead_fifths", "lead_bass",
        "pad_new_age", "pad_warm", "pad_polysynth", "pad_choir",
        "pad_bowed", "pad_metallic", "pad_halo", "pad_sweep",
        "fx_rain", "fx_soundtrack", "fx_crystal", "fx_atmosphere",
        "fx_brightness", "fx_goblins", "fx_echoes", "fx_sci_fi",
        "sitar", "banjo", "shamisen", "koto", "kalimba", "bagpipe", "fiddle", "shanai",
        "tinkle_bell", "agogo", "steel_drums", "woodblock", "taiko_drum",
        "melodic_tom", "synth_drum", "reverse_cymbal",
        "guitar_fret_noise", "breath_noise", "seashore", "bird_tweet",
        "telephone_ring", "helicopter", "applause", "gunshot",
        # Common short names
        "strings", "brass", "woodwinds", "organ", "guitar", "bass",
        "drums", "percussion", "synth", "choir", "voice",
    })
    
    errors: List[SemanticError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class SemanticAnalyzer:
    """
    Semantic analyzer for Clef scores.
    
    Validates:
    - Measure durations sum correctly to time signature
    - Ties connect identical pitches
    - Tuplets are mathematically valid
    - Voices align on the timeline
    - Dynamics apply correctly
    - Pedal usage is valid (down before up)
    - Instruments exist in the sound backend
    """
    
    def __init__(self, strict: bool = True):
        """
        Initialize the analyzer.
        
        Args:
            strict: If True, raise errors immediately. If False, collect all errors.
        """
        self.strict = strict
    
    def analyze(self, score: Score) -> ValidationContext:
        """
        Analyze a score for semantic correctness.
        
        Args:
            score: The parsed Score AST
            
        Returns:
            ValidationContext with any errors/warnings
            
        Raises:
            SemanticError: If strict mode and errors found
        """
        ctx = ValidationContext()
        
        # Set initial time signature and tempo from score
        if score.time_signature:
            ctx.current_time_signature = score.time_signature
        if score.tempo:
            ctx.current_tempo = score.tempo
        if score.key_signature:
            ctx.current_key = score.key_signature
        
        # Validate each staff
        for staff in score.staves:
            self._validate_staff(staff, ctx)
        
        # Check for unresolved ties
        if ctx.pending_ties:
            for key, pitch in ctx.pending_ties.items():
                staff_name, voice_num, _ = key
                self._add_error(
                    ctx,
                    f"Unresolved tie on {pitch} in staff '{staff_name}', voice {voice_num}",
                )
        
        if self.strict and ctx.errors:
            raise ctx.errors[0]
        
        return ctx
    
    def _add_error(self, ctx: ValidationContext, message: str,
                   location: Optional[Location] = None) -> None:
        """Add an error to the context."""
        error = SemanticError(message, location)
        ctx.errors.append(error)
        if self.strict:
            raise error
    
    def _add_warning(self, ctx: ValidationContext, message: str) -> None:
        """Add a warning to the context."""
        ctx.warnings.append(message)
    
    def _validate_staff(self, staff: Staff, ctx: ValidationContext) -> None:
        """Validate a staff."""
        ctx.current_staff = staff.name
        
        # Validate instrument if specified
        if staff.instrument:
            self._validate_instrument(staff.instrument, ctx, staff.location)
        
        # Collect voices and direct measures
        voices: List[Voice] = []
        direct_measures: List[Measure] = []
        
        for item in staff.contents:
            if isinstance(item, Voice):
                voices.append(item)
            elif isinstance(item, Measure):
                direct_measures.append(item)
            elif isinstance(item, TimeSignature):
                ctx.current_time_signature = item
            elif isinstance(item, TempoMark):
                ctx.current_tempo = item
            elif isinstance(item, KeySignature):
                ctx.current_key = item
            elif isinstance(item, InstrumentChange):
                self._validate_instrument(item.instrument, ctx, item.location)
        
        # Validate voices
        for voice in voices:
            self._validate_voice(voice, ctx)
        
        # Validate direct measures (as voice 1)
        if direct_measures:
            ctx.current_voice = 1
            for i, measure in enumerate(direct_measures):
                ctx.current_measure = i + 1
                self._validate_measure(measure, ctx)
        
        # Check voice alignment if multiple voices
        if len(voices) > 1:
            self._validate_voice_alignment(voices, ctx)
    
    def _validate_voice(self, voice: Voice, ctx: ValidationContext) -> None:
        """Validate a voice."""
        ctx.current_voice = voice.number
        
        measures: List[Measure] = []
        for item in voice.contents:
            if isinstance(item, Measure):
                measures.append(item)
            elif isinstance(item, TimeSignature):
                ctx.current_time_signature = item
            elif isinstance(item, TempoMark):
                ctx.current_tempo = item
        
        for i, measure in enumerate(measures):
            ctx.current_measure = measure.number or (i + 1)
            self._validate_measure(measure, ctx)
    
    def _validate_measure(self, measure: Measure, ctx: ValidationContext) -> None:
        """Validate a measure's duration and contents."""
        expected_duration = ctx.current_time_signature.beats_per_measure()
        
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
            # Measure contains voice blocks - validate each voice separately
            # but they should all sum to the same total duration
            voice_durations = {}
            saved_voice = ctx.current_voice
            
            for voice_num in sorted(voice_blocks.keys()):
                ctx.current_voice = voice_num
                actual_duration = Fraction(0)
                
                for voice_item in voice_blocks[voice_num]:
                    duration = self._get_item_duration(voice_item, ctx)
                    actual_duration += duration
                    
                    # Validate individual items
                    if isinstance(voice_item, (Note, Chord)):
                        self._validate_note_or_chord(voice_item, ctx)
                    elif isinstance(voice_item, Tuplet):
                        self._validate_tuplet(voice_item, ctx)
                    elif isinstance(voice_item, Slur):
                        self._validate_slur(voice_item, ctx)
                
                voice_durations[voice_num] = actual_duration
            
            # All voices should have the same duration (they're synchronized)
            if voice_durations:
                first_duration = list(voice_durations.values())[0]
                for voice_num, duration in voice_durations.items():
                    if duration != first_duration:
                        measure_num = measure.number or ctx.current_measure
                        self._add_error(
                            ctx,
                            f"Measure {measure_num} in staff '{ctx.current_staff}': "
                            f"voice {voice_num} has duration {duration} but voice {list(voice_durations.keys())[0]} "
                            f"has duration {first_duration} (voices must be synchronized)",
                            measure.location,
                        )
                
                # Check that the synchronized duration matches time signature
                if first_duration != expected_duration:
                    measure_num = measure.number or ctx.current_measure
                    self._add_error(
                        ctx,
                        f"Measure {measure_num} in staff '{ctx.current_staff}' "
                        f"has duration {first_duration} but time signature requires {expected_duration}",
                        measure.location,
                    )
            
            ctx.current_voice = saved_voice
            
            # Validate other content (dynamics, pedal, etc.)
            for item in other_content:
                if isinstance(item, Pedal):
                    self._validate_pedal(item, ctx)
                elif isinstance(item, Dynamic):
                    self._validate_dynamic(item, ctx)
                elif isinstance(item, TimeSignature):
                    ctx.current_time_signature = item
        else:
            # Normal measure - validate sequentially
            actual_duration = Fraction(0)
            
            for item in measure.contents:
                duration = self._get_item_duration(item, ctx)
                actual_duration += duration
                
                # Validate individual items
                if isinstance(item, (Note, Chord)):
                    self._validate_note_or_chord(item, ctx)
                elif isinstance(item, Tuplet):
                    self._validate_tuplet(item, ctx)
                elif isinstance(item, Slur):
                    self._validate_slur(item, ctx)
                elif isinstance(item, Pedal):
                    self._validate_pedal(item, ctx)
                elif isinstance(item, Dynamic):
                    self._validate_dynamic(item, ctx)
                elif isinstance(item, TimeSignature):
                    # Mid-measure time signature change
                    ctx.current_time_signature = item
                    expected_duration = item.beats_per_measure()
            
            # Check measure duration
            if actual_duration != expected_duration:
                measure_num = measure.number or ctx.current_measure
                self._add_error(
                    ctx,
                    f"Measure {measure_num} in staff '{ctx.current_staff}' voice {ctx.current_voice} "
                    f"has duration {actual_duration} but time signature requires {expected_duration}",
                    measure.location,
                )
    
    def _get_item_duration(self, item: Any, ctx: ValidationContext,
                          tuplet_ratio: Fraction = Fraction(1)) -> Fraction:
        """Get the duration of a measure item in whole notes."""
        if isinstance(item, (Note, Chord)):
            return item.duration.total_value() * tuplet_ratio
        elif isinstance(item, Rest):
            return item.duration.total_value() * tuplet_ratio
        elif isinstance(item, Tuplet):
            # Tuplet contents have modified duration
            inner_ratio = item.ratio() * tuplet_ratio
            total = Fraction(0)
            for sub_item in item.contents:
                total += self._get_item_duration(sub_item, ctx, inner_ratio)
            return total
        elif isinstance(item, Slur):
            total = Fraction(0)
            for sub_item in item.contents:
                total += self._get_item_duration(sub_item, ctx, tuplet_ratio)
            return total
        else:
            # Non-durational items (dynamics, pedal, etc.)
            return Fraction(0)
    
    def _validate_note_or_chord(self, item: Any, ctx: ValidationContext) -> None:
        """Validate a note or chord, including tie resolution."""
        pitches = [item.pitch] if isinstance(item, Note) else list(item.pitches)
        
        for pitch in pitches:
            midi = pitch.midi_number()
            key = (ctx.current_staff, ctx.current_voice, midi)
            
            # Check if this resolves a pending tie
            if key in ctx.pending_ties:
                expected_pitch = ctx.pending_ties[key]
                if not pitch.enharmonic_equal(expected_pitch):
                    self._add_error(
                        ctx,
                        f"Tie resolution failed: expected {expected_pitch} but got {pitch}",
                        item.location,
                    )
                del ctx.pending_ties[key]
            
            # If this note is tied, add to pending
            if item.tied:
                ctx.pending_ties[key] = pitch
    
    def _validate_tuplet(self, tuplet: Tuplet, ctx: ValidationContext) -> None:
        """Validate tuplet mathematical correctness."""
        if tuplet.actual <= 0:
            self._add_error(
                ctx,
                f"Tuplet 'actual' count must be positive, got {tuplet.actual}",
                tuplet.location,
            )
        if tuplet.normal <= 0:
            self._add_error(
                ctx,
                f"Tuplet 'normal' count must be positive, got {tuplet.normal}",
                tuplet.location,
            )
        if not tuplet.contents:
            self._add_error(
                ctx,
                "Tuplet cannot be empty",
                tuplet.location,
            )
        
        # Validate contents
        for item in tuplet.contents:
            if isinstance(item, (Note, Chord)):
                self._validate_note_or_chord(item, ctx)
            elif isinstance(item, Tuplet):
                # Nested tuplets
                self._validate_tuplet(item, ctx)
    
    def _validate_slur(self, slur: Slur, ctx: ValidationContext) -> None:
        """Validate slur contents."""
        if not slur.contents:
            self._add_warning(ctx, "Empty slur has no effect")
        
        for item in slur.contents:
            if isinstance(item, (Note, Chord)):
                self._validate_note_or_chord(item, ctx)
            elif isinstance(item, Tuplet):
                self._validate_tuplet(item, ctx)
    
    def _validate_pedal(self, pedal: Pedal, ctx: ValidationContext) -> None:
        """Validate pedal usage."""
        if pedal.type == PedalType.DOWN:
            if ctx.pedal_down:
                self._add_warning(ctx, "Pedal pressed while already down")
            ctx.pedal_down = True
        elif pedal.type == PedalType.UP:
            if not ctx.pedal_down:
                self._add_error(
                    ctx,
                    "Pedal released but was not down",
                    pedal.location,
                )
            ctx.pedal_down = False
        elif pedal.type == PedalType.CHANGE:
            # Pedal change is always valid (implies down after)
            ctx.pedal_down = True
    
    def _validate_dynamic(self, dynamic: Dynamic, ctx: ValidationContext) -> None:
        """Validate dynamic marking."""
        valid_dynamics = {"ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "fp", "sfz", "sf"}
        if dynamic.marking not in valid_dynamics:
            self._add_error(
                ctx,
                f"Unknown dynamic marking: {dynamic.marking}",
                dynamic.location,
            )
    
    def _validate_instrument(self, instrument: str, ctx: ValidationContext,
                            location: Optional[Location] = None) -> None:
        """Validate that an instrument is known."""
        if instrument.lower() not in ctx.known_instruments:
            self._add_warning(
                ctx, 
                f"Unknown instrument '{instrument}' - will use default piano sound"
            )
    
    def _validate_voice_alignment(self, voices: List[Voice], ctx: ValidationContext) -> None:
        """Validate that all voices have the same total duration."""
        voice_durations: Dict[int, Fraction] = {}
        
        for voice in voices:
            ctx.current_voice = voice.number
            total = Fraction(0)
            for item in voice.contents:
                if isinstance(item, Measure):
                    for content in item.contents:
                        total += self._get_item_duration(content, ctx)
            voice_durations[voice.number] = total
        
        # Check all voices have same duration
        durations = list(voice_durations.values())
        if durations and not all(d == durations[0] for d in durations):
            self._add_warning(
                ctx,
                f"Voices have different total durations in staff '{ctx.current_staff}': "
                f"{voice_durations}"
            )


def analyze(score: Score, strict: bool = True) -> ValidationContext:
    """
    Analyze a score for semantic correctness.
    
    This is a convenience function that creates an analyzer and runs it.
    
    Args:
        score: The parsed Score AST
        strict: If True, raise on first error. If False, collect all errors.
        
    Returns:
        ValidationContext with errors and warnings
        
    Raises:
        SemanticError: If strict mode and errors found
    """
    analyzer = SemanticAnalyzer(strict=strict)
    return analyzer.analyze(score)

