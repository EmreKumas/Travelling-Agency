import re
import os
import sqlite3


def create_python_file(file_name, port):
    # Create python file...
    python_file = open(file_name + ".py", "w+", encoding="utf8")

    # Read template file...
    template_file = open("Templates/Hotel.txt", encoding="utf8")
    line = template_file.readline()

    while line:

        # We will append each line into our new python file, except two lines...
        if "ENTER_PORT" in line:
            line = line.replace("ENTER_PORT", str(port))
        elif "ENTER_DATABASE" in line:
            line = line.replace("ENTER_DATABASE", file_name + ".db")

        python_file.write(line)

        line = template_file.readline()

    # Close files...
    python_file.close()
    template_file.close()


def format_hotel_name(hotel_name):
    new_hotel_name = re.sub("İ", 'I', hotel_name)
    new_hotel_name = re.sub("ı", 'i', new_hotel_name)
    new_hotel_name = re.sub("Ğ", 'G', new_hotel_name)
    new_hotel_name = re.sub("ğ", 'g', new_hotel_name)
    new_hotel_name = re.sub("Ü", 'U', new_hotel_name)
    new_hotel_name = re.sub("ü", 'u', new_hotel_name)
    new_hotel_name = re.sub("Ş", 'S', new_hotel_name)
    new_hotel_name = re.sub("ş", 's', new_hotel_name)
    new_hotel_name = re.sub("Ö", 'O', new_hotel_name)
    new_hotel_name = re.sub("ö", 'o', new_hotel_name)
    new_hotel_name = re.sub("Ç", 'C', new_hotel_name)
    new_hotel_name = re.sub("ç", 'c', new_hotel_name)

    # Determine python file name...
    python_file_name = re.sub("\s+", "_", new_hotel_name.strip())  # Replace spaces with underscores
    python_file_name = python_file_name.lower()  # Convert all characters to lower case

    return python_file_name


def create_database_file(file_name, room_count):
    # Firstly, create the database...
    database = create_connection(file_name)

    # Next, create tables...
    room_table_query = 'CREATE TABLE "room" ( `room_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, ' \
                       '`room_number` INTEGER NOT NULL UNIQUE )'
    execute_query(database, room_table_query)

    reservation_table_query = 'CREATE TABLE "reservation" ( `reservation_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, ' \
                       '`start_date` TEXT NOT NULL, `end_date` TEXT NOT NULL, `owner_name` TEXT NOT NULL, ' \
                       '`owner_mail` TEXT NOT NULL )'
    execute_query(database, reservation_table_query)

    room_reservation_table_query = 'CREATE TABLE `room_reservation` ( `room_id` INTEGER NOT NULL, ' \
                                   '`reservation_id` INTEGER NOT NULL, ' \
                                   'FOREIGN KEY(`reservation_id`) REFERENCES `reservation`(`reservation_id`), ' \
                                   'FOREIGN KEY(`room_id`) REFERENCES `room`(`room_id`) )'
    execute_query(database, room_reservation_table_query)

    # Next, we create hotel rooms...
    current_room = 101
    create_rooms = "INSERT INTO room(room_number) VALUES({})"

    for i in range(0, room_count):
        execute_query(database, create_rooms.format(current_room))
        current_room += 1

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


if __name__ == "__main__":
    print("Welcome to the hotel creator!")
    hotel_name = input("Enter hotel's name: ")
    room_count = int(input("Enter hotel's room count: "))
    port = int(input("Enter hotel's port: "))

    # Before sending hotel_name, we will change all its unicode characters into appropriate ones...
    file_name = format_hotel_name(hotel_name)

    create_python_file(file_name, port)
    create_database_file(file_name + ".db", room_count)

    print("\nHotel created successfully!")
    print("To run the server, just type: python " + file_name + ".py")
