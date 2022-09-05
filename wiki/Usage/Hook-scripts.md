# Server-side
The server-side hook scripts should be located in:  
`/var/lib/samba/sysvol/$server.$domain/scripts/$schoolname/custom/linux/`

eg: `/var/lib/samba/sysvol/linuxmuster.lan/scripts/default-school/custom/linux/`
These scripts are currently available:
- `sysstart.sh` -> is called in root context when the computer boots
- `logon.sh` -> is called in user context when a user logs in
- `sessionstart.sh` -> is called in user context right after the session has started (might only work on Gnome)
- `logoff.sh` -> not used
- `sysstop.sh` -> is called in root context when the computer shuts down

Please note: All other scripts in this directory (logoff.sh) are currently not used!

# Client-side
There are hook dirs available in `/etc/linuxmuster-linuxclient7`:
- `onBoot.d` -> equivalent to `sysstart.sh`
- `onLoginAsRoot.d` -> is called in root context when a user logs in
- `onLogin.d` -> equivalent to `logon.sh`
- `onSessionStarted.d` -> equivalent to `sessionstart.sh`
- `onLogoutAsRoot.d` -> is called in root context when a user logs out
- `onShutdown.d` -> equivalent to `sysstop.sh`

# Launching programs on login
To launch a program on login, you should the `sessionstart.sh` script or the `onSessionStarted.d` hook as they are executed when the user session is fully initialized.

# Using python scripts
Python scripts can also be used in hookdirs. They will have full access to the [linuxmusterLinuxclient7 library](https://linuxmuster.github.io/linuxmuster-linuxclient7).

# Environment
There are some environment variables available:
- Available in all scripts:
  - `$SYSVOL`: Contains absolute path to the local sysvol mount point. CAUTION! May contain space and `$`!
  - `$Network_domain`
  - `$Network_serverIp`
  - `$Computer_<ldap attribute>` where `<ldap attribute>` can be any LDAP attribute of the computer, eg. `$Computer_sophomorixAdminClass`
- Available only in server-side logon.sh and sessionstart.sh and client side onLogin.d and onSessionStarted.d:
  - `$SERVERHOME`: Contains absolute path to the local mount point of the home share of the user. CAUTION! May contain space, `(` and `:`!
  - `$User_<ldap attribute>` where `<ldap attribute>` can be any LDAP attribute of the user, eg. `$User_sAMAccountName` or `$User_sophomorixSchoolname`


To modify the environment of the host, you have to use the following commands: (only works in onLogin.d / logon.sh)
- `lmn-export <key>=<value>` to set an environment variable
- `lmn-unset <key>` to unset an environment variable

# Some ideas for scripts
This is an example for a logon script with some things you can try :)
```
# set wallpwaper
gsettings set org.gnome.desktop.background picture-uri file:///etc/linuxmuster-linuxclient7/Wallpaper.jpg &

# disbale hibernate
gsettings set org.gnome.desktop.session idle-delay 0

# diable lock button
gsettings set org.gnome.desktop.lockdown disable-lock-screen true

# export school, room and group
lmn-export SCHOOL=$User_sophomorixSchoolname
lmn-export ROOM=$Computer_sophomorixAdminClass
lmn-export GROUP=$(echo $Computer_memberOf | grep 'OU=device-groups' | awk '{ print $2 }' | awk -F\, '{ print $1 }' | awk -F\= '{ print $2 }' | sed -r 's/^d_//')
```