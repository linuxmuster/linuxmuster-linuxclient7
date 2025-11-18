scriptDir=$(/usr/sbin/linuxmuster-linuxclient7 get-constant scriptDir)
tmpEnvFile=$(/usr/sbin/linuxmuster-linuxclient7 get-constant tmpEnvironmentFilePath)

rm -f $tmpEnvFile

LinuxmusterLinuxclient7EnvFixActive=1 PATH=$PATH:$scriptDir/env-fix $scriptDir/onLogin

[ -f $tmpEnvFile ] && . $tmpEnvFile
rm -f $tmpEnvFile