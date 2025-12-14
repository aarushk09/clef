# Clef

**A notation-complete music programming language.**

Clef is a real programming language for music notation that can represent 100% of Western sheet music with accurate timing, dynamics, articulation, and polyphony. It uses rational number arithmetic to ensure mathematically exact timing with no floating-point drift.

## Features

### Notation Completeness

- **Notes** with octave and accidentals (C4, F#5, Bb3, etc.)
- **Rests** of any duration
- **Measures** (bars) with validation
- **Time signatures** (4/4, 3/4, 6/8, 5/4, etc.)
- **Tempo changes**
- **Multiple staves** for orchestration
- **Multiple voices** per staff for polyphony
- **Chords** with any number of notes
- **Ties** across bar lines
- **Slurs** for phrasing
- **Tuplets** (triplets, quintuplets, etc.)
- **Dotted notes** and double-dotted notes
- **Dynamics** (ppp → fff, sfz, fp)
- **Crescendo/decrescendo** hairpins
- **Articulations** (staccato, legato, accent, tenuto, marcato, fermata)
- **Ornaments** (grace notes, trills, mordents, turns)
- **Sustain pedal** markings
- **Instrument changes**
- **Key signatures**
- **Exact rhythmic placement** using fractions

### Technical Features

- **Rational timing**: All durations use Python's `Fraction` type—no floating-point drift
- **Formal grammar**: Lark-based parser with complete `.lark` grammar file
- **Full AST**: Immutable, dataclass-based abstract syntax tree
- **Semantic validation**: Measure duration checking, tie validation, tuplet math
- **Event engine**: Time-aligned events for accurate playback
- **FluidSynth backend**: Real instrument sounds via SoundFonts
- **MIDI export**: Standard MIDI file output
- **CLI tool**: Run, build, and validate from the command line
- **VS Code extension**: Syntax highlighting and IDE integration

## Installation

```bash
pip install clef-lang
```

### Dependencies

- Python 3.10+
- [pyfluidsynth](https://github.com/nwhitehead/pyfluidsynth) (for audio playback)
- A SoundFont file (.sf2) for instrument sounds

#### Installing FluidSynth

**macOS:**
```bash
brew install fluid-synth
pip install pyfluidsynth
```

**Ubuntu/Debian:**
```bash
sudo apt-get install fluidsynth libfluidsynth-dev
pip install pyfluidsynth
```

**Windows:**
Download FluidSynth from [GitHub releases](https://github.com/FluidSynth/fluidsynth/releases) and add to PATH.

#### Getting a SoundFont

Download a General MIDI SoundFont:
- [FluidR3_GM.sf2](https://member.keymusician.com/Member/FluidR3_GM/index.html) (recommended)
- [TimGM6mb.sf2](https://packages.debian.org/stable/timgm6mb-soundfont)

Set the path:
```bash
export CLEF_SOUNDFONT=/path/to/FluidR3_GM.sf2
```

## Quick Start

Create a file `hello.clef`:

```clef
score {
    tempo 120
    time 4/4
    key C major

    staff piano : piano {
        voice 1 {
            measure 1 {
                mf
                C4 q
                D4 q
                E4 q
                F4 q
            }
            
            measure 2 {
                G4 h
                E4 q
                C4 q
            }
        }
    }
}
```

Run it:

```bash
clef run hello.clef
```

Build to MIDI:

```bash
clef build hello.clef
```

Validate without playing:

```bash
clef validate hello.clef
```

## Language Reference

### Score Structure

```clef
score {
    tempo 120           // BPM
    time 4/4            // Time signature
    key G major         // Key signature

    staff name : instrument {
        voice 1 {
            measure {
                // notes, rests, dynamics, etc.
            }
        }
    }
}
```

### Notes

```clef
C4 q        // C in octave 4, quarter note
F#5 h       // F sharp in octave 5, half note
Bb3 e       // B flat in octave 3, eighth note
D##4 w      // D double sharp, whole note
Eb4 q.      // E flat, dotted quarter
G4 q..      // G, double dotted quarter
```

#### Duration Values

| Symbol | Duration |
|--------|----------|
| `w` | Whole note |
| `h` | Half note |
| `q` | Quarter note |
| `e` | Eighth note |
| `s` | Sixteenth note |
| `t` | Thirty-second note |
| `x` | Sixty-fourth note |

Add `.` for dotted, `..` for double-dotted.

### Rests

```clef
rest q      // Quarter rest
rest h.     // Dotted half rest
rest w      // Whole rest
```

### Chords

```clef
<C4, E4, G4> q          // C major chord, quarter note
<D4, F4, A4, C5> h      // D minor 7, half note
```

### Ties

```clef
C4 h tie    // Tie to next note
C4 h        // Tied from previous
```

### Tuplets

```clef
tuplet 3 in 2 {         // Triplet: 3 notes in the time of 2
    C4 e
    D4 e
    E4 e
}

tuplet 5 in 4 {         // Quintuplet: 5 notes in the time of 4
    C4 s
    D4 s
    E4 s
    F4 s
    G4 s
}
```

### Slurs

```clef
slur {
    C4 q
    D4 q
    E4 q
}
```

### Dynamics

```clef
ppp         // Pianississimo
pp          // Pianissimo
p           // Piano
mp          // Mezzo-piano
mf          // Mezzo-forte
f           // Forte
ff          // Fortissimo
fff         // Fortississimo
fp          // Forte-piano
sfz         // Sforzando
sf          // Sforzato

cresc over 4    // Crescendo over 4 beats
decresc over 2  // Decrescendo over 2 beats
dim over 8      // Diminuendo over 8 beats
```

### Articulations

```clef
C4 q staccato       // Short, detached
C4 q staccatissimo  // Very short
C4 q legato         // Smooth, connected
C4 q accent         // Emphasized attack
C4 q tenuto         // Full value, slight stress
C4 q marcato        // Strong accent
C4 q fermata        // Hold
```

Multiple articulations:
```clef
C4 q accent staccato
```

### Ornaments

```clef
C4 q trill          // Trill
C4 q trill D4       // Trill with auxiliary note
C4 q mordent        // Mordent
C4 q turn           // Turn
C4 q inverted_turn  // Inverted turn
grace D4 C4 q       // Grace note before C4
```

### Pedal

```clef
ped         // Press sustain pedal
ped_up      // Release pedal
ped_change  // Quick release and press
```

### Voices (Polyphony)

```clef
staff piano : piano {
    voice 1 {
        measure {
            E5 h
            D5 h
        }
    }
    voice 2 {
        measure {
            C4 w
        }
    }
}
```

### Multiple Staves

```clef
score {
    staff flute : flute {
        voice 1 {
            measure { G5 w }
        }
    }
    
    staff violin : violin {
        voice 1 {
            measure { D5 w }
        }
    }
    
    staff cello : cello {
        voice 1 {
            measure { G3 w }
        }
    }
}
```

### Time Signature Changes

```clef
measure 1 {
    time 3/4
    C4 q
    D4 q
    E4 q
}

measure 2 {
    time 4/4
    F4 q
    G4 q
    A4 q
    B4 q
}
```

### Instrument Changes

```clef
staff melody : flute {
    voice 1 {
        measure 1 {
            G5 w
        }
        instrument clarinet
        measure 2 {
            G5 w
        }
    }
}
```

### Comments

```clef
// Line comment

/* Block
   comment */
```

## CLI Reference

### Run a Score

```bash
clef run score.clef
clef run score.clef --soundfont ~/soundfonts/piano.sf2
```

### Build to MIDI/WAV

```bash
clef build score.clef                  # Output: score.mid
clef build score.clef -o output.mid    # Custom output path
clef build score.clef -f wav           # Render to WAV
```

### Validate

```bash
clef validate score.clef
clef validate score.clef --no-strict   # Show all errors
clef validate score.clef --show-ast    # Debug: show AST
```

### System Info

```bash
clef info
```

### Debug: Show Events

```bash
clef events score.clef
```

## VS Code Extension

Install the Clef extension for Visual Studio Code:

1. Copy the `vscode-extension` folder to your VS Code extensions directory
2. Or run `vsce package` and install the .vsix file

Features:
- Syntax highlighting
- Run score with Ctrl+Shift+R (Cmd+Shift+R on macOS)
- Validate with Ctrl+Shift+V (Cmd+Shift+V on macOS)
- Build to MIDI

## API Usage

```python
from clef import parse, analyze, compile_score
from clef.backends import FluidSynthBackend

# Parse source code
source = """
score {
    tempo 120
    time 4/4
    staff piano : piano {
        voice 1 {
            measure { C4 q D4 q E4 q F4 q }
        }
    }
}
"""

# Parse to AST
score = parse(source)

# Validate
context = analyze(score)

# Compile to events
graph = compile_score(score)

# Play
backend = FluidSynthBackend()
backend.play(graph)

# Or export to MIDI
from clef.backends import MidiFileBackend
midi = MidiFileBackend()
midi.export_midi(graph, "output.mid")
```

## Architecture

```
clef/
├── clef/
│   ├── parser/          # Lark-based parser
│   │   ├── parser.py    # Parser and transformer
│   │   └── __init__.py
│   ├── ast/             # AST node definitions
│   │   ├── nodes.py     # All AST nodes
│   │   └── __init__.py
│   ├── semantic/        # Semantic analysis
│   │   ├── analyzer.py  # Validation logic
│   │   └── __init__.py
│   ├── engine/          # Event compilation
│   │   ├── events.py    # Event definitions
│   │   ├── compiler.py  # AST → Events
│   │   └── __init__.py
│   ├── backends/        # Playback backends
│   │   ├── base.py      # Backend interface
│   │   ├── fluidsynth_backend.py
│   │   ├── midi_backend.py
│   │   └── __init__.py
│   ├── cli.py           # Command-line interface
│   ├── grammar.lark     # Formal grammar
│   └── __init__.py
├── vscode-extension/    # VS Code support
├── examples/            # Example scores
├── tests/               # Unit tests
├── pyproject.toml       # Package configuration
└── README.md
```

## Testing

```bash
pip install -e ".[dev]"
pytest tests/
```

## Examples

See the `examples/` directory:

- `simple_melody.clef` - Basic notes and rests
- `polyphony.clef` - Multiple voices
- `tuplets.clef` - Triplets and quintuplets
- `dynamics_and_articulation.clef` - All dynamics and articulations
- `ties_and_slurs.clef` - Tied notes and slurred phrases
- `chords.clef` - Chord notation
- `grace_notes_and_ornaments.clef` - Ornaments
- `pedal.clef` - Sustain pedal usage
- `multiple_staves.clef` - Orchestration
- `time_signature_changes.clef` - Meter changes
- `fur_elise_excerpt.clef` - Real music example

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass
2. Code follows existing style
3. New features include tests
4. Documentation is updated

## License

MIT License

## Acknowledgments

- [Lark](https://github.com/lark-parser/lark) - Parsing library
- [FluidSynth](https://www.fluidsynth.org/) - Software synthesizer
- [MIDIUtil](https://github.com/MarkCWirt/MIDIUtil) - MIDI file library

