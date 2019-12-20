const net = require('net');

const HOSTNAME = "localhost";
const PORT = 80;

class Customer{

    constructor(){
        this.customer = new net.Socket();
        this.connected = true;

        // Create a connection once an object is initialized.
        this.customer.connect(PORT, HOSTNAME);

        // Preventing back-end from collapsing if a connection cannot be established...
        this.customer.on('error', _ => {
            this.connected = false;
            console.log("Couldn't connect to the backend!");
        });
    }

    send_data(customer_data){
        return new Promise(resolve => {
            this.customer.on('connect', _ => {
                // Send customer data to agency socket.
                this.customer.write(JSON.stringify(customer_data));
            });

            this.customer.on('data', (data) => {
                // We will return the text we get from the agency socket after decoding it...
                var response = new Buffer.from(data).toString('utf8');

                // Convert it to a JSON.
                resolve(JSON.parse(response));
                this.customer.destroy();
            });
        });
    }
}

module.exports = Customer;