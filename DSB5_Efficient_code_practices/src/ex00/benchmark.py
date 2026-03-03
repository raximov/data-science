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
    result = [email for email in emails if email.endswith("@gmail.com")]
    return result

def compare():
    emails = get_emails()
    
    print("Running loop benchmark...")
    time_loop = timeit.timeit(lambda: with_loop(emails), number=90000000)
    
    print("Running list comprehension benchmark...")
    time_comprehension_list = timeit.timeit(lambda: with_comprehension_list(emails), number=90000000)

    if time_loop<time_comprehension_list:
        print('It is better to use a loop')
        print(time_loop, " vs ", time_comprehension_list)
    else:
        print("It is better to use a list comprehension")
        print(time_comprehension_list, " vs ", time_loop)

if __name__ == '__main__':
    compare()