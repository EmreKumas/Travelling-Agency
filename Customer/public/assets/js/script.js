$(document).ready(function(){
    ready_variables();
    $(document).on('click', '.add-customer-button', insert_customer);
    $(document).on('click', '.find-vacation', postForm);
});

// Variables...
var customer_div = null;
var add_new_customer = null;
var div_height = 0;
var customer_count = 1;
var backend_responses = {};

// HTML holders...
var centerized_div = '<div class="centerized" style="position: relative; top: 50%; transform: translateY(-50%);"></div>';

var loading_image_html = '<img src="assets/img/ajax-loader.gif">';
var loading_text_html = '<h6 class="mt-3 text-monospace">Please wait while we check.</h6>';

var no_response_heading = '<h2 class="text-uppercase">no response...</h2>';
var no_response_text = '<p class="text-justify">We tried to connect to our backend but couldn\'t get a response. Please try again after 1-3 minutes...</p>';

var success_heading = '<h2 class="text-uppercase">CONGRATULATIONS...</h2></div>';
var success_text = '<p class="text-justify">We have arranged your hotel and airline tickets as you have preferred. All other details and payment information is sent to your e-mail that you have provided.</p>';

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
    var current_row_div = '<div class="row current-row">';
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

function postForm(event){
    // Prevent the page from reloading...
    event.preventDefault();

    /* We need to get the values of the clicked form. To be able to detect that, we need to get the id of the button.
       And, then we will delete the customer keyword, so only the number will be left. */
    var index = parseInt(this.id.replace("submit", ""));

    // Getting form values.
    var data = {
        "name": $('#name' + index).val(),
        "mail": $('#mail' + index).val(),
        "hotel": $('#hotel' + index).val(),
        "airline": $('#airline' + index).val(),
        "start_date": $('#start_date' + index).val(),
        "end_date": $('#end_date' + index).val(),
        "vacationers": $('#vacationers' + index).val()
    };

    // Before fade off animation, we need to set customer-div height as we have stored in the div_height variable.
    $('.customer-div-' + index).height(div_height);

    // Fade off animation of form.
    $('.customer-div-' + index).fadeOut("slow", function(){
        bring_loading(index);
    });

    // Send form informations to back-end.
    $.post('/', data, function(resp) {
        
        // var key = 'response' + index;
        // backend_responses[key] = resp;
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

    // Lets wait for at least 3 seconds and show the results.
    setTimeout(check_response, 3000, index);
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
}

function check_response_interval(index, key, number_of_tries, interval_id){

    // Finish looking if the time has passed so much like 20 sec...
    var response = backend_responses[key];

    if(response !== undefined){

        // It is set.
        clearInterval(interval_id);
        alert("It is set");
    }else{

        // It couldn't be set.
        if(number_of_tries >= 20){
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
    // Firstly, we will set centerized_div to customer-div.
    $('.customer-div-' + index).html(centerized_div);

    // Next, we will give it a unique id.
    $('.centerized').attr('id', 'centerized' + index);
    $('.centerized').removeClass('centerized');

    // Then, we will append no response heading and text to this div.
    $('#centerized' + index).append(no_response_heading);
    $('#centerized' + index).append(no_response_text);

    // Then, we will fade it in...
    $('.customer-div-' + index).fadeIn("slow");
}

function loading_result_transition(index, response){

    // After fading out loading screen, we will fade in results screen.
    $('.customer-info').fadeOut("slow", () => {
        $('.customer-info').html(success_heading);
        $('.success').append(success_text);
        // Then, we will fade it in...
        $('.customer-info').fadeIn("slow", bring_results);
    });
}

function bring_results(){

}
