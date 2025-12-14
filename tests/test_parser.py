"""
Unit tests for the Clef parser.
"""

import pytest
from fractions import Fraction

from clef.parser import parse, ClefParseError
from clef.ast.nodes import (
    Score, Staff, Voice, Measure, Note, Rest, Chord,
    Pitch, Duration, Accidental, TimeSignature, TempoMark,
    KeySignature, Dynamic, Tuplet, Slur, Pedal, PedalType,
    Articulation, ArticulationType, Trill,
)


class TestBasicParsing:
    """Test basic parsing functionality."""
    
    def test_empty_score(self):
        """Test parsing an empty score."""
        source = "score { }"
        score = parse(source)
        assert isinstance(score, Score)
        assert len(score.staves) == 0
    
    def test_score_with_tempo(self):
        """Test parsing a score with tempo."""
        source = "score { tempo 120 }"
        score = parse(source)
        assert score.tempo is not None
        assert score.tempo.bpm == 120
    
    def test_score_with_time_signature(self):
        """Test parsing a score with time signature."""
        source = "score { time 3/4 }"
        score = parse(source)
        assert score.time_signature is not None
        assert score.time_signature.numerator == 3
        assert score.time_signature.denominator == 4
    
    def test_score_with_key_signature(self):
        """Test parsing a score with key signature."""
        source = "score { key G major }"
        score = parse(source)
        assert score.key_signature is not None
        assert score.key_signature.root == "G"
        assert score.key_signature.mode == "major"
    
    def test_key_signature_with_accidental(self):
        """Test parsing a key signature with accidental."""
        source = "score { key F# minor }"
        score = parse(source)
        assert score.key_signature.root == "F"
        assert score.key_signature.accidental == Accidental.SHARP
        assert score.key_signature.mode == "minor"


class TestStaffParsing:
    """Test staff parsing."""
    
    def test_single_staff(self):
        """Test parsing a single staff."""
        source = """
        score {
            staff piano {
            }
        }
        """
        score = parse(source)
        assert len(score.staves) == 1
        assert score.staves[0].name == "piano"
    
    def test_staff_with_instrument(self):
        """Test parsing a staff with instrument specification."""
        source = """
        score {
            staff melody : flute {
            }
        }
        """
        score = parse(source)
        assert score.staves[0].name == "melody"
        assert score.staves[0].instrument == "flute"
    
    def test_multiple_staves(self):
        """Test parsing multiple staves."""
        source = """
        score {
            staff violin { }
            staff cello { }
        }
        """
        score = parse(source)
        assert len(score.staves) == 2
        assert score.staves[0].name == "violin"
        assert score.staves[1].name == "cello"


