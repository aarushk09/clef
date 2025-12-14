"""
Command-line interface for the Clef music language.

Usage:
    clef run score.clef        # Play a score
    clef build score.clef      # Build to MIDI/audio
    clef validate score.clef   # Validate a score
    clef info                  # Show system info
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from clef import __version__
from clef.parser import parse, ClefParseError
from clef.semantic import analyze, SemanticError
from clef.engine import compile_score


console = Console()
error_console = Console(stderr=True)


def print_error(title: str, message: str, context: Optional[str] = None) -> None:
    """Print a formatted error message."""
    error_text = f"[bold red]{title}[/bold red]\n{message}"
    if context:
        error_text += f"\n\n[dim]{context}[/dim]"
    error_console.print(Panel(error_text, border_style="red", title="Error"))


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]OK[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def load_and_validate(source_path: Path, strict: bool = True):
    """
    Load, parse, and validate a Clef source file.
    
    Returns:
        Tuple of (score, context) if successful, raises exception otherwise
    """
    if not source_path.exists():
        raise FileNotFoundError(f"File not found: {source_path}")
    
    source = source_path.read_text(encoding="utf-8")
    
    # Parse
    try:
        score = parse(source, filename=str(source_path))
    except ClefParseError as e:
        raise e
    
    # Validate
    try:
        context = analyze(score, strict=strict)
    except SemanticError as e:
        raise e
    
    return score, context


@click.group()
@click.version_option(version=__version__, prog_name="clef")
def main():
    """
    Clef - A notation-complete music programming language.
    
    Clef can represent and play back any Western sheet music with
    accurate timing, dynamics, articulation, and polyphony.
    """
    pass


@main.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option("--soundfont", "-sf", type=click.Path(exists=True),
              help="Path to a SoundFont (.sf2) file")
@click.option("--no-validate", is_flag=True,
              help="Skip semantic validation")
def run(source: Path, soundfont: Optional[str], no_validate: bool):
    """
    Play a Clef score.
    
    Example:
        clef run myscore.clef
        clef run myscore.clef --soundfont ~/soundfonts/piano.sf2
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            # Load and validate
            task = progress.add_task("Loading score...", total=None)
            score, context = load_and_validate(source, strict=not no_validate)
            
            # Show warnings
            for warning in context.warnings:
                print_warning(warning)
            
            # Compile
            progress.update(task, description="Compiling events...")
            graph = compile_score(score)
            
            # Initialize backend
            progress.update(task, description="Initializing audio...")
            from clef.backends import FluidSynthBackend
            backend = FluidSynthBackend(soundfont_path=soundfont)
            
            if not backend.is_available():
                print_error(
                    "FluidSynth not available",
                    "Please install pyfluidsynth:\n  pip install pyfluidsynth"
                )
                sys.exit(1)
        
        # Play
        console.print(f"\n[bold]Playing:[/bold] {source.name}")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        try:
            backend.play(graph, blocking=True)
            print_success("Playback complete")
        except KeyboardInterrupt:
            backend.stop()
            console.print("\n[yellow]Playback stopped[/yellow]")
    
    except ClefParseError as e:
        print_error("Parse Error", e.message, e.context)
        sys.exit(1)
    except SemanticError as e:
        print_error("Semantic Error", e.message, e.context)
        sys.exit(1)
    except Exception as e:
        print_error("Error", str(e))
        sys.exit(1)


@main.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path),
              help="Output file path")
@click.option("--format", "-f", type=click.Choice(["midi", "wav"]),
              default="midi", help="Output format (default: midi)")
@click.option("--soundfont", "-sf", type=click.Path(exists=True),
              help="Path to a SoundFont (.sf2) file (for WAV output)")
@click.option("--no-validate", is_flag=True,
              help="Skip semantic validation")
