"""
MIDI file export backend for Clef.

Exports event graphs to Standard MIDI Files (SMF) for use with
external sequencers, DAWs, or notation software.
"""

from __future__ import annotations
from fractions import Fraction
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from midiutil import MIDIFile

from clef.backends.base import Backend, BackendError
from clef.engine.events import (
    EventGraph,
    Event,
    NoteEvent,
    TempoEvent,
    TimeSignatureEvent,
    PedalEvent,
    ProgramChangeEvent,
    DynamicEvent,
    ControlChangeEvent,
)


class MidiFileBackend(Backend):
    """
    MIDI file export backend.
    
    Exports Clef event graphs to Standard MIDI Files.
    Uses precise timing with high PPQN (pulses per quarter note)
    to maintain accuracy.
    """
    
    # Use high PPQN for precise timing
    PPQN = 960  # Pulses per quarter note
    
    @property
    def name(self) -> str:
        return "MIDI File"
    
    def is_available(self) -> bool:
        """Check if midiutil is available."""
        try:
            from midiutil import MIDIFile
            return True
        except ImportError:
            return False
    
    def play(self, graph: EventGraph, blocking: bool = True) -> None:
        """MIDI backend cannot play directly."""
        raise BackendError(
            "MIDI file backend cannot play audio. "
            "Use FluidSynth backend for playback."
        )
    
    def stop(self) -> None:
        """No playback to stop."""
        pass
    
    def render(self, graph: EventGraph, output_path: Path,
               format: str = "wav") -> None:
        """MIDI backend cannot render audio."""
        raise BackendError(
            "MIDI file backend cannot render audio. "
            "Export to MIDI and use an external tool for audio rendering."
        )
    
    def export_midi(self, graph: EventGraph, output_path: Path) -> None:
        """
        Export an event graph to a MIDI file.
        
        Args:
            graph: The event graph to export
            output_path: Path for the output MIDI file
        """
        # Determine number of tracks (one per staff + one for tempo/time sig)
        staff_ids = set()
        for event in graph.events:
            if event.staff_id != "__global__":
                staff_ids.add(event.staff_id)
        
        num_tracks = len(staff_ids) + 1  # +1 for global track
        
        # Create MIDI file
        midi = MIDIFile(
            numTracks=num_tracks,
            removeDuplicates=True,
            deinterleave=True,
            ticks_per_quarternote=self.PPQN,
        )
        
        # Track mapping
        track_map: Dict[str, int] = {"__global__": 0}
        for i, staff_id in enumerate(sorted(staff_ids), start=1):
            track_map[staff_id] = i
        
        # Set initial tempo (track 0 for global events)
        initial_tempo = graph.initial_tempo
        midi.addTempo(0, 0, initial_tempo)
        
        # Set initial time signature
        num, denom = graph.initial_time_signature
        # MIDI uses log2(denominator) for time signature
        denom_power = {1: 0, 2: 1, 4: 2, 8: 3, 16: 4, 32: 5}.get(denom, 2)
        midi.addTimeSignature(0, 0, num, denom_power, 24, 8)
        
        # Track names
        for staff_id, track in track_map.items():
            if staff_id != "__global__":
                midi.addTrackName(track, 0, staff_id)
        
        # Sort events
        graph.sort()
        
        # Process events
        for event in graph.events:
            track = track_map.get(event.staff_id, 0)
            
            # Convert time from whole notes to beats (quarter notes)
            time_in_beats = float(event.start_time * 4)
            
            if isinstance(event, NoteEvent):
                duration_in_beats = float(event.effective_duration() * 4)
                midi.addNote(
                    track,
                    event.channel,
                    event.midi_note,
                    time_in_beats,
                    duration_in_beats,
                    event.velocity,
                )
            
            elif isinstance(event, TempoEvent):
                midi.addTempo(0, time_in_beats, event.bpm)
            
            elif isinstance(event, TimeSignatureEvent):
                denom_power = {
                    1: 0, 2: 1, 4: 2, 8: 3, 16: 4, 32: 5
                }.get(event.denominator, 2)
                midi.addTimeSignature(
                    0, time_in_beats,
                    event.numerator, denom_power, 24, 8
                )
            
            elif isinstance(event, ProgramChangeEvent):
                midi.addProgramChange(
                    track,
                    event.channel,
                    time_in_beats,
                    event.program,
                )
            
            elif isinstance(event, PedalEvent):
                midi.addControllerEvent(
                    track,
                    0,  # Pedal usually on channel 0
                    time_in_beats,
                    64,  # Sustain pedal
                    event.value,
                )
            
            elif isinstance(event, ControlChangeEvent):
                midi.addControllerEvent(
                    track,
                    event.channel,
                    time_in_beats,
                    event.controller,
                    event.value,
                )
            
            elif isinstance(event, DynamicEvent):
                if event.is_hairpin and event.hairpin_duration and event.target_velocity:
                    # Generate expression curve for hairpin
                    self._add_hairpin(
                        midi, track, 0,
                        time_in_beats,
                        float(event.hairpin_duration * 4),
                        event.velocity,
                        event.target_velocity,
                    )
        
        # Write file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            midi.writeFile(f)
    
    def _add_hairpin(self, midi: MIDIFile, track: int, channel: int,
                    start_time: float, duration: float,
                    start_velocity: int, end_velocity: int) -> None:
        """
        Add a hairpin (crescendo/decrescendo) as expression CC events.
        
        Uses CC 11 (Expression) to create a smooth volume change.
        """
        # Number of steps for smooth transition
        steps = max(8, int(duration * 4))  # At least 8 steps
        step_duration = duration / steps
        velocity_step = (end_velocity - start_velocity) / steps
        
        for i in range(steps + 1):
            time = start_time + (i * step_duration)
            value = int(start_velocity + (i * velocity_step))
            value = max(0, min(127, value))
            
            midi.addControllerEvent(
                track,
                channel,
                time,
                11,  # Expression
                value,
            )

