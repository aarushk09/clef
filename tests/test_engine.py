"""
Unit tests for the Clef event engine.
"""

import pytest
from fractions import Fraction

from clef.parser import parse
from clef.semantic import analyze
from clef.engine import compile_score
from clef.engine.events import (
    NoteEvent, RestEvent, TempoEvent, PedalEvent,
    ProgramChangeEvent, DynamicEvent,
)


class TestEventCompilation:
    """Test event compilation from AST."""
    
    def test_simple_note_events(self):
        """Test compiling simple notes to events."""
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
        
        note_events = graph.get_note_events()
        assert len(note_events) == 4
        
        # Check timing
        assert note_events[0].start_time == Fraction(0)
        assert note_events[1].start_time == Fraction(1, 4)
        assert note_events[2].start_time == Fraction(2, 4)
        assert note_events[3].start_time == Fraction(3, 4)
    
    def test_note_midi_numbers(self):
        """Test MIDI note number conversion."""
        source = """
        score {
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
        
        note_events = graph.get_note_events()
        assert note_events[0].midi_note == 60  # C4
        assert note_events[1].midi_note == 62  # D4
        assert note_events[2].midi_note == 64  # E4
        assert note_events[3].midi_note == 65  # F4
    
    def test_rest_events(self):
        """Test compiling rests."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 q
                        rest q
                        E4 q
                        rest q
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        rest_events = [e for e in graph.events if isinstance(e, RestEvent)]
        assert len(rest_events) == 2
        assert rest_events[0].start_time == Fraction(1, 4)
        assert rest_events[1].start_time == Fraction(3, 4)


class TestTupletCompilation:
    """Test tuplet event compilation."""
    
    def test_triplet_timing(self):
        """Test that triplets have correct timing."""
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
                        F4 q
                        G4 h
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        note_events = graph.get_note_events()
        
        # Triplet: 3 eighth notes in the time of 2 eighth notes (= 1 quarter)
        # Each triplet note: 1/8 * 2/3 = 1/12
        triplet_duration = Fraction(1, 12)
        
        assert note_events[0].start_time == Fraction(0)
        assert note_events[0].duration == triplet_duration
        
        assert note_events[1].start_time == triplet_duration
        assert note_events[1].duration == triplet_duration
        
        assert note_events[2].start_time == triplet_duration * 2
        assert note_events[2].duration == triplet_duration
        
        # F4 starts after the triplet (1/4 beat)
        assert note_events[3].start_time == Fraction(1, 4)


class TestDynamicsCompilation:
    """Test dynamics event compilation."""
    
    def test_dynamic_velocity(self):
        """Test that dynamics set velocity."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        pp
                        C4 q
                        ff
                        D4 q
                        E4 h
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        note_events = graph.get_note_events()
        
        # First note should have pp velocity
        assert note_events[0].velocity == 33  # pp
        
        # Second and third notes should have ff velocity
        assert note_events[1].velocity == 112  # ff
        assert note_events[2].velocity == 112  # ff


class TestPedalCompilation:
    """Test pedal event compilation."""
    
    def test_pedal_events(self):
        """Test pedal down/up events."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        ped
                        C4 h
                        D4 q
                        E4 q
                        ped_up
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        pedal_events = [e for e in graph.events if isinstance(e, PedalEvent)]
        assert len(pedal_events) == 2
        
        assert pedal_events[0].value == 127  # down
        assert pedal_events[1].value == 0    # up


class TestChordCompilation:
    """Test chord event compilation."""
    
    def test_chord_simultaneous_notes(self):
        """Test that chord notes start at the same time."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        <C4, E4, G4> w
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        note_events = graph.get_note_events()
        assert len(note_events) == 3
        
        # All notes should start at the same time
        assert all(n.start_time == Fraction(0) for n in note_events)
        
        # All notes should have the same duration
        assert all(n.duration == Fraction(1) for n in note_events)
        
        # Check MIDI notes
        midi_notes = sorted(n.midi_note for n in note_events)
        assert midi_notes == [60, 64, 67]  # C4, E4, G4


class TestTieCompilation:
    """Test tie event compilation."""
    
    def test_tied_notes_extend_duration(self):
        """Test that tied notes combine into one longer event."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 h tie
                        C4 h
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        note_events = graph.get_note_events()
        
        # Should be only one note event with combined duration
        assert len(note_events) == 1
        assert note_events[0].duration == Fraction(1)  # h + h = w


class TestInstrumentCompilation:
    """Test instrument event compilation."""
    
    def test_program_change(self):
        """Test program change events."""
        source = """
        score {
            time 4/4
            staff melody : flute {
                voice 1 {
                    measure {
                        C4 w
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        program_events = [e for e in graph.events if isinstance(e, ProgramChangeEvent)]
        assert len(program_events) == 1
        assert program_events[0].program == 73  # Flute


class TestMultipleVoices:
    """Test multiple voice compilation."""
    
    def test_polyphonic_voices(self):
        """Test that multiple voices are compiled correctly."""
        source = """
        score {
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
        
        note_events = graph.get_note_events()
        assert len(note_events) == 2
        
        # Both notes start at the same time
        assert all(n.start_time == Fraction(0) for n in note_events)
        
        # Different voice IDs
        voice_ids = set(n.voice_id for n in note_events)
        assert len(voice_ids) == 2


class TestMultipleStaves:
    """Test multiple staff compilation."""
    
    def test_multiple_instruments(self):
        """Test that multiple staves use different channels."""
        source = """
        score {
            time 4/4
            staff flute : flute {
                voice 1 {
                    measure {
                        C5 w
                    }
                }
            }
            staff violin : violin {
                voice 1 {
                    measure {
                        G4 w
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        note_events = graph.get_note_events()
        assert len(note_events) == 2
        
        # Different channels
        channels = set(n.channel for n in note_events)
        assert len(channels) == 2


class TestArticulationCompilation:
    """Test articulation event compilation."""
    
    def test_staccato_duration(self):
        """Test that staccato reduces effective duration."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 q staccato
                        D4 q
                        E4 h
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        note_events = graph.get_note_events()
        
        # Staccato note should have reduced effective duration
        staccato_note = note_events[0]
        assert "staccato" in staccato_note.articulations
        assert staccato_note.effective_duration() == staccato_note.duration * Fraction(1, 2)


class TestTempoCompilation:
    """Test tempo event compilation."""
    
    def test_tempo_event(self):
        """Test tempo event creation."""
        source = """
        score {
            tempo 120
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 w
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        tempo_events = [e for e in graph.events if isinstance(e, TempoEvent)]
        assert len(tempo_events) == 1
        assert tempo_events[0].bpm == 120
        assert tempo_events[0].start_time == Fraction(0)


class TestEventGraphDuration:
    """Test event graph duration calculation."""
    
    def test_total_duration(self):
        """Test calculating total score duration."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 w
                    }
                    measure {
                        D4 w
                    }
                }
            }
        }
        """
        score = parse(source)
        graph = compile_score(score)
        
        # Two whole notes = 2 whole notes duration
        assert graph.get_duration() == Fraction(2)


class TestEventSorting:
    """Test event sorting."""
    
    def test_events_sorted_by_time(self):
        """Test that events are sorted chronologically."""
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
        graph.sort()
        
        # Check that events are in order
        prev_time = Fraction(-1)
        for event in graph:
            assert event.start_time >= prev_time
            prev_time = event.start_time

