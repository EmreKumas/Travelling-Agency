import socket
import json


# ########################################### CONSTANTS
HOSTNAME = "localhost"
PORT = 80
headers = \
          "POST / HTTP/1.1\r\n" \
          "Content-Type: application/json; charset=utf-8\r\n" \
          "Content-Length: {}\r\n" \
          "\r\n"

body_starting = "{\r\n"
body_ending = "}\r\n"
key_value = '    "{}": "{}"'
key_value_comma_ending = ",\r\n"
key_value_normal_ending = "\r\n"


# ########################################### FUNCTIONS
# noinspection PyShadowingNames
def process_customer_data(data):

    customer_data = json.loads(data)

    # Now, we need to contact with hotels and airlines.
    contact_hotels()

    # Add a reserved field to indicate if it is reserved or not.
    customer_data['reserved'] = 'reserved'

    return json.dumps(customer_data, ensure_ascii=False), customer_data['name']


def contact_hotels():

    # Lets create our request message...
    body = []

    request = headers.format('61') + body_starting
    for element in body:
        request += element
    request += body_ending

    # Now, we need to connect to the hotel socket...
    hotel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        hotel_socket.connect((HOSTNAME, 9000))
        hotel_socket.sendall(bytes(request, encoding="utf8"))
        response = hotel_socket.recv(4096).decode("utf8")
        hotel_socket.close()
    except socket.error:
        print("Couldn't connect to the target hotel!")


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
