To migrate an image from an old linuxmuster-client-adsso installation to the new one, please follow these steps:
CAUTION: This will break the login process until the new client is installed!  
DO NOT LOGOUT before the new client is installed, you will not be able to login again!  
WARNING! All custom scripts in `/etc/linuxmuster-client` will be deleted in the process! Make sure to back them up.

- Remove old linuxmuster-linuxclient7 entirely: `apt purge linuxmuster-client-adsso`
- Remove lightdm `apt purge lightdm`
- Install gdm3 `apt install --reinstall gdm3`
- Cleanup `apt autoremove`
- Follow the [setup instructions](setup) (again: DO NOT LOGOUT!!!)