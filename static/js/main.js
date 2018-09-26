var editRecipeButtons = $(".edit-recipe-btn")
var deleteRecipeButtons = $(".delete-recipe-btn")
var userID = $(".user-value").val()

function removeNoneUserButton(buttonID) {
    buttonID.each(function(entry){
        var thisValue = this.id;
        if (thisValue != userID) {
            buttonID[entry].remove();
        }
    });
}

$(document).ready(function(){
    
        $('.hide-me-btn').on("click", function() {
            $('.hide-me').fadeOut("fast")
        });
        
        $('.add-ingredient-row-btn').on("click", function() {
            
        });
        
        $('.delete-recipe-btn').on("click", function() {
            $(this).next().show()
        });
        
        removeNoneUserButton(editRecipeButtons);
        removeNoneUserButton(deleteRecipeButtons);
        
    });