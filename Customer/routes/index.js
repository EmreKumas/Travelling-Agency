const express = require('express');
const Customer = require('../socket');

const router = express.Router();

// All GET and POST requests are handled here...
router.post('/', (req, res) => {

    var customer = new Customer();
    var server_response = customer.send_data(req.body);

    // After server response arrives...
    server_response.then(response => {
        res.send(response);
    });
});

module.exports = router;