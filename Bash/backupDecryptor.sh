#!/bin/bash

KEY="$HOME/.gnupg/private-keys-v1.d/armored_key.asc"
BACKUP="/var/www/hacknet/backups"
OUTPUT="/tmp"
PASS="< Sandy Password >"

gpg --import "$KEY"

for file in "$BACKUP"/*.gpg; do
    filename=$(basename "$file" .gpg)
    outpath="$OUTPUT/$filename.sql"
    echo "🔵 Decrypting $file -> $outpath"

    if [ -n "$PASS" ]; then
        gpg --batch --yes --passphrase "$PASS" --pinentry-mode loopback -o "$outpath" -d "$file"
    else
        gpg --batch --yes -o "$outpath" -d "$file"
    fi

done

echo "🟢 Done! Files will be in $OUTPUT"