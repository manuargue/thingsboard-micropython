#!/usr/bin/bash
# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

set -e

upload=n
clean=n
build=n

usage() {
    echo "usage: PYPI_CREDENTIALS=user:password ./package.sh [--upload] [--clean] [--build]"
}

if [[ "$@" -eq 0 ]]; then
    usage
    exit 1
fi

for i in "$@"; do
    case $i in
        --upload|-u)
            upload=y
            ;;
        --clean|-c)
            clean=y
            ;;
        --build|-b)
            build=y
            ;;
        *)
            usage
            exit 1
            ;;
    esac
    shift
done

if [ "$clean" == "y" ]; then
    rm -rf dist/ thingsboard_micropython.egg-info/ __pycache__/ MANIFEST
fi

if [ "$build" == "y" ]; then
    python3 setup.py sdist
    twine check dist/thingsboard-micropython-*.tar.gz
fi

if [ "$upload" == "y" ]; then
    user="${PYPI_CREDENTIALS/:*}"
    password="${PYPI_CREDENTIALS#*:}"
    twine upload dist/thingsboard-micropython-*.tar.gz -u "$user" -p "$password"
fi
