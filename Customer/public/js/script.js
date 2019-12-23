$(document).ready(function(){
    ready_variables();
    $(document).on('click', '.add-customer-button', insert_customer);
    $(document).on('click', '.find-vacation', post_form);
    $(document).on('click', '.alternate-accept', accept_alternative);
    $(document).on('click', '.alternate-refuse', refuse_alternative);
});

// Variables...
var customer_div = null;
var add_new_customer = null;
var div_height = 0;
var customer_count = 1;
var backend_responses = {};

// HTML holders...
var centerized_div = '<div class="centerized" style="position: relative; top: 50%; transform: translateY(-50%);"></div>';

var loading_image_html = '<img src="/img/ajax-loader.gif">';
var loading_text_html = '<h6 class="mt-3 text-monospace">Please wait while we check.</h6>';

var no_response_heading = '<h2 class="text-uppercase">no response...</h2>';
var no_response_text = '<p class="text-justify">We tried to connect to our backend but couldn\'t get a response. Please try again after 1-3 minutes...</p>';

var fail_heading = '<h2 class="text-uppercase">NO RESERVATION IS AVAILABLE...</h2>';
var fail_text = '<p class="text-justify">We checked all available hotels and airlines, it seems like there is no suitable place for the time interval you have selected. You can try to change start and end dates and check if these dates are available for your preferred hotel and airline.</p>';

var success_heading = '<h2 class="text-uppercase">CONGRATULATIONS...</h2></div>';
var success_text = '<p class="text-justify">We have reserved your hotel and airline as you have preferred. All other details and payment information is sent to your e-mail that you have provided.</p>';
var success_informations = '<div class="info-div"><div class="row info-row"><div class="col-sm-4 col-3 text-left"><label class="col-form-label d-inline underline">Name:</label></div><div class="col text-left"><label class="col-form-label d-inline info-name">Name</label></div></div><div class="row info-row"><div class="col-sm-4 col-3 text-left"><label class="col-form-label d-inline underline">E-mail:</label></div><div class="col text-left"><label class="col-form-label d-inline info-mail">E-mail</label></div></div><div class="row info-row"><div class="col-sm-4 col-3 text-left"><label class="col-form-label d-inline underline">Hotel:</label></div><div class="col text-left"><label class="col-form-label d-inline info-hotel">Hotel</label></div></div><div class="row info-row"><div class="col-sm-4 col-3 text-left"><label class="col-form-label d-inline underline">Airline:</label></div><div class="col text-left"><label class="col-form-label d-inline info-airline">Airline</label></div></div><div class="row info-row"><div class="col-sm-4 col-3 text-left"><label class="col-form-label d-inline underline">Start Date:</label></div><div class="col text-left"><label class="col-form-label d-inline info-start">Start Date</label></div></div><div class="row info-row"><div class="col-sm-4 col-3 text-left"><label class="col-form-label d-inline underline">End Date:</label></div><div class="col text-left"><label class="col-form-label d-inline info-end">End Date</label></div></div><div class="row info-row"><div class="col-sm-4 col-3 text-left"><label class="col-form-label d-inline underline">Vacationers:</label></div><div class="col text-left"><label class="col-form-label d-inline info-vacationers">Vacationers</label></div></div></div>';

var alternate_heading = '<h2 class="text-uppercase">NO RESERVATION IS AVAILABLE...</h2>';
var alternate_text = '<p class="text-justify">We checked your preferred hotel and airline, it seems like there is no suitable place for the time interval you have selected. But we have an alternative option for you. If you agree, we will reserve with these options. If you disagree, we will try to give you some other alternatives.</p>';
var alternate_hotel_airline_div = '<div class="info-div"><div class="row info-row"><div class="col-sm-3 col-2 text-left"><label class="col-form-label d-inline underline">Hotel:</label></div><div class="col text-left"><label class="col-form-label d-inline alternate-hotel">Hotel</label></div></div><div class="row info-row"><div class="col-sm-3 col-2 text-left"><label class="col-form-label d-inline underline">Airline:</label></div><div class="col text-left"><label class="col-form-label d-inline alternate-airline">Airline</label></div></div></div>';
var alternate_buttons = '<div class="row" id="accept-refuse-div"><div class="col-auto text-right align-self-center"><button id="alternate-accept-1" class="btn btn-dark alternate-accept" type="button">Accept</button></div><div class="col text-left align-self-center"><button id="alternate-refuse-1" class="btn btn-outline-danger alternate-refuse" type="button">Refuse</button></div></div>';

