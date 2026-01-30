#!/usr/bin/env python3

import requests
from lxml import etree

SCRIPT_VERSION = "aurorawatchuk 1.0.0"

AWUK_URL = "https://aurorawatch-api.lancs.ac.uk/0.2.5/status/all-site-status.xml"


def get_status_ids(reduced_sensitivity):
    # Retrieves the all-site-status.xml file from AWUK and returns status_id values.
    # If reduced_sensitivity is specified, return all sites, otherwise just return 'alerting site'.
    # See AuroraWatch UK API docs for more info.
    # Fetch xml file.
    try:
        response = requests.get(
            AWUK_URL,
            # AWUK request that referer is used to identify clients accessing their API.
            headers={"referer": "https://github.com/cowgoesmoo69/aurorawatchuk_alerts"},
            timeout=10,
        )
    except Exception as e:
        print(f"Exception occurred fetching AuroraWatch UK all-site-status.xml: {e}")
        return None
    response.raise_for_status()
    # Process xml for status_id values.
    try:
        root = etree.fromstring(response.content)
    except Exception as e:
        # The response was not valid xml, return None
        print(f"Exception occurred creating element tree from response: {e}")
        return None

    status_ids = []
    if reduced_sensitivity:
        # Return all sites.
        sites = root.xpath("//site_status")
        return [
            {
                "site_id": site.get("site_id"),
                "site_url": site.get("site_url"),
                "status_id": site.get("status_id"),
            }
            for site in sites
        ]
    else:
        # Return only alerting site.
        site = root.xpath("//site_status[@alerting='true']")
        if not site:
            return None
        site = site[0]
        return [
            {
                "site_id": site.get("site_id"),
                "site_url": site.get("site_url"),
                "status_id": site.get("status_id"),
            }
        ]


def process_status_ids(
    status_ids,
):
    print(f"status_ids: {status_ids}.")
    # Determine the lowest-ranked status ID across sites and return it as an integer between 0 and 3.
    RANK_ORDER = ["green", "yellow", "amber", "red"]
    statuses = {s["status_id"] for s in status_ids}
    for i, rank in enumerate(RANK_ORDER):
        if rank in statuses:
            return i
    return None


def get_status(reduced_sensitivity=False):
    s_ids = get_status_ids(reduced_sensitivity)
    if not s_ids:
        return None
    else:
        return process_status_ids(s_ids)


def main():
    print("This script is not intended to be run as-is.")
    print(
        "Put this file in the same directory as your script and import: from aurorawatchuk import get_status."
    )
    # print(get_status())


if __name__ == "__main__":
    main()
