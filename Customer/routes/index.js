const express = require('express');

const router = express.Router();

// All GET and POST requests are handled here...
router.post('/', (req, res) => {
    
    var reservation = 'alternate';
    var response = req.body;

    if(reservation === 'reserved'){
        response['reserved'] = 'reserved';
    }else if(reservation === 'alternate'){
        response['reserved'] = 'alternate';
        response['hotel'] = '10';
        response['airline'] = '20';
    }else if(reservation === 'no_reservation'){
        response['reserved'] = 'no_reservation';
    }
    
    res.send(response);
});

module.exports = router;