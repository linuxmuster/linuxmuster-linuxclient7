# Client
Currently, the following distros are fully supported:
- Ubuntu 20.04 using GDM3 as a login manager and the Gnome desktop
## Setup
- Install a supported distro
- The admin user MUST be `linuxadmin`
- Make sure the hostname of the client fits an imported machine from your devices.csv
- Install the package linuxmuster-linuxclient7 (TODO: add repo)
- Run `sudo linuxmuster-linuxclient7 setup`
- Run `sudo linuxmuster-linuxclient7 prepare-image`
- Reboot and create an image IMMIDIATELY

# Server
- Disable browsing for printers by changing `Browsing On` to `Browsing Off` in `/etc/cups/cupsd.conf`
- Assign rooms, users or computers to your printer groups in AD as desired
- Adjust logon script on Server