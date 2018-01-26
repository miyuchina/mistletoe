#!/usr/bin/env bash

set -e

REPO="https://github.com/commonmark/CommonMark.git"

function main {
    git clone $REPO
    cd "CommonMark"
    python3 "test/spec_tests.py" --dump-tests > "../commonmark.json"
    cd ..
    rm -rf CommonMark
}

main

