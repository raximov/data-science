#!/bin/sh

INPUT="../ex03/hh_positions.csv"

head -n 1 "$INPUT" > header.tmp

tail -n +2 "$INPUT" | while IFS=',' read -r id created_at name has_test url
do
    clean_date=$(echo "$created_at" | tr -d '"' | cut -d'T' -f1)
    FILE="partition_$clean_date.csv"

    if [ ! -f "$FILE" ]; then
        cat header.tmp > "$FILE"
    fi

    echo "$id,$created_at,$name,$has_test,$url" >> "$FILE"
done

rm header.tmp

