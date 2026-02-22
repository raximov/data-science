import sys


def names_extractor():
    if len(sys.argv) != 2:
        raise Exception("Wrong number of arguments")

    input_file = sys.argv[1]

    with open(input_file, "r") as f:
        emails = f.read().strip().split('\n')

    with open("employees.tsv", "w") as f:
        f.write("Name\tSurname\tEmail\n")
        for email in emails:
            email = email.strip()
            if not email:
                continue
            local_part = email.split('@')[0]
            parts = local_part.split('.')
            name = parts[0].capitalize()
            surname = parts[1].capitalize()
            f.write(f"{name}\t{surname}\t{email}\n")


if __name__ == '__main__':
    names_extractor()
