#!/bin/bash

# This script checks the idle time of a Heroku app and scales down the web dynos if the app has been idle for more than a specified threshold.

# Get the current time in seconds since the epoch
current_time=$(date +%s)

# Get the last request time from the Heroku logs, convert it to seconds since the epoch
# The log format is expected to contain timestamps in the format '2024-xx-xx xx:xx:xx'
last_request_time=$(date -d "$(heroku logs --tail --app your-app-name | grep -Eo '2024-[0-9-]+ [0-9:]+')" +%s)

# Calculate the idle time by subtracting the last request time from the current time
idle_time=$((current_time - last_request_time))

# Define the idle threshold in seconds (15 minutes = 900 seconds)
idle_threshold=900

# Check if the idle time exceeds the threshold
if [ $idle_time -gt $idle_threshold ]; then
  # Scale down the web dynos if idle time exceeds the threshold
  heroku ps:scale web=0 --app your-app-name
  echo "Dynos scaled down due to inactivity."
else
  # Indicate that the dynos are still active
  echo "Dynos are still active."
fi