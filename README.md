# aurorawatchuk_alerts
Retrieves status information from AuroraWatch UK and sends an alert using Pushover if status is above the specified threshold.

This project is intended to be run as a background systemd service in a Linux environment. The instructions below are provided on that basis.

## Acknowledgements
[<img src="assets/aw-logo_w_300.jpg">](https://aurorawatch.lancs.ac.uk)

This project uses data that is made available by the [AuroraWatch UK](https://aurorawatch.lancs.ac.uk) project based at [Lancaster University](https://www.lancs.ac.uk). Neither [the author](https://github.com/cowgoesmoo69), nor this project, are in any way associated with, or endorsed by, AuroraWatch UK.

The data from AuroraWatch UK is made available under CC BY-NC-SA 3.0 Attribution-NonCommercial-ShareAlike 3.0 Unported.

Accordingly, this project is licensed under CC BY-NC-SA 4.0 Attribution-NonCommercial-ShareAlike 4.0 International. See [LICENSE](./LICENSE) for further details.

AuroraWatch UK have a range of smartphone apps and other methods of [receiving alerts](https://aurorawatch.lancs.ac.uk/alerts/) that may be sufficient for your needs.

## Usage
```
usage: python.exe -m app.aurorawatchuk_alerts [-h] [-a ALERT_INTERVAL] [-c CHECK_INTERVAL] [-r] [-t TTL] [-v] threshold

Fetch Aurorawatch UK status and send a Pushover alert if status is above threshold. This script requires a Pushover app token and a Pushover user/group key to be available
as environment variables PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY. Consult your operating system's documentation for information on how to set environment variables.

positional arguments:
  threshold             Sets the alert threshold, 1=yellow, 2=amber, 3=red

options:
  -h, --help            show this help message and exit
  -a, --alert-interval ALERT_INTERVAL
                        Sets a custom alert interval in seconds. Default is one hour.
  -c, --check-interval CHECK_INTERVAL
                        Sets a custom check interval in seconds. Default is five minutes.
  -r, --reduced-sensitivity
                        Only send alerts when status of all sites is above threshold.
  -t, --ttl TTL         Sets a custom alert ttl in seconds. Default is four hours.
  -v, --version         show program's version number and exit
```
## Installation
### Pre-requisites
- A system running a Linux distribution that uses systemd, e.g. [Debian](https://www.debian.org/), and sudo access.
- [git](https://git-scm.com/). Install with `sudo apt install git`.
- [Python 3](https://www.python.org/). This project is currently developed using [Python 3.14.2](https://www.python.org/downloads/release/python-3142/). It will probably work ok with 3.12+ but has not been exhaustively tested.
- Some additional Python libraries. Dependent upon which Linux distribution you're using some/all of these may already be present. Install using pip or your package manager.
  - requests
  - lxml
  - pytest
  - pytest-mock
- A [Pushover](https://pushover.net/) account.

### Step-by-step install instructions
These instructions assume you are either logged in at a physical terminal, or connecting over SSH etc.

These instructions are written primarily with Debian in mind, but they will probably work without modification on most Linux systems.
1. Create a new, minimal user account for the project to run under, e.g. aurora:

    ```sudo adduser aurora --no-create-home --disabled-password```. Enter whatever you like for name etc. when prompted.
1. Clone the project repository:

    `git clone https://github.com/cowgoesmoo69/aurorawatchuk_alerts.git`.
1. Change ownership of the directory and its contents:

    `sudo chown -R aurora: aurorawatchuk_alerts`.
1. Update permissions of the directory and its contents:

    `sudo chmod -R 755 aurorawatchuk_alerts`.
1. Move the directory into /opt:

    `sudo mv aurorawatchuk_alerts /opt`.
1. Create a directory to hold an environment file:

    `sudo mkdir /etc/opt/aurorawatchuk_alerts`.
1. [Log in](https://pushover.net/login) to your Pushover account.
1. [Create a new app](https://pushover.net/apps/build).
1. Fill in the name, description etc., agree to terms and click Create Application. (You might like to set the app icon to the AuroraWatch UK icon from the assets directory, so that it appears on the Pushover messages.)
1. Copy the API token into a note-taking app.
1. Go back to your Pushover [account page](https://pushover.net/).
1. Copy your user key into a note-taking app. (You could also create a delivery group, add multiple user keys to the group, and copy the group key if you wanted to send alerts to multiple users simultaneously.)
1. Create an environment file:

    `sudo nano /etc/opt/aurorawatchuk_alerts/env`

    containing

    ```
    PUSHOVER_USER_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    PUSHOVER_APP_TOKEN=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
    ```

    replacing the xs and ys with the keys you copied out of your Pushover account. Ctrl-s to save, Ctrl-x to exit.
1. Change the ownership of the directory and file:

    `sudo chown -R aurora: /etc/opt/aurorawatch-uk-alerts`.
1. Lock down the permissions of the directory and file:

    `sudo chmod -R 700 /etc/opt/aurorawatch-uk-alerts`.
1. Create a new systemd unit file:

    `sudo nano /etc/systemd/system/aurorawatch-uk-alerts.service`

    containing

    ```
    [Unit]
    Description=AuroraWatch UK Alerts
    After=network-online.target
    Wants=network-online.target

    [Service]
    User=aurora
    Group=aurora
    Type=exec
    ExitType=main
    KillMode=control-group
    Restart=no
    EnvironmentFile=/etc/opt/aurorawatchuk_alerts/env
    ### TODO ### the ExecStart line needs to be updated ### TODO ###
    ExecStart=/usr/bin/python3 /opt/aurorawatch-uk-alerts/app/aurorawatch-uk-alerts.py 2

    [Install]
    WantedBy=multi-user.target
    ```

    Ctrl-s to save, Ctrl-x to exit.

    (This example uses the default alert interval, check interval, sensitivity and ttl settings, and an alert threshold of amber. See usage section for details of command line arguments.)
1. Reload systemd unit files:

    `sudo systemctl daemon-reload`.
1. Enable the service:

    `sudo systemctl enable aurorawatchuk_alerts.service`.
1. Start the service:

    `sudo systemctl start aurorawatchuk_alerts.service`.
1. Check the service is running:

    `sudo systemctl status aurorawatchuk_alerts.service`.

    Something similar to the below should be seen:

    ```
    ### TODO ### Replace this section ### TODO ###
    ```