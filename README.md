# Live automatic speech recognition
This bash script runs speech-to-text on a live audio input and dumps the
results into a folder for futher processing. It uses the cloud-based
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

The script will run continuously until you stop it with Ctrl+C. After stopping
the recording, one or more background processes may still run as they wait to
download any remaining transcripts.

It is currently configured to use the default audio input, mix it down to mono
and compress it as 64kbps MP3 before transcription. The following parameters
can be adjusted by editing the settings in record.sh:

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

