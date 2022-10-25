# audio-mastering
Library that displays loudness (LUFS) statistics and plots for .wav audio files (single or multiple).

Run the driver `python tracks_profiler.py` from command line with the following options:

```
python tracks_profiler.py --help

Usage: tracks_profiler.py [OPTIONS]

Options:
  -f, --files PATH               File or folder to use.
  -s, --short-target FLOAT       Max for short-term loudness
  -i, --integrated-target FLOAT  Max for integrated loudness
  -p, --do-plot                  Show plots
  --help                         Show this message and exit.
  ```
