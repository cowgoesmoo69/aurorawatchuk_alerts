# Installation
## Pre-requisites
- A system running a Linux distribution that uses systemd, e.g. [Debian](https://www.debian.org/), and sudo access.
- [git](https://git-scm.com/). Install with `sudo apt install git`.
- [Python 3](https://www.python.org/). This project is currently developed using [Python 3.14.2](https://www.python.org/downloads/release/python-3142/). It will probably work ok with 3.11+ but has not been exhaustively tested.
- Some additional Python libraries. Dependent upon which Linux distribution you're using some/all of these may already be present. Install using pip or your package manager.
  - requests
  - lxml
  - pytest
  - pytest-mock
- A [Pushover](https://pushover.net/) account.

## Step-by-step install instructions

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
1. Create a venv and install required libraries:

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

    (This example uses the default alert interval, check interval, sensitivity and ttl settings, and an alert threshold of amber. See [README.md](README.md) for details of command line arguments.)
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
    ● aurorawatchuk_alerts.service - AuroraWatch UK Alerts
         Loaded: loaded (/etc/systemd/system/aurorawatchuk_alerts.service; enabled; preset: enabled)
         Active: active (running) since Thu 2026-01-29 18:42:08 UTC; 5s ago
       Main PID: 113880 (python3)
          Tasks: 1 (limit: 9440)
         Memory: 17.4M
            CPU: 167ms
         CGroup: /system.slice/aurorawatchuk_alerts.service
                 └─113880 /home/aurora/opt/aurorawatchuk_alerts/env/bin/python3 -m app.aurorawatchuk_alerts 3

    Jan 29 18:42:08 hostname systemd[1]: Starting aurorawatchuk_alerts.service - AuroraWatch UK Alerts...
    Jan 29 18:42:08 hostname systemd[1]: Started aurorawatchuk_alerts.service - AuroraWatch UK Alerts.
    ```