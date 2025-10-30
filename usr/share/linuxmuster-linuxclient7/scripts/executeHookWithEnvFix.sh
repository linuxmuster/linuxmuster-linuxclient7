# This script calls the desired hook and sources the temporary env
# file afterwards to apply environment changes from lmn-export and lmn-unset

scriptDir=$(/usr/sbin/linuxmuster-linuxclient7 get-constant scriptDir)

if [ ! -f $scriptDir/$1 ]; then
    echo "Unknown hook: $1!"
    return 1
    exit 1
fi

export LinuxmusterLinuxclient7EnvFixActive=1
tmpEnvFile=$(/usr/sbin/linuxmuster-linuxclient7 get-constant tmpEnvironmentFilePath)

rm -f $tmpEnvFile

# call hook script
$scriptDir/$1

unset LinuxmusterLinuxclient7EnvFixActive
source $tmpEnvFile 2> /dev/null
rm -f $tmpEnvFile