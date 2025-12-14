"""
FluidSynth playback backend for Clef.

Uses FluidSynth with SoundFonts for high-quality audio playback.
Supports General MIDI instruments, velocity-based dynamics,
sustain pedal, and accurate timing.
"""

from __future__ import annotations
import os
import time
import threading
from fractions import Fraction
from pathlib import Path
from typing import Optional, List, Dict, Any

from clef.backends.base import Backend, BackendError
from clef.engine.events import (
    EventGraph,
    Event,
    NoteEvent,
    TempoEvent,
    PedalEvent,
    ProgramChangeEvent,
    DynamicEvent,
    ControlChangeEvent,
)


class FluidSynthBackend(Backend):
    """
    FluidSynth-based playback backend.
    
    Features:
    - Real-time audio synthesis
    - SoundFont support (.sf2)
    - General MIDI program changes
    - Velocity-based dynamics
    - Sustain pedal (CC 64)
    - Expression control (CC 11)
    - Legato via note overlap
    - WAV rendering
    - MIDI export
    """
    
    def __init__(self, soundfont_path: Optional[str] = None):
        """
        Initialize the FluidSynth backend.
        
        Args:
            soundfont_path: Path to a SoundFont file. If None, attempts
                          to find a default system SoundFont.
        """
        self._synth = None
        self._soundfont_path = soundfont_path
        self._soundfont_id: Optional[int] = None
        self._playing = False
        self._play_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_tempo: int = 120
        
        # Track active notes for proper note-off
        self._active_notes: Dict[int, List[int]] = {}  # channel -> [notes]
    
    @property
    def name(self) -> str:
        return "FluidSynth"
    
    def is_available(self) -> bool:
        """Check if FluidSynth is available."""
        try:
            import fluidsynth
            # Try to create a synth to verify it actually works
            synth = fluidsynth.Synth()
            synth.delete()
            return True
        except (ImportError, OSError, Exception):
            return False
    
    def _find_soundfont(self) -> Optional[str]:
        """Find a SoundFont on the system."""
        # Common SoundFont locations
        search_paths = [
            # User-specified
            self._soundfont_path,
            # Environment variable
            os.environ.get("CLEF_SOUNDFONT"),
            # Linux
            "/usr/share/sounds/sf2/FluidR3_GM.sf2",
            "/usr/share/soundfonts/FluidR3_GM.sf2",
            "/usr/share/sounds/sf2/default.sf2",
            "/usr/share/soundfonts/default.sf2",
            "/usr/share/sounds/sf2/TimGM6mb.sf2",
            # macOS (Homebrew)
            "/usr/local/share/fluidsynth/FluidR3_GM.sf2",
            "/opt/homebrew/share/fluidsynth/FluidR3_GM.sf2",
            # Windows
            "C:/soundfonts/FluidR3_GM.sf2",
            "C:/Program Files/FluidSynth/share/soundfonts/FluidR3_GM.sf2",
            # Home directory
            Path.home() / ".local/share/soundfonts/FluidR3_GM.sf2",
            Path.home() / "soundfonts/FluidR3_GM.sf2",
        ]
        
        for path in search_paths:
            if path and Path(path).exists():
                return str(path)
        
        return None
    
    def _initialize(self) -> None:
        """Initialize the FluidSynth synthesizer."""
        if self._synth is not None:
            return
        
        try:
            import fluidsynth
        except ImportError:
            raise BackendError(
                "FluidSynth is not installed. "
                "Install with: pip install pyfluidsynth"
            )
        
        # Find SoundFont
        soundfont = self._find_soundfont()
        if not soundfont:
            raise BackendError(
                "No SoundFont found. Please install a SoundFont or set "
                "CLEF_SOUNDFONT environment variable to the path of a .sf2 file.\n"
                "You can download FluidR3_GM.sf2 from:\n"
                "https://member.keymusician.com/Member/FluidR3_GM/index.html"
            )
        
        # Create synth
        self._synth = fluidsynth.Synth()
        self._synth.start()
        
        # Load SoundFont
        self._soundfont_id = self._synth.sfload(soundfont)
        if self._soundfont_id < 0:
            raise BackendError(f"Failed to load SoundFont: {soundfont}")
        
        # Select default program for all channels
        for channel in range(16):
            self._synth.program_select(channel, self._soundfont_id, 0, 0)
            self._active_notes[channel] = []
    
    def _shutdown(self) -> None:
        """Shutdown the synthesizer."""
        if self._synth is not None:
            # Stop all notes
            for channel, notes in self._active_notes.items():
                for note in notes:
                    self._synth.noteoff(channel, note)
            
            self._synth.delete()
            self._synth = None
    
    def play(self, graph: EventGraph, blocking: bool = True) -> None:
        """
        Play back an event graph.
        
        Args:
            graph: The event graph to play
            blocking: If True, wait for playback to complete
        """
        self._initialize()
        self._stop_event.clear()
        
        if blocking:
            self._play_events(graph)
        else:
            self._play_thread = threading.Thread(
                target=self._play_events,
                args=(graph,),
                daemon=True,
            )
            self._play_thread.start()
    
    def _play_events(self, graph: EventGraph) -> None:
        """Play events in real-time."""
        self._playing = True
        self._current_tempo = graph.initial_tempo
        
        # Sort and prepare events
        graph.sort()
        
        # Convert events to absolute time in seconds
        timed_events = self._convert_to_seconds(graph)
        
        if not timed_events:
            self._playing = False
            return
        
        # Play events
        start_real_time = time.perf_counter()
        
        for event_time, event in timed_events:
            if self._stop_event.is_set():
                break
            
            # Wait until event time
            current_time = time.perf_counter() - start_real_time
            wait_time = float(event_time) - current_time
            if wait_time > 0:
                # Use small sleep intervals to allow stopping
                while wait_time > 0 and not self._stop_event.is_set():
                    time.sleep(min(wait_time, 0.01))
                    current_time = time.perf_counter() - start_real_time
                    wait_time = float(event_time) - current_time
            
            if self._stop_event.is_set():
                break
            
            # Process event
            self._process_event(event)
        
        # Wait for final notes to finish
        if not self._stop_event.is_set():
            time.sleep(0.5)
        
        self._playing = False
    
    def _convert_to_seconds(self, graph: EventGraph) -> List[tuple]:
        """Convert event times from whole notes to seconds."""
        events_with_time = []
        tempo = graph.initial_tempo
        last_tempo_time = Fraction(0)
        last_real_time = Fraction(0)
        
        # First, collect tempo changes
        tempo_changes = []
        for event in graph.events:
            if isinstance(event, TempoEvent):
                tempo_changes.append((event.start_time, event.bpm))
        tempo_changes.sort()
        
        def get_tempo_at(time: Fraction) -> int:
            """Get the tempo at a given time."""
            current_tempo = graph.initial_tempo
            for t, bpm in tempo_changes:
                if t <= time:
                    current_tempo = bpm
                else:
                    break
            return current_tempo
        
        def time_to_seconds(t: Fraction) -> Fraction:
            """Convert time in whole notes to seconds."""
            result = Fraction(0)
            prev_time = Fraction(0)
            prev_tempo = graph.initial_tempo
            
            for change_time, new_tempo in tempo_changes:
                if change_time >= t:
                    break
                # Add time before this tempo change
                duration = change_time - prev_time
                seconds_per_whole = Fraction(240, prev_tempo)  # 4 beats per whole, 60/bpm per beat
                result += duration * seconds_per_whole
                prev_time = change_time
                prev_tempo = new_tempo
            
            # Add remaining time
            duration = t - prev_time
            seconds_per_whole = Fraction(240, prev_tempo)
            result += duration * seconds_per_whole
            
            return result
        
        # Process all events
        for event in graph.events:
            event_time_seconds = time_to_seconds(event.start_time)
            
            if isinstance(event, NoteEvent):
                # Add note on
                events_with_time.append((event_time_seconds, ("note_on", event)))
                
                # Add note off
                end_time = event.start_time + event.effective_duration()
                end_time_seconds = time_to_seconds(end_time)
                events_with_time.append((end_time_seconds, ("note_off", event)))
            else:
                events_with_time.append((event_time_seconds, ("other", event)))
        
        # Sort by time
        events_with_time.sort(key=lambda x: x[0])
        
        return events_with_time
    
    def _process_event(self, event_data: tuple) -> None:
        """Process a single event."""
        event_type, event = event_data
        
        if event_type == "note_on" and isinstance(event, NoteEvent):
            self._synth.noteon(event.channel, event.midi_note, event.velocity)
            self._active_notes[event.channel].append(event.midi_note)
        
        elif event_type == "note_off" and isinstance(event, NoteEvent):
            self._synth.noteoff(event.channel, event.midi_note)
            if event.midi_note in self._active_notes[event.channel]:
                self._active_notes[event.channel].remove(event.midi_note)
        
        elif isinstance(event, ProgramChangeEvent):
            self._synth.program_select(
                event.channel, 
                self._soundfont_id, 
                0,  # bank
                event.program
            )
        
        elif isinstance(event, PedalEvent):
            self._synth.cc(event.channel, 64, event.value)
        
        elif isinstance(event, ControlChangeEvent):
            self._synth.cc(event.channel, event.controller, event.value)
        
        elif isinstance(event, TempoEvent):
            self._current_tempo = event.bpm
    
    def stop(self) -> None:
        """Stop playback immediately."""
        self._stop_event.set()
        
        if self._synth is not None:
            # Stop all notes immediately
            for channel, notes in self._active_notes.items():
                for note in list(notes):
                    self._synth.noteoff(channel, note)
                self._active_notes[channel] = []
        
        if self._play_thread is not None:
            self._play_thread.join(timeout=1.0)
            self._play_thread = None
    
    def render(self, graph: EventGraph, output_path: Path,
               format: str = "wav") -> None:
        """
        Render an event graph to an audio file.
        
        Note: This requires FluidSynth to be compiled with audio file support.
        For a simpler approach, we can use MIDI export + external conversion.
        """
        try:
            import fluidsynth
        except ImportError:
            raise BackendError("FluidSynth is not installed")
        
        soundfont = self._find_soundfont()
        if not soundfont:
            raise BackendError("No SoundFont found")
        
        # Create offline synth for rendering
        synth = fluidsynth.Synth()
        
        # FluidSynth settings for file rendering
        # This is a simplified approach - full implementation would use
        # FluidSynth's sequencer with file renderer
        
        # For now, we'll export to MIDI and recommend external conversion
        midi_path = output_path.with_suffix(".mid")
        self.export_midi(graph, midi_path)
        
        # Try to use fluidsynth command line if available
        import subprocess
        try:
            result = subprocess.run(
                [
                    "fluidsynth",
                    "-ni",  # No interactive mode
                    "-g", "1.0",  # Gain
                    "-o", f"audio.file.name={output_path}",
                    "-o", "audio.file.type=" + format,
                    "-F", str(output_path),
                    soundfont,
                    str(midi_path),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise BackendError(
                    f"FluidSynth rendering failed: {result.stderr}\n"
                    f"MIDI file saved to: {midi_path}"
                )
        except FileNotFoundError:
            raise BackendError(
                f"FluidSynth command-line tool not found.\n"
                f"MIDI file saved to: {midi_path}\n"
                f"Use an external tool to convert MIDI to {format}."
            )
    
    def export_midi(self, graph: EventGraph, output_path: Path) -> None:
        """Export an event graph to a MIDI file."""
        from clef.backends.midi_backend import MidiFileBackend
        
        midi_backend = MidiFileBackend()
        midi_backend.export_midi(graph, output_path)
    
    def __del__(self):
        """Cleanup on deletion."""
        self._shutdown()

