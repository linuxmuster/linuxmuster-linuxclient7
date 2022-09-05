## About this plugin
This plugin starts Conky when the user logs in.

**Maintainer**: [dorian@linuxmuster.net](mailto:dorian@linuxmuster.net)

## Install this plugin

##### Dependencies
Run this to install the required dependencies

```bash
#!/bin/bash
apt-get install conky
```

##### Script
Copy this script to `/etc/linuxmuster-linuxclient7/onSessionStarted.d/99-plugin-conky.sh` and make it executable.
```bash
#!/bin/bash
# start conky
killall /usr/bin/conky &
sleep 1
/usr/bin/conky &
```