import sys
from analytics import *
import config

if __name__ == '__main__':

    logging.basicConfig(
        filename='analytics.log',
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("Starting report generation process")
    try:
        if len(sys.argv) == 2:
            logging.info(f"Processing file: {sys.argv[1]}")
            research = Research(sys.argv[1])
            data = research.file_reader(has_header=True)
            analytics = research.Analytics(data)
            head, tail = analytics.counts()
            head_fraction, tail_fraction = analytics.fractions(head, tail)
            random_predictions = analytics.predict_random(config.num_of_steps)
            last_prediction = analytics.predict_last()

            # Count heads and tails in predictions
            pred_heads = sum(pred[0] for pred in random_predictions)
            pred_tails = sum(pred[1] for pred in random_predictions)

            # Generate report
            report = config.report_template.format(
                total_observations=len(data),
                tails=tail,
                heads=head,
                tail_percentage=tail_fraction * 100,
                head_percentage=head_fraction * 100,
                num_steps=config.num_of_steps,
                tail_forecast=pred_tails,
                head_forecast=pred_heads
            )

            print(report)
            saved_file = analytics.save_file(report, "report", "txt")
            logging.info("Report generation completed successfully")
            print(f"\nReport saved to: {saved_file}")

            # Send success Telegram notification
            research.send_telegram_message(success=True)
            logging.info("Report generation completed successfully")

        else:
            error_msg = "There should be a valid path to the csv file. Usage: Python3 first_constructor.py <file_path>"
            logging.error(error_msg)
            raise ValueError(error_msg)

    except Exception as e:
        error_msg = f"Error in report generation: {str(e)}"
        logging.error(error_msg)
        print(f"Error: {error_msg}")

        # Send error Telegram notification
        research = Research(sys.argv[1] if len(sys.argv) >= 2 else "dummy")
        research.send_telegram_message(success=False)
        sys.exit(1)