import socket
import json


# ########################################### CONSTANTS
HOSTNAME = "localhost"
PORT = 80


# ########################################### FUNCTIONS
# noinspection PyShadowingNames
def process_customer_data(data):

    customer_data = json.loads(data)

    # Add a reserved field to indicate if it is reserved or not.
    customer_data['reserved'] = 'reserved'

    return json.dumps(customer_data, ensure_ascii=False), customer_data['name']


if __name__ == "__main__":
    # Setting up the connection...
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOSTNAME, PORT))
    server.listen(5)

    # Empty string for customer name...
    customer_name = ""

    # While server is running...
    while True:
        connection, address = server.accept()

        # While a connection is established...
        while True:
            customer_data = connection.recv(4096).decode("utf8")
            # If there is no data, exit the loop...
            if not customer_data:
                break

            # Process customer data...
            customer_data, customer_name = process_customer_data(customer_data)

            # And, send a response back to the customer...
            connection.send(bytes(customer_data, encoding="utf8"))

        # Close the connection...
        connection.close()
        print("Customer with the name '" + customer_name + "' is disconnected!")
