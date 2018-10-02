$(document).ready(function(){
    
    $('.hide-me-btn').on("click", function() {
        $('.hide-me').fadeOut("fast")
    });
        
    // This will make the button appear to confirm and actually delete a recipe
    
    $('.delete-recipe-btn').on("click", function() {
        $(this).next().show()
    });
        
});