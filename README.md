# Live automatic speech recognition
This bash script runs speech-to-text on a live audio input and dumps the
results into a folder for futher processing. It uses the
[Speechmatics](https://www.speechmatics.com/) service for ASR, but could easily
be adapted to use anything.

## Dependencies
- avconv (or ffmpeg)
- libmp3lame
- Python 2.7

## Usage
You will need a Speechmatics user ID and API key to run the script. Once you
have those, run it like so:

    ./record.sh {uid} {api-key}

The script is configured to use the default input, mix it down to mono and
compress it as 64kbps MP3. The following parameters can be adjusted by editing
the settings in record.sh:

- chunk length
- output folders
- language
- input channels
- sample rate
- codec and bitrate

## Authors
- Chris Baume
- Speechmatics

## Licence
This code is released under an MIT Licence.

