#!/usr/bin/env python3
import timeit
import random
from collections import Counter

def get_list():
    million = 1000000
    return [random.randrange(101) for _ in range(million)]

def create_dictionary_manual(mil_list):
    dictionary = {}
    for n in range(101):
        dictionary[n] = 0
    for n in mil_list:
        dictionary[n] += 1    
    return dictionary

def get_top_10_manual(d):
    sorted_items = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_items[:10])

def create_dictionary_counter(mil_list):
    return Counter(mil_list)

def get_top_10_counter(counter):
    return dict(counter.most_common(10))

if __name__ == '__main__':
    mil_list = get_list()
    dic_manual = create_dictionary_manual(mil_list)
    dic_counter = create_dictionary_counter(mil_list)
    time_my_function = timeit.timeit(lambda: create_dictionary_manual(mil_list), number = 10)
    time_counter = timeit.timeit(lambda: create_dictionary_counter(mil_list), number = 10)
    time_my_function_top = timeit.timeit(lambda: get_top_10_manual(dic_manual), number = 10)
    time_counter_top = timeit.timeit(lambda: get_top_10_counter(dic_counter), number = 10)
    print(f"my function: {time_my_function:.7f}\nCounter: {time_counter:.7f}\nmy top: {time_my_function_top:.7f}\nCounter's top:{time_counter_top:.7f}")
