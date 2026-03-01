import sys
from random import randint

class Research:

    def __init__(self, file_name):
        self.file_name = file_name

    def file_reader(self, has_header = True):
        try:
            with open(self.file_name, 'r') as file:
                lines = file.readlines()

            # Check if file has at least 2 lines (header + at least one data line)
            if has_header:
                if len(lines) < 2:
                    raise ValueError("File must contain a header and at least one data line")

                # Validate header
                header = lines[0].strip().split(',')
                if len(header) != 2:
                    raise ValueError("Header must contain exactly two strings separated by a comma")

                # Check that both header elements are non-empty strings
                if not all(header):
                    raise ValueError("Header must contain two non-empty strings")
            elif not has_header and len(lines) < 1:
                raise ValueError("File must contain at least one data line")
            # Validate data lines
            result = []
            for i, line in enumerate(lines[0:], start=1):  # start=2 for line numbering (header is line 1)
                line = line.strip()

                if has_header and i==1:
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

                result.append([int(data[0]), int(data[1])])
            # If all validations pass, return the file contents
            return result

        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.file_name}' not found")
        except PermissionError:
            raise PermissionError(f"Permission denied to read file '{self.file_name}'")
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    class Calculations:
        def __init__(self, data):
            self.data = data

        def counts(self):
            head = sum(row[0] for row in self.data)
            tail = sum(row[1] for row in self.data)
            return head, tail

        def fractions(self, head, tail):
            total = head + tail
            head_fraction = (head / total)
            tail_fraction = (tail / total)
            return head_fraction, tail_fraction

    class Analytics(Calculations):
        def predict_random(self, num_predictions):
            predictions = []
            for _ in range(num_predictions):
                head = randint(0, 1)
                tail = 1 - head
                predictions.append([head, tail])
            return predictions

        def predict_last(self):
            if self.data:
                return self.data[-1]
            else:
                return None


if __name__ == '__main__':
    if len(sys.argv) == 2:
        research = Research(sys.argv[1])
        data = research.file_reader(has_header=True)
        analytics = research.Analytics(data)
        head, tail = analytics.counts()
        head_fraction, tail_fraction = analytics.fractions(head, tail)
        random_predictions = analytics.predict_random(3)
        last_prediction = analytics.predict_last()
        print(data)
        print(head, tail)
        print(f"{head_fraction:.4f} {tail_fraction:.4f}")
        print(random_predictions)
        print(last_prediction)

    else:
        raise ValueError("There should be a valid path to the csv file. Usage: Python3 first_constructor.py <file_path>")