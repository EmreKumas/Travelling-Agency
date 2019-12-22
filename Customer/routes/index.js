const express = require('express');
const Customer = require('../socket');

const router = express.Router();

// All GET and POST requests are handled here...
router.get('/', (req, res) => {

    // Get all hotel names by connecting to the agency...
    var request = {'hotel_names': true};

    var customer = new Customer();
    
    if(customer.connected){
        var server_response = customer.send_data(request);

        // After server response arrives...
        server_response.then(response => {
            res.render('index', response);
        });
    }else
        res.render(null);
});

router.post('/', (req, res) => {

    var customer = new Customer();
    
    if(customer.connected){
        var server_response = customer.send_data(req.body);

        // After server response arrives...
        server_response.then(response => {
            res.send(response);
        });
    }else
        res.send(null);
});

module.exports = router;