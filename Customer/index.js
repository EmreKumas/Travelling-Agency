const express = require('express');
const expressLayouts = require('express-ejs-layouts');

const app = express();
const PORT = process.env.PORT || 5000;

// Serving all static files...
app.use(express.static(__dirname + '/public'));

// EJS
app.use(expressLayouts);
app.set('view engine', 'ejs');

// Bodyparser
app.use(express.urlencoded({ extended: false }));

// Routing to the index page.
app.use('/', require('./routes/index'));

// Starting the server...
app.listen(PORT, console.log(`Server started on port ${PORT}`));
