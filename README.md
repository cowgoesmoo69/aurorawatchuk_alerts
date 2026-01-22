# Acknowledgements
[<img src="assets/aw-logo_w_300.jpg">](https://aurorawatch.lancs.ac.uk)

This project uses data that is made available by the [Aurorawatch UK](https://aurorawatch.lancs.ac.uk) project based at [Lancaster University](https://www.lancs.ac.uk). Neither [the author](https://github.com/cowgoesmoo69), nor this project, are in any way associated with, or endorsed by, Aurorawatch UK.

The data from Aurorawatch UK is made available under CC BY-NC-SA 3.0 Attribution-NonCommercial-ShareAlike 3.0 Unported. Accordingly, this project is licensed under CC BY-NC-SA 4.0 Attribution-NonCommercial-ShareAlike 4.0 International. See [LICENSE](./LICENSE) for further details.

# aurorawatch-uk
Retrieves status information from Aurorawatch UK and sends an alert using Pushover if all sites provided in the primary API output are reporting red.

Aurorawatch UK already have a range of smartphone apps and other methods of [receiving alerts]((https://aurorawatch.lancs.ac.uk/alerts/)) that are probably sufficient for most people's needs, and offer greater flexibility than this project. The author wanted only notifications of all sites reporting red, specifically via Pushover.

This project is intended to be run as a background systemd service in a Linux environment. The pre-requisites and installation instructions are provided on that basis.

# Pre-requisites
- A system running a Linux distribution that uses systemd, e.g. [Debian](https://www.debian.org/), and sudo access.
- [git](https://git-scm.com/). Install with `sudo apt install git`.
- [Python 3](https://www.python.org/). This project is currently developed using [Python 3.14.2](https://www.python.org/downloads/release/python-3142/). It will probably work ok with most earlier versions, but YMMV.
- Some Python libraries. Dependent upon which Linux distribution you're using some/all of these may already be present.
  - [Requests HTTP library](https://pypi.org/project/requests/). Dependent upon which Linux distribution you're using this can either be installed by running

    `python3 -m pip install requests` or

    `sudo apt install python3-requests` from the command line.
  - [lxml library](https://pypi.org/project/lxml/). Dependent upon which Linux distribution you're using this can either be installed by running

    `python3 -m pip install lxml` or

    `sudo apt install python3-lxml` from the command line.
- A [Pushover](https://pushover.net/) account.

# Installation
These instructions assume you are either logged in at a physical terminal, or connecting over SSH etc.

These instructions are written primarily with Debian in mind, but they will probably work without modification on most Linux systems.
1. Create a new, minimal user account for the project to run under, e.g. aurora:

    ```sudo adduser aurora --no-create-home --disabled-password```. Enter whatever you like for name etc. when prompted.
1. Clone the project repository:

    `git clone https://github.com/cowgoesmoo69/aurorawatch-uk-alerts.git`.
1. Change ownership of the directory and its contents:

    `sudo chown -R aurora: aurorawatch-uk-alerts`.
1. Update permissions of the directory and its contents:

    `sudo chmod -R 755 aurorawatch-uk-alerts`.
1. Move the directory into /opt:

    `sudo mv aurorawatch-uk-alerts /opt`.
1. Create a directory to hold an environment file:

    `sudo mkdir /etc/opt/aurorawatch-uk-alerts`.
1. [Log in](https://pushover.net/login) to your Pushover account.
1. [Create a new app](https://pushover.net/apps/build).
1. Fill in the name, description etc., agree to terms and click Create Application.
1. Copy the API token into a note-taking app.
1. Go back to your Pushover [account page](https://pushover.net/).
1. Copy your user key into a note-taking app. (You could also create a delivery group, add multiple user keys to the group, and copy the group key if you wanted to send alerts to multiple users simultaneously.)
1. Create an environment file:

    `sudo nano /etc/opt/aurorawatch-uk-alerts/aurorawatch-uk-alerts.env`

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
    Description=Aurorawatch UK Alerts
    After=network-online.target
    Wants=network-online.target

    [Service]
    User=aurora
    Group=aurora
    Type=exec
    ExitType=main
    KillMode=control-group
    Restart=no
    EnvironmentFile=/etc/opt/aurorawatch-uk-alerts/aurorawatch-uk-alerts.env
    ExecStart=/usr/bin/python3 /opt/aurorawatch-uk-alerts/app/aurorawatch-uk-alerts.py

    [Install]
    WantedBy=multi-user.target
    ```

    Ctrl-s to save, Ctrl-x to exit.
1. Reload systemd unit files:

    `sudo systemctl daemon-reload`.
1. Enable the service:

    `sudo systemctl enable aurorawatch-uk-alerts.service`.
1. Start the service:

    `sudo systemctl start aurorawatch-uk-alerts.service`.
1. Check the service is running:

    `sudo systemctl status aurorawatch-uk-alerts.service`.

    Something similar to the below should be seen:

    ```
    🟢 aurorawatch-uk-alerts.service - Aurorawatch UK Alerts
         Loaded: loaded (/etc/systemd/system/aurorawatch-uk-alerts.service; enabled; preset: enabled)
         Active: active (running) since Thu 2026-01-22 17:13:38 UTC; 5s ago
       Main PID: 14015 (python3)
          Tasks: 1 (limit: 9440)
         Memory: 21.1M
            CPU: 138ms
         CGroup: /system.slice/aurorawatch-uk-alerts.service
                 └─14015 /usr/bin/python3 /opt/aurorawatch-uk-alerts/app/aurorawatch-uk-alerts.py

    Jan 22 17:13:38 hostname systemd[1]: Starting aurorawatch-uk-alerts.service - Aurorawatch UK Alerts...
    Jan 22 17:13:38 hostname systemd[1]: Started aurorawatch-uk-alerts.service - Aurorawatch UK Alerts.
    ```