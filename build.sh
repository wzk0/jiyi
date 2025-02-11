#!/bin/bash

build_version=0.4.0

sh version.sh

export https_proxy="http://127.0.0.1:2080"

flet build apk --arch=arm64-v8a --product=记易 --org=org.wzk --build-version="${build_version}"