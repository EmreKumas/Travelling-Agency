import socket
import sqlite3

# ########################################### GLOBAL VARIABLES
HOSTNAME = "localhost"
PORT = 4118
DATABASE = "hilton.db"
SELECT_QUERY = "SELECT room.room_id, room.room_number, reservation.start_date, reservation.end_date, " \
               "reservation.owner_name, reservation.owner_mail FROM room " \
               "LEFT JOIN room_reservation ON room.room_id = room_reservation.room_id " \
               "LEFT JOIN reservation ON reservation.reservation_id = room_reservation.reservation_id;"

INSERT_RESERVATION_QUERY = "INSERT INTO reservation(start_date, end_date, owner_name, owner_mail) " \
                           "VALUES({}, {}, '{}', '{}');"

INSERT_ROOM_RESERVATION_QUERY = "INSERT INTO room_reservation VALUES({}, {});"

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

# List of rooms to reserve
rooms_to_reserve = []


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
    # Lets connect to the database and get all room data...
    database = create_db_connection()
    db_data = select_all_rooms(database)

    # For each room we will check if it is not reserved for the selected time period...
    reserved_rooms = set()
    rooms_to_reserve.clear()

    # We will check this for all vacationers, we need to find reservable rooms for each of them...
    vacationer_count = int(meaningful_data['vacationers'])
    for i in range(0, vacationer_count):
        found_room = check_available_room(db_data, reserved_rooms)
        if found_room is not None:
            rooms_to_reserve.append(found_room)

    # Now, check if there are enough rooms for this vacationer group...
    if len(rooms_to_reserve) == vacationer_count:
        return database, True
    else:
        return database, False


def check_available_room(db_data, reserved_rooms):
    found_room = None
    for room in db_data:
        # If start_date column(index 2) is None, it means it is not reserved...
        # Otherwise, we will check the dates...
        if room[2] is None and room[0] not in reserved_rooms:
            found_room = int(room[0])
            reserved_rooms.add(int(room[0]))
            break
        else:
            # If this room is in the list of reserved_rooms, we don't need to check it...
            if int(room[0]) in reserved_rooms:
                continue

            # If intended end date is smaller than or equal to reserved start date, we can reserve it OR
            # if intended start date is greater than or equal to that reserved end date, we can reserve it...
            if int(meaningful_data['end_date']) <= int(room[2]) or int(meaningful_data['start_date']) >= int(room[3]):
                # If found room equals to something else, no need to change it...
                if found_room is None:
                    found_room = int(room[0])
                continue
            else:
                # If not, we will check if this room's number equals to the room_to_reserve. If yes, we will empty it.
                if int(room[0]) == found_room:
                    found_room = None
                reserved_rooms.add(int(room[0]))

    # If found_room is not None, we will add it to the reserved_rooms list...
    if found_room is not None:
        reserved_rooms.add(found_room)

    return found_room


def create_db_connection():
    database = None
    try:
        database = sqlite3.connect(DATABASE)
    except sqlite3.Error:
        print("Couldn't connect to database!")

    return database


def select_all_rooms(database):
    cursor = database.cursor()
    cursor.execute(SELECT_QUERY)

    db_data = cursor.fetchall()
    return db_data


def update_database(database, enough_place, meaningful_data):
    # We will update the database if the request message includes reserve to be true AND there is enough place...
    if not enough_place:
        meaningful_data['reserved'] = 'no_reservation'
        return
    elif meaningful_data['reserve'] != 'true':
        meaningful_data['reserved'] = 'enough_place'
        return

    cursor = database.cursor()

    for room in rooms_to_reserve:
        query = INSERT_RESERVATION_QUERY.format(meaningful_data['start_date'], meaningful_data['end_date'],
                                                meaningful_data['name'], meaningful_data['mail'])
        cursor.execute(query)
        reservation_id = cursor.lastrowid
        query = INSERT_ROOM_RESERVATION_QUERY.format(room, reservation_id)
        cursor.execute(query)

    # Commit the changes...
    database.commit()

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

            # Now, we need to check the database if there is enough place...
            database, enough_place = check_database(meaningful_data)

            # Reserving by updating the database if the request is that...
            update_database(database, enough_place, meaningful_data)

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
