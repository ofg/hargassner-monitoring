#!/bin/bash

while true; do
  echo "# Running data pull script at $(date)"
  poetry run python hargassner_web_api_pull/hg_data_pull.py 
  sleep 60
done;