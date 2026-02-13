#!/bin/sh

VACANCY="$1"

URL="https://api.hh.ru/vacancies?text=$(printf '%s' "$VACANCY" | sed 's/ /%20/g')&per_page=20"

curl -s "$URL" | jq '.' > hh.json

