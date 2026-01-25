#!/usr/bin/env python3

import argparse
import os
import random
import time
from aurorawatchuk import get_status
from datetime import date, datetime, timedelta
from pushover import send_alert

SCRIPT_VERSION = "aurorawatch-uk-alerts 2.0.0"


def argparser():
    parser = argparse.ArgumentParser(
        description="Fetch Aurorawatch UK status and send a Pushover alert if status is above threshold. This script requires a Pushover app token and a Pushover user/group key to be available as environment variables PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY. Consult your operating system's documentation for information on how to set environment variables."
    )
    parser.add_argument(
        "threshold", help="Sets the alert threshold, 1=yellow, 2=amber, 3=red"
    )
    parser.add_argument(
        "-a",
        "--alert-interval",
        help="Sets a custom alert interval in seconds. Default is one hour.",
        default=3600,
    )
    parser.add_argument(
        "-c",
        "--check-interval",
        help="Sets a custom check interval in seconds. Default is five minutes.",
        default=300,
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Turns on DEBUG output",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--reduced-sensitivity",
        help="Only send alerts when status of all sites is above threshold.",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--ttl",
        help="Sets a custom alert ttl in seconds. Default is four hours.",
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
    global REDUCED_SENSITIVITY
    REDUCED_SENSITIVITY = args.reduced_sensitivity
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
    # Validate alert interval
    global ALERT_INTERVAL
    ALERT_INTERVAL = int(args.alert_interval)
    if DEBUG:
        print("Validating alert interval.")
    if isinstance(ALERT_INTERVAL, int):
        if ALERT_INTERVAL > 0:
            pass
        else:
            raise ValueError("Alert interval cannot be negative.")
    else:
        raise TypeError("Alert interval must be an integer.")
    # Validate check interval
    global CHECK_INTERVAL
    CHECK_INTERVAL = int(args.check_interval)
    if DEBUG:
        print("Validating check interval.")
    if isinstance(CHECK_INTERVAL, int):
        if CHECK_INTERVAL > 0:
            if CHECK_INTERVAL >= 180:
                pass
            else:
                raise ValueError("Check interval cannot be less than three minutes.")
        else:
            raise ValueError("Check interval cannot be negative.")
    else:
        raise TypeError("Check interval must be an integer.")
    # Validate ttl value.
    global TTL
    TTL = int(args.ttl)
    if DEBUG:
        print("Validating TTL.")
    if isinstance(TTL, int):
        if TTL > 0 and TTL <= 31536000:
            pass
        else:
            raise ValueError("TTL must be betwen 1 and 31536000.")
    else:
        raise TypeError("TTL must be an integer.")
    # Check for necessary environment variables.
    if DEBUG:
        print("DEBUG: Checking for environment variables.")
    global PUSHOVER_APP_TOKEN
    PUSHOVER_APP_TOKEN = os.environ.get("PUSHOVER_APP_TOKEN")
    global PUSHOVER_USER_KEY
    PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY")
    if not PUSHOVER_USER_KEY or not PUSHOVER_APP_TOKEN:
        raise RuntimeError("Missing environment variable(s).")


def main():
    STATUS_TEXT = ["GREEN", "YELLOW", "AMBER", "RED"]
    last_alert_time = 0
    while True:
        status = get_status(REDUCED_SENSITIVITY)
        if status == None:
            if DEBUG:
                print("An error occurred fetching status, skipping.")
        else:
            now = time.time()
            if DEBUG:
                print(f"Current status: {STATUS_TEXT[status]}.")
            if status >= THRESHOLD:
                should_alert = last_alert_time == 0 or (
                    now - last_alert_time >= ALERT_INTERVAL
                )
                if should_alert:
                    if DEBUG:
                        print("Sending alert.")
                    args = {
                        "token": PUSHOVER_APP_TOKEN,
                        "user": PUSHOVER_USER_KEY,
                        "message": f"AuroraWatch UK Status: {STATUS_TEXT[status]}.",
                        "ttl": TTL,
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
            time.sleep(
                CHECK_INTERVAL
            )  # AWUK request no shorter than 3-minute interval.


if __name__ == "__main__":
    pre_checks()
    main()
