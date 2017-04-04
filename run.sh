#!/usr/bin/env bash

# Clears batch file to make sure it is using UTF-8 as encoding

if [[ $# != 5 ]] ; then

    echo 'Using following output and input files: '
    echo "./log_input/log.txt ./log_output/hosts.txt ./log_output/hours.txt ./log_output/resources.txt ./log_output/blocked.txt"
    log="./log_input/log2.txt.test"
    hosts="./log_output/hosts.txt"
    hours="./log_output/hours.txt"
    resources="./log_output/resources.txt"
    resources="./log_output/blocked.txt"
else
    log=$1
    hosts=$2
    hours=$3
    resources=$4
    resources=$5
fi

# After reviewing raw data using Vi I noticed it does not have a unique charset (ASCII): /[^ -~]
# iconv excludes lines with weird characters @todo add excluded lines into an error log file.
echo "Ensuring raw data has utf-8 codification"
echo "[$(date)] Starting Fixing encoding raw data.." >> ./log_output/results.txt
log_utf8_filename=$(echo $log | sed -e 's/.txt//g')_cleaned.txt
echo "New log filename:"
echo $log_utf8_filename
echo "[$(date)] Starting Fixing encoding raw data.." >> ./log_output/results.txt
iconv -f ascii -t utf-8//TRANSLIT -c $log > $log_utf8_filename
echo "[$(date)] Finished cleaning batch data.." >> ./log_output/results.txt

# /Users/Angel/anaconda/bin/python ./src/detective.py $log_utf8_filename ./log_output/hosts.txt ./log_output/hours.txt ./log_output/resources.txt ./log_output/blocked.txt

