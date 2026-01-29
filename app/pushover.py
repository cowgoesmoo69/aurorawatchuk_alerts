#!/usr/bin/env python3

from dataclasses import dataclass, fields
import io
import re
import requests
import time
from typing import BinaryIO

SCRIPT_VERSION = "pushover 1.0.0"

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


@dataclass
class Validate:
    # https://pushover.net/api
    #
    # required
    token: str  # Application token/key from Pushover.
    user: str  # User/group key of Pushover recipient.
    message: str  # Message to be sent.

    # optional
    # Haven't included attachment_base64 or attachment_type.
    # attachment_base64 isn't required as we can easily pass an attachment tuple in the call to requests.
    # attachment_type isn't included as it appears to only be necessary when using attachment_base64.
    attachment: tuple[str, BinaryIO, str] | None = None
    device: str | None = None
    html: int | None = None
    monospace: int | None = None
    priority: int | None = None
    sound: str | None = None  # Only built-in Pushover sounds currently supported.
    timestamp: int | None = None
    title: str | None = None
    ttl: int | None = None
    url: str | None = None
    url_title: str | None = None

    def __post_init__(self):
        # Validate token, user parameters.
        for field in ("token", "user"):
            a = getattr(self, field)
            if isinstance(a, str):
                if re.fullmatch(r"[a-z0-9]{30}", a):
                    pass
                else:
                    raise ValueError(
                        f"Required parameter '{field}' must be 30 characters, only a-z and 0-9."
                    )
            else:
                raise TypeError(f"Required parameter '{field}' must be a string.")

        # Validate message parameter.
        b = getattr(self, "message")
        if isinstance(b, str):
            if len(b) > 0 and len(b) <= 1024:
                pass
            else:
                raise ValueError(
                    "Required parameter 'message' must be between 1 and 1024 characters."
                )
        else:
            raise TypeError("Required parameter 'message' must be a string.")

        # Validate attachment.
        c = getattr(self, "attachment")
        if not c == None:
            fname, fobj, ftype = c
            # Check filename.
            if isinstance(fname, str):
                # Imposing arbitrary 32 character limit, it's only a filename and doesn't seem to get used anywhere once it goes into the API anyway.
                if len(fname) > 1 and len(fname) < 32:
                    pass
                else:
                    raise ValueError(
                        "Filename item in 'attachment' must be between 1 and 64 characters"
                    )
            else:
                raise TypeError("Filename item in 'attachment' must be a string.")
            # Check file.
            if isinstance(fobj, io.IOBase):
                if fobj.seekable():
                    # Find current position in stream.
                    pos = fobj.tell()
                    # Seek to end of stream.
                    fobj.seek(0, 2)
                    # Find offset from start, i.e. size.
                    size = fobj.tell()
                    # Return to previous position.
                    fobj.seek(0, pos)
                    if size <= 5 * 1024 * 1024:
                        pass
                    else:
                        raise ValueError("File item in 'attachment' exceeds 5MB limit.")
                else:
                    raise ValueError(
                        "File item in 'attachment' must be a seekable file object."
                    )
            else:
                raise TypeError("File item in 'attachment' must be a file-like object.")
            if isinstance(ftype, str):
                # Check type is image/jpeg or image/png. Other image formats probably work fine, but these definitely work.
                allowed_types = ["image/jpeg", "image/png"]
                if ftype in allowed_types:
                    pass
                else:
                    raise ValueError(
                        f"Filetype item in 'attachment' must be one of: {', '.join(allowed_types)}."
                    )
            else:
                raise TypeError("Filetype item in 'attachment' must be a string.")

        # Validate device name. 25 characters, a-z, A-Z, 0-9, underscore, hyphen.
        d = getattr(self, "device")
        if not d == None:
            if isinstance(d, str):
                if re.fullmatch(r"^[a-zA-Z0-9_-]{1,25}$", d):
                    pass
                else:
                    raise ValueError(
                        "Optional parameter 'device' must be 1 to 25 characters, only letters, numbers, underscores and hyphens."
                    )
            else:
                raise TypeError("Optional parameter 'device' must be a string.")

        # Validate html, monospace, priority parameters.
        # Check they are all integers.
        for field in ("html", "monospace", "priority"):
            e = getattr(self, field)
            if e is not None:
                if isinstance(e, int):
                    pass
                else:
                    raise TypeError(f"Optional parameter '{field}' must be an integer.")
                if field == "html" or field == "monospace":
                    if e >= 0 and e <= 1:
                        pass
                    else:
                        raise ValueError(
                            f"Optional parameter '{field}' must be 0 or 1."
                        )
                if field == "priority":
                    if e >= -2 and e <= 2:
                        pass
                    else:
                        raise ValueError(
                            "Optional parameter 'priority' must be between -2 and 2."
                        )
        # Check html and monospace not both 1.
        if getattr(self, "html") == 1 and getattr(self, "monospace") == 1:
            raise ValueError(
                "Optional parameters 'html' and 'monospace' cannot both be 1."
            )

        # Validate sound parameter.
        f = getattr(self, "sound")
        if f is not None:
            if isinstance(f, str):
                valid_sounds = [
                    "pushover",
                    "bike",
                    "bugle",
                    "cashregister",
                    "classical",
                    "cosmic",
                    "falling",
                    "gamelan",
                    "incoming",
                    "intermission",
                    "magic",
                    "mechanical",
                    "pianobar",
                    "siren",
                    "spacealarm",
                    "tugboat",
                    "alien",
                    "climb",
                    "persistent",
                    "echo",
                    "updown",
                    "vibrate",
                    "none",
                ]
                if f in valid_sounds:
                    pass
                else:
                    lines = [
                        "Optional parameter 'sound' is not a valid Pushover sound.",
                        f"Valid sounds are: {', '.join(valid_sounds)}.",
                    ]
                    emsg = "\n".join(lines)
                    raise ValueError(emsg)
            else:
                raise TypeError("Optional parameter 'sound' must be a string.")

        # Validate timestamp parameter. Max five years in future.
        g = getattr(self, "timestamp")
        if not g == None:
            if isinstance(g, int):
                if g >= 0:
                    if g < (int(time.time()) + 157680000):
                        pass
                    else:
                        raise ValueError(
                            "Optional parameter 'timestamp' cannot be greater than five years in the future."
                        )
                else:
                    raise ValueError(
                        "Optional parameter 'timestamp' must be greater than 0."
                    )
            else:
                raise TypeError("Optional parameter 'timestamp' must be an integer.")

        # Validate title parameter.
        h = getattr(self, "title")
        if not h == None:
            if isinstance(h, str):
                if len(h) > 0 and len(h) <= 250:
                    pass
                else:
                    raise ValueError(
                        "Optional parameter 'title' must be between 1 and 250 characters."
                    )
            else:
                raise TypeError("Optional parameter 'title' must be a string.")

        # Validate ttl parameter. Max one year, 31536000 seconds.
        i = getattr(self, "ttl")
        if not i == None:
            if isinstance(i, int):
                if i > 0 and i <= 31536000:
                    pass
                else:
                    raise ValueError(
                        "Optional parameter 'ttl' must be between 1 and 31536000."
                    )
            else:
                raise TypeError("Optional parameter 'ttl' must be an integer.")

        # Validate url parameter.
        j = getattr(self, "url")
        if not j == None:
            if isinstance(j, str):
                if len(j) > 8 and len(j) <= 512:
                    pass
                else:
                    raise ValueError(
                        "Optional parameter 'url' must be between 8 and 512 characters."
                    )
            else:
                raise TypeError("Optional parameter 'url' must be a string.")
            # Check url at least starts https://, after that up to the user to validate.
            if re.fullmatch(r"^https://.*", j):
                pass
            else:
                raise ValueError(
                    "Optional parameter 'url' does not appear to be a valid url, must start with https://."
                )

        # Validate url_title parameter.
        k = getattr(self, "url_title")
        if not k == None:
            if isinstance(k, str):
                if len(k) > 0 and len(k) <= 512:
                    pass
                else:
                    raise ValueError(
                        "Optional parameter 'url_title' must be between 1 and 512 characters."
                    )
            else:
                raise TypeError("Optional parameter 'url_title' must be a string.")
            # Check there's a url to go with the title.
            if j == None:
                raise ValueError(
                    "Optional parameter 'url_title' was passed without a corresponding 'url' parameter."
                )
        # End validation checks.


