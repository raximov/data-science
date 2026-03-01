import logging
from random import randint
import requests
import json

# Configure logging
logging.basicConfig(
    filename='analytics.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Research:

    def __init__(self, file_name):
        logging.info(f"Initializing Research with file: {file_name}")
        self.file_name = file_name

    def file_reader(self, has_header = True):
        logging.info(f"Reading file: {self.file_name}, has_header: {has_header}")
        try:
            with open(self.file_name, 'r') as file:
                lines = file.readlines()
                logging.info(f"Successfully read {len(lines)} lines from file")

            # Check if file has at least 2 lines (header + at least one data line)
            if has_header:
                if len(lines) < 2:
                    error_msg = "File must contain a header and at least one data line"
                    logging.error(error_msg)
                    raise ValueError(error_msg)

                # Validate header
                header = lines[0].strip().split(',')
                if len(header) != 2:
                    error_msg = "Header must contain exactly two strings separated by a comma"
                    logging.error(error_msg)
                    raise ValueError(error_msg)

                # Check that both header elements are non-empty strings
                if not all(header):
                    error_msg = "Header must contain two non-empty strings"
                    logging.error(error_msg)
                    raise ValueError(error_msg)

            elif not has_header and len(lines) < 1:
                error_msg = "File must contain at least one data line"
                logging.error(error_msg)
                raise ValueError(error_msg)
            # Validate data lines
            result = []
            for i, line in enumerate(lines[0:], start=1):  # start=2 for line numbering (header is line 1)
                line = line.strip()

                if has_header and i==1:
                    continue

                data = line.split(',')
                if len(data) != 2:
                    error_msg = f"Line {i}: Each data line must contain exactly two values separated by a comma"
                    logging.error(error_msg)
                    raise ValueError(error_msg)

                # Check: Both Values Either 0 or 1
                if not all(item.strip() in ['0', '1'] for item in data):
                    error_msg = f"Line {i}: Data values must be either 0 or 1"
                    logging.error(error_msg)
                    raise ValueError(error_msg)


                # Check: Never both 0 or both 1
                if data[0] == data[1]:
                    error_msg = f"Line {i}: Data line contains both values as {data[0]}, but should have one 0 and one 1"
                    logging.error(error_msg)
                    raise ValueError(error_msg)


                result.append([int(data[0]), int(data[1])])

            logging.info(f"Successfully processed {len(result)} data lines")
            return result

        except FileNotFoundError:
            error_msg = f"File '{self.file_name}' not found"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)
        except PermissionError:
            error_msg = f"Permission denied to read file '{self.file_name}'"
            logging.error(error_msg)
            raise PermissionError(error_msg)
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)

    def send_telegram_message(self, success=True):
        logging.info("Sending Telegram notification")
        try:
            if success:
                message = "The report has been successfully created"
            else:
                message = "The report hasn't been created due to an error"

            # Import config here to avoid circular imports
            import config

            payload = {
                'chat_id': config.telegram_chat_id,
                'text': message
            }

            response = requests.post(config.telegram_webhook_url, data=payload)
            if response.status_code == 200:
                logging.info(f"Telegram message sent successfully: {message}")
            else:
                logging.error(f"Failed to send Telegram message. Status code: {response.status_code}")

        except Exception as e:
            logging.error(f"Error sending Telegram message: {str(e)}")

    class Calculations:
        def __init__(self, data):
            logging.info(f"Initializing Calculations with {len(data)} data points")
            self.data = data

        def counts(self):
            logging.info("Calculating counts of heads and tails")
            head = sum(row[0] for row in self.data)
            tail = sum(row[1] for row in self.data)
            logging.info(f"Counts calculated: heads={head}, tails={tail}")
            return head, tail

        def fractions(self, head, tail):
            logging.info("Calculating fractions")
            total = head + tail
            head_fraction = (head / total)
            tail_fraction = (tail / total)
            logging.info(f"Fractions calculated: heads={head_fraction:.4f}, tails={tail_fraction:.4f}")
            return head_fraction, tail_fraction

    class Analytics(Calculations):
        def predict_random(self, num_predictions):
            logging.info(f"Generating {num_predictions} random predictions")
            predictions = []
            for _ in range(num_predictions):
                head = randint(0, 1)
                tail = 1 - head
                predictions.append([head, tail])
            logging.info(f"Generated {len(predictions)} random predictions")
            return predictions

        def predict_last(self):
            logging.info("Retrieving last prediction from data")
            if self.data:
                last_item = self.data[-1]
                logging.info(f"Last prediction: {last_item}")
                return last_item
            else:
                logging.warning("No data available for last prediction")
                return None

        def save_file(self, data, filename, extension='txt'):
            logging.info(f"Saving data to {filename}.{extension}")
            full_filename = f"{filename}.{extension}"
            try:
                with open(full_filename, 'w') as file:
                    file.write(data)

                logging.info(f"Successfully saved data to {full_filename}")
                return full_filename

            except Exception as e:
                error_msg = f"Error saving file {full_filename}: {str(e)}"
                logging.error(error_msg)
                raise Exception(error_msg)

