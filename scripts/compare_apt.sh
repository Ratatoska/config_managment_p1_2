#!/usr/bin/env bash
set -euo pipefail
status=$(mktemp)
trap 'rm -f -- "$status"' EXIT
apt-get -o "Dir::State::status=$status" -s --no-install-recommends \
    install hello=2.10-3build1
apt-cache -o "Dir::State::status=$status" -o APT::Cache::GivenOnly=true \
    dotty hello jq zlib1g libc6 libjq1 libgcc-s1 gcc-14-base libonig5