def build(source: Path, output: Optional[Path], format: str,
          soundfont: Optional[str], no_validate: bool):
    """
    Build a Clef score to MIDI or audio.
    
    Examples:
        clef build myscore.clef                    # Output: myscore.mid
        clef build myscore.clef -o output.mid     # Custom output path
        clef build myscore.clef -f wav            # Render to WAV
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            # Load and validate
            task = progress.add_task("Loading score...", total=None)
            score, context = load_and_validate(source, strict=not no_validate)
            
            # Show warnings
            for warning in context.warnings:
                print_warning(warning)
            
            # Compile
            progress.update(task, description="Compiling events...")
            graph = compile_score(score)
            
            # Determine output path
            if output is None:
                suffix = ".mid" if format == "midi" else f".{format}"
                output = source.with_suffix(suffix)
            
            # Export
            progress.update(task, description=f"Exporting to {format.upper()}...")
            
            if format == "midi":
                from clef.backends import MidiFileBackend
                backend = MidiFileBackend()
                backend.export_midi(graph, output)
            else:
                from clef.backends import FluidSynthBackend
                backend = FluidSynthBackend(soundfont_path=soundfont)
                backend.render(graph, output, format=format)
        
        print_success(f"Built: {output}")
    
    except ClefParseError as e:
        print_error("Parse Error", e.message, e.context)
        sys.exit(1)
    except SemanticError as e:
        print_error("Semantic Error", e.message, e.context)
        sys.exit(1)
    except Exception as e:
        print_error("Error", str(e))
        sys.exit(1)


@main.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option("--strict/--no-strict", default=True,
              help="Stop on first error vs collect all errors")
@click.option("--show-ast", is_flag=True,
              help="Show the parsed AST")
def validate(source: Path, strict: bool, show_ast: bool):
    """
    Validate a Clef score without playing.
    
    Checks for:
    - Syntax errors
    - Measure duration correctness
    - Tie validity
    - Tuplet math
    - Voice alignment
    - Pedal usage
    - Instrument validity
    
    Examples:
        clef validate myscore.clef
        clef validate myscore.clef --no-strict  # Show all errors
        clef validate myscore.clef --show-ast   # Debug output
    """
    try:
        source_text = source.read_text(encoding="utf-8")
        
        # Parse
        try:
            score = parse(source_text, filename=str(source))
        except ClefParseError as e:
            print_error("Parse Error", e.message, e.context)
            sys.exit(1)
        
        if show_ast:
            console.print("\n[bold]Abstract Syntax Tree:[/bold]")
            console.print(score)
            console.print()
        
        # Validate
        try:
            context = analyze(score, strict=strict)
        except SemanticError as e:
            print_error("Semantic Error", e.message, e.context)
            sys.exit(1)
        
        # Show results
        if context.errors:
            console.print(f"\n[red]Found {len(context.errors)} error(s):[/red]")
            for error in context.errors:
                console.print(f"  • {error.message}")
            sys.exit(1)
        
        if context.warnings:
            console.print(f"\n[yellow]Warnings ({len(context.warnings)}):[/yellow]")
            for warning in context.warnings:
                console.print(f"  • {warning}")
        
        # Success summary
        table = Table(title=f"Validation: {source.name}", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value")
        
        table.add_row("Staves", str(len(score.staves)))
        
        total_measures = 0
        for staff in score.staves:
            for item in staff.contents:
                if hasattr(item, 'contents'):
                    for sub in item.contents:
                        if hasattr(sub, '__class__') and sub.__class__.__name__ == 'Measure':
                            total_measures += 1
        table.add_row("Measures", str(total_measures) if total_measures else "N/A")
        
        if score.tempo:
            table.add_row("Tempo", f"{score.tempo.bpm} BPM")
        if score.time_signature:
            table.add_row("Time Signature", str(score.time_signature))
        if score.key_signature:
            table.add_row("Key", str(score.key_signature))
        
        console.print()
        console.print(table)
        print_success("Validation passed!")
    
    except FileNotFoundError:
        print_error("File Not Found", f"Cannot find: {source}")
        sys.exit(1)
    except Exception as e:
        print_error("Unexpected Error", str(e))
        sys.exit(1)


@main.command()
def info():
    """
    Show system information and available backends.
    """
    table = Table(title="Clef System Information")
    table.add_column("Component", style="cyan")
    table.add_column("Status")
    table.add_column("Details")
    
    # Version
    table.add_row("Clef Version", __version__, "")
    
    # Python
    import platform
    table.add_row(
        "Python",
        f"{platform.python_version()}",
        platform.platform()
    )
    
    # FluidSynth
    try:
        import fluidsynth
        table.add_row(
            "FluidSynth",
            "[green]Available[/green]",
            "pyfluidsynth installed"
        )
    except (ImportError, OSError, Exception) as e:
        table.add_row(
            "FluidSynth",
            "[red]Not Available[/red]",
            f"pip install pyfluidsynth ({type(e).__name__})"
        )
    
    # MidiUtil
    try:
        import midiutil
        table.add_row(
            "MIDI Export",
            "[green]Available[/green]",
            "midiutil installed"
        )
    except ImportError:
        table.add_row(
            "MIDI Export",
            "[red]Not Available[/red]",
            "pip install midiutil"
        )
    
    # SoundFont
    try:
        from clef.backends.fluidsynth_backend import FluidSynthBackend
        backend = FluidSynthBackend()
        sf_path = backend._find_soundfont()
        if sf_path:
            table.add_row(
                "SoundFont",
                "[green]Found[/green]",
                sf_path
            )
        else:
            table.add_row(
                "SoundFont",
                "[yellow]Not Found[/yellow]",
                "Set CLEF_SOUNDFONT env var"
            )
    except Exception:
        table.add_row(
            "SoundFont",
            "[yellow]Unknown[/yellow]",
            "FluidSynth not available"
        )
    
    console.print()
    console.print(table)
    
    # File associations
    console.print("\n[bold]File Extensions:[/bold]")
    console.print("  .clef - Clef score files")
    console.print("  .mid  - MIDI export")
    console.print("  .wav  - Audio export")


@main.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
def events(source: Path):
    """
    Debug: Show the event graph for a score.
    
    Displays all events with their precise timing in whole notes.
    """
    try:
        score, _ = load_and_validate(source)
        graph = compile_score(score)
        
        table = Table(title=f"Events: {source.name}")
        table.add_column("Time", style="cyan")
        table.add_column("Type")
        table.add_column("Staff")
        table.add_column("Voice")
        table.add_column("Details")
        
        from clef.engine.events import NoteEvent, RestEvent, TempoEvent, PedalEvent
        
        for event in graph:
            time_str = str(event.start_time)
            event_type = event.__class__.__name__.replace("Event", "")
            
            if isinstance(event, NoteEvent):
                details = f"MIDI {event.midi_note}, dur={event.duration}, vel={event.velocity}"
            elif isinstance(event, RestEvent):
                details = f"dur={event.duration}"
            elif isinstance(event, TempoEvent):
                details = f"{event.bpm} BPM"
            elif isinstance(event, PedalEvent):
                details = "down" if event.value > 0 else "up"
            else:
                details = ""
            
            table.add_row(
                time_str,
                event_type,
                event.staff_id,
                str(event.voice_id),
                details
            )
        
        console.print()
        console.print(table)
        console.print(f"\nTotal events: {len(graph)}")
        console.print(f"Duration: {graph.get_duration()} whole notes")
    
    except Exception as e:
        print_error("Error", str(e))
        sys.exit(1)


@main.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path),
              help="Output Clef file path (default: source with .clef extension)")
@click.option("--dpi", default=300, help="PDF rendering DPI (default: 300)")
@click.option("--first-page", type=int, help="First page to process (1-indexed)")
@click.option("--last-page", type=int, help="Last page to process (1-indexed)")
def transcribe(source: Path, output: Optional[Path], dpi: int,
               first_page: Optional[int], last_page: Optional[int]):
    """
    Transcribe sheet music (PDF/MusicXML/MIDI) to Clef code.
    
    Uses Optical Music Recognition to convert PDF sheet music into
    editable Clef source code that can then be compiled to MIDI.
    
    Supported formats:
    - PDF (requires pdf2image + poppler)
    - MusicXML (.xml, .musicxml, .mxl)
    - MIDI (.mid, .midi)
    
    Examples:
        clef transcribe sheet_music.pdf              # Output: sheet_music.clef
        clef transcribe score.pdf -o myscore.clef   # Custom output path
        clef transcribe score.pdf --dpi 400         # Higher quality OCR
        clef transcribe song.mid                    # Convert MIDI to Clef
        clef transcribe score.musicxml              # Convert MusicXML to Clef
    
    Workflow:
        1. clef transcribe sheet_music.pdf -o score.clef
        2. Edit score.clef as needed
        3. clef build score.clef -o output.mid
    """
    try:
        from clef.transcribe import transcribe_pdf, TranscriptionResult
        from clef.transcribe.transcriber import transcribe_musicxml, transcribe_midi
        
        console.print(f"\n[bold]Transcribing:[/bold] {source.name}\n")
        
        # Determine input type and output path
        suffix = source.suffix.lower()
        
        if output is None:
            output = source.with_suffix(".clef")
        
        # Transcribe based on format
        if suffix == ".pdf":
            result = transcribe_pdf(
                str(source),
                output_path=str(output),
                dpi=dpi,
                first_page=first_page,
                last_page=last_page,
            )
        elif suffix in (".xml", ".musicxml", ".mxl"):
            result = transcribe_musicxml(
                str(source),
                output_path=str(output),
            )
        elif suffix in (".mid", ".midi"):
            result = transcribe_midi(
                str(source),
                output_path=str(output),
            )
        else:
            print_error(
                "Unsupported Format",
                f"Cannot transcribe {suffix} files.\n"
                "Supported: .pdf, .xml, .musicxml, .mxl, .mid, .midi"
            )
            sys.exit(1)
        
        # Show results
        if result.warnings:
            for warning in result.warnings:
                print_warning(warning)
        
        if result.errors:
            for error in result.errors:
                print_error("Transcription Error", error)
            sys.exit(1)
        
        if result.success:
            # Show summary
            console.print()
            table = Table(title="Transcription Result", show_header=False)
            table.add_column("Property", style="cyan")
            table.add_column("Value")
            
            table.add_row("Output", str(output))
            
            if result.score:
                if result.score.title:
                    table.add_row("Title", result.score.title)
                if result.score.tempo:
                    table.add_row("Tempo", f"{result.score.tempo} BPM")
                if result.score.time_signature:
                    num, denom = result.score.time_signature
                    table.add_row("Time Signature", f"{num}/{denom}")
                if result.score.key_signature:
                    table.add_row("Key", result.score.key_signature)
                table.add_row("Staves", str(len(result.score.staves)))
                
                total_measures = sum(
                    len(staff.measures) for staff in result.score.staves
                )
                table.add_row("Measures", str(total_measures))
            
            console.print(table)
            console.print()
            
            print_success(f"Transcribed to: {output}")
            console.print()
            console.print("[dim]Next steps:[/dim]")
            console.print(f"  1. Edit [cyan]{output}[/cyan] as needed")
            console.print(f"  2. Run [cyan]clef validate {output}[/cyan] to check")
            console.print(f"  3. Run [cyan]clef build {output}[/cyan] to create MIDI")
        else:
            print_error("Transcription Failed", "Could not transcribe the file")
            sys.exit(1)
    
    except ImportError as e:
        print_error(
            "Missing Dependencies",
            f"{e}\n\n"
            "Install transcription dependencies with:\n"
            "  pip install pdf2image music21\n\n"
            "For PDF support, also install poppler:\n"
            "  Windows: Download from https://github.com/osbourne/poppler-windows/releases\n"
            "  macOS:   brew install poppler\n"
            "  Linux:   apt install poppler-utils"
        )
        sys.exit(1)
    except Exception as e:
        print_error("Error", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

