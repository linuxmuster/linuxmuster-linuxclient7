#!/bin/bash

# DO NOT MODIFY THIS SCRIPT! Changes will be overwritten by updates!
# For custom scripts create your own script in this directory, this is just and example.

echo "onShutdown.d Hook called with env:"
echo "Sysvol: $SYSVOL"
echo "Domain: $Network_domain"
echo "Server hostname: $Network_serverHostname"
echo "Room: $Computer_sophomorixAdminClass"
Computer_hardwareGroup=$(echo $Computer_memberOf | grep 'OU=device-groups' | awk '{ print $2 }' | awk -F\, '{ print $1 }' | awk -F\= '{ print $2 }' | sed -r 's/^d_//')
echo "Hardware group: $Computer_hardwareGroup"