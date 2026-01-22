#!/usr/bin/env python3
#
# This script expects PUSHOVER_GROUP_KEY and PUSHOVER_APP_TOKEN to be present as
# environment variables. See installation instructions for further information.
#
from datetime import date, datetime, timedelta
from lxml import etree
import os
import random
import requests
import time

DEBUG = False  # Set to True to enable noisier output in terminal.

PUSHOVER_GROUP_KEY = os.environ.get("PUSHOVER_GROUP_KEY")  # Pushover group key.
PUSHOVER_APP_TOKEN = os.environ.get("PUSHOVER_APP_TOKEN")  # Pushover app token.
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
AWUK_URL = "https://aurorawatch-api.lancs.ac.uk/0.2.5/status/all-site-status.xml"


def check_env():
    if DEBUG:
        print("DEBUG: Checking for environment variables.")
    # Check environment variables exist.
    if not PUSHOVER_GROUP_KEY or not PUSHOVER_APP_TOKEN:
        raise RuntimeError("Missing environment variable(s).")
    if DEBUG:
        print("DEBUG: Environment variables found.")


def send_pushover_alert(
    message,
    priority=0,
    ttl=14400,
):
    # Sends a notification using Pushover.
    #
    # priority defaults to 0, normal priority.
    # ttl defaults to 14400 seconds (four hours) so messages expire and disappear.
    payload = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_GROUP_KEY,
        "message": message,
        "priority": priority,
        "ttl": ttl,
        "url": "",
        "url_title": "https://aurorawatch.lancs.ac.uk/",
    }
    try:
        if DEBUG:
            print("Sending Pushover message.")
        response = requests.post(PUSHOVER_URL, data=payload, timeout=10)
        if DEBUG:
            print("DEBUG: Checking if Pushover send successful.")
        response.raise_for_status()
        if DEBUG:
            print("DEBUG: Pushover send successful.")
    except Exception as e:
        print(f"An exception occurred while sending Pushover message: {e}")


def get_status_ids():
    # Retrieves the all-site-status.xml file from AWUK and returns all status_id values.
    try:
        # Fetch xml file.
        if DEBUG:
            print("DEBUG: Fetching all-site-status.xml from AWUK.")
        response = requests.get(
            AWUK_URL,
            headers={
                "referer": "https://github.com/cowgoesmoo69/aurorawatch-uk-alerts"
            },
            timeout=10,
        )
        if DEBUG:
            print("DEBUG: Checking if fetch was successful.")
        response.raise_for_status()
        if DEBUG:
            print("DEBUG: Fetch was successful.")
        # Process xml file for status IDs.
        if DEBUG:
            print("DEBUG: Processing all-site-status.xml.")
        root = etree.fromstring(response.content)
        sites = root.xpath("//site_status")
        status_ids = []
        for site in sites:
            status_ids.append(
                {
                    # "site_id": site.get("site_id"), # Might use in the future.
                    # "site_url": site.get("site_url"), # Might use in the future.
                    "status_id": site.get("status_id"),
                }
            )
        if DEBUG:
            print("DEBUG: Returning status IDs.")
        return status_ids
    except Exception as e:
        print(f"An exception occurred while retrieving/processing site statuses: {e}")


def get_current_status(
    status_ids,
):
    # Determine the lowest-ranked status ID across all sites and return it.
    #
    # Function only returns red if all sites are reporting red. Even if all sites are
    # reporting red, there is no guarantee you will see aurora borealis in the UK;
    # variables such as cloud cover, weather, light pollution etc. may prevent
    # aurora being visible in your location.
    if DEBUG:
        print("DEBUG: Checking for lowest-ranked status ID.")
    RANK_ORDER = ["green", "yellow", "amber", "red"]
    statuses = {s["status_id"] for s in status_ids}
    for rank in RANK_ORDER:
        if rank in statuses:
            if DEBUG:
                print(f"DEBUG: Lowest-ranked status ID is {rank}, returning.")
            return rank
    if DEBUG:
        print("DEBUG: Failed to find a valid status ID, returning None.")
    return None


def go_to_sleep():
    # Calculate time of next check. Top of next hour, plus a random number of minutes
    # and seconds so that check is performed in first ten minutes of hour. Avoids hitting
    # the AWUK API at exactly the same time each hour.
    #
    # Aurorawatch UK ask that individual clients leave at least three minutes between
    # requests. However, since aurora borealis is not an on/off phenomenon, hourly
    # checks are plenty fast enough.
    t = datetime.now()
    n = t.replace(minute=0, second=0, microsecond=0) + timedelta(
        hours=1, minutes=random.randint(0, 9), seconds=random.randint(0, 59)
    )
    if DEBUG:
        print(f"DEBUG: Next check at {n.strftime('%Y-%m-%d %H:%M:%S')}")
    # Calculate how long to sleep for.
    s = (n - t).total_seconds()
    # Sleep.
    if DEBUG:
        print(f"DEBUG: Sleeping for {s} seconds.")
    time.sleep(s)


def main():
    while True:
        status_ids = get_status_ids()
        status = get_current_status(status_ids)
        # Send alert only if all sites reporting red.
        if status == "red":
            # Send high priority alert.
            send_pushover_alert("All sites reporting RED status.", 1)
        go_to_sleep()


if __name__ == "__main__":
    check_env()
    main()