function ready_variables(){
    
    // Get the html we're going to copy.
    customer_div = $('.customer-div-1').html();
    
    // Also get the add new customer area.
    add_new_customer = $('.add-here').html();

    // Set div_height.
    div_height = $('.customer-div-1').innerHeight();
}

function insert_customer(){
    
    // A new customer added.
    customer_count++;

    // Clear current content and replace it with new content.
    // But before we add the HTML, we need to set different IDs for the new_customer.
    var new_customer = customer_div.replace('id="name1"', 'id="name' + customer_count + '"'); // Name field
    new_customer = new_customer.replace('id="mail1"', 'id="mail' + customer_count + '"'); // Mail field
    new_customer = new_customer.replace('id="hotel1"', 'id="hotel' + customer_count + '"'); // Hotel field
    new_customer = new_customer.replace('id="airline1"', 'id="airline' + customer_count + '"'); // Airline field
    new_customer = new_customer.replace('id="start_date1"', 'id="start_date' + customer_count + '"'); // start_date field
    new_customer = new_customer.replace('id="end_date1"', 'id="end_date' + customer_count + '"'); // end_date field
    new_customer = new_customer.replace('id="vacationers1"', 'id="vacationers' + customer_count + '"'); // vacationers field
    new_customer = new_customer.replace('id="submit1"', 'id="submit' + customer_count + '"'); // Submit button
    
    $(".add-here").html(new_customer);
    
    // After adding html, we will add customer-div class and delete add-here class.
    $(".add-here").addClass("customer-div-" + customer_count);
    $(".add-here").removeClass("add-here");
    
    new_customer_added();
}

function new_customer_added(){
    
    // Let's add a new block for the users to be able to add new customers.
    var current_row_div = '<div class="row customer-row current-row">';
    var col_five_div = '<div class="col-5 text-center align-self-center add-here">';
    var col_two_div = '<div class="col-2">';
    
    // If customer number is even, we will add new row.
    if(customer_count % 2 == 0){
        // Preparation
        $(".current-row").addClass("after-this");
        $(".current-row").removeClass("current-row");
        
        // Actions
        $(".after-this").after(current_row_div);
        $(".current-row").append(col_five_div);
        $(".add-here").append(add_new_customer);
        
        // Maintenance
        $(".after-this").removeClass("after-this");
    }else{
        $(".current-row").append(col_two_div);
        $(".current-row").append(col_five_div);
        $(".add-here").append(add_new_customer);
    }
}

function post_form(event){
    // Prevent the page from reloading...
    event.preventDefault();

    /* We need to get the values of the clicked form. To be able to detect that, we need to get the id of the button.
       And, then we will delete the customer keyword, so only the number will be left. */
    var index = parseInt(this.id.replace("submit", ""));

    // Before posting form, we will convert dates into a number to be able to evaluate easier...
    var start_date_converted = (new Date($('#start_date' + index).val())).getTime() / 1000;
    var end_date_converted = (new Date($('#end_date' + index).val())).getTime() / 1000;

    // Getting form values.
    var data = {
        "name": $('#name' + index).val(),
        "mail": $('#mail' + index).val(),
        "hotel": $('#hotel' + index).val(),
        "airline": $('#airline' + index).val(),
        "start_date": start_date_converted,
        "end_date": end_date_converted,
        "vacationers": $('#vacationers' + index).val()
    };

    // Before fade off animation, we need to set customer-div height as we have stored in the div_height variable.
    $('.customer-div-' + index).height(div_height);

    // Fade off animation of form.
    $('.customer-div-' + index).fadeOut("slow", function(){
        bring_loading(index);
    });

    jQuery.ajaxSettings.traditional = true;

    // Send form informations to back-end.
    $.post('/', data, function(resp) {
        
        var key = 'response' + index;
        backend_responses[key] = resp;
    });
}

