#!/bin/bash

[ -z $1 ] && echo "Usage: $0 <IP>" && exit 1
VM_IP=$1

sync() {
    rsync -rltDvz --no-perms ./etc ./usr root@$VM_IP:/
    #rsync -avzp --chown 0:0 ./usr root@$VM_IP:/
    #rsync -avzp --chown 0:0 ./etc root@$VM_IP:/
}

sync

inotifywait -r -m -e close_write --format '%w%f' ./etc ./usr | while read MODFILE
do
    echo need to rsync ${MODFILE%/*} ...
    sync
done