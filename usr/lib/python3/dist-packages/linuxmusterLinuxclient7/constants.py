#!/usr/bin/python3

templateUser = "linuxadmin"
userTemplateDir = "/home/" + templateUser
defaultDomainAdminUser = "global-admin"

# {} will be substituted for the username
gtkBookmarksFile = "/home/{}/.config/gtk-3.0/bookmarks"

shareMountBasepath = "/home/{}/media"
hiddenShareMountBasepath = "/srv/samba/{}"
machineAccountSysvolMountPath = "/var/lib/samba/sysvol"
defaultShareLetterTemplate = " ({letter}:)"

etcBaseDir = "/etc/linuxmuster-linuxclient7"
shareBaseDir = "/usr/share/linuxmuster-linuxclient7"
configFileTemplateDir = shareBaseDir + "/templates"
scriptDir = shareBaseDir + "/scripts"

legacyNetworkConfigFilePath = etcBaseDir + "/network.conf"
configFilePath = etcBaseDir + "/config.yml"
# {} will be substituted for the username
tmpEnvironmentFilePath = "/home/{}/.linuxmuster-linuxclient7-environment.sh"

notTemplatableFiles = ["/etc/sssd/sssd.conf", "/etc/linuxmuster-linuxclient7/network.conf"]

# cleanup
obsoleteFiles = [
    "/etc/profile.d/99-linuxmuster.sh",
    "/etc/sudoers.d/linuxmuster",
    "/etc/profile.d/linuxmuster-proxy.sh",
    "/etc/bash_completion.d/99-linuxmuster-client-adsso.sh",
    "/etc/profile.d/99-linuxmuster-client-adsso.sh",
    "/etc/sudoers.d/linuxmuster-client-adsso",
    "/usr/sbin/linuxmuster-client-adsso",
    "/usr/sbin/linuxmuster-client-adsso-print-logs",
    "/etc/systemd/system/linuxmuster-client-adsso.service",
    f"{userTemplateDir}/.config/autostart/linuxmuster-client-adsso-autostart.desktop",
    "/etc/cups/client.conf",
    "/usr/share/linuxmuster-linuxclient7/templates/linuxmuster-client-adsso.service",
    "/usr/share/linuxmuster-linuxclient7/templates/linuxmuster-client-adsso-autostart.desktop",
    "/etc/security/pam_mount.conf.xml",
    f"{configFileTemplateDir}/pam_mount.conf.xml"
]

obsoleteDirectories = [
    "/etc/linuxmuster-client",
    "/etc/linuxmuster-client-adsso",
    "/usr/share/linuxmuster-client-adsso"
]
