# Shares
- Shares are configured via GPO and can be modified by:
  - using the linuxmuster-webui `client configuration -> Drives` menu
  - using gpedit on a Windows client
  - modifying the file `/var/lib/samba/sysvol/linuxmuster.lan/Policies/{someUUID}/User/Preferences/Drives/Drives.xml` on the linuxmuster server. (Replace `someUUID` with the UUID of the policy)
- If you want to customize the naming of shares which have drive letters, you can use the `nameTemplate` parameter in the `shares`-section of the config file (`/etc/linuxmuster-linuxclient7/config.yml`):
  ```yaml
  shares:
    nameTemplate: "{label} ({letter}:)"
  ```
  - Shares without drive letters always have the label as a name
  - For the users home share, the label is the username

# Printers
- Printers MUST have the same name in cups and devices.csv!
- To use a printer, either the computer or user must be member of the printers group
  - Printer group membership can be controlled in the linuxmuster-webu `group membership` menu

# Proxy server
To configure a proxy server, add this to your logon.sh script:
```
PROXY_DOMAIN=linuxmuster.lan
PROXY_HOST=http://firewall.$PROXY_DOMAIN
PROXY_PORT=3128

# set proxy via env (for Firefox)
lmn-export no_proxy=127.0.0.0/8,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12,localhost,.local,.$PROXY_DOMAIN
lmn-export http_proxy=$PROXY_HOST:$PROXY_PORT
lmn-export ftp_proxy=$PROXY_HOST:$PROXY_PORT
lmn-export https_proxy=$PROXY_HOST:$PROXY_PORT

# set proxy gconf (for Chrome)
gsettings set org.gnome.system.proxy ignore-hosts "['127.0.0.0/8','10.0.0.0/8','192.168.0.0/16','127.0.0/12','localhost','.local','.$PROXY_DOMAIN']"
gsettings set org.gnome.system.proxy mode "manual"
gsettings set org.gnome.system.proxy.http port "$PROXY_PORT"
gsettings set org.gnome.system.proxy.http host "$PROXY_HOST"
gsettings set org.gnome.system.proxy.https port "$PROXY_PORT"
gsettings set org.gnome.system.proxy.https host "$PROXY_HOST"
gsettings set org.gnome.system.proxy.ftp port "$PROXY_PORT"
gsettings set org.gnome.system.proxy.ftp host "$PROXY_HOST"

```
