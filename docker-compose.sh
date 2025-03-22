#!/bin/bash

set -e

# Build the Docker image for the API
docker build -t n8n-api .

# Set environment variables
export Drive_URL="https://www.googleapis.com/drive/v3/files"

# Mount a temporary drive to download files from Google Drive
mkdir /tmp/google_drive
mount -t tmpfs tmpfs -o size=10G,uid=1000,gid=1000 /tmp/google_drive

# Download files from Google Drive and save them locally
for file in $(curl -s "$Drive_URL/manifest" | jq -r '.files[] | @uri'); do
  curl -s -L "$file" --output /tmp/$file
done

# Run the merge_video function
python3 main.py --urls=/tmp/

# Clean up
rm -rf /tmp/google_drive