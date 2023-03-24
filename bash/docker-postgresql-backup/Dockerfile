FROM alpine:latest

RUN apk add --update --no-cache bash p7zip dos2unix curl rclone postgresql-client

WORKDIR /etc/cron.d

RUN rm -rf *
ADD crontab.txt backup
RUN chmod 0644 backup
RUN dos2unix backup
RUN crontab backup

WORKDIR /root

COPY backup.sh .
RUN chmod 0744 *.sh
RUN dos2unix *.sh

RUN mkdir -p .config/rclone/
RUN touch .config/rclone/rclone.conf

CMD ["crond", "-f"]
