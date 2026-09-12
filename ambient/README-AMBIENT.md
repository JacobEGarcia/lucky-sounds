# LUCKY CAT - ambient pack 2

4 seamless loops, same bell-collar / A-major-pentatonic palette as sound
identity pack 1. All procedural (gen_ambient.py), royalty-free.

## Files (ogg2/ - 44.1 kHz stereo OGG Vorbis q6, -16 LUFS, TP < -1.5 dBTP, linear two-pass loudnorm)
- room_day.ogg        36.0s  warm air bed, sparse mallet plinks, distant purr swells
- room_night.ogg      36.0s  darker air, low-register bells, soft crickets
- room_rain.ogg       36.0s  steady rain bed, occasional low mallet
- music_pet_theme.ogg 22.9s  gentle 8-bar music-box lullaby, loops on the bar line

## Seamlessness
Loop construction: 3-cent detuned stereo pair rendered first, then each
channel loopified with the same wrap-correct crossfade (tail folded onto head
at a shared cut point; for the theme the cut is exactly the 8-bar boundary so
the loop is musically correct). Verified numerically: per-channel wrap delta
is below the p99 consecutive-sample delta of the file in every loop.

## Demo
demo-ambient.html (paths relative: ogg2/<name>.ogg). Click toggles a loop.

## Rebuild
python3 gen_ambient.py   # renders wav2/
# encode: linear two-pass loudnorm I=-16 TP=-1.5 LRA=11 -> libvorbis q6
