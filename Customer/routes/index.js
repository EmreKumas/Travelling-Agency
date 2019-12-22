const express = require('express');
const Customer = require('../socket');

const router = express.Router();

// All GET and POST requests are handled here...
router.get('/', (req, res) => {

    res.render('index');
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