def send_alert(**kwargs):
    """Function to send an alert using Pushover.
    The following kwargs are mandatory:
    - app_token is the application-specific token in Pushover.
    - key is the user or group key of the Pushover recipient(s).
    - message is the message to send.

    The following kwargs are optional:
    - attachment: tuple[str, BinaryIO, str] is an image to include with the message.
      e.g. ("image.jpg", open("path/to/image.jpg", "rb"), "image/jpeg")
    - device is a specific device name associated with a user key to be the recipient, instead of all devices.
    - html tells the Pushover API to treat message as containing html. Cannot be used in conjunction with monospace.
    - monospace tells the Pushover API to use a monospace typeface for the message. Cannot be used in conjunction with html.
    - priority determines the message priority.
    - sound tells the Pushover API what sound to play on the device(s) that receive the message.
    - timestamp overrides the default timestamp on the message.
    - title overrides the Pushover app name for the message title.
    - ttl specifies how long before the message expires and is automatically deleted by the recipient's device(s).
    - url specifies a url to be added to the message as a hyperlink.
    - url_title specifies custom text for the url hyperlink.
    """

    # Use dataclass to validate the kwargs.
    payload_obj = Validate(**kwargs)

    # Create the message payload, exclude None items and any attachment.
    msg_payload = {}
    for field in fields(payload_obj):
        value = getattr(payload_obj, field.name)
        if value is not None and field.name != "attachment":
            msg_payload[field.name] = value

    # Create arguments to be passed to requests.post()
    args = {
        "url": PUSHOVER_URL,
        "data": msg_payload,
    }

    # If there is an attachment, add it to args.
    attachment = getattr(payload_obj, "attachment")
    if attachment is not None:
        args["files"] = {"attachment": attachment}

    print(f"args: {args}")
    response = requests.post(**args)
    response.raise_for_status()
    return response


def main():
    # testing only
    # image = ("image.jpg", open("valid/path/to/image.jpg", "rb"), "image/jpeg")
    # send_alert(token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", user="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", message="testing", attachment=image)
    print("This script is not intended to be run as-is.")
    print(
        "Put this file in the same directory as your script and import: from pushover import send_alert"
    )


if __name__ == "__main__":
    main()
