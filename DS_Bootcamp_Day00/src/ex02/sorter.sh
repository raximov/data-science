#!/bin/sh

INPUT="../ex01/hh.csv"
OUTPUT="hh_sorted.csv"

head -n 1 "$INPUT" > "$OUTPUT"
tail -n +2 "$INPUT" | sort -t',' -k2,2 -k1,1 >> "$OUTPUT"

