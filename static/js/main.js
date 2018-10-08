// GLOBAL VARIABLES ------------------------------------------------------------

var mongodbRecipeIngredientData = $('#recipe_ingredients').val();

// FUNCTIONS -------------------------------------------------------------------

function updateDatabase(){

// This function will push updated information to the database without having to refresh the page...
    
    var recipeID = $('.recipe-id').val()
    
    $.ajax({
        url: '/update_recipe/' + recipeID,
        data: $('form').serialize(),
        type: 'POST',
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function dataToJSON(databaseExtract){

// This function converts any data pulled from MONGODB into a list of JSON objects
    
    var convertToString = JSON.stringify(databaseExtract);
    var revisedString = convertToString.replace(/u'/g,"'");
    var almostJsonData = JSON.parse(revisedString);
    var almostJsonData2 = almostJsonData.replace(/'/g,"\"");
    var jsonData = JSON.parse(almostJsonData2);
    
    return jsonData;
}

// May not need this function now...

// function showRecipeIngredients(databaseExtract){
//     var recipeIngredients = dataToJSON(databaseExtract);
    
//     var ingredientsData = []
    
//     for (i = 0; i < recipeIngredients.length; i++){
//         ingredientsData.push(Object.entries(recipeIngredients[i]));
//     }
    
//     console.log(ingredientsData)
    
//     for (i = 0; i < ingredientsData.length; i++){
//         var newIngredientRow = "<tr><td>" + ingredientsData[i][0][0] + "</td><td>" + ingredientsData[i][0][1] + "</td><td><button class='remove-ingredient' value='" + ingredientsData[i][0][0] + "/" + ingredientsData[i][0][1] + "'>-</button></td>";
        
//         $(newIngredientRow).insertAfter('.ingredients-table-header');
//     }
// }

function deleteIngredientFromRecipe(){
    $('.remove-ingredient').on("click", function() {
        var thisIngredientID = $(this).val();
        console.log(thisIngredientID);
        
       var recipeID = $('.recipe-id').val()
    
        $.ajax({
            url: '/delete_ingredient_from_recipe/' + recipeID + '/' + thisIngredientID,
            type: 'POST',
            success: function(response) {
            console.log(response);
            },
            error: function(error) {
            console.log(error);
            }
        });
    });
}

// DOCUMENT FUNCTIONS ----------------------------------------------------------

$(document).ready(function(){

    //  This is to close any pop up button...

    $('.hide-me-btn').on("click", function() {
        $('.hide-me').fadeOut("fast")
    });
        
    // This will make the button to confirm and actually delete a recipe appear
    
    $('.delete-recipe-btn').on("click", function() {
        $(this).next().show()
    });
    
    // This runs the update database function on click...
       
    $('.update-recipe-btn').click(function() {
        updateDatabase();
    });
    
});