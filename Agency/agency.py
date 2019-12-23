import socket
import json
import sqlite3


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
def check_hotels(meaningful_data):
    # Lets get all hotel data and find the hotel port we want to communicate first...
    hotels = get_hotels()
    target_port = None
    hotel_reserved_status = None

    # If hotel data is actually an array, it means we have proposed some alternatives. So we need to check it...
    if isinstance(meaningful_data['hotel'], str):
        for hotel in hotels:
            if meaningful_data['hotel'] == hotel[0]:
                target_port = int(hotel[1])

        if target_port is None:
            print("This hotel does not exists anymore...")
            return None

        # Then, we contact with this hotel to check if there is enough place...
        hotel_reserved_status = contact_hotel_with_port(meaningful_data, target_port, "false")
    else:
        # Means it is an array, we will check if the customer accepted the alternate offer...
        if meaningful_data['accept_refuse'] == 'accept':
            # We will reserve the hotel at last location in hotel list...
            for hotel in hotels:
                if meaningful_data['hotel'][-1] == hotel[0]:
                    target_port = int(hotel[1])

            if target_port is None:
                print("This hotel does not exists anymore...")
                return None

            # Then, we contact with this hotel to check if there is enough place...
            hotel_reserved_status = contact_hotel_with_port(meaningful_data, target_port, "false")

    # Reserve places in the hotel if there is enough place...
    if hotel_reserved_status == 'enough_place':
        hotel_reserved_status = contact_hotel_with_port(meaningful_data, target_port, "true")
    # Else, we need to check other hotels to be able to offer alternatives...
    else:
        # If hotel data is an array, we copy all elements...
        if isinstance(meaningful_data['hotel'], str):
            visited_hotels = [meaningful_data['hotel']]
        else:
            visited_hotels = meaningful_data['hotel'].copy()
        for hotel in hotels:
            # If we have not visited, this hotel yet...
            if hotel[0] not in visited_hotels:
                target_port = int(hotel[1])

                # Then, we contact with this hotel to check if there is enough place...
                hotel_reserved_status = contact_hotel_with_port(meaningful_data, target_port, "false")

                # If this hotel has enough place, we will ask the customer...
                if hotel_reserved_status == 'enough_place' and isinstance(meaningful_data['hotel'], str):
                    meaningful_data['hotel'] = [meaningful_data['hotel'], hotel[0]]
                    break
                elif hotel_reserved_status == 'enough_place':
                    new_list = meaningful_data['hotel'].copy()
                    new_list.append(hotel[0])
                    meaningful_data['hotel'] = new_list.copy()
                    break

    return hotel_reserved_status


def contact_hotel_with_port(meaningful_data, hotel_port, reserve):

    # Lets create our request message...
    body = create_body(meaningful_data, reserve)

    request = headers.format(calculate_body_size(body)) + body_starting
    for element in body:
        request += element
    request += body_ending

    # Now, we need to connect to the hotel socket and send our request...
    hotel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    response = send_data_to_socket(hotel_socket, hotel_port, request)

    # Processing response...
    return process_data(response)


def send_data_to_socket(target_socket, target_port, data):
    response = ''
    try:
        target_socket.connect((HOSTNAME, target_port))
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

    if hotel_reserved_status == 'reserved':
        meaningful_data['reserved'] = 'reserved'
    elif hotel_reserved_status == 'enough_place':
        meaningful_data['reserved'] = 'alternate'
    else:
        meaningful_data['reserved'] = 'no_reservation'

    return json.dumps(meaningful_data, ensure_ascii=False)


def register_hotel_airline(connection, meaningful_data, table_name, name_column, port_column):

    # Connect to the database...
    database = create_connection(table_name + "s.db")

    if table_name == 'hotel':
        hotel_airline_name = meaningful_data['hotel_name']
    else:
        hotel_airline_name = meaningful_data['airline_name']

    # We insert the hotel_airline into the database...
    insert_hotel_airline = ("INSERT INTO {}({}, {}) VALUES('{}', {})"
                            .format(table_name, name_column, port_column,
                                    hotel_airline_name, int(meaningful_data['port'])))

    # We also need to send back a response to to creator...
    response = {}

    try:
        cursor = database.cursor()
        cursor.execute(insert_hotel_airline)

        # Lastly, commit and close the database...
        database.commit()
        database.close()
        response['register'] = 'registered'

    except sqlite3.Error as e:
        print(e)
        response['register'] = 'error'

    # Send a response back to the creator...
    response = json.dumps(response, ensure_ascii=False)

    connection.send(bytes(response, encoding="utf8"))


def create_connection(db_name):

    connection = None
    try:
        connection = sqlite3.connect(db_name)
    except sqlite3.Error as e:
        print(e)

    return connection


def send_hotel_names(connection):

    # First, lets get all hotel names...
    hotel_names = list(map(lambda x: x[0], get_hotels()))

    response = {'hotels': []}

    for hotel in hotel_names:
        response['hotels'].append(hotel)

    # Send a response back to the customer...
    response = json.dumps(response, ensure_ascii=False)

    connection.send(bytes(response, encoding="utf8"))


def get_hotels():
    # Connect to the database...
    database = create_connection('hotels.db')

    # Get all hotels...
    hotels = select_all_hotels(database)

    # And close the connection...
    database.close()

    return hotels


def select_all_hotels(database):
    cursor = database.cursor()

    try:
        query = "SELECT hotel_name, hotel_port FROM hotel;"
        cursor.execute(query)
    except sqlite3.Error as e:
        print(e)
        return None

    return cursor.fetchall()


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

            # We need to determine whom the connection belongs to...
            if 'register' in meaningful_data:
                # We check if this is a hotel register...
                if meaningful_data['register'] == 'hotel':
                    register_hotel_airline(connection, meaningful_data, 'hotel', 'hotel_name', 'hotel_port')
                    break
                else:
                    register_hotel_airline(connection, meaningful_data, 'airline', 'airline_name', 'airline_port')
                    break

            elif 'hotel_names' in meaningful_data:
                # Means customer wants to get all hotel names...
                send_hotel_names(connection)
                break

            # Set customer name...
            customer_name = meaningful_data['name']

            # Check if there is enough place in hotels...
            hotel_reserved_status = check_hotels(meaningful_data)

            # Create our response message back to the customer...
            response = create_response(meaningful_data, hotel_reserved_status)

            # And, send a response back to the customer...
            connection.send(bytes(response, encoding="utf8"))

        # Close the connection...
        connection.close()
