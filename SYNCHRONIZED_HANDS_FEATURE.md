# Synchronized Hands Feature

## Overview

Clef now supports writing piano music with both hands together in the same measure, making it easy to translate traditional piano scores where right and left hand are written together.

## Syntax

```clef
measure 1 {
    // Dynamics and pedal apply to the whole measure
    p
    ped
    
    // Right hand (voice 1)
    voice 1 {
        rest q.
        G#6 e staccato
        rest e
        G#6 e staccato
    }
    
    // Left hand (voice 2)
    voice 2 {
        G#2 e
        rest e
        D#3 e
        rest e
        G#3 e
        rest e
    }
}
```

## Key Features

✅ **Synchronized Start**: Both voices start at the same time (measure start)  
✅ **Independent Timing**: Each voice maintains its own timeline within the measure  
✅ **Shared Context**: Dynamics, pedal, and other markings apply to the whole measure  
✅ **Validation**: Semantic analyzer ensures both voices sum to the correct measure duration  
✅ **Exact Timing**: All timing uses rational fractions - no floating-point drift

## Example: La Campanella

The `test_liszt.clef` file demonstrates this feature with Liszt's La Campanella:

- **6/8 time signature** with both hands synchronized
- **Right hand**: High bell motif (G#6, A6, E6) with staccato
- **Left hand**: Jumping bass accompaniment (G#2, D#3, G#3)
- **Pedal markings** applied to the whole measure
- **Dynamics** (p, mf) applied measure-wide

## Event Output

When compiled, both voices start at the same measure time:

```
Time 0:    Left hand: G#2 (MIDI 44)
Time 0:    Right hand: Rest (3/8 duration)
Time 3/8:  Right hand: G#6 (MIDI 92) staccato
Time 1/4:  Left hand: D#3 (MIDI 51)
Time 1/2:  Left hand: G#3 (MIDI 56)
Time 5/8:  Right hand: G#6 (MIDI 92) staccato
```

## Validation

The semantic analyzer:
- Validates that all voices in a measure sum to the correct duration
- Ensures voices are synchronized (same total duration)
- Checks individual voice content (ties, tuplets, etc.)

## Compilation

The event compiler:
- Compiles all voices starting from the same measure start time
- Maintains independent timelines for each voice
- Calculates measure duration from the longest voice
- Preserves exact fractional timing

## Usage

```bash
# Validate
clef validate test_liszt.clef

# Build to MIDI
clef build test_liszt.clef -o la_campanella.mid

# View events
clef events test_liszt.clef
```

## Benefits

1. **Natural Notation**: Write piano music the way it's traditionally notated
2. **Easy Translation**: Direct mapping from sheet music to Clef code
3. **Synchronized Playback**: Both hands play together correctly
4. **Flexible**: Can still use separate voice blocks for independent sections

