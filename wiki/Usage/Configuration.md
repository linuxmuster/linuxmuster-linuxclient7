# Shares
- Shares are configured via GPO and can be modified using gpedit on a Windows client
- If you don't have access to a Windows client, you can modify the file `/var/lib/samba/sysvol/linuxmuster.lan/Policies/{someUUID}/User/Preferences/Drives/Drives.xml` on the linuxmuster server directly. (Replace `someUUID` with the UUID of the policy)

# Printers
- Printers MUST have the same name in cups and devices.csv!
- Printers can be assigned to groups in the AD

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
