#!/usr/bin/env python3
import timeit
import sys

def get_emails():
    emails = [
     'john@gmail.com',
     'james@gmail.com', 
     'alice@yahoo.com', 
     'anna@live.com',
     'philipp@gmail.com'
    ]
    return emails * 5


def with_loop(emails):
    result = []
    for email in emails:
        if email.endswith("@gmail.com"):
            result.append(email)
    return result

def with_comprehension_list(emails):
    return [email for email in emails if email.endswith("@gmail.com")]

def with_map(emails):
    return list(map(lambda email: email if email.endswith('@gmail.com') else None, emails))

def with_filter(emails):
     return list(filter(None, map(lambda email: email if email.endswith('@gmail.com') else None, emails)))

def process(task, count):
    emails = get_emails()
    if task == "loop":    
        time_loop = timeit.timeit(lambda: with_loop(emails), number=count)
        print(time_loop)
    elif task == "list_comprehension": 
        time_comprehension_list = timeit.timeit(lambda: with_comprehension_list(emails), number=count)
        print(time_comprehension_list)
    elif task == "map":
        time_map = timeit.timeit(lambda: with_map(emails), number=count)
        print(time_map)
    elif task == "filter":
        time_filter = timeit.timeit(lambda: with_filter(emails), number=count)
        print(time_filter)
    else:
        print ("Error: Task type not found.")
    


if __name__ == '__main__':
    if len(sys.argv) == 3:
        try:
            process(sys.argv[1], int(sys.argv[2]))
        except ValueError:
            print("Error: Second argument needs to be an integer")
    else:
        print("Usage: $python3 benchmark.py <task> <count>")
        print("Example: $python3 benchmark.py loop 100000")
