#!/usr/bin/env python3

import argparse
import os
import time
from aurorawatchuk import get_status
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
    Checks environment variables, validates command line arguments.
    Returns dict with config info for use elsewhere.
    """
    config = {}
    
    # Environment variables.
    # App token.
    token = os.environ.get("PUSHOVER_APP_TOKEN")
    if token is None:
        raise RuntimeError("PUSHOVER_APP_TOKEN environment variable missing.")
    config["token"] = token
    # User key.
    user = os.environ.get("PUSHOVER_USER_KEY")
    if user is None:
        raise RuntimeError("PUSHOVER_APP_TOKEN environment variable missing.")
    config["user"] = user

    # Parse command line arguments.
    args = argparser()
    
    # Reduced sensitivity option.
    config["reduced_sensitivity"] = args.reduced_sensitivity
    
    # Threshold.
    try:
        threshold = int(args.threshold)
    except ValueError:
        raise TypeError("Threshold must be an integer.")
    if threshold in range(1,(3 + 1),1):
        config["threshold"] = threshold
    else:
        raise ValueError("Threshold must be between 1 and 3.")
    
    # Alert interval
    try:
        alert_interval = int(args.alert_interval)
    except ValueError:
        raise TypeError("Alert interval must be an integer.")
    if alert_interval > 0:
        config["alert_interval"] = alert_interval
    else:
        raise ValueError("Alert interval must be > 0.")
    
    # Check interval
    try:
        check_interval = int(args.check_interval)
    except ValueError:
        raise TypeError("Check interval must be an integer.")
    if check_interval >= 180:
        config["check_interval"] = check_interval
    else:
        raise ValueError("Check interval must be >= 180.")
    
    # TTL.
    try:
        ttl = int(args.ttl)
    except ValueError:
        raise TypeError("TTL must be an integer.")
    if ttl in range(1,(31536000 + 1),1):
        config["ttl"] = ttl
    else:
        raise ValueError("TTL must be betwen 1 and 31536000.")

    return config


def should_alert(config, state):
    if state["current_status"] == None:
        return False
    if state["current_status"] < config["threshold"]:
        state.update(
            {
                "last_alert_time": 0,
                "last_alert_status": 0
                }
            )
        return False
    now = time.time()
    if state["last_alert_time"] == 0 or (now - state["last_alert_time"] >= config["alert_interval"]) or state["current_status"] > state["last_alert_status"]:
        state.update(
            {
                "last_alert_time": now,
                "last_alert_status": state["current_status"]
                }
            )
        return True


def main():
    status_text = ["GREEN", "YELLOW", "AMBER", "RED"]
    config = pre_checks()
    state = {
        "current_status": 0,
        "last_alert_status": 0,
        "last_alert_time": 0,
        }
    #print(config)
    while True:
        state["current_status"] = get_status(config["reduced_sensitivity"])
        print(f"Current status: {state['current_status']}")
        if should_alert(config, state):
            args = {
                "token": config["token"],
                "user": config["user"],
                "message": f"AuroraWatch UK Status: {status_text[state["current_status"]]}.",
                "ttl": config["ttl"],
            }
            # Send RED alerts as high priority.
            if state["current_status"] == 3:
                args["priority"] = 1
            send_alert(**args)
        time.sleep(config["check_interval"])


if __name__ == "__main__":
    main()
