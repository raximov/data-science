#!/bin/sh

INPUT="../ex02/hh_sorted.csv"
OUTPUT="hh_positions.csv"

head -n 1 "$INPUT" > "$OUTPUT"

tail -n +2 "$INPUT" | awk -F',' '
BEGIN { OFS="," }
{
    id=$1
    created_at=$2
    name=$3
    has_test=$4
    url=$5

    gsub(/^"/,"",name)
    gsub(/"$/,"",name)

    result=""

    if (name ~ /Junior/) result="Junior"
    if (name ~ /Middle/) {
        if (result=="") result="Middle"
        else result=result"/Middle"
    }
    if (name ~ /Senior/) {
        if (result=="") result="Senior"
        else result=result"/Senior"
    }

    if (result=="") result="-"

    print id,created_at,"\""result"\"",has_test,url
}
' >> "$OUTPUT"

