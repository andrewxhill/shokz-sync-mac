#!/bin/bash
# Spike: runs from a LaunchAgent with StartOnMount; logs what it sees and tries a write.
{
  echo "$(date '+%H:%M:%S') fired; volumes: $(ls /Volumes | tr '\n' ',')"
  for v in "/Volumes/SPIKEFAT"; do
    [ -d "$v" ] && { echo probe > "$v/probe.txt" && echo "wrote $v/probe.txt" || echo "write FAILED $v"; }
  done
} >> "$(dirname "$0")/probe.log" 2>&1