function bring_loading(index){

    // Firstly, we will set centerized_div to customer-div.
    $('.customer-div-' + index).html(centerized_div);

    // Next, we will give it a unique id.
    $('.centerized').attr('id', 'centerized' + index);
    $('.centerized').removeClass('centerized');

    // Then, we will append loading image and text to this div.
    $('#centerized' + index).append(loading_image_html);
    $('#centerized' + index).append(loading_text_html);

    // Then, we will fade it in...
    $('.customer-div-' + index).fadeIn("slow");

    // Lets wait for at least 2 seconds and show the results.
    setTimeout(check_response, 2000, index);
}

function check_response(index){

    // If after 3 seconds the response from backend has not been arrived, we will wait until the response arrive.
    var key = 'response' + index;
    var response = backend_responses[key];

    if(response === undefined){
        
        // Try to set response variable every second...
        let responseTimer = setInterval(() => {
            response = backend_responses[key];
        }, 1000);

        // Check each second if it set...
        setTimeout(check_response_interval, 1000, index, key, 1, responseTimer);
    }

    if(response !== undefined)
        // Fade off animation.
        $('.customer-div-' + index).fadeOut("slow", function(){
            response_arrived(index, response);
        });
}

function check_response_interval(index, key, number_of_tries, interval_id){

    // Finish looking if the time has passed so much like 20 sec...
    var response = backend_responses[key];

    if(response !== undefined){

        // It is set.
        clearInterval(interval_id);
        // Fade off animation.
        $('.customer-div-' + index).fadeOut("slow", function(){
            response_arrived(index, response);
        });
    }else{

        // It couldn't be set.
        if(number_of_tries >= 10){
            clearInterval(interval_id);
            // Fade off animation.
            $('.customer-div-' + index).fadeOut("slow", function(){
                no_response(index);
            });
        }else
            setTimeout(check_response_interval, 1000, index, key, number_of_tries + 1, interval_id);
    }
}

function no_response(index){
    // Firstly, we will need to delete everything inside the div.
    $('#centerized' + index).empty();

    // Then, we will append no response heading and text to this div.
    $('#centerized' + index).append(no_response_heading);
    $('#centerized' + index).append(no_response_text);

    // Then, we will fade it in...
    $('.customer-div-' + index).fadeIn("slow");
}

function response_arrived(index, response){

    // After response arrives, we will check if it is a success.
    if(response['reserved'] === 'reserved')
        success_screen(index, response);
    else if(response['reserved'] === 'alternate')
        alternate_screen(index, response);
    else
        fail_screen(index);
}

function success_screen(index, response){
    // Firstly, we will need to delete everything inside the div.
    $('#centerized' + index).empty();

    // Then, we will append success heading and text to this div.
    $('#centerized' + index).append(success_heading);
    $('#centerized' + index).append(success_text);
    $('#centerized' + index).append(success_informations);

    // After appending success_informations, we need to set unique ids to each element.
    $('.info-name').attr('id', 'info-name-' + index);
    $('.info-name').removeClass('info-name');
    $('.info-mail').attr('id', 'info-mail-' + index);
    $('.info-mail').removeClass('info-mail');
    $('.info-hotel').attr('id', 'info-hotel-' + index);
    $('.info-hotel').removeClass('info-hotel');
    $('.info-airline').attr('id', 'info-airline-' + index);
    $('.info-airline').removeClass('info-airline');
    $('.info-start').attr('id', 'info-start-' + index);
    $('.info-start').removeClass('info-start');
    $('.info-end').attr('id', 'info-end-' + index);
    $('.info-end').removeClass('info-end');
    $('.info-vacationers').attr('id', 'info-vacationers-' + index);
    $('.info-vacationers').removeClass('info-vacationers');

    // Before we set informations, we need to convert timestamps into date, back again.
    start_date_converted = new Date(response['start_date'] * 1000);
    start_date_converted = zeroPad(start_date_converted.getDate(), 2) + '.' +
                           zeroPad((start_date_converted.getMonth() + 1), 2) + '.' +
                           zeroPad(start_date_converted.getFullYear(), 4);
    end_date_converted = new Date(response['end_date'] * 1000);
    end_date_converted = zeroPad(end_date_converted.getDate(), 2) + '.' +
                           zeroPad((end_date_converted.getMonth() + 1), 2) + '.' +
                           zeroPad(end_date_converted.getFullYear(), 4);

    // Set informations based on response.
    $('#info-name-' + index).text(response['name']);
    $('#info-mail-' + index).text(response['mail']);


    // Set informations based on response.
    if(Array.isArray(response['hotel']))
        $('#info-hotel-' + index).text(response['hotel'][(response['hotel'].length) - 1]);
    else
        $('#info-hotel-' + index).text(response['hotel']);

    if(Array.isArray(response['airline']))
        $('#info-airline-' + index).text(response['airline'][(response['airline'].length) - 1]);
    else
        $('#info-airline-' + index).text(response['airline']);    
    
    $('#info-start-' + index).text(start_date_converted);
    $('#info-end-' + index).text(end_date_converted);
    $('#info-vacationers-' + index).text(response['vacationers']);

    // Then, we will fade it in...
    $('.customer-div-' + index).fadeIn("slow");
}

