#!/usr/bin/env python3
import os

if __name__ == '__main__':
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"Your current virtual env is {venv_path}")
    else:
        print("You are not in a virtual environment.")