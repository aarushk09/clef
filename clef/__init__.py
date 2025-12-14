"""
Clef - A notation-complete music programming language.

Clef can represent 100% of Western sheet music with accurate timing,
dynamics, articulation, and polyphony, using rational number timing.
"""

__version__ = "0.1.0"
__author__ = "Clef Contributors"

from clef.parser.parser import parse
from clef.semantic.analyzer import analyze
from clef.engine.compiler import compile_score
from clef.backends.fluidsynth_backend import FluidSynthBackend

__all__ = [
    "parse",
    "analyze", 
    "compile_score",
    "FluidSynthBackend",
    "__version__",
]

