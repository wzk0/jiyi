#!bin/bash
VERSION=$(sed -n "5s/.*JIYI_VERSION = '\(.*\)'.*/\1/p" main.py)
echo $VERSION > JIYI_VERSION
sh version.sh
flet build apk --arch="arm64-v8a" --product="记易" --org="org.wzk" --build-version=$VERSION