// A useful function...
function zeroPad(num, places) {
    return String(num).padStart(places, '0')
}

function alternate_screen(index, response){
    // Firstly, we will need to delete everything inside the div.
    var div_id = "#centerized" + index;
    $(div_id).empty();

    // Then, we will append alternate heading and text to this div.
    $(div_id).append(alternate_heading);
    $(div_id).append(alternate_text);
    $(div_id).append(alternate_hotel_airline_div);
    $(div_id).append(alternate_buttons);

    // After appending alternate screen, we need to set unique ids to each element.
    $('.alternate-hotel').attr('id', 'alternate-hotel-' + index);
    $('.alternate-hotel').removeClass('alternate-hotel');
    $('.alternate-airline').attr('id', 'alternate-airline-' + index);
    $('.alternate-airline').removeClass('alternate-airline');
    $(div_id + ' .alternate-accept').attr('id', 'alternate-accept-' + index);
    $(div_id + ' .alternate-refuse').attr('id', 'alternate-refuse-' + index);

    // Set informations based on response.
    if(Array.isArray(response['hotel']))
        $('#alternate-hotel-' + index).text(response['hotel'][(response['hotel'].length) - 1]);
    else
        $('#alternate-hotel-' + index).text(response['hotel']);

    if(Array.isArray(response['airline']))
        $('#alternate-airline-' + index).text(response['airline'][(response['airline'].length) - 1]);
    else
        $('#alternate-airline-' + index).text(response['airline']);

    // Then, we will fade it in...
    $('.customer-div-' + index).fadeIn("slow");
}

function fail_screen(index){
    // Firstly, we will need to delete everything inside the div.
    $('#centerized' + index).empty();

    // Then, we will append fail heading and text to this div.
    $('#centerized' + index).append(fail_heading);
    $('#centerized' + index).append(fail_text);

    // Then, we will fade it in...
    $('.customer-div-' + index).fadeIn("slow");
}

function accept_alternative(){
    var index = parseInt(this.id.replace("alternate-accept-", ""));
    var key = 'response' + index;

    // Fade off animation of form.
    $('.customer-div-' + index).fadeOut("slow", function(){
        bring_loading(index);
    });

    var data = backend_responses[key];
    data['accept_refuse'] = 'accept';

    jQuery.ajaxSettings.traditional = true;

    // Send form informations to back-end.
    $.post('/', data, function(resp) {
        
        backend_responses[key] = resp;
    });
}

function refuse_alternative(){
    var index = parseInt(this.id.replace("alternate-refuse-", ""));
    var key = 'response' + index;

    // Fade off animation of form.
    $('.customer-div-' + index).fadeOut("slow", function(){
        bring_loading(index);
    });

    var data = backend_responses[key];
    data['accept_refuse'] = 'refuse';

    jQuery.ajaxSettings.traditional = true;

    // Send form informations to back-end.
    $.post('/', data, function(resp) {
        
        var key = 'response' + index;
        backend_responses[key] = resp;
    });
}
