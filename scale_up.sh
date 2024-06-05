#!/bin/bash

# This script is used to scale up the web dynos for a Heroku application.
# It sets the number of web dynos to 1 for the specified application.

# Define the application name
APP_NAME="asbestos-dashboard"

# Scale up the web dynos to 1
# The 'heroku ps:scale' command is used to change the number of dynos for a process type.
# In this case, it sets the number of web dynos to 1 for the application specified by $APP_NAME.
heroku ps:scale web=1 --app $APP_NAME

# Print confirmation message
# This message confirms that the web dynos have been successfully scaled up to 1.
echo "Web dynos scaled up to 1."
