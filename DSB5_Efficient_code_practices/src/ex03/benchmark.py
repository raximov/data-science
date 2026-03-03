#!/usr/bin/env python3
import timeit
import sys
from functools import reduce


def with_loop(number):
    sum = 0
    for n in range(1, number+1):
        sum += (n*n)
    return sum
    
def with_reduce(number):
    return reduce(
        lambda running_total, current_num: running_total + current_num ** 2,
        range(1, number + 1), 0
        )

def process(task, count, number):
    if task == "loop":    
        time_loop = timeit.timeit(lambda: with_loop(number), number=count)
        print(time_loop)
    elif task == "reduce":
        time_filter = timeit.timeit(lambda: with_reduce(number), number=count)
        print(time_filter)
    else:
        print ("Error: Task type not found.")
    


if __name__ == '__main__':
    if len(sys.argv) == 4:
        try:
            count = int(sys.argv[2])
            number = int(sys.argv[3])
            if(count < 1 or number < 1):
                print("Error: Both count and number needs to be greater than or equal to 1")
            else:
                process(sys.argv[1], count, number)
        except ValueError:
            print("Error: 2nd and 3rd arguments need to be integers")
            print("Usage: $python3 benchmark.py <task> <count> <number>")
            print("Example: $python3 benchmark.py loop 100000 5")
    else:
        print("Usage: $python3 benchmark.py <task> <count> <number>")
        print("Example: $python3 benchmark.py loop 100000")
