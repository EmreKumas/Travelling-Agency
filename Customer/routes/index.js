const express = require('express');

const router = express.Router();

// All GET and POST requests are handled here...
router.post('/', (req, res) => {
    res.send(req.body);
});

module.exports = router;