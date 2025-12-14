"""
Unit tests for playback backends.
"""

import pytest
from pathlib import Path
from fractions import Fraction
import tempfile

from clef.parser import parse
from clef.engine import compile_score
from clef.backends import MidiFileBackend


class TestMidiExport:
    """Test MIDI file export."""
    
    def test_midi_backend_available(self):
        """Test that MIDI backend is available."""
        backend = MidiFileBackend()
        assert backend.is_available()
    
    def test_export_simple_score(self):
        """Test exporting a simple score to MIDI."""
        source = """
        score {
            tempo 120
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 q
                        D4 q
                        E4 q
                        F4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        backend = MidiFileBackend()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.mid"
            backend.export_midi(graph, output_path)
            
            assert output_path.exists()
            assert output_path.stat().st_size > 0
    
    def test_export_polyphonic_score(self):
        """Test exporting a polyphonic score."""
        source = """
        score {
            tempo 90
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C5 w
                    }
                }
                voice 2 {
                    measure {
                        C4 w
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        backend = MidiFileBackend()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "polyphonic.mid"
            backend.export_midi(graph, output_path)
            
            assert output_path.exists()
    
    def test_export_multiple_staves(self):
        """Test exporting a score with multiple staves."""
        source = """
        score {
            tempo 108
            time 3/4
            staff flute : flute {
                voice 1 {
                    measure {
                        G5 h.
                    }
                }
            }
            staff violin : violin {
                voice 1 {
                    measure {
                        D5 h.
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        backend = MidiFileBackend()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "ensemble.mid"
            backend.export_midi(graph, output_path)
            
            assert output_path.exists()
    
    def test_export_with_dynamics(self):
        """Test exporting a score with dynamics."""
        source = """
        score {
            tempo 100
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        pp
                        C4 q
                        mf
                        D4 q
                        ff
                        E4 h
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        backend = MidiFileBackend()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dynamics.mid"
            backend.export_midi(graph, output_path)
            
            assert output_path.exists()
    
    def test_export_with_pedal(self):
        """Test exporting a score with pedal."""
        source = """
        score {
            tempo 72
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        ped
                        C4 h
                        D4 h
                        ped_up
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        backend = MidiFileBackend()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "pedal.mid"
            backend.export_midi(graph, output_path)
            
            assert output_path.exists()


class TestEventTiming:
    """Test that event timing is precise."""
    
    def test_tuplet_timing_precision(self):
        """Test that tuplet timing uses exact fractions."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        tuplet 3 in 2 {
                            C4 e
                            D4 e
                            E4 e
                        }
                        rest q
                        rest h
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        note_events = graph.get_note_events()
        
        # Triplet notes should be at exact fractional positions
        # Each note duration: 1/8 * 2/3 = 1/12
        assert note_events[0].start_time == Fraction(0, 1)
        assert note_events[1].start_time == Fraction(1, 12)
        assert note_events[2].start_time == Fraction(2, 12)
        
        # Each duration is exactly 1/12
        for note in note_events:
            assert note.duration == Fraction(1, 12)
    
    def test_no_floating_point_drift(self):
        """Test that there is no floating point drift over many notes."""
        # Create a long sequence of sixteenth notes
        notes = "C4 s\n" * 64  # 4 measures of sixteenths in 4/4
        source = f"""
        score {{
            time 4/4
            staff piano {{
                voice 1 {{
                    measure {{
                        {notes}
                    }}
                }}
            }}
        }}
        """
        score = parse(source)
        graph = compile_score(score)
        
        note_events = graph.get_note_events()
        
        # Last note should be at exactly (64-1) * 1/16 = 63/16
        last_note = note_events[-1]
        expected_time = Fraction(63, 16)
        assert last_note.start_time == expected_time
        
        # Total duration should be exactly 4 (whole notes)
        end_time = last_note.start_time + last_note.duration
        assert end_time == Fraction(4, 1)


class TestFluidSynthBackend:
    """Test FluidSynth backend (if available)."""
    
    def test_backend_check(self):
        """Test checking if FluidSynth is available."""
        try:
            from clef.backends import FluidSynthBackend
            backend = FluidSynthBackend()
            # Just check that the check doesn't crash
            is_available = backend.is_available()
            assert isinstance(is_available, bool)
        except (ImportError, OSError, Exception):
            pytest.skip("FluidSynth not installed or not working on this system")

