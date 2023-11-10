#!/bin/bash

while true; do
  poetry run python hargassner_web_api_pull/hg_data_pull.py 
  sleep 120
done;