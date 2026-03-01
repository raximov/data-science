num_of_steps = 3

report_template = """Report:
We made {total_observations} observations by tossing a coin: {tails} were tails and {heads} were heads.
The probabilities are {tail_percentage:.2f}% and {head_percentage:.2f}%, respectively.
Our forecast is that in the next {num_steps} observations we will have: {tail_forecast} tails and {head_forecast} heads."""