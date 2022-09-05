In some scenarios, we need to execute a command with root permissions in user context:
- When mounting a samba share
- When installing a printer

For these scenarios, there is a special script: `/usr/share/linuxmuster-linuxclient7/scripts/sudoTools`. Normal users are allowed to execute it, as they have a sudoers entry in `/etc/sudoers.d/linuxmuster-linuxclient7` which permits NOPASSWD sudo on this script.  
Inside the script, the `SUDO_USER` environment variable is used to determine which user executed the script. Because of this, there is no security risk involved, as the user will only be able to influence their own context.