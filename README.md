# aurorawatchuk_alerts
Retrieves status information from AuroraWatch UK and sends an alert using Pushover if status is above the specified threshold.

This project is intended to be run as a background systemd service in a Linux environment. See [INSTALL.md](INSTALL.md) for further instructions.

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
