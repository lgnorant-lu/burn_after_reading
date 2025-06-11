#!/bin/sh
# This script is the entrypoint for the backend container.
# It waits for any command passed to it (like the uvicorn CMD from the Dockerfile)
# and executes it. This standard shell script entrypoint is more robust
# than using 'sh -c' directly in the CMD, as it ensures proper signal
# handling and process management within the Docker container.

set -e

# The "$@" holds the command and arguments passed to the script,
# which in our case will be: 'uvicorn src.main:app --host ...'
exec "$@" 