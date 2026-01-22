# Acknowledgements
[<img src="assets/aw-logo_w_300.jpg">](https://aurorawatch.lancs.ac.uk)

This project uses data that is made available by the [Aurorawatch UK](https://aurorawatch.lancs.ac.uk) project based at [Lancaster University](https://www.lancs.ac.uk). Neither [the author](https://github.com/cowgoesmoo69), nor this project, are in any way associated with or endorsed by Aurorawatch UK.

The data is made available under CC BY-NC-SA 3.0 Attribution-NonCommercial-ShareAlike 3.0 Unported. Accordingly, this project is licensed under CC BY-NC-SA 4.0 Attribution-NonCommercial-ShareAlike 4.0 International. See [LICENSE](./LICENSE) for further details.

# aurorawatch-uk
Retrieves status information from Aurorawatch UK and sends alerts using [Pushover](https://pushover.net/).

This project is intended to be run as a background systemd service in a Linux environment. The pre-requisites and installation instructions are provided on that basis.

# Pre-requisites
- A system running a Linux distribution that uses systemd, e.g. [Debian](https://www.debian.org/).
- [Python 3](https://www.python.org/). This project is currently developed using [Python 3.14.2](https://www.python.org/downloads/release/python-3142/).
- [Requests HTTP library](https://pypi.org/project/requests/). Dependent upon the particular distribution of Linux you are using this can either be installed by running `python3 -m pip install requests` or `sudo apt install python3-requests` from the command line.
- A [Pushover](https://pushover.net/) account.