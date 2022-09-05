**Maintainer**: [dorian@linuxmuster.net](mailto:dorian@linuxmuster.net), [@dorianim](https://github.com/dorianim)
**Status**: ✅ stable

## About

This plugin starts Conky when the user logs in. 

## Install

##### Dependencies
Run this to install the required dependencies

```bash
#!/bin/bash
apt-get install conky
```

##### Files
Copy these files to the given locations and give them their respective rights.

`/etc/linuxmuster-linuxclient7/onSessionStarted.d/99-plugin-conky.sh`, `555`
```bash
#!/bin/bash
# start conky
killall /usr/bin/conky &
sleep 1
/usr/bin/conky &
```