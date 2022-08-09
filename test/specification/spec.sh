#!/usr/bin/env bash

set -e

VERSION="0.28"
URL="https://spec.commonmark.org/$VERSION/spec.json"

function main {
    echo "Using version $VERSION..."

    curl -k -o commonmark.json $URL

    echo "Done."
}

main

