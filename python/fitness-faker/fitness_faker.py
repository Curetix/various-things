import argparse
import os
import sys
import math
import calendar
from random import randint
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def date_to_nano(ts: datetime):
    """
    Takes a datetime object and returns POSIX UTC in nanoseconds
    """
    return calendar.timegm(ts.utctimetuple()) * int(1e9)


def get_dataset_id(start: datetime, end: datetime):
    return "{start}-{end}".format(start=date_to_nano(start), end=date_to_nano(end))


def get_datasource_identifier(datasource, project_number):
    return "{type}:{dataType}:{projectNumber}:{deviceManufacturer}:{deviceModel}:{deviceId}:{dataStreamName}".format(
        type=datasource["type"],
        dataType=datasource["dataType"]["name"],
        projectNumber=project_number,
        deviceManufacturer=datasource["device"]["manufacturer"],
        deviceModel=datasource["device"]["model"],
        deviceId=datasource["device"]["uid"],
        dataStreamName=datasource["dataStreamName"]
    )


class Fitness:
    def __init__(self):
        self.project_number = 415267609441
        self.datasource = {
            "dataStreamName": "Curetix Fitness",
            "type": "derived",
            "application": {
                "name": "Curetix Fitness (beta)",
                "version": "0.1.5"
            },
            "dataType": {
                "field": [
                    {
                        "name": "steps",
                        "format": "integer"
                    }
                ],
                "name": "com.google.step_count.delta"
            },
            "device": {
                "manufacturer": "Xiaomi",
                "model": "Smart Band 7",
                "type": "watch",
                "uid": "123456789",
                "version": "1.0"
            }
        }
        self.datasource_id = get_datasource_identifier(self.datasource, self.project_number)
        self.credentials = self.authenticate()
        self.fitness = build('fitness', 'v1', credentials=self.credentials)

    @staticmethod
    def authenticate():
        scopes = [
            "https://www.googleapis.com/auth/fitness.activity.read",
            "https://www.googleapis.com/auth/fitness.activity.write"
        ]
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                    creds = flow.run_local_server(port=3000)
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                creds = flow.run_local_server(port=3000)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    def get_datasource(self):
        try:
            ds = self.fitness.users().dataSources().get(userId="me", dataSourceId=self.datasource_id).execute()
            return ds
        except HttpError:
            print("Datasource not found!")
            return None

    def create_datasource(self):
        try:
            ds = self.fitness.users().dataSources().create(userId="me", body=self.datasource).execute()
            return ds
        except HttpError as error:
            print(error)
            return None

    def delete_datasource(self):
        try:
            self.fitness.users().dataSources().get(userId="me", dataSourceId=self.datasource_id).execute()
            return True
        except HttpError as error:
            print(error)
            return False

    def get_dataset(self, start: datetime, end: datetime):
        try:
            ds = self.fitness.users().dataSources().datasets().get(
                userId="me",
                dataSourceId=self.datasource_id,
                datasetId=get_dataset_id(start, end)
            ).execute()
            return ds
        except HttpError as error:
            print(error)
            return False

    def fill_dataset(self, start_date: datetime, end_date: datetime):
        delta = end_date - start_date
        days = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
        points = []
        for d in days:
            steps = randint(10000, 12000)
            start_time = datetime(d.year, d.month, d.day, randint(8, 20), randint(0, 59), randint(0, 59))
            minutes = math.ceil(steps/100) + randint(-20, 20)
            end_time = start_time + timedelta(minutes=minutes)
            points.append({
                "dataTypeName": "com.google.step_count.delta",
                "startTimeNanos": date_to_nano(start_time),
                "endTimeNanos": date_to_nano(end_time),
                "value": [
                    {
                        "intVal": steps
                    }
                ]
            })

        start_total = points[0]["startTimeNanos"]
        end_total = points[len(points) - 1]["endTimeNanos"]
        body = {
            "dataSourceId": self.datasource_id,
            "minStartTimeNs": start_total,
            "maxEndTimeNs": end_total,
            "point": points
        }
        try:
            ds = self.fitness.users().dataSources().datasets().patch(
                userId="me",
                dataSourceId=self.datasource_id,
                datasetId="{}-{}".format(start_total, end_total),
                body=body
            ).execute()
            return ds
        except HttpError as error:
            print(error)
            return None

    def delete_dataset(self, start: datetime, end: datetime):
        try:
            self.fitness.users().dataSources().datasets().delete(
                userId="me",
                dataSourceId=self.datasource_id,
                datasetId=get_dataset_id(start, end)
            ).execute()
            return True
        except HttpError as error:
            print(error)
            return False


def main():
    fitness = Fitness()

    parser = argparse.ArgumentParser(description="Google Fitness Faker")
    parser.add_argument("command", help="Command to run: create_source, delete_source, create_set, delete_set")
    parser.add_argument("--start-date", help="Start date for dataset, format year-month-day")
    parser.add_argument("--end-date", help="End date for dataset, format year-month-day")
    parser.add_argument("--quick-set", help="Fill data for current month of current year up to current day",
                        action="store_true", default=False)
    parser.add_argument("--full-delete",
                        help="In combination with delete_set, delete all data between 2000,1,1 and current date")
    args = parser.parse_args()

    if not args.command:
        print("No command provided")
        sys.exit(1)

    if args.command == "create_source":
        print("Creating datasource.")
        print(fitness.create_datasource())
    elif args.command == "delete_source":
        print("Deleting datasource.")
        print(fitness.delete_datasource())
    elif args.command == "create_set":
        if not fitness.get_datasource():
            print("Creating datasource.")
            print(fitness.create_datasource())

        if args.quick_set:
            now = datetime.now()
            print(fitness.fill_dataset(datetime(now.year, now.month, 1), datetime(now.year, now.month, now.day - 1)))
            print("Done")
        elif not args.start_date or not args.end_date:
            print("start_date or end_date not provided")
            sys.exit(1)
        else:
            start = [int(s) for s in args.start_date.split("-")]
            end = [int(s) for s in args.end_date.split("-")]
            print(fitness.fill_dataset(datetime(*start), datetime(*end)))
            print("Done")
    elif args.command == "delete_set":
        if not fitness.get_datasource():
            print("Datasource not found")
            sys.exit()

        if args.full_delete:
            now = datetime.now()
            print(fitness.delete_dataset(datetime(2000, 1, 1), datetime(now.year, now.month, now.day)))
            print("Done")
        elif not args.start_date or not args.end_date:
            print("start_date or end_date not provided")
            sys.exit(1)
        else:
            start = [int(s) for s in args.start_date.split("-")]
            end = [int(s) for s in args.end_date.split("-")]
            print(fitness.delete_dataset(datetime(*start), datetime(*end)))
            print("Done")
    else:
        print("Invalid command!")
        parser.print_help()


if __name__ == '__main__':
    main()
