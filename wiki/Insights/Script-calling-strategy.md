
## Scrips
The scripts in `/usr/share/linuxmuster-linuxclient7/scripts` are called in the following way:
### onBoot
This is called via /etc/systemd/system/linuxmuster-linuxclient7.service.
This file is placed there in adsso-setup via the template in `/usr/share/linuxmuster-linuxclient7/templates/linuxmuster-linuxclient7.service`.

### onLoginLogoutAsRoot
This is called via pam_exec in /etc/pam.d/common-session. 
This file is placed there in adsso-setup via the template in `/usr/share/linuxmuster-linuxclient7/templates/common-session`.  
Pam_exec calls this script on login AND on logout. If it is a login our logout is determined by the `PAM_TYPE` environment variable.

### onLogin
This is called via `/usr/share/linuxmuster-linuxclient7/scripts/executeHookWithEnvFix.sh`, which is called by `/etc/profile.d/99-linuxmuster-linuxclient7.sh` The reason for this is the [environment workaround](Environment-workaround)

### onSessionStart
This is called via `/home/$user/.config/autostart`.
This file is placed there in adsso-setup via the template in `/usr/share/linuxmuster-linuxclient7/templates/linuxmuster-linuxclient7-autostart.desktop`.

## Hooks
The hook scrips and dirs are then called internally using the `hooks` module.