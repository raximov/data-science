import sys


def call_center(clients, participants, recipients):
    clients_set = set(clients)
    recipients_set = set(recipients)
    result = clients_set - recipients_set
    return result


def potential_clients(clients, participants, recipients):
    clients_set = set(clients)
    participants_set = set(participants)
    result = participants_set - clients_set
    return result


def loyalty_program(clients, participants, recipients):
    clients_set = set(clients)
    participants_set = set(participants)
    result = clients_set - participants_set
    return result


def main():
    clients = ['andrew@gmail.com', 'jessica@gmail.com', 'ted@mosby.com',
               'john@snow.is', 'bill_gates@live.com', 'mark@facebook.com',
               'elon@paypal.com', 'jessica@gmail.com']
    participants = ['walter@heisenberg.com', 'vasily@mail.ru',
                    'pinkman@yo.org', 'jessica@gmail.com', 'elon@paypal.com',
                    'pinkman@yo.org', 'mr@robot.gov', 'eleven@yahoo.com']
    recipients = ['andrew@gmail.com', 'jessica@gmail.com', 'john@snow.is']

    if len(sys.argv) != 2:
        raise Exception("Wrong number of arguments")

    task = sys.argv[1]

    if task == 'call_center':
        result = call_center(clients, participants, recipients)
    elif task == 'potential_clients':
        result = potential_clients(clients, participants, recipients)
    elif task == 'loyalty_program':
        result = loyalty_program(clients, participants, recipients)
    else:
        raise Exception(f"Unknown task: {task}")

    for email in result:
        print(email)


if __name__ == '__main__':
    main()
