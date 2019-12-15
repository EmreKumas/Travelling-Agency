const express = require('express');

const app = express();
const PORT = process.env.PORT || 5000;

// Serving all static files...
app.use(express.static("public"));

// Routing to the index page.
app.use('/', require('./routes/index'));

// Starting the server...
app.listen(PORT, console.log(`Server started on port ${PORT}`));
