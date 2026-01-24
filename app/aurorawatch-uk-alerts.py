#!/usr/bin/env python3

import argparse
import os
import random
import time
from aurorawatchuk import get_status
from datetime import date, datetime, timedelta
from pushover import send_alert

SCRIPT_VERSION="2.0.0"
# TODO
# Integrate alert interval and check interval into ArgumentParser
ALERT_INTERVAL = 3600 # 1 hour
CHECK_INTERVAL = 300  # 5 minutes

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
    parser.add_argument(
        "-t",
        "--ttl",
        help="Sets a custom ttl in seconds. Default is four hours.",
        default=14400,
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
    # Validate threshold value.
    if DEBUG:
        print("Validating supplied threshold value.")
    global THRESHOLD
    THRESHOLD = int(args.threshold)
    if isinstance(THRESHOLD, int):
        if THRESHOLD >= 1 and THRESHOLD <= 3:
            pass
        else:
            raise ValueError("Threshold must be between 1 and 3.")
    else:
        raise TypeError("Threshold must be an integer.")
    if DEBUG:
        print("Threshold passed validation.")
    # Validate ttl value.
    global TTL
    TTL = args.ttl
    if DEBUG:
        print("Validating TTL.")
    if isinstance(TTL, int):
        if TTL > 0 and TTL <= 31536000:
            pass
        else:
            raise ValueError("TTL must be betwen 1 and 31536000.")
    else:
        raise TypeError("TTL must be an integer.")
    if DEBUG:
        print("TTL passed validation.")
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


def main():
    STATUS_TEXT = ["GREEN", "YELLOW", "AMBER", "RED"]
    last_alert_time = 0
    while True:
        status = get_status()
        now = time.time()
        if DEBUG:
            print(f"Current status: {STATUS_TEXT[status]}.")
        if status >= THRESHOLD:
            should_alert = (
                last_alert_time = 0 or
                (now - last_alert_time >= ALERT_INTERVAL)
                )
            if should_alert:
                if DEBUG:
                    print("Sending alert.")
                args = {
                    "token": PUSHOVER_APP_TOKEN,
                    "user": PUSHOVER_USER_KEY,
                    "message": f"AuroraWatch UK Status: {STATUS_TEXT[status]}.",
                    "ttl": TTL
                    }
                # Send RED alerts as high priority.
                if status == 3:
                    args["priority"] = 1
                send_alert(**args)
                last_alert_time = now
            else:
                if DEBUG:
                    print("Status above threshold, but alert recently sent.")
        else:
            # Reset if status drops below threshold.
            last_alert_time = 0
        if DEBUG:
            print("Sleeping...")
        time.sleep(CHECK_INTERVAL) # AWUK request no shorter than 3-minute interval.


if __name__ == "__main__":
    pre_checks()
    main()
