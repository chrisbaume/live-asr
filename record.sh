#!/bin/bash

if [ "$#" -ne 2 ]; then
  echo "Usage: ./record.sh {uid} {api-key}"
fi

seconds=30
audiofolder="all-audio"
transcriptfolder="all-trans"
logfolder="all-logs"
language="en-GB"
samplerate=44100
channels=1
codec="libmp3lame"
bitrate="64k"
uid="$1"
apikey="$2"

while true; do
  date=`date +%Y-%m-%d_%H-%M-%S`
  avconv -f alsa -ac ${channels} -ar ${samplerate} -ab ${bitrate} -i pulse -acodec ${codec} -t ${seconds} -y ${audiofolder}/${date}.mp3
  if [ $? -ne 0 ]; then
    exit 0
  fi
  nohup python -u speechmatics.py -f ${audiofolder}/${date}.mp3 -l ${language} -i ${uid} -t ${apikey} -o ${transcriptfolder}/${date}.json > ${logfolder}/${date}.log 2> ${logfolder}/${date}.err & 
done
