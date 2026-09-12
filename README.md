# LUCKY CAT - sound identity pack 1

15 procedural sounds, one palette: bell-collar timbre, A major pentatonic
(A B C# E F#), warm gold feel. No samples, no licensed material - every sound
is synthesized in gen_lucky.py (numpy), so the pack is royalty-free forever.

## Files (ogg/ - 44.1 kHz stereo OGG Vorbis q6)
BRAND
- audio_logo.ogg      ~1.6s  A5-C#6-E6 bell motif over warm A3 pluck, shimmer tail
- startup_chime.ogg   ~1.0s  soft rising fourth + air swell
NOTIFICATIONS
- notify_message.ogg  ~0.7s  two soft mallet notes (E5 -> A5)
- notify_task_done.ogg ~1.0s ascending triad + coin sparkle
- notify_alert.ogg    ~0.8s  two gentle low bell taps (no harshness)
UI
- ui_tap.ogg          ~0.12s short tick
- ui_toggle.ogg       ~0.28s two-tone click
- ui_success.ogg      ~0.55s bell + fifth
- ui_error.ogg        ~0.4s  soft low droop (never buzzy)
TAMAGOTCHI PET
- pet_eat.ogg         ~0.75s munching bursts
- pet_play.ogg        ~0.85s bouncy arpeggio
- pet_sleep.ogg       ~1.7s  descending lullaby + soft breath
- pet_happy.ogg       ~1.2s  purr + rising chirp
- pet_sad.ogg         ~1.0s  descending minor third, soft vibrato
- pet_evolve.ogg      ~1.9s  sparkle gliss into A major bell chord

## Loudness
Musical pieces (logo, chime, sleep, happy, evolve): -16 LUFS, TP < -1.5 dBTP.
Short UI blips: peak-normalized to -1.5 dBFS (LUFS is meaningless at 120 ms).

## Demo
Open demo.html (paths are relative: ogg/<name>.ogg). Buttons grouped
brand / notifications / UI / pet.

## Rebuild
python3 gen_lucky.py   # renders wav/
# encode loop in build notes: libvorbis q6, loudnorm or peak per above
