# Clef Language Extension for VS Code

Syntax highlighting and language support for the [Clef](https://github.com/clef-lang/clef) music programming language.

## Features

- **Syntax Highlighting**: Full syntax highlighting for Clef files (`.clef`)
- **Run Score**: Play your score directly from VS Code (Ctrl+Shift+R / Cmd+Shift+R)
- **Validate**: Check your score for errors (Ctrl+Shift+V / Cmd+Shift+V)
- **Build**: Export to MIDI or WAV

## Requirements

- Python 3.10+
- Clef language installed (`pip install clef-lang`)
- For playback: pyfluidsynth and a SoundFont file

## Extension Settings

- `clef.pythonPath`: Path to Python interpreter with Clef installed
- `clef.soundfontPath`: Path to a SoundFont (.sf2) file
- `clef.validateOnSave`: Automatically validate on save (default: true)

## Commands

- **Clef: Run Score** - Play the current score
- **Clef: Validate Score** - Check for errors
- **Clef: Build to MIDI** - Export to MIDI or WAV

## Example

```clef
score {
    tempo 120
    time 4/4

    staff piano : piano {
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
```

## Installation

1. Install the Clef Python package: `pip install clef-lang`
2. Install this extension
3. Open a `.clef` file

## License

MIT

