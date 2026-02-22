import sys


def letter_starter():
    if len(sys.argv) != 2:
        raise Exception("Wrong number of arguments")

    email = sys.argv[1]

    with open("employees.tsv", "r") as f:
        lines = f.readlines()

    name = None
    for line in lines[1:]:
        parts = line.strip().split('\t')
        if len(parts) == 3 and parts[2] == email:
            name = parts[0]
            break

    if name is None:
        raise Exception(f"Email {email} not found")

    print(f"Dear {name}, welcome to our team! We are sure that it will be "
          f"a pleasure to work with you. That's a precondition for the "
          f"professionals that our company hires.")


if __name__ == '__main__':
    letter_starter()
