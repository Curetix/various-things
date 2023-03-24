# docker-postgresql-backup

Dockerized cron running a regular PostgreSQL dump on Alpine Linux.
These dumps are uploaded to a rclone remote destination.

Perfect for deployment on [Fly.io](https://fly.io) (no costs, yet) or other PaaS.

# Configuration

## Environment variables

* **POSTGRES_URI** - full PostgreSQL URI in the form of postgres://[user]:[password]@[host]:[port]/[database]
* **HEALTHCHECK_URL** _(optional)_ - if set, this URL will be pinged after the job is run
* **RCLONE_DESTINATION** - during backup, the script will run `rclone copy ./$TIME.tar.gz $RCLONE_DESTINATION`, see below
* **PGDUMP_OPTIONS** _(optional)_ - additional flags for pg_dump, for example selecting schemas with `--schema`

## rclone

### a) [Connection strings](https://rclone.org/docs/#connection-strings)

Set **RCLONE_DESTINATION** to the desired connection string, for example:

```text
RCLONE_DESTINATION=:s3,provider=Storj,access_key_id=somekey,secret_access_key=somekey,endpoint=gateway.storjshare.io:backup-bucket
```

Notice the colon at the *end* of the string, after which you can specify the path
(or in this case, the name of the S3 bucket).

### b) [Environment variables](https://rclone.org/docs/#config-file)

Alternatively, you can configure a remote using environment variables and the set **RCLONE_DESTINATION** accordingly.

```text
RCLONE_CONFIG_DEFAULT_TYPE=s3
RCLONE_CONFIG_DEFAULT_PROVIDER=Storj
RCLONE_CONFIG_DEFAULT_ACCESS_KEY_ID=somekey
RCLONE_CONFIG_DEFAULT_SECRET_ACCESS_KEY=somekey
RCLONE_CONFIG_DEFAULT_ENDPOINT=gateway.storjshare.io

RCLONE_DESTINATION=default:backup-bucket
```

## Cron

The default crontab looks like this:

```text
05 */6 * * * /root/backup.sh "$POSTGRES_URI" "$RCLONE_DESTINATION" "$HEALTHCHECK_URL" "$PGDUMP_OPTIONS"
```

If you want to add multiple backup jobs, set new environment variables add a line to the crontab.txt:

```text
05 */6 * * * /root/backup.sh "$POSTGRES_URI" "$RCLONE_DESTINATION" "$HEALTHCHECK_URL" "$PGDUMP_OPTIONS"
10 */12 * * * /root/backup.sh "$POSTGRES_URI_OTHER_DB" "$RCLONE_DESTINATION_S3"
```
