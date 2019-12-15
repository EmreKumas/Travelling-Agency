$(document).ready(function(){
    ready_variables();
    $(document).on('click', '.add-customer-button', insert_customer);
});

var customer_info = null;
var add_new_customer = null;
customer_count = 1;

function ready_variables(){
    
    // Get the html we're going to copy.
    customer_info = $(".customer-info").html();
    
    // Also get the add new customer area.
    add_new_customer = $(".add-here").html();
}

function insert_customer(){
    
    // Clear current content and replace it with new content.
    $(".add-here").html(customer_info);
    // After adding html, we will delete add-here class.
    $(".add-here").removeClass("add-here");
    customer_count++;
    
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
