#!/bin/bash

#Is this script necessary?

# Define the application name
APP_NAME="asbestos-dashboard"

# Scale up the web dynos to 1
heroku ps:scale web=1 --app $APP_NAME

# Print confirmation message
echo "Web dynos scaled up to 1."
