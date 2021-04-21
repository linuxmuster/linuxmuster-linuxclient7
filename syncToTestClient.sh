#!/bin/bash

[ -z $1 ] && echo "Usage: $0 <IP>" && exit 1

VM_IP=$1

rsync -avzp --chown 0:0 ./etc ./usr root@$VM_IP:/

inotifywait -r -m -e close_write --format '%w%f' ./etc ./usr | while read MODFILE
do
    echo need to rsync ${MODFILE%/*} ...
    rsync -avzp --chown 0:0 ./etc ./usr root@$VM_IP:/
done