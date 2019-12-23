import socket
import sqlite3

# ########################################### GLOBAL VARIABLES
HOSTNAME = "localhost"
PORT = 593
DATABASE = "emirates.db"
FLIGHT_CAPACITY = 12
SELECT_QUERY = "SELECT flight.flight_id, flight.flight_date, COUNT(reservation.reservation_id) FROM flight " \
               "LEFT JOIN flight_reservation ON flight.flight_id = flight_reservation.flight_id " \
               "LEFT JOIN reservation ON reservation.reservation_id = flight_reservation.reservation_id " \
               "GROUP BY(flight.flight_id);"

INSERT_FLIGHT_QUERY = "INSERT INTO flight(flight_date) VALUES('{}');"

INSERT_RESERVATION_QUERY = "INSERT INTO reservation(owner_name, owner_mail) " \
                           "VALUES('{}', '{}');"

INSERT_FLIGHT_RESERVATION_QUERY = "INSERT INTO flight_reservation VALUES({}, {});"

headers = \
    "HTTP/1.1 200 OK\r\n" \
    "Content-Type: application/json; charset=utf-8\r\n" \
    "Content-Length: {}\r\n" \
    "\r\n"

body_starting = "{\r\n"
body_ending = "}\r\n"
key_value = '    "{}": "{}"'
key_value_comma_ending = ",\r\n"
key_value_normal_ending = "\r\n"

# List of flights to reserve
flights_to_reserve = []


# ########################################### FUNCTIONS
def process_data(data):
    # First, we need to get meaningful data...
    meaningful_data = {}
    for line in data.splitlines():
        if "name" in line:
            meaningful_data['name'] = line[13:-2]
        elif "mail" in line:
            meaningful_data['mail'] = line[13:-2]
        elif "start_date" in line:
            meaningful_data['start_date'] = line[19:-2]
        elif "end_date" in line:
            meaningful_data['end_date'] = line[17:-2]
        elif "vacationers" in line:
            meaningful_data['vacationers'] = line[20:-2]
        elif "reserve" in line:
            meaningful_data['reserve'] = line[16:-1]

    return meaningful_data


def check_database(meaningful_data):
    # Lets connect to the database and get all flight data...
    database = create_db_connection()
    db_data = select_all_flights(database)

    # For each flight, we will check its dates if it is the same as customer's start and end dates...
    flights_to_reserve.clear()

    # We try to find reservable flights for all vacationers, so we need to pay attention to that...
    found_flight_start = check_available_flight(database, db_data, int(meaningful_data['vacationers']), int(meaningful_data['start_date']))
    found_flight_end = check_available_flight(database, db_data, int(meaningful_data['vacationers']), int(meaningful_data['end_date']))

    # After we check, we need to close the database...
    database.close()

    # Finally, check if flights found for both start and end dates...
    if found_flight_start is not None and found_flight_end is not None:
        flights_to_reserve.append(found_flight_start)
        flights_to_reserve.append(found_flight_end)
        return True
    else:
        return False


def check_available_flight(database, db_data, vacationer_count, flight_date):

    for flight in db_data:
        # If flight_date column(index 1) is the same as flight date, it means we can reserve it if there is free space...
        if int(flight[1]) == flight_date:

            # For capacity, we check if the count column(index 2) + vacationer_count is less than or equal to FLIGHT_CAPACITY...
            if int(flight[2]) + vacationer_count <= FLIGHT_CAPACITY:
                # If enough place, we return the id of flight...
                return int(flight[0])
            else:
                # If not enough place, we return None to indicate there is no flight that customer can reserve for this airline...
                return None

    # After loop ends, if the code reaches here, it means there is no flight created for this date.
    # If vacationer count is less than or equal to FLIGHT_CAPACITY, we create a new flight...
    if vacationer_count > FLIGHT_CAPACITY:
        # Vacationer count is so many that one flight cannot carry all of them, so return None...
        return None

    # Create a new flight...
    return create_new_flight(database, flight_date)


def create_db_connection():
    database = None
    try:
        database = sqlite3.connect(DATABASE)
    except sqlite3.Error:
        print("Couldn't connect to database!")

    return database


def select_all_flights(database):
    cursor = database.cursor()
    cursor.execute(SELECT_QUERY)

    return cursor.fetchall()


def create_new_flight(database, flight_date):

    query = INSERT_FLIGHT_QUERY.format(str(flight_date))
    cursor = database.cursor()
    cursor.execute(query)

    new_flight_id = cursor.lastrowid
    # Commit the changes
    database.commit()

    return new_flight_id


def update_database(flight_available, meaningful_data):
    # Lets connect to the database...
    database = create_db_connection()

    # We will update the database if the request message includes reserve to be true AND flight is available...
    if not flight_available:
        meaningful_data['reserved'] = 'no_reservation'
        return
    elif meaningful_data['reserve'] != 'true':
        meaningful_data['reserved'] = 'flight_available'
        return

    cursor = database.cursor()

    # For each vacationer, we will insert new query...
    vacationer_count = int(meaningful_data['vacationers'])

    for vacationer in range(0, vacationer_count):
        query = INSERT_RESERVATION_QUERY.format(meaningful_data['name'], meaningful_data['mail'])
        cursor.execute(query)
        reservation_id = cursor.lastrowid

        # Now, we insert into flight_reservation two times, both for start and end dates...
        query = INSERT_FLIGHT_RESERVATION_QUERY.format(flights_to_reserve[0], reservation_id)
        cursor.execute(query)
        query = INSERT_FLIGHT_RESERVATION_QUERY.format(flights_to_reserve[1], reservation_id)
        cursor.execute(query)

    # Commit the changes and close the database...
    database.commit()
    database.close()

    # Lastly, we will add reserved tag...
    meaningful_data['reserved'] = 'reserved'


def create_body(meaningful_data):
    body = [key_value.format('name', meaningful_data['name']) + key_value_comma_ending,
            key_value.format('mail', meaningful_data['mail']) + key_value_comma_ending,
            key_value.format('start_date', meaningful_data['start_date']) + key_value_comma_ending,
            key_value.format('end_date', meaningful_data['end_date']) + key_value_comma_ending,
            key_value.format('vacationers', meaningful_data['vacationers']) + key_value_comma_ending,
            key_value.format('reserved', meaningful_data['reserved']) + key_value_normal_ending]

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


if __name__ == "__main__":
    # Setting up the connection...
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOSTNAME, PORT))
    server.listen(5)

    # While server is running...
    while True:
        connection, address = server.accept()

        # While a connection is established...
        while True:
            data = connection.recv(4096).decode("utf8")
            # If there is no data, exit the loop...
            if not data:
                break

            # Processing data...
            meaningful_data = process_data(data)

            # Now, we need to check the database if there are available flights...
            flight_available = check_database(meaningful_data)

            # Reserving by updating the database if the request is that...
            update_database(flight_available, meaningful_data)

            # Creating body contents
            body = create_body(meaningful_data)

            # Creating response
            response = headers.format(calculate_body_size(body)) + body_starting
            for element in body:
                response += element
            response += body_ending

            connection.send(bytes(response, encoding="utf8"))

        # Close the connection...
        connection.close()
        print("Connection broken!")