class TestVoiceParsing:
    """Test voice parsing."""
    
    def test_single_voice(self):
        """Test parsing a single voice."""
        source = """
        score {
            staff piano {
                voice 1 {
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        assert len(voices) == 1
        assert voices[0].number == 1
    
    def test_multiple_voices(self):
        """Test parsing multiple voices."""
        source = """
        score {
            staff piano {
                voice 1 { }
                voice 2 { }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        assert len(voices) == 2


class TestNoteParsing:
    """Test note parsing."""
    
    def test_simple_note(self):
        """Test parsing a simple note."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        C4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        notes = [n for n in measures[0].contents if isinstance(n, Note)]
        
        assert len(notes) == 1
        assert notes[0].pitch.name == "C"
        assert notes[0].pitch.octave == 4
        assert notes[0].duration.base_value == Fraction(1, 4)
    
    def test_note_with_accidental(self):
        """Test parsing a note with accidental."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        F#4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        notes = [n for n in measures[0].contents if isinstance(n, Note)]
        
        assert notes[0].pitch.name == "F"
        assert notes[0].pitch.accidental == Accidental.SHARP
    
    def test_dotted_note(self):
        """Test parsing a dotted note."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        C4 q.
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        notes = [n for n in measures[0].contents if isinstance(n, Note)]
        
        assert notes[0].duration.dots == 1
        assert notes[0].duration.total_value() == Fraction(3, 8)
    
    def test_double_dotted_note(self):
        """Test parsing a double dotted note."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        C4 q..
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        notes = [n for n in measures[0].contents if isinstance(n, Note)]
        
        assert notes[0].duration.dots == 2
    
    def test_tied_note(self):
        """Test parsing a tied note."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        C4 h tie
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        notes = [n for n in measures[0].contents if isinstance(n, Note)]
        
        assert notes[0].tied is True


class TestRestParsing:
    """Test rest parsing."""
    
    def test_simple_rest(self):
        """Test parsing a simple rest."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        rest q
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        rests = [r for r in measures[0].contents if isinstance(r, Rest)]
        
        assert len(rests) == 1
        assert rests[0].duration.base_value == Fraction(1, 4)
    
    def test_dotted_rest(self):
        """Test parsing a dotted rest."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        rest q.
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        rests = [r for r in measures[0].contents if isinstance(r, Rest)]
        
        assert rests[0].duration.dots == 1


class TestChordParsing:
    """Test chord parsing."""
    
    def test_simple_chord(self):
        """Test parsing a simple chord."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        <C4, E4, G4> q
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        chords = [c for c in measures[0].contents if isinstance(c, Chord)]
        
        assert len(chords) == 1
        assert len(chords[0].pitches) == 3
        assert chords[0].pitches[0].name == "C"
        assert chords[0].pitches[1].name == "E"
        assert chords[0].pitches[2].name == "G"


class TestTupletParsing:
    """Test tuplet parsing."""
    
    def test_triplet(self):
        """Test parsing a triplet."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        tuplet 3 in 2 {
                            C4 e
                            D4 e
                            E4 e
                        }
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        tuplets = [t for t in measures[0].contents if isinstance(t, Tuplet)]
        
        assert len(tuplets) == 1
        assert tuplets[0].actual == 3
        assert tuplets[0].normal == 2
        assert len(tuplets[0].contents) == 3
    
    def test_quintuplet(self):
        """Test parsing a quintuplet."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        tuplet 5 in 4 {
                            C4 s
                            D4 s
                            E4 s
                            F4 s
                            G4 s
                        }
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        tuplets = [t for t in measures[0].contents if isinstance(t, Tuplet)]
        
        assert tuplets[0].actual == 5
        assert tuplets[0].normal == 4


class TestDynamicParsing:
    """Test dynamic parsing."""
    
    def test_dynamic_markings(self):
        """Test parsing various dynamic markings."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        pp
                        C4 q
                        mf
                        D4 q
                        ff
                        E4 q
                        sfz
                        F4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        dynamics = [d for d in measures[0].contents if isinstance(d, Dynamic)]
        
        assert len(dynamics) == 4
        assert dynamics[0].marking == "pp"
        assert dynamics[1].marking == "mf"
        assert dynamics[2].marking == "ff"
        assert dynamics[3].marking == "sfz"


class TestArticulationParsing:
    """Test articulation parsing."""
    
    def test_staccato(self):
        """Test parsing staccato articulation."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        C4 q staccato
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        notes = [n for n in measures[0].contents if isinstance(n, Note)]
        
        assert len(notes[0].articulations) == 1
        assert notes[0].articulations[0].type == ArticulationType.STACCATO
    
    def test_multiple_articulations(self):
        """Test parsing multiple articulations."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        C4 q accent tenuto
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        notes = [n for n in measures[0].contents if isinstance(n, Note)]
        
        assert len(notes[0].articulations) == 2


class TestPedalParsing:
    """Test pedal parsing."""
    
    def test_pedal_down(self):
        """Test parsing pedal down."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        ped
                        C4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        pedals = [p for p in measures[0].contents if isinstance(p, Pedal)]
        
        assert len(pedals) == 1
        assert pedals[0].type == PedalType.DOWN
    
    def test_pedal_up(self):
        """Test parsing pedal up."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        ped_up
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        pedals = [p for p in measures[0].contents if isinstance(p, Pedal)]
        
        assert pedals[0].type == PedalType.UP


class TestSlurParsing:
    """Test slur parsing."""
    
    def test_slur_group(self):
        """Test parsing a slur group."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        slur {
                            C4 q
                            D4 q
                            E4 q
                        }
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        slurs = [s for s in measures[0].contents if isinstance(s, Slur)]
        
        assert len(slurs) == 1
        assert len(slurs[0].contents) == 3


class TestOrnamentParsing:
    """Test ornament parsing."""
    
    def test_trill(self):
        """Test parsing a trill."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        C4 q trill
                    }
                }
            }
        }
        """
        score = parse(source)
        voices = [v for v in score.staves[0].contents if isinstance(v, Voice)]
        measures = [m for m in voices[0].contents if isinstance(m, Measure)]
        notes = [n for n in measures[0].contents if isinstance(n, Note)]
        
        assert len(notes[0].ornaments) == 1


class TestParseErrors:
    """Test parse error handling."""
    
    def test_missing_brace(self):
        """Test error on missing closing brace."""
        source = "score {"
        with pytest.raises(ClefParseError):
            parse(source)
    
    def test_invalid_duration(self):
        """Test error on invalid duration."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        C4 z
                    }
                }
            }
        }
        """
        with pytest.raises(ClefParseError):
            parse(source)
    
    def test_invalid_pitch(self):
        """Test error on invalid pitch name."""
        source = """
        score {
            staff piano {
                voice 1 {
                    measure {
                        X4 q
                    }
                }
            }
        }
        """
        with pytest.raises(ClefParseError):
            parse(source)


class TestComments:
    """Test comment parsing."""
    
    def test_line_comment(self):
        """Test line comments are ignored."""
        source = """
        // This is a comment
        score {
            // Another comment
            tempo 120
        }
        """
        score = parse(source)
        assert score.tempo.bpm == 120
    
    def test_block_comment(self):
        """Test block comments are ignored."""
        source = """
        /* This is a
           multi-line comment */
        score {
            tempo 120
        }
        """
        score = parse(source)
        assert score.tempo.bpm == 120

