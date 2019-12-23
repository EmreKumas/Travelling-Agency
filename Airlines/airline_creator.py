import re
import os
import json
import sqlite3
import socket


AGENCY_HOSTNAME = "localhost"
AGENCY_PORT = 80


def create_python_file(file_name, flight_capacity, port):
    # Create python file...
    python_file = open(file_name + ".py", "w+", encoding="utf8")

    # Read template file...
    template_file = open("Templates/Airline.txt", encoding="utf8")
    line = template_file.readline()

    while line:

        # We will append each line into our new python file, except three lines...
        if "ENTER_PORT" in line:
            line = line.replace("ENTER_PORT", str(port))
        elif "ENTER_DATABASE" in line:
            line = line.replace("ENTER_DATABASE", file_name + ".db")
        elif "ENTER_CAPACITY" in line:
            line = line.replace("ENTER_CAPACITY", str(flight_capacity))

        python_file.write(line)

        line = template_file.readline()

    # Close files...
    python_file.close()
    template_file.close()


def format_airline_name(airline_name):
    new_airline_name = re.sub("İ", 'I', airline_name)
    new_airline_name = re.sub("ı", 'i', new_airline_name)
    new_airline_name = re.sub("Ğ", 'G', new_airline_name)
    new_airline_name = re.sub("ğ", 'g', new_airline_name)
    new_airline_name = re.sub("Ü", 'U', new_airline_name)
    new_airline_name = re.sub("ü", 'u', new_airline_name)
    new_airline_name = re.sub("Ş", 'S', new_airline_name)
    new_airline_name = re.sub("ş", 's', new_airline_name)
    new_airline_name = re.sub("Ö", 'O', new_airline_name)
    new_airline_name = re.sub("ö", 'o', new_airline_name)
    new_airline_name = re.sub("Ç", 'C', new_airline_name)
    new_airline_name = re.sub("ç", 'c', new_airline_name)

    # Determine python file name...
    corrected_airline_name = re.sub("\s+", "_", new_airline_name.strip())  # Replace spaces with underscores
    python_file_name = corrected_airline_name.lower()  # Convert all characters to lower case

    return python_file_name, corrected_airline_name


def create_database_file(file_name):
    # Firstly, create the database...
    database = create_connection(file_name)

    # Next, create tables...
    flight_table_query = 'CREATE TABLE "flight" ( `flight_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `flight_date` TEXT )'
    execute_query(database, flight_table_query)

    reservation_table_query = 'CREATE TABLE "reservation" ( `reservation_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, ' \
                              '`owner_name` TEXT NOT NULL, `owner_mail` TEXT NOT NULL )'
    execute_query(database, reservation_table_query)

    flight_reservation_table_query = 'CREATE TABLE "flight_reservation" ( `flight_id` INTEGER NOT NULL, ' \
                                     '`reservation_id` INTEGER NOT NULL, ' \
                                     'FOREIGN KEY(`reservation_id`) REFERENCES `reservation`(`reservation_id`), ' \
                                     'FOREIGN KEY(`flight_id`) REFERENCES `flight`(`flight_id`) )'
    execute_query(database, flight_reservation_table_query)

    # Lastly, commit and close the database...
    database.commit()
    database.close()


def create_connection(file_name):

    # Before creating the database, we need to delete if database exists to prevent duplicate tables...
    if os.path.exists(file_name):
        os.remove(file_name)

    connection = None
    try:
        connection = sqlite3.connect(file_name)
    except Error as e:
        print(e)

    return connection


def execute_query(database, query):
    try:
        cursor = database.cursor()
        cursor.execute(query)
    except Error as e:
        print(e)


def contact_agency(airline_name, port):
    agency_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Create the data to send...
    data_to_send = {'register': 'airline', 'airline_name': airline_name, 'port': port}
    data_to_send = json.dumps(data_to_send, ensure_ascii=False)

    # Connect to the agency...
    try:
        agency_socket.connect((AGENCY_HOSTNAME, AGENCY_PORT))
        agency_socket.sendall(bytes(data_to_send, encoding="utf8"))
        response = agency_socket.recv(4096).decode("utf8")
        agency_socket.close()

        # Convert straight text into a dictionary...
        response = json.loads(response)

        if response['register'] == 'registered':
            return True

    except socket.error:
        print("Couldn't connect to the agency!")

    return False


if __name__ == "__main__":
    print("Welcome to the airline creator!")
    airline_name = input("Enter airline's name: ")
    flight_capacity = int(input("Enter airline's flight capacity: "))
    port = int(input("Enter airline's port: "))

    # Before sending airline_name, we change all its unicode characters into appropriate ones...
    file_name, corrected_airline_name = format_airline_name(airline_name)

    create_python_file(file_name, flight_capacity, port)
    create_database_file(file_name + ".db")

    # After the airline is created, we need to contact with the agency to add it into airline list...
    reserved_status = contact_agency(airline_name.strip(), port)

    if reserved_status:
        # Means airline created successfully and added to the airline list in agency server...
        print("\nAirline created successfully!")
        print("To run the server, just type: python " + file_name + ".py")
    else:
        # We will delete created files...
        if os.path.exists(file_name + ".py"):
            os.remove(file_name + ".py")
        if os.path.exists(file_name + ".db"):
            os.remove(file_name + ".db")
