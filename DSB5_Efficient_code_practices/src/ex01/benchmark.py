#!/usr/bin/env python3
import timeit

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

def compare():
    count = 90000000
    emails = get_emails()    
    print(f"Running benchmarks with {count} iterations...")
    
    print("Running loop benchmark...")
    time_loop = timeit.timeit(lambda: with_loop(emails), number=count)
    
    print("Running list comprehension benchmark...")
    time_comprehension_list = timeit.timeit(lambda: with_comprehension_list(emails), number=count)
    
    print("Running map benchmark...")
    time_map = timeit.timeit(lambda: with_map(emails), number=count)

    times = [
        (time_loop, "loop"),
        (time_comprehension_list, "list comprehension"),
        (time_map, "map")
    ]
    
    sorted_times = sorted(times, key = lambda x: x[0])
    fastest = sorted_times[0][1]
    print(f"It is better to use a {fastest}")
    time_values = [t[0] for t in sorted_times]
    print(" vs ".join(str(t) for t in time_values))


if __name__ == '__main__':
    compare()