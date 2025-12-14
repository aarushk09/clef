"""
Base class for Clef playback backends.

All playback backends must inherit from this class and implement
the required methods.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from clef.engine.events import EventGraph


class BackendError(Exception):
    """Exception raised by playback backends."""
    pass


class Backend(ABC):
    """
    Abstract base class for playback backends.
    
    Backends are responsible for:
    - Playing back event graphs in real-time
    - Rendering to audio files
    - Exporting to MIDI files
    """
    
    @abstractmethod
    def play(self, graph: EventGraph, blocking: bool = True) -> None:
        """
        Play back an event graph.
        
        Args:
            graph: The event graph to play
            blocking: If True, wait for playback to complete
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop playback immediately."""
        pass
    
    @abstractmethod
    def render(self, graph: EventGraph, output_path: Path,
               format: str = "wav") -> None:
        """
        Render an event graph to an audio file.
        
        Args:
            graph: The event graph to render
            output_path: Path for the output file
            format: Audio format (wav, mp3, etc.)
        """
        pass
    
    @abstractmethod
    def export_midi(self, graph: EventGraph, output_path: Path) -> None:
        """
        Export an event graph to a MIDI file.
        
        Args:
            graph: The event graph to export
            output_path: Path for the output MIDI file
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this backend is available on the system.
        
        Returns:
            True if the backend can be used
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this backend."""
        pass

