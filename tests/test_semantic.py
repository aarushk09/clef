"""
Unit tests for the Clef semantic analyzer.
"""

import pytest
from fractions import Fraction

from clef.parser import parse
from clef.semantic import analyze, SemanticError


class TestMeasureDuration:
    """Test measure duration validation."""
    
    def test_valid_measure_4_4(self):
        """Test a valid 4/4 measure."""
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
        context = analyze(score)
        assert len(context.errors) == 0
    
    def test_invalid_measure_too_short(self):
        """Test a measure that is too short."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 q
                        D4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        with pytest.raises(SemanticError):
            analyze(score)
    
    def test_invalid_measure_too_long(self):
        """Test a measure that is too long."""
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
                        G4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        with pytest.raises(SemanticError):
            analyze(score)
    
    def test_valid_measure_3_4(self):
        """Test a valid 3/4 measure."""
        source = """
        score {
            time 3/4
            staff piano {
                voice 1 {
                    measure {
                        C4 q
                        D4 q
                        E4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        context = analyze(score)
        assert len(context.errors) == 0
    
    def test_valid_dotted_notes(self):
        """Test a measure with dotted notes."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 q.
                        D4 e
                        E4 h
                    }
                }
            }
        }
        """
        score = parse(source)
        context = analyze(score)
        assert len(context.errors) == 0


class TestTupletValidation:
    """Test tuplet validation."""
    
    def test_valid_triplet(self):
        """Test a valid triplet."""
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
        context = analyze(score)
        assert len(context.errors) == 0
    
    def test_valid_quintuplet(self):
        """Test a valid quintuplet."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        tuplet 5 in 4 {
                            C4 e
                            D4 e
                            E4 e
                            F4 e
                            G4 e
                        }
                        A4 h
                    }
                }
            }
        }
        """
        score = parse(source)
        context = analyze(score)
        assert len(context.errors) == 0


class TestTieValidation:
    """Test tie validation."""
    
    def test_valid_tie(self):
        """Test a valid tie between same pitches."""
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
        context = analyze(score)
        assert len(context.errors) == 0
    
    def test_unresolved_tie(self):
        """Test an unresolved tie at end of score."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 w tie
                    }
                }
            }
        }
        """
        score = parse(source)
        with pytest.raises(SemanticError):
            analyze(score)


class TestPedalValidation:
    """Test pedal validation."""
    
    def test_valid_pedal_usage(self):
        """Test valid pedal down then up."""
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
        context = analyze(score)
        assert len(context.errors) == 0
    
    def test_invalid_pedal_up_without_down(self):
        """Test pedal up without prior down."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 w
                        ped_up
                    }
                }
            }
        }
        """
        score = parse(source)
        with pytest.raises(SemanticError):
            analyze(score)


class TestDynamicValidation:
    """Test dynamic validation."""
    
    def test_valid_dynamics(self):
        """Test valid dynamic markings."""
        source = """
        score {
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
        context = analyze(score)
        assert len(context.errors) == 0


class TestInstrumentValidation:
    """Test instrument validation."""
    
    def test_valid_instrument(self):
        """Test valid instrument name."""
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
        context = analyze(score)
        assert len(context.errors) == 0
    
    def test_unknown_instrument_warning(self):
        """Test that unknown instrument generates warning."""
        source = """
        score {
            time 4/4
            staff melody : kazoo {
                voice 1 {
                    measure {
                        C4 w
                    }
                }
            }
        }
        """
        score = parse(source)
        context = analyze(score, strict=False)
        assert len(context.warnings) > 0
        assert "kazoo" in context.warnings[0].lower()


class TestNonStrictMode:
    """Test non-strict validation mode."""
    
    def test_collect_multiple_errors(self):
        """Test that non-strict mode collects all errors."""
        source = """
        score {
            time 4/4
            staff piano {
                voice 1 {
                    measure {
                        C4 q
                    }
                    measure {
                        D4 q
                    }
                }
            }
        }
        """
        score = parse(source)
        context = analyze(score, strict=False)
        # Both measures are wrong (too short)
        assert len(context.errors) == 2

