#!/bin/sh

rm -f partition_*.csv

header=$(head -n 1 ../ex03/hh_positions.csv)

tail -n +2 ../ex03/hh_positions.csv | while IFS=',' read -r id created_at name has_test url
do
    date_only=$(echo $created_at | cut -d'T' -f1)
    echo "$header" > temp.csv
    echo "$id,$created_at,$name,$has_test,$url" >> temp.csv
    if [ -f "partition_$date_only.csv" ]; then
        tail -n +2 temp.csv >> "partition_$date_only.csv"
    else
        mv temp.csv "partition_$date_only.csv"
    fi
done
rm -f temp.csv
