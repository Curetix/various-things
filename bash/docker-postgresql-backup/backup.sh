#!/bin/bash

# Check if required programs are installed
command -v pg_dump >/dev/null 2>&1 || { echo >&2 "pg_dump is not installed."; exit 1; }
command -v rclone >/dev/null 2>&1 || { echo >&2 "rclone is not installed."; exit 1; }

if ! command -v 7zz &> /dev/null; then
  alias 7z="7zz"
fi
command -v 7z >/dev/null 2>&1 || { echo >&2 "7zip is not installed."; exit 1; }

postgres_uri=$1
rclone_destination=$2
healthcheck_url=$3
dump_options=$4

function health_ping {
  if [ -n "$healthcheck_url" ]; then
    if ! command -v curl &> /dev/null; then
      echo >&2 "curl is not installed. Cannot perform healthcheck ping!"
    else
      # first argument, default to 0
      status=${1:-0}
      echo "Pinging health check..."
      curl -sS --retry 2 "$healthcheck_url/$status"
      echo -e "\n"
    fi
  fi
}

# Proper ISO-8061 would use colons as delimiter of time units, but many filesystems do not allow this character
timestamp=$(date -u +"%Y-%m-%dT%H-%M-%SZ")
dump_file=./$timestamp.tar
archive_file=./$timestamp.7z

echo "Starting backup..."

if pg_dump --file=$dump_file --format=tar $dump_options "$postgres_uri"; then
  echo "Database dump created."
else
  echo >&2 "Database dump failed."
  rm -f $dump_file
  health_ping 1
  exit 1
fi

# 7zip with standard and progress output streams disabled
if 7z -y -bso0 -bsp0 a $archive_file $dump_file; then
  echo "Compressed archive."
  rm -f $dump_file
else
  echo >&2 "Could not compress archive."
  health_ping 1
  exit 1
fi

if rclone copy $archive_file $rclone_destination; then
  echo "Database dump uploaded to remote."
  health_ping
  rm -f $archive_file
else
  echo >&2 "Upload failed."
  health_ping 1
  exit 1
fi
