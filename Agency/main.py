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
def contact_hotel(meaningful_data, reserve):

    # Lets create our request message...
    body = create_body(meaningful_data, reserve)

    request = headers.format(calculate_body_size(body)) + body_starting
    for element in body:
        request += element
    request += body_ending

    # Now, we need to connect to the hotel socket and send our request...
    hotel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    response = send_data_to_socket(hotel_socket, request)

    # Processing response...
    return process_data(response)


def send_data_to_socket(target_socket, data):
    response = ''
    try:
        target_socket.connect((HOSTNAME, 9000))
        target_socket.sendall(bytes(data, encoding="utf8"))
        response = target_socket.recv(4096).decode("utf8")
        target_socket.close()
    except socket.error:
        print("Couldn't connect to the target hotel!")

    return response


def process_data(data):
    # We need to get meaningful data...
    reserved_status = None
    for line in data.splitlines():
        if "reserved" in line:
            reserved_status = line[17:-1]

    return reserved_status


def create_body(customer_data, reserve):
    body = [key_value.format('name', customer_data['name']) + key_value_comma_ending,
            key_value.format('mail', customer_data['mail']) + key_value_comma_ending,
            key_value.format('start_date', customer_data['start_date']) + key_value_comma_ending,
            key_value.format('end_date', customer_data['end_date']) + key_value_comma_ending,
            key_value.format('vacationers', customer_data['vacationers']) + key_value_comma_ending,
            key_value.format('reserve', reserve) + key_value_normal_ending]

    return body


def calculate_body_size(body):
    text = ''
    for element in body:
        text += element

    # Plus 4 is to be on the safe-side, because header-lengths could be calculated as well...
    length = len(text) + 4

    # Also we need to add one more for each unicode character...
    for element in body:
        length += sum(element.count(x) for x in ("İ", "ı", "ğ", "Ğ", "ü", "Ü", "ş", "Ş", "ö", "Ö", "ç", "Ç"))

    return length


def create_response(meaningful_data, hotel_reserved_status):

    if hotel_reserved_status == 'no_reservation':
        meaningful_data['reserved'] = 'no_reservation'
    else:
        meaningful_data['reserved'] = 'reserved'

    return json.dumps(meaningful_data, ensure_ascii=False)


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

            # Convert straight text into a dictionary...
            meaningful_data = json.loads(customer_data)

            # Set customer name...
            customer_name = meaningful_data['name']

            # Check if there is enough place in the hotel...
            hotel_reserved_status = contact_hotel(meaningful_data, "false")

            # Reserve places in the hotel if there is enough place...
            if hotel_reserved_status == 'enough_place':
                hotel_reserved_status = contact_hotel(meaningful_data, "true")

            # Create our response message back to the customer...
            response = create_response(meaningful_data, hotel_reserved_status)

            # And, send a response back to the customer...
            connection.send(bytes(response, encoding="utf8"))

        # Close the connection...
        connection.close()
        print("Customer with the name '" + customer_name + "' is disconnected!")
