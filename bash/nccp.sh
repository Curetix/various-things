#!/bin/bash

# nccp - Nextcloud Copy for TrueNAS Scale with TrueCharts Nextcloud
# Copy a file/folder from [SOURCE] to [DESTINATION] (Nextcloud data folder),
# set the ownership to www-data, and run the occ files:scan command

set -e

if [ -z "$1" ]; then
  echo "usage: nccp [SOURCE] [DESTINATION]"
  exit 1
fi

if [ -z "$2" ]; then
  echo "usage: nccp [SOURCE] [DESTINATION]"
  exit 1
fi

SOURCE="$1"
DESTINATION="$2"
NEXTCLOUD_POD=$(sudo k3s kubectl -n ix-nextcloud get pods --no-headers | grep -E -v "(redis|postgresql|cronjob)" | awk '{print $1}')

echo "Copying files..."
sudo rsync -ah --info="progress2" --exclude="*.zip" --exclude="*.rar" --exclude="*.7z" "$SOURCE" "$DESTINATION"

echo "Setting permissions..."
sudo chown -R www-data:www-data "$DESTINATION"

echo "Starting Nextcloud scan..."
sudo k3s kubectl -n ix-nextcloud exec -it $NEXTCLOUD_POD -c nextcloud -- runuser -u www-data -- php occ files:scan -n -p ${DESTINATION/"/mnt/store/cloud"/}