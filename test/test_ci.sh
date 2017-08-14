#!/usr/bin/env bash

set -e

function main {
    if [[ "$1" == "" ]]; then
        echo "[Error] Specify how far you want to go back."
        exit 1
    fi

    CURR_BRANCH="$(get_current_branch)"

    git checkout --quiet HEAD~$1
    render_to_file "out2.html"
    OLD_SHA=$(get_sha "out2.html")

    git checkout --quiet "$CURR_BRANCH"
    render_to_file "out.html"
    NEW_SHA=$(get_sha "out2.html")

    if [[ "$OLD_SHA" == "$NEW_SHA" ]]; then
        cleanup
    else
        get_diff
    fi
}

function get_current_branch {
    git rev-parse --abbrev-ref HEAD
}

function render_to_file {
    python3 -m mistletoe "test/samples/syntax.md" > "$1"
}

function get_sha {
    md5 -q "$1"
}

function cleanup {
    echo "All good."
    rm out2.html
}

function get_diff {
    echo "Diff exits; prompting for review..."
    diff out.html out2.html | view -
}

main $1
