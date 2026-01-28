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
1. Create a new user account for the project to run under, e.g. aurora:

    `sudo adduser aurora --disabled-password`. Enter a name when prompted, e.g. "AuroraWatch UK Alerts service account".
1. Use sudo to login as the new user:

    `sudo su - aurora`.
1. Create a new folder and cd into it:

    `mkdir /home/aurora/opt`

    then

    `cd /home/aurora/opt`.
1. Clone the project repository and cd into it:

    `git clone https://github.com/cowgoesmoo69/aurorawatchuk_alerts.git`

    then

    `cd /home/aurora/opt/aurorawatchuk_alerts`.
1. Collect user/group key and app token from Pushover.
  - Log in to your Pushover account.
  - Create a new app and make a note of the API token.
  - Make a note of the recipient user/group key.
1. Create an environment file:
    `nano /home/aurora/opt/aurorawatchuk_alerts/keys.env`

    containing

    ```
    PUSHOVER_USER_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    PUSHOVER_APP_TOKEN=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
    ```

    replacing the xs and ys with the keys from your Pushover account. Ctrl-s to save, Ctrl-x to exit.
1. Optional Step - Create a venv to run in:

    In the root of the repo run:

    `python3 -m venv env`,

    `source env/bin/activate`,

    `pip install -r requirements.txt`,

    `deactivate`.
1. Create a new systemd unit file:

    `sudo nano /etc/systemd/system/aurorawatchuk_alerts.service`

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
    EnvironmentFile=/home/aurora/opt/aurorawatchuk_alerts/keys.env
    ExecStart=cd /home/aurora/opt/aurorawatchuk_alerts && env/bin/python3 -m app.aurorawatchuk_alerts 2

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