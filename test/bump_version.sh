#!/usr/bin/env bash

set -e

OLD_VERSION=$1
NEW_VERSION=$2

if [[ $OLD_VERSION == "" || $NEW_VERSION == "" ]]; then
    echo "[Error] Missing version numbers."
    exit 1
fi

FILES="README.md mistletoe/__init__.py"

for FILE in $FILES; do
    sed -e "s/$OLD_VERSION/$NEW_VERSION/g" "$FILE" > "$FILE.tmp"
    mv $FILE{.tmp,}
done

git diff

