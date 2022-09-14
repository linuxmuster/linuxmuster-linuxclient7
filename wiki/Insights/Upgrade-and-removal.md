## Upgrade
On every upgrade, the command `linuxmuster-linuxclient7 upgrade` is executed. It does the following:
1. Check if linuxmuster-linuxclient7 is set up
2. Upgrade config files if required:
  - `/etc/linuxmuster-linuxclient7/network.conf`
3. Apply all templates.
4. Restart services.
5. Delete old files which could cause conflicts

## Removal
When the package is removed, the command `linuxmuster-linuxclient7 clean` is executed. It does the following:
1. Clear user cache
2. Clear / leave domain join
3. Clear /etc/pam.d/common-session:
  - Remove lines containing one of `["pam_mkhomedir.so", "pam_exec.so", "pam_mount.so", "linuxmuster.net", "linuxmuster-linuxclient7"]`.
  - This will prevent a logon brick
