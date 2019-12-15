import socket


# ########################################### CONSTANTS
HOSTNAME = socket.gethostname()
PORT = 80


if __name__ == "__main__":
    # Setting up the connection...
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOSTNAME, PORT))
    server.listen(5)

    # While server is running...
    while True:
        connection, address = server.accept()
        customer_data = ""

        # While a connection is established...
        while True:
            data = connection.recv(4096)
            # If there is no data, exit the loop...
            if not data:
                break

            # Concatenate the data...
            customer_data += data
            print(customer_data)

            # And, send a response back to the customer...
            connection.send("Welcome customer!")

        # Close the connection...
        connection.close()
        print("Customer disconnected!")
