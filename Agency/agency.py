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
def check_hotels_airlines(meaningful_data, hotel_or_airline):
    # Lets get all data and find the port we want to communicate first...
    # If we are checking hotel...
    if hotel_or_airline == "hotel":
        names_and_ports, _ = get_hotels_airlines()
        request_list = meaningful_data['hotel']
    else:
        _, names_and_ports = get_hotels_airlines()
        request_list = meaningful_data['airline']

    target_port = None
    reserved_status = None

    # If data is actually an array, it means we have proposed some alternatives. So we need to check it...
    if isinstance(request_list, str):
        for name_and_port in names_and_ports:
            if request_list == name_and_port[0]:
                target_port = int(name_and_port[1])

        if target_port is None:
            print("This {} does not exist anymore...".format(hotel_or_airline))
            return None

        # Then, we contact with this to check if there is enough place...
        reserved_status = contact_with_port(meaningful_data, target_port, "false")
    else:
        # Means it is an array, we will check if the customer accepted the alternate offer...
        if meaningful_data['accept_refuse'] == 'accept':
            # We will reserve the last location in request list...
            for name_and_port in names_and_ports:
                if request_list[-1] == name_and_port[0]:
                    target_port = int(name_and_port[1])

            if target_port is None:
                print("This {} does not exist anymore...".format(hotel_or_airline))
                return None

            # Then, we contact with this to check if there is enough place...
            reserved_status = contact_with_port(meaningful_data, target_port, "false")

    # If there is not enough place, we need to check others to be able to offer alternatives...
    if reserved_status != 'enough_place':
        # If data is an array, we copy all elements...
        if isinstance(request_list, str):
            visited_places = [request_list]
        else:
            visited_places = request_list.copy()
        for name_and_port in names_and_ports:
            # If we have not visited this yet...
            if name_and_port[0] not in visited_places:
                target_port = int(name_and_port[1])

                # Then, we contact with this to check if there is enough place...
                reserved_status = contact_with_port(meaningful_data, target_port, "false")

                # If it has enough place, we will ask the customer...
                if (reserved_status == 'enough_place' or reserved_status == 'flight_available') and \
                        isinstance(request_list, str):
                    request_list = [request_list, name_and_port[0]]
                    break
                elif reserved_status == 'enough_place' or reserved_status == 'flight_available':
                    new_list = request_list.copy()
                    new_list.append(name_and_port[0])
                    request_list = new_list.copy()
                    break
    else:
        if isinstance(request_list, str):
            meaningful_data[hotel_or_airline] = request_list
        else:
            meaningful_data[hotel_or_airline] = request_list.copy()
        return [reserved_status, target_port, None]

    # If the code reaches here, it means we propose an alternative hotel to the customer...
    if isinstance(request_list, str):
        meaningful_data[hotel_or_airline] = request_list
    else:
        meaningful_data[hotel_or_airline] = request_list.copy()
    return [reserved_status, target_port, "alternative"]


def reserve_hotel_airline(hotel_reserve_infos, airline_reserve_infos, meaningful_data):
    # Assign variables...
    hotel_alternative = hotel_reserve_infos[2]
    hotel_port = hotel_reserve_infos[1]
    hotel_reserved_status = hotel_reserve_infos[0]
    airline_alternative = airline_reserve_infos[2]
    airline_port = airline_reserve_infos[1]
    airline_reserved_status = airline_reserve_infos[0]

    # Reserve places in the hotel and airline if any of them is not an alternative.
    # Because we need to ask the customer if they want to accept the alternative before we reserve them...
    if hotel_alternative == 'alternative' or airline_alternative == 'alternative':
        meaningful_data['reserved'] = 'alternate'
        return

    # If not alternative, we need to make sure there are enough places for hotel and available flight for airline...
    if hotel_reserved_status == 'enough_place' and airline_reserved_status == 'flight_available':
        contact_with_port(meaningful_data, hotel_port, "true")
        contact_with_port(meaningful_data, airline_port, "true")

        meaningful_data['reserved'] = 'reserved'

    # If not, we will return no_reservation...
    else:
        meaningful_data['reserved'] = 'no_reservation'


def contact_with_port(meaningful_data, port, reserve):
    # Lets create our request message...
    body = create_body(meaningful_data, reserve)

    request = headers.format(calculate_body_size(body)) + body_starting
    for element in body:
        request += element
    request += body_ending

    # Now, we need to connect to the socket and send our request...
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    response = send_data_to_socket(target_socket, port, request)

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


def send_hotel_airline_names(connection):
    # First, lets get all hotel and airline names...
    hotel_names, airline_names = get_hotels_airlines()
    hotel_names = list(map(lambda x: x[0], hotel_names))
    airline_names = list(map(lambda x: x[0], airline_names))

    response = {'hotels': hotel_names.copy(), 'airlines': airline_names.copy()}

    # Send a response back to the customer...
    response = json.dumps(response, ensure_ascii=False)

    connection.send(bytes(response, encoding="utf8"))


def get_hotels_airlines():
    # Connect to the database...
    database = create_connection('hotels.db')

    # Get all hotels...
    hotels = select_all_hotels_airlines(database, 'hotel', 'hotel_name', 'hotel_port')

    # And close the connection...
    database.close()

    # Connect to the database...
    database = create_connection('airlines.db')

    # Get all airlines...
    airlines = select_all_hotels_airlines(database, 'airline', 'airline_name', 'airline_port')

    # And close the connection...
    database.close()

    return hotels, airlines


def select_all_hotels_airlines(database, table_name, name_column, port_column):
    cursor = database.cursor()

    try:
        query = "SELECT {}, {} FROM {};".format(name_column, port_column, table_name)
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

            elif 'get_hotels_airlines' in meaningful_data:
                # Means customer wants to get all hotel and airline names...
                send_hotel_airline_names(connection)
                break

            # Set customer name...
            customer_name = meaningful_data['name']

            # Check if there are enough place in hotels and airlines...
            hotel_reserve_infos = check_hotels_airlines(meaningful_data, 'hotel')
            airline_reserve_infos = check_hotels_airlines(meaningful_data, 'airline')

            # If there are enough spaces for both hotels and airlines, we will reserve them...
            reserve_hotel_airline(hotel_reserve_infos, airline_reserve_infos, meaningful_data)

            # Create our response message back to the customer...
            response = json.dumps(meaningful_data, ensure_ascii=False)

            # And, send a response back to the customer...
            connection.send(bytes(response, encoding="utf8"))

        # Close the connection...
        connection.close()
