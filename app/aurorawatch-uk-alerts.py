#!/usr/bin/env python3

import argparse
from pushover import send_alert
from datetime import date, datetime, timedelta
from lxml import etree
import os
import random
import requests
import time

SCRIPT_VERSION="2.0.0"

AWUK_URL = "https://aurorawatch-api.lancs.ac.uk/0.2.5/status/all-site-status.xml"

def argparser():
    parser = argparse.ArgumentParser(
        description="Fetch Aurorawatch UK status and send a Pushover alert if status is above threshold. This script requires a Pushover app token and a Pushover user/group key to be available as environment variables PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY. Consult your operating system's documentation for information on how to set environment variables."
    )
    parser.add_argument(
        "threshold", help="Sets the alert threshold, 1=yellow, 2=amber, 3=red"
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Turns on DEBUG output",
        action="store_true",
    )
    parser.add_argument("-v", "--version", action="version", version=SCRIPT_VERSION)
    return parser.parse_args()


def pre_checks():
    """
    Processes supplied command-line arguments and checks that required environment variables exist.
    Format validation of the app token and the user key is performed within the pushover.py module.
    """
    args = argparser()
    global DEBUG
    DEBUG = args.debug
    # Validate supplied threshold value.
    if DEBUG:
        print("Validating supplied threshold value.")
    global THRESHOLD
    THRESHOLD = args.threshold
    if isinstance(THRESHOLD, int):
        if THRESHOLD >=1 and THRESHOLD <=3:
            pass
        else:
            raise ValueError("Threshold must be between 1 and 3.")
    else:
        raise TypeError("Threshold must be an integer.")
    if DEBUG:
        print("Threshold passed validation.")
    # Check for necessary environment variables.
    if DEBUG:
        print("DEBUG: Checking for environment variables.")
    global PUSHOVER_APP_TOKEN
    PUSHOVER_APP_TOKEN = os.environ.get("PUSHOVER_APP_TOKEN")
    global PUSHOVER_USER_KEY
    PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY")
    if not PUSHOVER_USER_KEY or not PUSHOVER_APP_TOKEN:
        raise RuntimeError("Missing environment variable(s).")
    if DEBUG:
        print("DEBUG: Environment variables found.")


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
            args = {
                "token": PUSHOVER_APP_TOKEN,
                "user": PUSHOVER_USER_KEY,
                "message": "All sites reporting red status.",
                "priority": 1,
                "ttl": (3600 * 4)
                }
            send_alert(**args)
        go_to_sleep()


if __name__ == "__main__":
    pre_checks()
    main()
