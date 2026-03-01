import sys

class Research:

    def __init__(self, file_name):
        self.file_name = file_name

    def file_reader(self):
        try:
            with open(self.file_name, 'r') as file:
                lines = file.readlines()

            # Check if file has at least 2 lines (header + at least one data line)
            if len(lines) < 2:
                raise ValueError("File must contain a header and at least one data line")

            # Validate header
            header = lines[0].strip().split(',')
            if len(header) != 2:
                raise ValueError("Header must contain exactly two strings separated by a comma")

            # Check that both header elements are non-empty strings
            if not all(header):
                raise ValueError("Header must contain two non-empty strings")

            # Validate data lines
            for i, line in enumerate(lines[1:], start=2):  # start=2 for line numbering (header is line 1)
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                data = line.split(',')
                if len(data) != 2:
                    raise ValueError(f"Line {i}: Each data line must contain exactly two values separated by a comma")

                # Check: Both Values Either 0 or 1
                if not all(item.strip() in ['0', '1'] for item in data):
                    raise ValueError(f"Line {i}: Data values must be either 0 or 1")

                # Check: Never both 0 or both 1
                if data[0] == data[1]:
                    raise ValueError(f"Line {i}: Data line contains both values as {data[0]}, but should have one 0 and one 1")

            # If all validations pass, return the file contents
            return ''.join(lines)

        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.file_name}' not found")
        except PermissionError:
         raise PermissionError(f"Permission denied to read file '{self.file_name}'")
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def print_file(self):
        print(self.file_reader())


if __name__ == '__main__':
    if len(sys.argv) == 2:
        read_var = Research(sys.argv[1])
        read_var.print_file()
    else:
        raise ValueError("There should be a valid path to the csv file. Usage: Python3 first_constructor.py <file_path>")