#!/bin/bash

# Is this script necessary?

# Get the current time and the last request time from your log or database
current_time=$(date +%s)
last_request_time=$(date -d "$(heroku logs --tail --app your-app-name | grep -Eo '2024-[0-9-]+ [0-9:]+')" +%s)
idle_time=$((current_time - last_request_time))

# Define the idle threshold (15 minutes = 900 seconds)
idle_threshold=900

if [ $idle_time -gt $idle_threshold ]; then
  # Scale down the web dynos if idle time exceeds the threshold
  heroku ps:scale web=0 --app your-app-name
  echo "Dynos scaled down due to inactivity."
else
  echo "Dynos are still active."
fi
