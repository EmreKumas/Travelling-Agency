const express = require('express');

const router = express.Router();

// All GET and POST requests are handled here...
router.post('/', (req, res) => {
    console.log(req.body);
    res.send("CEVAP");
});

module.exports = router;