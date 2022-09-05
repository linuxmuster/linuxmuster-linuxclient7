# Using Conky

## About this plugin
This plugin starts conky when the user logs in.

## Install this plugin

##### Dependencies
Run this to install the required dependencies

```bash
apt install conky
```

##### Script
Copy this script to `/etc/linuxmuster-linuxclient7/onSessionStarted.d/99-plugin-conky.sh` and make it executable.
```bash
# start conky
killall /usr/bin/conky &
sleep 1
/usr/bin/conky &
```