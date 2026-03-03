#!/usr/bin/env python3
import sys
import resource
import time

def read_file_to_list(filename):
    try:
        with open(filename, 'r') as file:
            return [line.rstrip('\n') for line in file]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except PermissionError:
        print(f"Error: No permission to read '{filename}'.")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


if __name__ == '__main__':
    if len(sys.argv) == 2:
        usage_before = resource.getrusage(resource.RUSAGE_SELF)
        lines = read_file_to_list(sys.argv[1])
        for line in lines:
            pass
        
        usage_after = resource.getrusage(resource.RUSAGE_SELF)
        peak_memory_kib = usage_after.ru_maxrss
        peak_memory_gb = peak_memory_kib / (1024 ** 2)
        user_time = usage_after.ru_utime - usage_before.ru_utime
        system_time = usage_after.ru_stime - usage_before.ru_stime
        total_cpu_time = user_time + system_time
    
        print(f"Peak Memory Usage = {peak_memory_gb:.3f} GB")
        print(f"User Mode Time + System Mode Time = {total_cpu_time:.2f}s")

    else:
        print("Usage: $python3 ordinary.py <file_path>")
